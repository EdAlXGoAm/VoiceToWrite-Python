import pyautogui
from unidecode import unidecode

# Type text with pyautogui
class type_text:
    def __init__(self, text):
        self.text = text
        # Decode text to remove accents
        unaccented_text = unidecode(text)
        # Type the text
        pyautogui.typewrite(unaccented_text)