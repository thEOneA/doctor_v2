# voice_of_the_doctor.py
from dotenv import load_dotenv
load_dotenv()

import os
import platform
import subprocess
import logging
from gtts import gTTS
from pydub import AudioSegment
from io import BytesIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def text_to_speech_with_gtts(input_text, output_filepath="final.wav", language="en"):
    """
    Convert text to speech using gTTS, save as WAV, and play it immediately.
    Handles errors gracefully.
    
    Args:
        input_text (str): Text to convert to speech (limited to 200 characters per request, split if longer).
        output_filepath (str): Path to save the final WAV file (default: 'final.wav').
        language (str): Language code (default: "en" for English).
    
    Returns:
        None: Plays audio directly, no return value needed for synchronous use.
    """
    try:
        # Split text into chunks of 200 characters if longer
        chunk_size = 200
        if len(input_text) > chunk_size:
            chunks = [input_text[i:i + chunk_size] for i in range(0, len(input_text), chunk_size)]
        else:
            chunks = [input_text]

        # Generate MP3 for each chunk and combine
        mp3_filepath = "temp.mp3"
        combined_audio = AudioSegment.empty()

        for chunk in chunks:
            tts = gTTS(text=chunk, lang=language, slow=False)
            tts.save(mp3_filepath)
            chunk_audio = AudioSegment.from_mp3(mp3_filepath)
            combined_audio = combined_audio + chunk_audio

        # Export combined audio as WAV
        combined_audio.export(output_filepath, format="wav")

        # Play the WAV audio immediately
        os_name = platform.system()
        if os_name == "Windows":
            # Use PowerShell with Media.SoundPlayer for WAV playback
            subprocess.run(
                ['powershell', '-c', f'(New-Object Media.SoundPlayer "{os.path.abspath(output_filepath)}").PlaySync()'],
                check=True
            )
        elif os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath], check=True)
        elif os_name == "Linux":  # Linux
            subprocess.run(['ffplay', '-nodisp', '-autoexit', output_filepath], check=True)
        else:
            raise OSError("Unsupported operating system")

        # Clean up temporary MP3 file
        if os.path.exists(mp3_filepath):
            os.remove(mp3_filepath)

    except Exception as e:
        logging.error(f"Unexpected error in text-to-speech with gTTS: {e}")

# Example usage (for testing)
if __name__ == "__main__":
    test_text = "With what I see, I think you have a mild rash, try using a soothing cream like hydrocortisone."
    text_to_speech_with_gtts(test_text)
    print("Audio played.")