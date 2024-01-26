# text2speech.py

import pyttsx3

from typing import Literal

# LOCAL IMPORTS
from .config import config

class Text2Speech():
    def __init__(self, gender:Literal["male", "female"]="female"):
        self.__engine = pyttsx3.init()

        try:
            # Set the voice
            self.__voice_id = config.read("text2speech", gender)
        except:
            # Default voice in case there was a config exception
            self.__voice_id = self.__engine.getProperty('voices')[0]
        
    def say(self, text):
        self.__engine.setProperty('voice', self.__voice_id)
        self.__engine.say(text)
        self.__engine.runAndWait()
        self.__engine.stop()
        
    def stop(self):
        self.__engine.stop()        
        
    # TODO: Add functionality for pause also, with the button icon changed
        
# # DEBUGGING
# if __name__ == "__main__":
#     t = Text2Speech()
#     t.say("Hello world")
    