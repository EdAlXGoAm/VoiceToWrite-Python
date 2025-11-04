"""
Script para extraer audio de un archivo de video y guardarlo como MP3.
"""
import os
from moviepy.editor import VideoFileClip

if __name__ == "__main__":
    input_filename = "2025-01-23 10-35-17"
    output_filename = "2025-01-23 10-35-17"
    
    input_dir = "D:/git-edalx/v_to_w_py/input_video/"
    input_path = os.path.join(input_dir, input_filename + ".mp4")
    output_path = os.path.join(input_dir, output_filename + ".mp3")
    
    video = VideoFileClip(input_path)
    video.audio.write_audiofile(output_path)
    video.close()
    
    print(f"Audio extraído exitosamente: {output_path}")

