from deep_translator import (GoogleTranslator)

#--- Libraries for Azure voice to text real time ---#
from p_libs import lib_Azure_STT_realtime as Az_vtt_rt
#--- Modules for Tkinter GUI ---#
from p_modules import mod_tkinter_STT as tk_STT

#--- Libraries for save in queue ---#
import queue
import threading

import tkinter as tk

class TextWriterThread(threading.Thread):
    def __init__(self, textbox, text_queue, textbox_trnslated, language_to):
        threading.Thread.__init__(self)
        self.textbox = textbox
        self.text_queue = text_queue
        self.textbox_trnslated = textbox_trnslated
        self.language_to = language_to
        self._stop_event = threading.Event()

        # Set the text color to red
        self.textbox.tag_configure("red", foreground="red")
        self.textbox.tag_configure("black", foreground="black")
        # Set the text color to black
        self.textbox_trnslated.tag_configure("red", foreground="red")
        self.textbox_trnslated.tag_configure("black", foreground="black")

    def run(self):
        color = "red"
        while not self._stop_event.is_set():
            if not self.text_queue.empty():
                if color == "red":
                    color = "black"
                else:
                    color = "red"
                text = self.text_queue.get()
                self.textbox.insert(tk.END, text + "\n", color)
                self.textbox.see(tk.END)
                try:
                    translated_text = GoogleTranslator(source='auto', target=self.language_to).translate(
                        text)
                    self.textbox_trnslated.insert(tk.END, translated_text + "\n", color)
                except Exception:
                    print("unsupported by GoogleTranslate")

    def stop(self):
        self._stop_event.set()

def start_stop_Recognizer(SpeechRecognizer, btn, dis_btn, thread=None):
    if btn.cget("text").split()[0] == "Start":
        SpeechRecognizer.start_continuous_recognition()
        if thread is not None:
            thread.start()
        for dis_btn in dis_btn:
            dis_btn.config(state="disabled")
            dis_btn.config(bg="#f7f6f9", fg="black")
        print("STT started")
    else:
        SpeechRecognizer.stop_continuous_recognition()
        if thread is not None:
            thread.stop()
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
    # Create a stack to store the text
    text_queue_es_conv = queue.Queue()
    text_queue_en_conv = queue.Queue()
    # Create an instance of the SpeechRecognizer class
    SpeechRecognizer_es = Az_vtt_rt.SpeechRecognizer(key="16ea2c90f3ed45638a3de04014217697", region="eastus", language="es-MX", type_text=True)
    SpeechRecognizer_en = Az_vtt_rt.SpeechRecognizer(key="16ea2c90f3ed45638a3de04014217697", region="eastus", language="en-US", type_text=True)
    SpeechRecognizer_es_conv = Az_vtt_rt.SpeechRecognizer(key="16ea2c90f3ed45638a3de04014217697", region="eastus", language="es-MX", type_text=False, text_queue=text_queue_es_conv)
    SpeechRecognizer_en_conv = Az_vtt_rt.SpeechRecognizer(key="16ea2c90f3ed45638a3de04014217697", region="eastus", language="en-US", type_text=False, text_queue=text_queue_en_conv)
    # Create an instance of the AzureSTTGUI class
    AzureSTTGUI = tk_STT.AzureSTTGUI()
    
    text_writer_es_conv = TextWriterThread(AzureSTTGUI.frame3.textbox, text_queue_es_conv, AzureSTTGUI.frame5.textbox, "en")
    text_writer_es_conv.daemon = True
    text_writer_en_conv = TextWriterThread(AzureSTTGUI.frame4.textbox, text_queue_en_conv, AzureSTTGUI.frame6.textbox, "es")
    text_writer_en_conv.daemon = True

    # Function to execute the external function and change the button text
    def button_functions_es():
        start_stop_Recognizer(SpeechRecognizer_es, AzureSTTGUI.frame1.button, [AzureSTTGUI.frame2.button, AzureSTTGUI.frame3.button, AzureSTTGUI.frame4.button])
        change_text_btn_lbl_start_stop("es-MX", AzureSTTGUI.frame1.label, AzureSTTGUI.frame1.button)

    def button_functions_en():
        start_stop_Recognizer(SpeechRecognizer_en, AzureSTTGUI.frame2.button, [AzureSTTGUI.frame1.button, AzureSTTGUI.frame3.button, AzureSTTGUI.frame4.button])
        change_text_btn_lbl_start_stop("es-US", AzureSTTGUI.frame2.label, AzureSTTGUI.frame2.button)

    def button_functions_es_conv():
        start_stop_Recognizer(SpeechRecognizer_es_conv, AzureSTTGUI.frame3.button, [AzureSTTGUI.frame1.button, AzureSTTGUI.frame2.button, AzureSTTGUI.frame4.button], text_writer_es_conv)
        change_text_btn_lbl_start_stop("es-MX", AzureSTTGUI.frame3.label, AzureSTTGUI.frame3.button)

    def button_functions_en_conv():
        start_stop_Recognizer(SpeechRecognizer_en_conv, AzureSTTGUI.frame4.button, [AzureSTTGUI.frame1.button, AzureSTTGUI.frame2.button, AzureSTTGUI.frame3.button], text_writer_en_conv)
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