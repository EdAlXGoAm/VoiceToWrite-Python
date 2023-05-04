#--- Libraries for type text with pyautogui ---#
from p_libs import lib_PyAutoGUI_type as PyAGUI_w
#--- Libraries for save in queue ---#
import queue

import azure.cognitiveservices.speech as speechsdk

class SpeechRecognizer:
    def __init__(self, key, region, language, type_text, text_queue=None):
        self.key = key
        self.region = region
        self.language = language
        self.type_text = type_text
        self.text_queue = text_queue if text_queue is not None else queue.Queue()
        self.speech_config = speechsdk.SpeechConfig(subscription=self.key, region=self.region, speech_recognition_language=self.language)
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)
        self.speech_recognizer.recognized.connect(self.speech_recognized)
    
    # Start continuous speech recognition
    def start_continuous_recognition(self):
        self.speech_recognizer.start_continuous_recognition()

    # Stop continuous speech recognition
    def stop_continuous_recognition(self):
        self.speech_recognizer.stop_continuous_recognition()

    # Callback function for continuous speech recognition
    def speech_recognized(self, evt):
        text = evt.result.text
        # Print the text captured by the microphone
        print("Texto reconocido: {}".format(text))
        # Type the text captured by the microphone
        if self.type_text:
            PyAGUI_w.type_text(text)
        else:
            self.text_queue.put(text)
