# Copyright 2019 Linus S.
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

from . import shippingHandling


class Communications(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.add_event('skill.communications.intercom.new',
                       self.handle_new_intercom)
        # Start the server/ get the socket
        self.sock = py2p.MeshSocket("0.0.0.0", 4444)
        self.log.info("Starting the receiving loop...")
        # Start up a new thread for recieveing messages
        t = threading.Thread(target=shippingHandling.startLoop, args=(self.sock,), daemon=True)
        t.start()
        # TODO: Auto connect to others

    def send_intercom(self, message):
        """Send messages to all other devices
        """
        shippingHandling.send_message(self.sock, message, message_type="intercom")

    def handle_new_intercom(self, message):
        """A intercom was called"""
        # Get the announcement
        announcement = message.data.get("message")
        self.log.info("New intercom announcement incoming!: {}".format(announcement))
        # Make a BLING sound (Might want to change this)
        self.acknowledge()
        self.speak_dialog("new.intercom", data={"message": announcement})

    @intent_file_handler('broadcast.intercom.intent')
    def handle_communications(self, message):
        # Get the announcement
        announcement = message.data.get("announcement")
        while not announcement:
            announcement = self.get_response("get.new.announcement.name")

        # OKay, we got the announcement
        # Time to send the message to all...
        self.send_intercom(announcement)
        self.speak_dialog('broadcasting.intercom')


def create_skill():
    return Communications()
