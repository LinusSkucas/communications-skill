from mycroft import MycroftSkill, intent_file_handler
# TODO: import new client code

class Communications(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.add_event('skill.communications.intercom.new', self.handle_new_intercom)  # TODO: Get recieving code to messagebus message here
        # Start the server

    def send_intercom(self, message):
        """Send messages to all other devices
        """
        # TODO: Connect to new sending code
        pass

    def handle_new_intercom(self, message):
        """A intercom was called"""
        # Get the announcement
        announcement = message.data.get("message")
        # TODO: Make a bling sound!
        self.speak_dialog("new.intercom", data={"message": announcement})

    @intent_file_handler('broadcast.intercom.intent')
    def handle_communications(self, message):
        # Get the announcement
        announcement = message.data.get("announcement")
        while not announcement:
            announcement = self.get_response("get.new.announcement.name.dialog")

        # OKay, we got the announcement
        # Time to send the message to all...
        self.send_message(announcement, "intercom")
        self.speak_dialog('broadcasting.intercom')


def create_skill():
    return Communications()

