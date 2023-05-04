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

        class create_frame(tk.Frame):
            def __init__(self, parent, label_text, button_text):
                super().__init__(parent, bg='#f4f5ff')
                self.grid(padx=5, pady=5, sticky='nsew')

                self.label = tk.Label(self, text=label_text)
                self.label.grid(row=0, column=0, padx=5, pady=5)

                self.button = tk.Button(self, text=button_text, bg="#673ee6", fg="white")
                self.button.grid(row=1, column=0, padx=5, pady=5)

                self.textbox = tk.Text(self, width=50, height=10, wrap="word", font=self.master.custom_font)
                self.textbox.grid(row=2, column=0, padx=5, pady=5)

        # Frame 1:
        self.frame1 = create_frame(self, "Press to start", "Start es-MX")
        self.frame1.grid(row=0, column=0, padx=5, pady=5)

        # Frame 2:
        self.frame2 = create_frame(self, "Press to start", "Start en-US")
        self.frame2.grid(row=0, column=1, padx=5, pady=5)

        # Frame 3:
        self.frame3 = create_frame(self, "Press to start", "Start es-MX")
        self.frame3.grid(row=1, column=0, padx=5, pady=5)

        # Frame 4:
        self.frame4 = create_frame(self, "Press to start", "Start en-US")
        self.frame4.grid(row=1, column=1, padx=5, pady=5)

    def close(self):
        # Event to close the window
        self.quit()