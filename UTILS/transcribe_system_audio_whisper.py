#! python3.7

"""
Script para transcribir y traducir audio del sistema (loopback) en tiempo real usando OpenAI Whisper.
Captura el audio que se reproduce en el sistema (altavoces), lo transcribe con Whisper y lo traduce con GPT-4.
Útil para transcribir videollamadas, videos, música, etc.
"""

import argparse
import os
import numpy as np
import pyaudiowpatch as pyaudio
import torch
import tempfile
import wave
import sys
import traceback

from datetime import datetime, timedelta, UTC
from queue import Queue
from time import sleep
from sys import platform
from openai import OpenAI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=0.5,
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
    # Bytes object which holds audio data for the current phrase
    phrase_bytes = bytes()

    # Parámetros para la grabación con PyAudioWPatch
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    CHUNK = 1024
    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    transcription = []
    translations = []

    try:
        # Inicializamos PyAudio
        p = pyaudio.PyAudio()

        # Obtener el dispositivo WASAPI loopback (salida del sistema)
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            if not default_speakers.get("isLoopbackDevice", False):
                found_loopback = False
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        default_speakers = loopback
                        found_loopback = True
                        break
                
                if not found_loopback:
                    loopback_devices = list(p.get_loopback_device_info_generator())
                    if loopback_devices:
                        # Usar el primer dispositivo loopback disponible si no encontramos una coincidencia
                        default_speakers = loopback_devices[0]
        
        except Exception as e:
            print(f"Error al obtener información del dispositivo WASAPI: {str(e)}")
            try:
                # Intentar usar el dispositivo loopback de Altavoces
                for i in range(p.get_device_count()):
                    device_info = p.get_device_info_by_index(i)
                    if "Loopback" in device_info["name"]:
                        default_speakers = device_info
                        break
            except:
                print("No se encontró ningún dispositivo loopback. El programa no podrá capturar audio del sistema.")
                return
            
        print(f"Grabando desde: {default_speakers['name']}")
        
        # Usamos la tasa de muestreo nativa del dispositivo
        RATE = int(default_speakers["defaultSampleRate"])

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

        # Abrimos el stream para grabar audio desde el dispositivo loopback (salida del sistema)
        stream = p.open(
            format=FORMAT,
            channels=int(default_speakers["maxInputChannels"]),
            rate=RATE,
            frames_per_buffer=CHUNK,
            input=True,
            input_device_index=default_speakers["index"],
            # Añadir parámetros para mejorar la respuesta en tiempo real
            start=True,  # Iniciar inmediatamente
        )

        # Cue the user that we're ready to go.
        print("Listo para transcribir la salida del sistema.")
        print("Reproduce algún sonido en tu computadora para comenzar a transcribir.")
        print("Presiona Ctrl+C para detener la grabación.\n")

        # Variables para controlar el procesamiento
        last_processing_time = datetime.now(UTC)
        audio_buffer = []  # Para acumular chunks de audio
        last_transcript = ""
        recording_start_time = None

        while True:
            try:
                now = datetime.now(UTC)
                
                # Verificar si ha pasado suficiente tiempo sin audio para considerar una nueva frase
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    if recording_start_time and phrase_bytes:
                        # Si tenemos audio acumulado, procesarlo como una frase completa antes de empezar una nueva
                        process_audio = True
                        phrase_complete = True
                    else:
                        # No hay audio para procesar, solo reiniciar
                        process_audio = False
                        phrase_complete = True
                        phrase_bytes = bytes()
                        audio_buffer = []
                        recording_start_time = None
                else:
                    # Continuamos con la misma frase
                    process_audio = False
                    phrase_complete = False
                
                # Leer un nuevo chunk de audio
                try:
                    # No bloqueante con timeout corto para mejor respuesta
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    
                    # Verificar si este chunk tiene audio (no es silencio)
                    # Una forma simple de verificar es comprobar si hay valores distintos de cero
                    has_audio = any(b != 0 for b in data[:100])
                    
                    if has_audio:
                        # Si tenemos audio, actualizamos el tiempo de grabación
                        phrase_time = now
                        
                        # Si es el primer chunk con audio, marcar el inicio de la grabación
                        if recording_start_time is None:
                            recording_start_time = now
                        
                        # Añadir datos al buffer y a los bytes acumulados
                        audio_buffer.append(data)
                        phrase_bytes += data
                        
                        # Verificar si tenemos suficientes datos para procesar
                        # Y si ha pasado suficiente tiempo desde el último procesamiento
                        if (len(phrase_bytes) > 0 and  # Cualquier cantidad de audio es suficiente
                            (now - last_processing_time).total_seconds() >= record_timeout):
                            process_audio = True
                
                except Exception as e:
                    sleep(0.1)
                    continue
                
                # Procesar el audio acumulado si es necesario
                if process_audio:
                    last_processing_time = now
                    
                    # Crear un archivo temporal WAV
                    temp_wav = None
                    try:
                        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                        temp_wav_name = temp_wav.name
                        temp_wav.close()
                        
                        with wave.open(temp_wav_name, 'wb') as wf:
                            wf.setnchannels(int(default_speakers["maxInputChannels"]))
                            wf.setsampwidth(2)
                            wf.setframerate(RATE)
                            wf.writeframes(phrase_bytes)
                        
                        # Usar la API de OpenAI para transcribir
                        try:
                            with open(temp_wav_name, "rb") as audio_file:
                                result = client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=audio_file
                                )
                                text = result.text.strip()
                                
                                # Solo continuar si tenemos texto
                                if text:
                                    # Decidir si agregamos una nueva línea o actualizamos la última
                                    if phrase_complete or not transcription:
                                        # Si es una nueva frase o no hay transcripciones previas
                                        transcription.append(text)
                                        translation = translate_text(text, target_language)
                                        translations.append(translation)
                                        last_transcript = text
                                    else:
                                        # Si estamos continuando la frase anterior, siempre actualizar
                                        # sin verificación adicional (como en transcribe_microphone_whisper.py)
                                        transcription[-1] = text
                                        translation = translate_text(text, target_language)
                                        translations[-1] = translation
                                        last_transcript = text
                                    
                                    # Limpiar la consola para mostrar la transcripción actualizada
                                    os.system('cls' if os.name=='nt' else 'clear')
                                    
                                    print("Traducción al " + target_language + ":")
                                    for line in translations:
                                        print(line)
                                    
                                    print("\nTranscripción original:")
                                    for line in transcription:
                                        print(line)
                                    
                                    print("\nGrabando... (Presiona Ctrl+C para detener)")
                                    print('', end='', flush=True)
                            
                            # Si la frase está completa, reiniciar el buffer para la siguiente frase
                            if phrase_complete:
                                phrase_bytes = bytes()
                                audio_buffer = []
                                recording_start_time = None
                            else:
                                # Mantener un equilibrio entre contexto y rendimiento en tiempo real
                                # Mantener aproximadamente 3 segundos de audio para contexto, pero no más
                                # para evitar retardos muy largos
                                keep_chunks = int(RATE * 3 / CHUNK)  # Mantener ~3 segundos
                                if len(audio_buffer) > keep_chunks:
                                    audio_buffer = audio_buffer[-keep_chunks:]
                                    phrase_bytes = b''.join(audio_buffer)
                            
                        except Exception as e:
                            print(f"Error en la transcripción: {str(e)}")
                    except Exception as e:
                        print(f"Error al procesar audio: {str(e)}")
                    finally:
                        # Asegurarse de que el archivo temporal se elimine
                        try:
                            if temp_wav_name and os.path.exists(temp_wav_name):
                                os.unlink(temp_wav_name)
                        except Exception as e:
                            print(f"Error al eliminar archivo temporal: {str(e)}")
                
                # Evitar consumo excesivo de CPU pero mantener buena velocidad de respuesta
                sleep(0.01)  # Reducido de 0.05 para mayor velocidad de respuesta
            except KeyboardInterrupt:
                break
            except Exception as e:
                sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nGrabación detenida por el usuario.")
    except Exception as e:
        print(f"Error en la configuración: {str(e)}")
    finally:
        # Limpieza
        try:
            if 'stream' in locals() and stream:
                stream.stop_stream()
                stream.close()
            if 'p' in locals() and p:
                p.terminate()
        except Exception as e:
            print(f"Error durante la limpieza: {str(e)}")

    if transcription:
        print("\n\nResultado final:")
        for i, line in enumerate(transcription):
            print(f"Traducción: {translations[i]}")
            print(f"Original: {line}")
            print("")
    else:
        print("\n\nNo se capturó ninguna transcripción.")


if __name__ == "__main__":
    main()

