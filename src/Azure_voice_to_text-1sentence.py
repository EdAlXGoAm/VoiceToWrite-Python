import azure.cognitiveservices.speech as speechsdk

# Definir la llave y región de tu servicio de Azure Speech Services
speech_key = "KEY"
service_region = "REGION"

# Configurar el cliente de Speech Services
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language="es-MX")

# Configurar el reconocedor de voz en tiempo real
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

print("Habla ahora...")

# Escuchar el micrófono y transcribir la voz a texto en tiempo real
result = speech_recognizer.recognize_once()

# Imprimir el texto transrito
print(result.text)