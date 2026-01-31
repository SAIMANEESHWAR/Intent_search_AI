"""
Process multiple uploaded video clips.
Saves each clip, extracts frames with clip-prefixed names, generates captions.
"""
import sys
import os
import json
import shutil
import subprocess

def default_logger(msg):
    print(msg)

SOURCE_CLIPS_DIR = "source_clips"
FRAMES_DIR = "frames"
FPS = 5

def extract_frames_for_clip(video_path: str, output_prefix: str, frames_dir: str):
    """Extract frames from a video with a given prefix (e.g. clip_001_frame)."""
    os.makedirs(frames_dir, exist_ok=True)
    output_pattern = os.path.join(frames_dir, f"{output_prefix}_%04d.jpg")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={FPS}",
        "-y", output_pattern
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def process_clips_logic(file_data, update_status=default_logger):
    """
    Process multiple uploaded video files.
    file_data: list of (filename, file_content_bytes) - content read before passing.
    """
    try:
        update_status("Starting processing for uploaded clips...")

        # 1. Clean and prepare directories
        update_status("🧹 Preparing directories...")
        if os.path.exists(FRAMES_DIR):
            shutil.rmtree(FRAMES_DIR)
        clips_dir = "clips"
        if os.path.exists(clips_dir):
            shutil.rmtree(clips_dir)
        os.makedirs(SOURCE_CLIPS_DIR, exist_ok=True)
        os.makedirs(FRAMES_DIR, exist_ok=True)
        os.makedirs(clips_dir, exist_ok=True)

        # 2. Save uploaded files
        saved_paths = []
        for idx, (filename, content) in enumerate(file_data):
            clip_id = f"{idx + 1:03d}"
            ext = os.path.splitext(filename)[1] or ".mp4"
            save_path = os.path.join(SOURCE_CLIPS_DIR, f"clip_{clip_id}{ext}")
            with open(save_path, "wb") as f:
                f.write(content)
            saved_paths.append((clip_id, save_path))
            update_status(f"📥 Saved clip {idx + 1}/{len(file_data)}: {os.path.basename(save_path)}")

        # 3. Update config
        update_status("📝 Updating config...")
        config = {
            "mode": "clips",
            "sources": [p for _, p in saved_paths],
            "clip_count": len(saved_paths)
        }
        with open("video_config.json", "w") as f:
            json.dump(config, f, indent=4)

        # 4. Extract frames from each clip
        for clip_id, video_path in saved_paths:
            update_status(f"🎞️ Extracting frames from clip {clip_id}...")
            prefix = f"clip_{clip_id}_frame"
            extract_frames_for_clip(video_path, prefix, FRAMES_DIR)

        # 5. Generate captions for all frames (reuse caption_frames.py)
        update_status("🤖 Generating visual captions (this may take a while)...")
        subprocess.run([sys.executable, "caption_frames.py"], check=True)

        update_status("COMPLETED")

    except Exception as e:
        update_status(f"ERROR: {str(e)}")
        raise e


if __name__ == "__main__":
    print("Use via FastAPI /process-clips endpoint with file uploads.")
