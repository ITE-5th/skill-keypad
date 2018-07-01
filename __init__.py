# File Path Manager
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import json
import os
import time

from mycroft import MycroftSkill
from mycroft.util.log import LOG
from websocket import create_connection

LOG.warning('Skill Keypad is Running ')

try:
    from .code.keypad import Keypad
    from mycroft.messagebus.client.ws import WebsocketClient
    from mycroft.messagebus.message import Message
except ImportError:
    # re-install yourself
    from msm import MycroftSkillsManager

    msm = MycroftSkillsManager()
    msm.install("https://github.com/ITE-5th/skill-keypad")

sleep_time = 1


class KeypadSkill(MycroftSkill):
    def __init__(self):
        super(KeypadSkill, self).__init__("ImageCaptionSkill")
        self.keypad_client = Keypad()
        self.keypad_client.start(self.keypad_callback)
        self.last_msg_time = 0
        self.callbacks = {
            0: lambda: send_message_1('caption'),
            1: lambda: send_message_1('question what is this'),
            2: lambda: send_message_1('face'),
            3: None,
            4: None,
            5: None,
            6: None,
            7: None,
            8: None,
            9: None,
            "A": lambda: os.system('reboot'),
            "B": lambda: os.system('systemctl poweroff -i'),
            "C": None,
            "D": None,
            "*": None,
            "#": None,
        }

    def keypad_callback(self, key):
        print(key)
        if (self.last_msg_time + sleep_time) < time.time():
            self.last_msg_time = time.time()
            if self.callbacks[key] is not None:
                self.callbacks[key]()
            else:
                LOG.warning('NOT DEFINED')
        else:
            LOG.warning('Ignoring')

    def stop(self):
        super(KeypadSkill, self).shutdown()
        LOG.warning("Keypad Skill CLOSED")
        self.keypad_client.cleanup()


def send_message(message):
    def onConnected(event=None):
        LOG.warning("Connected, speaking to Mycroft...'" + message + "'")
        messagebusClient.emit(
            Message("recognizer_loop:utterance",
                    data={'utterances': [message]}))
        LOG.warning("sent!")
        messagebusClient.close()
        exit()

    # Establish a connection with the messagebus
    LOG.info("Creating client")
    messagebusClient = WebsocketClient()
    messagebusClient.on('connected', onConnected)


URL_TEMPLATE = "{scheme}://{host}:{port}{path}"


def send_message_1(message, host="localhost", port=8181, path="/core", scheme="ws"):
    payload = json.dumps({
        "type": "recognizer_loop:utterance",
        "context": "",
        "data": {
            "utterances": [message]
        }
    })
    url = URL_TEMPLATE.format(scheme=scheme, host=host, port=str(port), path=path)
    ws = create_connection(url)
    ws.send(payload)
    ws.close()


def create_skill():
    return KeypadSkill()
