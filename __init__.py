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
