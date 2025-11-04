"""
Script para reconocimiento de voz desde el micrófono usando Azure Speech Services.
"""
import azure.cognitiveservices.speech as speechsdk

def recognize_from_microphone():
    """
    Reconoce una frase desde el micrófono usando Azure Speech Services.
    """
    # Configuración de Azure Speech
    speech_config = speechsdk.SpeechConfig(
        subscription='259e5fd1add44f78ad8275e956740a7a', 
        region='eastus'
    )
    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, 
        audio_config=audio_config
    )

    print("Habla en tu micrófono...")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Reconocido: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No se pudo reconocer el habla: {}".format(
            speech_recognition_result.no_match_details
        ))
        return None
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Reconocimiento de voz cancelado: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Detalles del error: {}".format(cancellation_details.error_details))
            print("¿Configuraste la clave y región del recurso de voz?")
        return None

if __name__ == "__main__":
    recognize_from_microphone()

