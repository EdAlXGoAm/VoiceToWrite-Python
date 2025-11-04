"""
Script para extraer audio de un archivo de video y guardarlo como MP3.
Versión simple con rutas directas.
"""
from moviepy.editor import VideoFileClip

if __name__ == "__main__":
    input_path = "C:/Users/uif05375/Downloads/2025-05-15 07-35-13_clip1.mp4"
    output_path = "C:/Users/uif05375/Downloads/2025-05-15 07-35-13_clip1.mp3"
    
    clip = VideoFileClip(input_path)
    clip.audio.write_audiofile(output_path)
    clip.close()
    
    print(f"Audio extraído exitosamente: {output_path}")

