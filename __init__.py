# File Path Manager
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import json
import os

from mycroft import MycroftSkill
from mycroft.util.log import LOG
from websocket import create_connection

LOG.warning('Skill Keypad is Running ')

try:
    from .code.keypad import Keypad
except ImportError:
    # re-install yourself
    from msm import MycroftSkillsManager

    msm = MycroftSkillsManager()
    msm.install("https://github.com/ITE-5th/skill-keypad")


class KeypadSkill(MycroftSkill):
    def __init__(self):
        super(KeypadSkill, self).__init__("ImageCaptionSkill")
        self.keypad_client = Keypad()
        self.keypad_client.start(self.keypad_callback)

        self.callbacks = {
            0: lambda: send_message('caption'),
            1: lambda: LOG('NOT DEFINED'),
            2: lambda: LOG('NOT DEFINED'),
            3: lambda: LOG('NOT DEFINED'),
            4: lambda: LOG('NOT DEFINED'),
            5: lambda: LOG('NOT DEFINED'),
            6: lambda: LOG('NOT DEFINED'),
            7: lambda: LOG('NOT DEFINED'),
            8: lambda: LOG('NOT DEFINED'),
            9: lambda: LOG('NOT DEFINED'),
            "A": lambda: os.system('sudo reboot'),
            "B": lambda: os.system('sudo shutdown'),
            "C": lambda: LOG('NOT DEFINED'),
            "D": lambda: LOG('NOT DEFINED'),
            "*": lambda: LOG('NOT DEFINED'),
            "#": lambda: LOG('NOT DEFINED'),
        }

    def keypad_callback(self, key):
        print(key)
        if self.callbacks[key] is not None:
            self.callbacks[key]()

    def stop(self):
        super(KeypadSkill, self).shutdown()
        LOG.info("Keypad Skill CLOSED")
        self.keypad_client.cleanup()


URL_TEMPLATE = "{scheme}://{host}:{port}{path}"


def send_message(message, host="localhost", port=8181, path="/core", scheme="ws"):
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
