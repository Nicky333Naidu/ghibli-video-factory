import os
import subprocess
import tempfile
from pathlib import Path


def _run(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result


def compile_video(scenes, output_path):
    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            scene_videos = []

            for i, scene in enumerate(scenes, start=1):
                image = scene["image_path"]
                narration = scene["narration_path"]
                scene_mp4 = tmpdir / f"scene_{i}.mp4"

                duration = 5
                try:
                    probe = subprocess.check_output([
                        "ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", narration
                    ], text=True).strip()
                    duration = max(float(probe), 1.0)
                except Exception:
                    pass

                vf = (
                    "zoompan=z='min(zoom+0.0008,1.12)':d=125:"
                    "s=1280x720:fps=25,"
                    "scale=1280:720,"
                    "pad=1280:720:(ow-iw)/2:(oh-ih)/2"
                )

                _run([
                    "ffmpeg", "-y", "-loop", "1", "-i", image, "-i", narration,
                    "-vf", vf,
                    "-t", str(duration),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-shortest", str(scene_mp4)
                ])
                scene_videos.append(scene_mp4)

            concat_list = tmpdir / "concat.txt"
            concat_list.write_text("
".join([f"file '{p.as_posix()}'" for p in scene_videos]), encoding="utf-8")
            temp_video = tmpdir / "final_no_music.mp4"

            _run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-c", "copy", str(temp_video)
            ])

            bg_music = None
            for candidate in ["background_music.mp3", "music.mp3", "assets/background_music.mp3", "output/background_music.mp3"]:
                if os.path.exists(candidate):
                    bg_music = candidate
                    break

            if bg_music:
                _run([
                    "ffmpeg", "-y", "-i", str(temp_video), "-stream_loop", "-1", "-i", bg_music,
                    "-filter_complex", "[1:a]volume=0.1[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2",
                    "-c:v", "copy", "-c:a", "aac", "-shortest", output_path
                ])
            else:
                _run(["ffmpeg", "-y", "-i", str(temp_video), "-c", "copy", output_path])

        return True
    except Exception as e:
        print(f"Video compilation failed: {e}")
        return False
