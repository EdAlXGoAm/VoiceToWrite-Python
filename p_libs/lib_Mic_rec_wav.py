import pyaudio
import wave
import threading

class AudioRecorder:
    def __init__(self, filename, channels=1, rate=44100, chunk=1024):
        self.filename = filename
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.frames = []
        self.recording = False
        self.thread = None

    def start(self):
        self.recording = True
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def stop(self):
        self.recording = False
        self.thread.join()

        # Guardar la grabación en un archivo WAV
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def record(self):
        audio = pyaudio.PyAudio()

        # Iniciar la grabación
        stream = audio.open(format=pyaudio.paInt16, channels=self.channels,
                rate=self.rate, input=True,
                frames_per_buffer=self.chunk)

        self.frames = []

        print("Grabando...")

        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)

        print("¡Grabación terminada!")

        # Detener la grabación
        stream.stop_stream()
        stream.close()
        audio.terminate()