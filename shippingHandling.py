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
"""Part of the Communications skill to recieve messages and messagebus them over to the skill, which announces them"""
import time

from mycroft.messagebus.send import send
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser
import ipaddress
import netifaces
import json


def send_communication_to_messagebus(msg_type, msg):
    send("skill.communications.{}.new".format(msg_type), {"message": "{}".format(str(msg))})


def start_receiving_Loop(socket, mycroft_id):
    # Start the forever loop
    while True:
        time.sleep(1)
        msg = socket.recv()
        if msg is not None:
            action = json.loads(str(msg.packets[1]))["action"]
            recipient = json.loads(str(msg.packets[1]))["recipients"]
            # Only react to message if is to me
            if recipient == "all" or recipient == mycroft_id:
                if action == "intercom":
                    # Send to messagebus: intercom
                    send_communication_to_messagebus("intercom", msg.packets[1])
                elif action == "call":
                    # Handle call etc...
                    pass
                # Do more handling here
                else:
                    pass


def start_advertisement_loop(name):
    """Start advertising to other devices about the ip address"""
    # Get the local ip address
    try:
        ip = netifaces.ifaddresses("wlan0").get(netifaces.AF_INET)[0].get("addr")
    except ValueError:
        ip = netifaces.ifaddresses("en0").get(netifaces.AF_INET)[0].get("addr")  # Try with ethernet if there is no ip

    info = ServiceInfo(
        "_http._tcp.local.",
        "Mycroft Communications Skill - {}._http._tcp.local.".format(name),
        addresses=[ipaddress.ip_address(ip).packed],
        port=4444,
        properties={"type": "mycroft_device"},
    )

    zeroconf = Zeroconf()
    # Registering service
    zeroconf.register_service(info)
    try:
        while True:
            time.sleep(0.1)
    finally:
        # Unregister service for whatever reason
        zeroconf.unregister_service(info)
        zeroconf.close()


class MycroftAdvertisimentListener(object):

    def remove_service(self, zeroconf, type, name):
        # We should maybe do something here. Not sure.
        pass

    def add_service(self, zeroconf, service_type, name):
        info = zeroconf.get_service_info(service_type, name)
        if bool(info.properties) and b"type" in info.properties and info.properties.get(b'type') == b"mycroft_device":
            # Get ip address
            ip = str(ipaddress.ip_address(info.addresses[0]))
            send_communication_to_messagebus("device", ip)


def start_new_service_listener_loop(sock):
    """Respond to new services: add them to the database"""
    global socket
    socket = sock
    zeroconf = Zeroconf()
    listener = MycroftAdvertisimentListener()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    try:
        while True:
            pass
    finally:
        zeroconf.close()


def send_message(socket, message, message_type, mycroft_id, mycroft_name, recipient="all"):
    """
    Args: TYPE and Message and WHO FOR (Needed if not intercom"""
    if message_type is not "intercom" and recipient is None:
        # Check that when there is a message, it has a specified recipient
        raise ValueError("[communicationsSkill/shippingHandling] To send a message, you need to specify a recipient")
    message = {"action": message_type, "recipients": recipient, "data": message,
               "sender": {"mycroft_id": mycroft_id,
                          "mycroft_name": mycroft_name}}
    time.sleep(1)
    socket.send(str(json.dumps(message)))
