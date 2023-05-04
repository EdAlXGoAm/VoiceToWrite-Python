from deep_translator import (GoogleTranslator)
import deepl

import azure.cognitiveservices.speech as speechsdk

#--- Libraries for Azure voice to text real time ---#
from p_libs import lib_Azure_STT_realtime as Az_vtt_rt
#--- Modules for Tkinter GUI ---#
from p_modules import mod_tkinter_STT as tk_STT

#--- Libraries for save in queue ---#
import queue
import threading
import time

#--- Libraries for GUI ---#
import tkinter as tk

class TranslatorThread(threading.Thread):
    def __init__(self, textbox_trnslated, text_queue, language_to, translate_nucleus, speech_nucleus=None, partial=False):
        threading.Thread.__init__(self)
        self.textbox_trnslated = textbox_trnslated
        self.text_queue = text_queue
        self.language_to = language_to
        self.translate_nucleus = translate_nucleus
        self.speech_nucleus = speech_nucleus
        self.partial = partial
        self._stop_event = threading.Event()

        # Set the text color to black
        self.textbox_trnslated.tag_configure("red", foreground="red")
        self.textbox_trnslated.tag_configure("black", foreground="black")

    def run(self):
        color = "black"
        while not self._stop_event.is_set():
            time.sleep(0.5)
            if not self.text_queue.empty():
                text = self.text_queue.get()
                if False:
                    try:
                        translated_text = GoogleTranslator(source='auto', target=self.language_to).translate(
                            text)
                        if self.partial:
                            self.textbox_trnslated.delete(0.0, "end")
                        self.textbox_trnslated.insert(tk.END, translated_text + "\n", color)
                    except Exception:
                        print("unsupported by GoogleTranslate")
                else:
                    try:
                        if self.language_to == "en":
                            self.language_to = "EN-US"
                        elif self.language_to == "es":
                            self.language_to = "ES"
                        translated_text = self.translate_nucleus.translate_text(text, target_lang=self.language_to).text
                        if self.partial:
                            self.textbox_trnslated.delete(0.0, "end")
                        self.textbox_trnslated.insert(tk.END, translated_text + "\n", color)
                    except Exception:
                        print("unsupported by Deepl")
                if not self.partial:
                    self.textbox_trnslated.see(tk.END)
                    # result = self.speech_nucleus.speak_text_async(translated_text).get()
                    if color == "black":
                        color = "red"
                    else:
                        color = "black"

    def stop(self):
        self._stop_event.set()
        print("Thread stopped")

class TextWriterThread(threading.Thread):
    def __init__(self, textbox, text_queue, partial=False, to_translate_queue=None):
        threading.Thread.__init__(self)
        self.textbox = textbox
        self.text_queue = text_queue
        self.partial = partial
        self.to_translate_queue = to_translate_queue if to_translate_queue is not None else None
        self._stop_event = threading.Event()

        # Set the text color to red
        self.textbox.tag_configure("red", foreground="red")
        self.textbox.tag_configure("black", foreground="black")

    def run(self):
        color = "black"
        while not self._stop_event.is_set():
            time.sleep(0.5)
            if not self.text_queue.empty():
                text = self.text_queue.get()
                if self.partial:
                    self.textbox.delete(0.0, "end")
                self.textbox.insert(tk.END, text + "\n", color)
                self.to_translate_queue.put(text)
                if not self.partial:
                    self.textbox.see(tk.END)
                    if color == "black":
                        color = "red"
                    else:
                        color = "black"

    def stop(self):
        self._stop_event.set()
        print("Thread stopped")

def start_stop_Recognizer(SpeechRecognizer, btn, dis_btn, thread=None, thread_partial=None, thread_translator=None, thread_translator_partial=None):
    if btn.cget("text").split()[0] == "Start":
        SpeechRecognizer.start_continuous_recognition()
        if thread is not None:
            thread.start()
            thread_partial.start()
            thread_translator.start()
            thread_translator_partial.start()
        for dis_btn in dis_btn:
            dis_btn.config(state="disabled")
            dis_btn.config(bg="#f7f6f9", fg="black")
        print("STT started")
    else:
        SpeechRecognizer.stop_continuous_recognition()
        if thread is not None:
            thread.stop()
            thread_partial.stop()
            thread_translator.stop()
            thread_translator_partial.stop()
        for dis_btn in dis_btn:
            dis_btn.config(state="normal")
            dis_btn.config(bg="#673ee6", fg="white")
        print("STT stopped")
        
# Function to change the button text
def change_text_btn_lbl_start_stop(language, lbl, btn):
    if btn.cget("text").split()[0] == "Start":
        lbl.config(text="Press to stop")
        btn.config(text="Stop " + language, bg="#fc5084", fg="white")
    else:
        lbl.config(text="Press to start")
        btn.config(text="Start " + language, bg="#673ee6", fg="white")

if __name__ == "__main__":
    # Speech To Text credentials
    # ------------------------------
    STT_key="16ea2c90f3ed45638a3de04014217697"
    STT_region="eastus"
    # Text To Speech credentials
    # ------------------------------
    TTS_key="16ea2c90f3ed45638a3de04014217697"
    TTS_region="eastus"
    # DeepL credentials
    # ------------------------------
    DeepL_key="69a29ffb-4e00-a3e2-5d80-7a3571ba6739:fx"
    # ElevenLabs credentials
    # ------------------------------
    ElevenLabs_key=""

    # Initializing DeepL translator
    DeepL_translator = deepl.Translator(DeepL_key, verify_ssl=False)

    # Initializing Azure SpeechSynthesizer
    speech_config = speechsdk.SpeechConfig(subscription=TTS_key, region=TTS_region)
    speech_config.speech_synthesis_voice_name = "es-MX-DaliaNeural"
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    # Create necessary queues
    text_queue_es_conv = queue.Queue() # Queue to save the text output from the SpeechRecognizer ES
    partial_text_queue_es_conv = queue.Queue() # Queue to save the partial text output from the SpeechRecognizer ES
    to_translate_text_queue_es_conv = queue.Queue() # Queue to save the text to translate ES to EN
    partial_to_translate_text_queue_es_conv = queue.Queue() # Queue to save the partial text to translate ES to EN

    text_queue_en_conv = queue.Queue() # Queue to save the text output from the SpeechRecognizer EN
    partial_text_queue_en_conv = queue.Queue() # Queue to save the partial text output from the SpeechRecognizer EN
    to_translate_text_queue_en_conv = queue.Queue() # Queue to save the text to translate EN to ES
    partial_to_translate_text_queue_en_conv = queue.Queue() # Queue to save the partial text to translate EN to ES
    
    # Create an instance of the SpeechRecognizer class
    # ---- SR in spanish (type_text=True) ----
    SpeechRecognizer_es = Az_vtt_rt.SpeechRecognizer(key=STT_key, region=STT_region, language="es-MX", type_text=True)
    # ---- SR in english (type_text=True) ----
    SpeechRecognizer_en = Az_vtt_rt.SpeechRecognizer(key=STT_key, region=STT_region, language="en-US", type_text=True)
    # ---- SR in spanish (conversation - queue) ----
    SpeechRecognizer_es_conv = Az_vtt_rt.SpeechRecognizer(key=STT_key, region=STT_region, language="es-MX", type_text=False, text_queue=text_queue_es_conv, partial_text=partial_text_queue_es_conv)
    # ---- SR in english (conversation - queue) ----
    SpeechRecognizer_en_conv = Az_vtt_rt.SpeechRecognizer(key=STT_key, region=STT_region, language="en-US", type_text=False, text_queue=text_queue_en_conv, partial_text=partial_text_queue_en_conv)

    # Creating window of the AzureSTTGUI class
    AzureSTTGUI = tk_STT.AzureSTTGUI()
    
    # THREAD: Takes queue text and writes it in the textbox ES
    text_writer_es_conv = TextWriterThread(AzureSTTGUI.frame3.textbox, text_queue_es_conv, to_translate_queue=to_translate_text_queue_es_conv)
    text_writer_es_conv.daemon = True
    # THREAD: Takes queue text, translates it and writes it in the textbox ES
    text_translater_es_conv = TranslatorThread(AzureSTTGUI.frame5.textbox, to_translate_text_queue_es_conv, "en", DeepL_translator, speech_synthesizer)
    text_translater_es_conv.daemon = True
    # THREAD: Takes queue partial text and writes it in the textbox ES - EN
    partial_text_writer_es_conv = TextWriterThread(AzureSTTGUI.frame7.textbox, partial_text_queue_es_conv, partial=True, to_translate_queue=partial_to_translate_text_queue_es_conv)
    partial_text_writer_es_conv.daemon = True
    # THREAD: Takes queue partial text, translates it and writes it in the textbox ES - EN
    partial_text_translater_es_conv = TranslatorThread(AzureSTTGUI.frame8.textbox, partial_to_translate_text_queue_es_conv, "en", DeepL_translator, partial=True)
    partial_text_translater_es_conv.daemon = True

    # THREAD: Takes queue text and writes it in the textbox EN
    text_writer_en_conv = TextWriterThread(AzureSTTGUI.frame4.textbox, text_queue_en_conv, to_translate_queue=to_translate_text_queue_en_conv)
    text_writer_en_conv.daemon = True
    # THREAD: Takes queue text, translates it and writes it in the textbox EN
    text_translater_en_conv = TranslatorThread(AzureSTTGUI.frame6.textbox, to_translate_text_queue_en_conv, "es", DeepL_translator, speech_synthesizer)
    text_translater_en_conv.daemon = True
    # THREAD: Takes queue partial text and writes it in the textbox EN - ES
    partial_text_writer_en_conv = TextWriterThread(AzureSTTGUI.frame7.textbox, partial_text_queue_en_conv, partial=True, to_translate_queue=partial_to_translate_text_queue_en_conv)
    partial_text_writer_en_conv.daemon = True
    # THREAD: Takes queue partial text, translates it and writes it in the textbox EN - ES
    partial_text_translater_en_conv = TranslatorThread(AzureSTTGUI.frame8.textbox, partial_to_translate_text_queue_en_conv, "es", DeepL_translator, partial=True)
    partial_text_translater_en_conv.daemon = True

    # Function to execute the external function and change the button text
    def button_functions_es():
        start_stop_Recognizer(SpeechRecognizer_es, AzureSTTGUI.frame1.button, [AzureSTTGUI.frame2.button, AzureSTTGUI.frame3.button, AzureSTTGUI.frame4.button])
        change_text_btn_lbl_start_stop("es-MX", AzureSTTGUI.frame1.label, AzureSTTGUI.frame1.button)

    def button_functions_en():
        start_stop_Recognizer(SpeechRecognizer_en, AzureSTTGUI.frame2.button, [AzureSTTGUI.frame1.button, AzureSTTGUI.frame3.button, AzureSTTGUI.frame4.button])
        change_text_btn_lbl_start_stop("es-US", AzureSTTGUI.frame2.label, AzureSTTGUI.frame2.button)

    def button_functions_es_conv():
        start_stop_Recognizer(SpeechRecognizer_es_conv, AzureSTTGUI.frame3.button, [AzureSTTGUI.frame1.button, AzureSTTGUI.frame2.button, AzureSTTGUI.frame4.button], text_writer_es_conv, partial_text_writer_es_conv, text_translater_es_conv, partial_text_translater_es_conv)
        change_text_btn_lbl_start_stop("es-MX", AzureSTTGUI.frame3.label, AzureSTTGUI.frame3.button)

    def button_functions_en_conv():
        start_stop_Recognizer(SpeechRecognizer_en_conv, AzureSTTGUI.frame4.button, [AzureSTTGUI.frame1.button, AzureSTTGUI.frame2.button, AzureSTTGUI.frame3.button], text_writer_en_conv, partial_text_writer_en_conv, text_translater_en_conv, partial_text_translater_en_conv)
        change_text_btn_lbl_start_stop("es-US", AzureSTTGUI.frame4.label, AzureSTTGUI.frame4.button)

    # Asign command to button es-MX
    AzureSTTGUI.frame1.button.config(command=button_functions_es)
    # Asign command to button en-US
    AzureSTTGUI.frame2.button.config(command=button_functions_en)
    # Asign command to button es-MX conversation
    AzureSTTGUI.frame3.button.config(command=button_functions_es_conv)
    # Asign command to button en-US conversation
    AzureSTTGUI.frame4.button.config(command=button_functions_en_conv)

    # Start the Tkinter GUI
    AzureSTTGUI.mainloop()