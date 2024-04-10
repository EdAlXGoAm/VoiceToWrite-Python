import pyautogui
import time
import threading

class MoveMouse:
    def __init__(self):
        self.moving = False
        self.thread = None

    def start(self):
        self.moving = True
        self.thread = threading.Thread(target=self.move_mouse)
        self.thread.start()

    def stop(self):
        self.moving = False
        self.thread.join()

    def move_mouse(self):
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {
            "photo": open(image_path, "rb")
        }
        data = {
            "chat_id": chat_id,
            "caption": message
        }
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Mensaje enviado con éxito.")
        else:
            print(f"Error al enviar el mensaje. Código de respuesta: {response.status_code}")