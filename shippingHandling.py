"""Part of the Communications skill to recieve messages and messagebus them over to the skill, which announces them"""
import py2p
import time
from mycroft.messagebus.send import send


def send_communication_to_messagebus(msg_type, msg):
    send("skill.communications.{}.new".format(msg_type), {"message": "{}".format(str(msg))})


def startLoop(socket):
    # Get connected
    # Start the forever loop
    while True:
        time.sleep(1)
        msg = socket.recv()
        if msg is not None:
            message = str(msg.packets[1])
            # Send to messagebus
            send_communication_to_messagebus("intercom", message)
