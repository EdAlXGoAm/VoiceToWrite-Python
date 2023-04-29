#--- Libraries for Azure voice to text real time ---#
from p_libs import lib_Azure_STT_realtime as Az_vtt_rt
#--- Modules for Tkinter GUI ---#
from p_modules import mod_tkinter_STT as tk_STT

def start_stop_Recognizer():
    if AzureSTTGUI.btn_run_STT.cget("text") == "Start":
        SpeechRecognizer.start_continuous_recognition()
        print("STT started")
    else:
        SpeechRecognizer.stop_continuous_recognition()
        print("STT stopped")

if __name__ == "__main__":
    # Create an instance of the SpeechRecognizer class
    SpeechRecognizer = Az_vtt_rt.SpeechRecognizer(key="16ea2c90f3ed45638a3de04014217697", region="eastus", language="es-MX", type_text=True)
    # Create an instance of the AzureSTTGUI class
    AzureSTTGUI = tk_STT.AzureSTTGUI(start_stop_Recognizer)
    # Start the Tkinter GUI
    AzureSTTGUI.mainloop()