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
        while self.moving:
            # Mueve el mouse a la izquierda
            pyautogui.move(-2, 0, duration=0.1)
            time.sleep(1)
            
            # Mueve el mouse a la derecha
            pyautogui.move(2, 0, duration=0.1)
            time.sleep(1)