#! python3.7

"""
Script para transcribir y traducir audio del micrófono en tiempo real usando OpenAI Whisper.
Captura audio del micrófono, lo transcribe con Whisper y lo traduce con GPT-4.
"""

import argparse
import os
import numpy as np
import speech_recognition as sr
from openai import OpenAI
import torch
import tempfile
import wave

from datetime import datetime, timedelta, UTC
from queue import Queue
from time import sleep
from sys import platform


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    parser.add_argument("--target_language", default="español",
                        help="Language to translate the transcription to.", type=str)
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    # Configurar el cliente de OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY no está configurada.")
        print("Por favor, configura la variable de entorno OPENAI_API_KEY:")
        print("  Windows: set OPENAI_API_KEY=tu_clave_aqui")
        print("  Linux/Mac: export OPENAI_API_KEY=tu_clave_aqui")
        return
    
    client = OpenAI(api_key=openai_api_key)

    # El idioma al que se traducirá
    target_language = args.target_language

    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # Bytes object which holds audio data for the current phrase
    phrase_bytes = bytes()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    # Important for linux users.
    # Prevents permanent application hang and crash by using the wrong Microphone
    if 'linux' in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == 'list':
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"Microphone with name \"{name}\" found")
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=16000)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    transcription = []
    translations = []

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Función para traducir texto usando GPT-4.1-nano
    def translate_text(text, target_language):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": f"Eres un traductor que convierte texto del inglés al {target_language}. Traduce solamente el texto, sin añadir comentarios ni explicaciones."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error en la traducción: {str(e)}")
            return f"[Error de traducción: {str(e)}]"

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Cue the user that we're ready to go.
    print("Ready to transcribe.\n")

    while True:
        try:
            now = datetime.now(UTC)
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_bytes = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now
                
                # Combine audio data from queue
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()

                # Add the new audio data to the accumulated data for this phrase
                phrase_bytes += audio_data

                # Crear un archivo temporal WAV
                temp_wav = None
                try:
                    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                    temp_wav_name = temp_wav.name
                    temp_wav.close()  # Cerramos el archivo primero para evitar problemas de permisos
                    
                    with wave.open(temp_wav_name, 'wb') as wf:
                        wf.setnchannels(1)  # Mono
                        wf.setsampwidth(2)  # 2 bytes per sample
                        wf.setframerate(16000)  # 16kHz
                        wf.writeframes(phrase_bytes)
                    
                    # Usar la API de OpenAI para transcribir con la nueva API v1.0.0
                    try:
                        with open(temp_wav_name, "rb") as audio_file:
                            # Utilizamos el nuevo método de la API v1.0.0
                            result = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file
                            )
                            text = result.text.strip()

                            # If we detected a pause between recordings, add a new item to our transcription.
                            # Otherwise edit the existing one.
                            if phrase_complete or not transcription:
                                transcription.append(text)
                                translation = translate_text(text, target_language)
                                translations.append(translation)
                            else:
                                transcription[-1] = text
                                translation = translate_text(text, target_language)
                                translations[-1] = translation

                            # Clear the console to reprint the updated transcription.
                            os.system('cls' if os.name=='nt' else 'clear')
                            
                            print("Traducción al " + target_language + ":")
                            for line in translations:
                                print(line)
                                
                            print("\nTranscripción original:")
                            for line in transcription:
                                print(line)
                                
                            # Flush stdout.
                            print('', end='', flush=True)
                    except Exception as e:
                        print(f"Error en la transcripción: {str(e)}")
                finally:
                    # Asegurarse de que el archivo temporal se elimine correctamente
                    try:
                        if temp_wav_name and os.path.exists(temp_wav_name):
                            os.unlink(temp_wav_name)
                    except Exception as e:
                        print(f"Error al eliminar archivo temporal: {str(e)}")
            else:
                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\nResultado final:")
    for i, line in enumerate(transcription):
        print(f"Traducción: {translations[i]}")
        print(f"Original: {line}")
        print("")


if __name__ == "__main__":
    main()

