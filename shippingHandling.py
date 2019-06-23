"""Part of the Communications skill to recieve messages and messagebus them over to the skill, which announces them"""
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


def send_message(socket, message, message_type, recipients=None):
    """TODO: REVAMP: People, intercom, specific devices
    Args: TYPE and Message and WHO FOR (Needed if not intercom"""
    if message_type is not "intercom" and recipients is None:
        # Check that when there is a message, it has a specified recipient
        raise ValueError("[communicationsSkill/shippingHandling] To send a message, you need to specify a recipient")
    # TODO: change so that we can support more than just intercom and just one device
    time.sleep(1)
    if message_type is "intercom":
        # send intercom message
        socket.send(str(message))
