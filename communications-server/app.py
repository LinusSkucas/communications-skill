from flask import Flask, request
from mycroft.messagebus.send import send
import json

app = Flask(__name__)


def send_communication_to_messagebus(msg_type, msg):
    send("skill.communications.{}.new".format(msg_type), {"message": "{}".format(str(msg))})


@app.route('/communications/<msg_type>/new', methods=['POST'])
def new_message(msg_type):
    """When someone sent a new message to the computer
    format:
    THe<type> is the type of message( intercom, call, video, message)
    the message is {message: message, computer:the computer from where it was sent}
    """
    # TODO: need authentication header
    message = request.get_json(force=True)
    message = message['message']
    send_communication_to_messagebus(msg_type=str(msg_type), msg=str(message))

    return "200"



# app.run(host="0.0.0.0", port=8090, debug=False)
