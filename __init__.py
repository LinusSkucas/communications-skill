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
import threading
import py2p
from mycroft import MycroftSkill, intent_file_handler
from mycroft.api import DeviceApi
from mycroft.util.parse import match_one, normalize
import string
import json
import time

from . import shippingHandling


class Communications(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.devices = []
        self.devices_recognizion = {}

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
        """Lowercase and normalize any strings get rid of puncuations :)"""
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
        announcement = json.loads(message.data.get("message"))["data"]
        self.log.info("New intercom announcement incoming!: {}".format(announcement))
        # Make a BLING sound (Might want to change this)
        self.acknowledge()
        self.speak_dialog("new.intercom", data={"message": announcement})

    def handle_new_message(self, message):
        """A message was received"""
        announcement = message.data.get("message")
        sender = message.data.get("sender")

        self.log.info("New intercom message incoming!: {}".format(announcement))
        # Make a BLING sound (Might want to change this)
        self.acknowledge()
        self.speak_dialog("new.message", data={"message": announcement, "sender": sender})

    def handle_new_device(self, message):
        ip = message.data.get("message")["ip"]
        name = message.data.get("message")["name"]
        description = message.data.get("message")["description"]
        uuid = message.data.get("message")["uuid"]
        self.log.info("New Mycroft Communications device at: {}".format(ip))
        self.sock.connect(str(ip), 4445)
        self.devices.append({"ip": ip, "name": name, "uuid": uuid, "description": description})  # Add to device list
        for device in self.devices:
            self.devices_recognizion[str(self._get_ready(device.get("name")))] = str(device.get("uuid"))
            self.devices_recognizion[str(self._get_ready(device.get("description")))] = str(device.get("uuid"))
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
        device = message.data.get("device")
        while not device:
            device = self.get_response("get.device.name.message")

        device_id, confidence = match_one(device, self.devices_recognizion)
        if confidence < 0.6:
            return

        announcement = message.data.get("message")
        while not announcement:
            announcement = self.get_response("get.new.announcement.name")

        intercom_names = self.translate_list("intercom.device.names")
        if device in intercom_names:
            self.send_intercom(announcement)
            self.speak_dialog("broadcasting.intercom")
            return

        self.send_message(message, device_id)
        self.speak_dialog("message.sending")



def create_skill():
    return Communications()
