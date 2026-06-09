import os
import time
import shutil
from gradio_client import Client

# Using stable, public spaces that handle basic inputs reliably
FALLBACK_SPACES = [
    "multimodalart/flux-tarot-lora", 
    "black-forest-labs/FLUX.1-schnell"
]

def generate_image(prompt, output_path):
    for space in FALLBACK_SPACES:
        try:
            print(f"Attempting image generation with space: {space}")
            client = Client(space)
            
            # Structuring parameters explicitly based on the target Space requirements
            if "schnell" in space:
                # Schnell endpoint expects: prompt, seed, width, height, num_inference_steps
                result = client.predict(
                    prompt=prompt,
                    seed=0,
                    width=1024,
                    height=768,
                    num_inference_steps=4,
                    api_name="/infer"
                )
            else:
                # Tarot/Standard LoRA endpoints usually accept simpler positional args
                result = client.predict(
                    prompt, 
                    api_name="/predict"
                )

            # Gradio returns a string path to a local temp file or a list containing it
            image_path = result[0] if isinstance(result, (list, tuple)) else result
            
            if isinstance(image_path, str) and os.path.exists(image_path):
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                # Safely move the file from gradio temp to your asset folder
                shutil.move(image_path, output_path)
                print(f"Success! Saved image to {output_path}")
                return True

        except Exception as e:
            print(f"Warning: {space} failed with error: {e}")
            print("Waiting 5 seconds before trying next fallback...")
            time.sleep(5)
            continue

    return False
