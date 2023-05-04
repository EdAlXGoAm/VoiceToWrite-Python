import tkinter as tk
from tkinter import font

class AzureSTTGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice to Write")
        self.protocol("WM_DELETE_WINDOW", self.close)
        # Set fixed window size
        self.geometry("900x800")

        self.custom_font = font.Font(family="Calibri", size=12)

        # Keep the window in the foreground
        self.wm_attributes("-topmost", 1)
        # Disable window rescaling
        self.resizable(False, False)
        self.configure(bg='#fbfafb')

        # Frame 1:
        # ----------------------------------

        # Create a frame for the first label and button
        frame1 = tk.Frame(self, bg='#f4f5ff')
        frame1.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        # Create a label widget and place it on the window
        self.lbl_run_STT_es = tk.Label(frame1, text="Press to start")
        self.lbl_run_STT_es.grid(row=0, column=0, padx=5, pady=5)

        # Create a button and place it on the window
        self.btn_run_STT_es = tk.Button(frame1, text="Start es-MX", bg="#673ee6", fg="white")
        self.btn_run_STT_es.grid(row=1, column=0, padx=5, pady=5)

        # Create a text box widget and place it on the window
        self.txt_run_STT_es = tk.Text(frame1, width=50, height=10, wrap="word", font=self.custom_font)
        self.txt_run_STT_es.grid(row=2, column=0, padx=5, pady=5)

        # Frame 2:
        # ----------------------------------

        # Create a frame for the second label and button
        frame2 = tk.Frame(self, bg='#f4f5ff')
        frame2.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        # Create a label widget and place it on the window
        self.lbl_run_STT_en = tk.Label(frame2, text="Press to start")
        self.lbl_run_STT_en.grid(row=0, column=0, padx=5, pady=5)

        # Create a button and place it on the window
        self.btn_run_STT_en = tk.Button(frame2, text="Start en-US", bg="#673ee6", fg="white")
        self.btn_run_STT_en.grid(row=1, column=0, padx=5, pady=5)

        # Create a text box widget and place it on the window
        self.txt_run_STT_en = tk.Text(frame2, width=50, height=10, wrap="word", font=self.custom_font)
        self.txt_run_STT_en.grid(row=2, column=0, padx=5, pady=5)

    def close(self):
        # Event to close the window
        self.quit()