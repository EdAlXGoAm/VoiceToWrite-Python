import azure.cognitiveservices.speech as speechsdk

speech_key = "KEY"
service_region = "REGION"

# Configuramos el reconocimiento de voz
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language="es-MX")
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# Creamos el objeto del reconocimiento de voz y definimos el evento que se ejecutará cada vez que se detecte un resultado
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

def speech_recognized(evt):
    text = evt.result.text
    print("Texto reconocido: {}".format(text))

# Asociamos el evento al reconocedor de voz
speech_recognizer.recognized.connect(speech_recognized)

# Iniciamos el reconocimiento de voz en tiempo real
speech_recognizer.start_continuous_recognition()

# Esperamos a que el usuario presione una tecla para detener el reconocimiento
input("Presiona cualquier tecla para detener el reconocimiento de voz...\n")

# Paramos el reconocimiento de voz
speech_recognizer.stop_continuous_recognition()