import os

from providers import llm_provider, image_provider, music_provider, video_provider

DEFAULT_TOPIC = "A cozy Ghibli-style cottage in a rainy forest"
OUTPUT_DIR = "output"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("[1/5] Generating scene plan...")
    scenes = llm_provider.generate_scene_json(DEFAULT_TOPIC)

    gathered_scenes = []
    print("[2/5] Generating images and narration...")
    for scene in scenes:
        scene_number = scene["scene_number"]
        image_path = os.path.join(OUTPUT_DIR, f"scene_{scene_number}.png")
        narration_path = os.path.join(OUTPUT_DIR, f"scene_{scene_number}.mp3")

        print(f"  - Scene {scene_number}: image")
        image_provider.generate_image(scene["image_prompt"], image_path)

        print(f"  - Scene {scene_number}: narration")
        music_provider.generate_narration(scene["narration_text"], narration_path)

        gathered_scenes.append(
            {
                **scene,
                "image_path": image_path,
                "narration_path": narration_path,
            }
        )

    print("[3/5] Generating background music...")
    bg_music_path = "background_music.mp3"
    music_provider.generate_background_music(bg_music_path)

    print("[4/5] Compiling final video...")
    final_output = "output.mp4"
    video_provider.compile_video(gathered_scenes, final_output)

    print(f"[5/5] Done: {final_output}")


if __name__ == "__main__":
    main()
