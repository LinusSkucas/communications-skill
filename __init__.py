# Copyright 2020 Linus S.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from mycroft import MycroftSkill, intent_file_handler, intent_handler
from mycroft.api import DeviceApi
from mycroft.util.parse import match_one, normalize
from adapt.intent import IntentBuilder
import threading
import py2p
import string
import json
import time

from . import shippingHandling


class Communications(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.devices = []
        self.devices_recognition = {}

    def initialize(self):
        self.add_event('skill.communications.intercom.new',
                       self.handle_new_intercom)
        self.add_event('skill.communications.device.new',
                       self.handle_new_device)
        self.add_event('skill.communications.message.new',
                       self.handle_new_message)
        # Start the server/ get the socket
        self.sock = py2p.MeshSocket("0.0.0.0", 4445)
        self.log.info("Starting the receiving loop...")
        # Start up a new thread for receiving messages
        self.device = DeviceApi().get()
        r = threading.Thread(target=shippingHandling.start_receiving_Loop, args=(self.sock, self.device["uuid"],),
                             daemon=True)
        r.start()
        # Auto connect to others:
        # Start new advertisement thread
        self.log.info("Starting the device advertisement thread...")
        a = threading.Thread(target=shippingHandling.start_advertisement_loop, args=(self.device["name"],
                                                                                     self.device["uuid"],
                                                                                     self.device["description"],),
                             daemon=True)
        a.start()
        # Begin Listener thread
        self.log.info("Starting the listener thread...")
        L = threading.Thread(target=shippingHandling.start_new_service_listener_loop, args=(self.sock,), daemon=True)
        L.start()

    def _get_ready(self, utter):
        """Lowercase and normalize any strings get rid of punctuations :)"""
        return normalize(utter, remove_articles=True).lower().translate({ord(c): None for c in string.punctuation})

    def send_intercom(self, message):
        """Send messages to all other devices
        """
        shippingHandling.send_message(self.sock, message, message_type="intercom",
                                      mycroft_id=self.device["uuid"], mycroft_name=self.device["name"])

    def send_message(self, message, device_id):
        shippingHandling.send_message(self.sock, message, message_type="message", mycroft_id=self.device["uuid"],
                                      mycroft_name=self.device["name"], recipient=device_id)

    def handle_new_intercom(self, message):
        """A intercom was called"""
        # Get the announcement
        data = message.data.get("data")
        sender_name = message.data.get("sender_name")
        sender_id = message.data.get("sender_id")

        self.log.info("New intercom announcement incoming!: {}".format(data))
        # Make a BLING sound (Might want to change this)
        self.acknowledge()
        self.speak_dialog("new.intercom", data={"message": data})
        self.set_reply_contexts(sender_id=sender_id, sender_name=sender_name)

    def handle_new_message(self, message):
        """A message was received"""
        data = message.data.get("data")
        sender_name = message.data.get("sender_name")
        sender_id = message.data.get("sender_id")

        self.log.info("New intercom message incoming!: {}".format(data))
        # Make a BLING sound (Might want to change this)
        self.acknowledge()
        self.speak_dialog("new.message", data={"message": data, "sender": sender_name})
        self.set_reply_contexts(sender_id=sender_id, sender_name=sender_name)

    def set_reply_contexts(self, sender_id, sender_name):
        """Set the reply contexts so users can reply. These are set as recipient..."""
        self.set_context("recipient_id", sender_id)
        self.set_context("recipient_name", sender_name)

    def handle_new_device(self, message):
        ip = message.data.get("ip")
        name = message.data.get("name")
        description = message.data.get("description")
        uuid = message.data.get("uuid")
        self.log.info("New Mycroft Communications device at: {}".format(ip))
        self.sock.connect(str(ip), 4445)
        self.devices.append({"ip": ip, "name": name, "uuid": uuid, "description": description})  # Add to device list
        for device in self.devices:
            self.devices_recognition[str(self._get_ready(device.get("name")))] = str(device.get("uuid"))
            self.devices_recognition[str(self._get_ready(device.get("description")))] = str(device.get("uuid"))
        self.log.info("Done connecting to device")

    @intent_file_handler('broadcast.intercom.intent')
    def handle_intercom(self, message):
        # Get the announcement
        announcement = message.data.get("announcement")
        while not announcement:
            announcement = self.get_response("get.new.announcement.name")

        # OKay, we got the announcement
        # Time to send the message to all...
        self.send_intercom(announcement)
        self.speak_dialog('broadcasting.intercom')

    @intent_file_handler('message.intent')
    def handle_message(self, message):
        intercom = False
        device = message.data.get("device")
        while not device:
            device = self.get_response("get.device.name.message")

        # Check if the user wants to send an intercom
        intercom_names = self.translate_list("intercom.device.names")
        if device in intercom_names:
            intercom = True

        device_id, confidence = match_one(device, self.devices_recognition)
        if confidence < 0.6 and not intercom:
            return

        announcement = message.data.get("message")
        while not announcement:
            announcement = self.get_response("get.new.announcement.name")
        if intercom:
            self.send_intercom(announcement)
            self.speak_dialog("broadcasting.intercom")
            return
        self.send_message(announcement, device_id)
        self.speak_dialog("message.sending")

    @intent_handler(IntentBuilder("ReplyIntent").require("Respond").require("recipient_name")
                    .require("recipient_id").optionally("Message"))
    def handle_respond(self, message):
        recipient_name = message.data.get("recipient_name")
        recipient_id = message.data.get("recipient_id")
        reply_message = self.get_response(dialog="reply.message", data={"name": recipient_name}, num_retries=2)
        if reply_message is None:
            return
        self.send_message(message=reply_message, device_id=recipient_id)
        self.speak_dialog("message.sending")


def create_skill():
    return Communications()
