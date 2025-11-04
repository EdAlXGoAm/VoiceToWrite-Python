# Transcripción y Traducción de Audio

Este proyecto permite capturar y transcribir audio en tiempo real.

## Características

- Captura audio de salida del sistema (lo que escuchas por los altavoces)
- Transcribe el audio utilizando OpenAI Whisper
- Traduce automáticamente al español (o cualquier otro idioma configurado)
- Muestra la transcripción y traducción en tiempo real

## Requisitos

- Python 3.7 o superior
- PyAudioWPatch (para captura de audio del sistema)
- OpenAI API Key

## Instalación

1. Clona este repositorio
2. Instala las dependencias:

```
pip install -r requirements.txt
```

## Uso

Para capturar el audio del micrófono:

```
python UTILS/transcribe_microphone_whisper.py
```

Para capturar el audio del sistema (altavoces):

```
python UTILS/transcribe_system_audio_whisper.py
```

Opciones disponibles:
- `--record_timeout`: Duración de cada grabación en segundos (default: 2)
- `--phrase_timeout`: Tiempo de silencio para considerar una nueva línea (default: 3)
- `--target_language`: Idioma al que traducir (default: español)

Para detener la grabación, presiona Ctrl+C.

## Cómo funciona

El programa utiliza PyAudioWPatch para capturar el audio que sale por los altavoces del sistema (utilizando WASAPI loopback en Windows). El audio capturado se envía a la API de OpenAI Whisper para transcripción, y luego se traduce utilizando GPT-4.1-nano.
