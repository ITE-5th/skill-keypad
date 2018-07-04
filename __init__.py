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
        self.callbacks = {
            0: lambda: send_message_1('caption'),
            1: lambda: send_message_1('caption'),
            2: lambda: self.send_question(),
            3: lambda: send_message_1('face'),
            4: lambda: send_message_1('capture'),
            5: lambda: send_message_1('add'),
            6: lambda: send_message_1('remove'),
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

    def send_question(self):

        phrase_to_say = 'Please say your question'
        question = self.get_phrase(phrase_to_say)
        if question:
            send_message_1('question ' + question)
        else:
            self.speak('unable to get your question')

    def keypad_callback(self, key):
        print(key)
        camera_file = FilePathManager.resolve('/resources/click.wav')
        os.system('aplay -Dhw:0,0 ' + camera_file)

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
