from mycroft import MycroftSkill, intent_file_handler


class Communications(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.add_event('skill.communications.intercom.new', self.handle_new_intercom)

    def handle_new_intercom(self, message):
        """A intercom was called"""
        # Get the announcement
        announcement = message.data.get("message")
        self.speak_dialog("new.intercom", data={"message": announcement})

    @intent_file_handler('broadcast.intercom.intent')
    def handle_communications(self, message):
        self.speak_dialog('broadcasting.intercom')


def create_skill():
    return Communications()

