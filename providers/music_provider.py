import os
import shutil
import tempfile
from urllib.request import urlopen

from gtts import gTTS


def generate_narration(text, output_path):
    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        tts = gTTS(text=text, lang="en")
        tts.save(output_path)
        return True
    except Exception as e:
        print(f"Narration generation failed: {e}")
        return False


def generate_background_music(output_path):
    public_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with urlopen(public_url, timeout=30) as response, open(output_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print(f"Background music download failed: {e}")
        return False
