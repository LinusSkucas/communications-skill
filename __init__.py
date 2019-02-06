from mycroft import MycroftSkill, intent_file_handler
import requests
import json

class Communications(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.add_event('skill.communications.intercom.new', self.handle_new_intercom)
        # Start the server


    def get_ips(self, message_type):
        """Get the ip addresses of Mycroft devices
        Returns a list of ip addresses with ports
        """
        #Get the ips
        # todo: tell user to set up device
        if message_type == "intercom":
            mycroft_ips = self.settings.get("mycroft_ips")
            self.log.info("Intercom")
            self.settings["mycroft_ips"] = ["10.0.1.36"]

        # TODO: do a messaging - Only find one ip

        ips = []

        # add ports
        for ip in mycroft_ips:
            ips.append(self._add_port(ip))

        return ips


    def _add_port(self, ip):
        """Adds the port to the ip address"""
        # todo: Should make this port configurable
        return ip +":8090"

    def _make_request(self, server, url, message):
        """make the request to the other web servers"""
        requests.post("http://"+server+url, json={"message": message})

    def make_request(self, servers, url, message):
        """Send multiple requests to multiple servers"""
        for server in servers:
            self._make_request(server, url, message)

    def send_message(self, message, message_type):
        """Send messages to other devices
        Intercom -> To all devices
        Messaging -> To a specific device
        """
        if message_type == "intercom":
            mycroft_ips = self.get_ips(message_type)
            self.make_request(mycroft_ips, "/communications/intercom/new", message)
        elif message_type == "message":
            pass

    def handle_new_intercom(self, message):
        """A intercom was called"""
        # Get the announcement
        announcement = message.data.get("message")
        self.speak_dialog("new.intercom", data={"message": announcement})

    @intent_file_handler('broadcast.intercom.intent')
    def handle_communications(self, message):
        # Get the announcement
        announcement = message.data.get("announcement")
        while not announcement:
            announcement = self.get_response("make.new.announcement")

        # OKay, we got the announcement
        # Time to send the message to all...
        self.send_message(announcement, "intercom")

        self.speak_dialog('broadcasting.intercom')


def create_skill():
    return Communications()

