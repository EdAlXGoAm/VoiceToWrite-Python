#--- Libraries for Azure voice to text real time ---#
from p_libs import lib_Azure_STT_realtime as Az_vtt_rt
#--- Modules for Tkinter GUI ---#
from p_modules import mod_tkinter_STT as tk_STT

def start_stop_Recognizer(SpeechRecognizer, btn, dis_btn):
    if btn.cget("text").split()[0] == "Start":
        SpeechRecognizer.start_continuous_recognition()
        dis_btn.config(state="disabled")
        dis_btn.config(bg="#f7f6f9", fg="black")
        print("STT started")
    else:
        SpeechRecognizer.stop_continuous_recognition()
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
    # Create an instance of the SpeechRecognizer class
    SpeechRecognizer_es = Az_vtt_rt.SpeechRecognizer(key="16ea2c90f3ed45638a3de04014217697", region="eastus", language="es-MX", type_text=True)
    SpeechRecognizer_en = Az_vtt_rt.SpeechRecognizer(key="16ea2c90f3ed45638a3de04014217697", region="eastus", language="en-US", type_text=True)
    # Create an instance of the AzureSTTGUI class
    AzureSTTGUI = tk_STT.AzureSTTGUI()

    # Function to execute the external function and change the button text
    def button_functions_es():
        start_stop_Recognizer(SpeechRecognizer_es, AzureSTTGUI.btn_run_STT_es, AzureSTTGUI.btn_run_STT_en)
        change_text_btn_lbl_start_stop("es-MX", AzureSTTGUI.lbl_run_STT_es, AzureSTTGUI.btn_run_STT_es)

    def button_functions_en():
        start_stop_Recognizer(SpeechRecognizer_en, AzureSTTGUI.btn_run_STT_en, AzureSTTGUI.btn_run_STT_es)
        change_text_btn_lbl_start_stop("es-US", AzureSTTGUI.lbl_run_STT_en, AzureSTTGUI.btn_run_STT_en)

    # Asign command to button es-MX
    AzureSTTGUI.btn_run_STT_es.config(command=button_functions_es)
    # Asign command to button en-US
    AzureSTTGUI.btn_run_STT_en.config(command=button_functions_en)

    # Start the Tkinter GUI
    AzureSTTGUI.mainloop()