# File Path Manager
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import json
import os
import time

from mycroft import MycroftSkill
from mycroft.util.log import LOG
from websocket import create_connection

from .file_path_manager import FilePathManager

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

    def callback_fn(self, command):
        try:
            command_strip__lower = command.strip().lower()
            if command_strip__lower == "":
                return None

            # if command_strip__lower == 'shutdown':
            #     return lambda: os.system('systemctl poweroff -i')
            #
            # if command_strip__lower == 'reboot':
            #     return lambda: os.system('reboot')

            return lambda: send_message(command)
        except:
            return None

    def get_callbacks(self):
        return {
            0: self.callback_fn(self.settings.get("key_0", "")),
            1: self.callback_fn(self.settings.get("key_1", "")),
            2: self.callback_fn(self.settings.get("key_2", "")),
            3: self.callback_fn(self.settings.get("key_3", "")),
            4: self.callback_fn(self.settings.get("key_4", "")),
            5: self.callback_fn(self.settings.get("key_5", "")),
            6: self.callback_fn(self.settings.get("key_6", "")),
            7: self.callback_fn(self.settings.get("key_7", "")),
            8: self.callback_fn(self.settings.get("key_8", "")),
            9: self.callback_fn(self.settings.get("key_9", "")),
            "A": self.callback_fn(self.settings.get("key_a", "")),
            "B": self.callback_fn(self.settings.get("key_b", "")),
            "C": self.callback_fn(self.settings.get("key_c", "")),
            "D": self.callback_fn(self.settings.get("key_d", "")),
            "*": self.callback_fn(self.settings.get("key_star", "")),
            "#": self.callback_fn(self.settings.get("key_hash", "")),
        }

    def keypad_callback(self, key):
        print(key)

        if (self.last_msg_time + sleep_time) < time.time():
            self.last_msg_time = time.time()
            callbacks = self.get_callbacks()
            if callbacks[key] is not None:
                click_file = FilePathManager.resolve('/resources/click.wav')
                os.system('aplay -Dhw:0,0 ' + click_file)
                callbacks[key]()
            else:
                LOG.warning('NOT DEFINED')
        else:
            LOG.warning('Ignoring')

    def stop(self):
        super(KeypadSkill, self).shutdown()
        LOG.warning("Keypad Skill CLOSED")
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
