from mycroft import MycroftSkill, intent_file_handler


class Communications(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('communications.intent')
    def handle_communications(self, message):
        self.speak_dialog('communications')


def create_skill():
    return Communications()

