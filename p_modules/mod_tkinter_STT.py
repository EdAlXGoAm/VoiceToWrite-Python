import tkinter as tk

class AzureSTTGUI(tk.Tk):
    def __init__(self, external_button_functions):
        super().__init__()
        self.title("Voice to Write")
        # Set fixed window size
        self.geometry("133x100")
        # Keep the window in the foreground
        self.wm_attributes("-topmost", 1)
        # Disable window rescaling
        self.resizable(False, False)
        self.configure(bg='#e37165')

        # Set the overrideredirect property to True to remove the default title bar
        self.overrideredirect(True)
        # Create a custom frame to simulate a title bar
        self.title_bar = tk.Frame(self, bg='#e98e9c', relief='raised', bd=1)
        # Add a close button to the title bar
        self.close_button = tk.Button(self.title_bar, text='x', command=self.quit, bg='#e98e9c', fg='white', padx=5)
        # Align the close button to the right
        self.close_button.pack(side='right')
        # Add a label to display the window name in the title bar
        self.title_label = tk.Label(self.title_bar, text="Voice to Write", bg='#e98e9c', fg='white', padx=5)
        # Align the label to the left
        self.title_label.pack(side='left')
        # Place the title bar at the top of the window
        self.title_bar.pack(expand=1, fill='x')
        # Function to move the window by dragging the element with the mouse
        def move_window(event):
            self.geometry(f"+{event.x_root}+{event.y_root}")
        # Bind the title bar motion to the move window function
        self.title_bar.bind("<B1-Motion>", move_window)
        # Bind the title label motion to the move window function
        self.title_label.bind("<B1-Motion>", move_window)
        
        # Create a label widget and place it on the window
        self.lbl_run_STT = tk.Label(self, text="Press to start", bg="#1a76d2", fg="white")
        self.lbl_run_STT.pack()

        # Create a button and place it on the window
        self.btn_run_STT = tk.Button(self, text="Start", bg="#f2f8f5", fg="#058527", command=self.button_functions)
        self.btn_run_STT.pack()

        # Provide the external function to the button
        self.external_button_functions = external_button_functions

    # Function to execute the external function and change the button text
    def button_functions(self):
        self.external_button_functions()
        self.change_text()

    # Function to change the button text
    def change_text(self):
        if self.btn_run_STT.cget("text") == "Start":
            self.lbl_run_STT.config(text="Press to stop")
            self.btn_run_STT.config(text="Stop", bg="#f7c3c4", fg="#c02910")
        else:
            self.lbl_run_STT.config(text="Press to start")
            self.btn_run_STT.config(text="Start", bg="#f2f8f5", fg="#058527")