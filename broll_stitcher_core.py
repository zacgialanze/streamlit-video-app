import os, requests, subprocess, shutil, sys

PEXELS_API_KEY = "ehCrKcnr76eMIDFefGdCjgohBkYQrFAeO59IGeHDPPWHv7z9QvlJ4WjG"
GIPHY_API_KEY = "G67MyryGBvg6365DgjyNi2Tulbiu80GQ"
TEMP = "temp"
OUTPUT = "output"

os.makedirs(TEMP, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(msg.encode('utf-8', errors='replace'))
            sys.stdout.buffer.write(b'\n')
        else:
            print(msg.encode('utf-8', errors='replace').decode())

def download_pexels_videos(query, count):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": count}
    res = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    if res.status_code != 200:
        return []
    clips = []
    for i, video in enumerate(res.json().get("videos", [])):
        url = sorted(video["video_files"], key=lambda x: -x["width"])[0]["link"]
        out = os.path.join(TEMP, f"clip_pexels_{i+1}.mp4")
        with requests.get(url, stream=True) as r, open(out, "wb") as f:
            shutil.copyfileobj(r.raw, f)
        clips.append(out)
        if len(clips) >= count:
            break
    return clips

def download_giphy_videos(query, count):
    params = {"api_key": GIPHY_API_KEY, "q": query, "limit": count}
    res = requests.get("https://api.giphy.com/v1/gifs/search", params=params)
    if res.status_code != 200:
        return []
    clips = []
    for i, gif in enumerate(res.json().get("data", [])):
        url = gif["images"]["original_mp4"]["mp4"]
        out = os.path.join(TEMP, f"clip_giphy_{i+1}.mp4")
        with requests.get(url, stream=True) as r, open(out, "wb") as f:
            shutil.copyfileobj(r.raw, f)
        clips.append(out)
    return clips

def normalize_clip(input_path, output_path, duration, aspect):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        clip_duration = float(result.stdout.strip())
    except:
        clip_duration = 5

    loop_count = int(duration // clip_duration) + 1

    unique_id = os.path.splitext(os.path.basename(output_path))[0]
    list_path = os.path.join(TEMP, f"loop_list_{unique_id}.txt")
    looped_path = os.path.join(TEMP, f"looped_full_{unique_id}.mp4")

    with open(list_path, "w") as f:
        clip_path = os.path.abspath(input_path).replace("\\", "/")
        for _ in range(loop_count):
            f.write(f"file '{clip_path}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-c", "copy", looped_path
    ], check=True)

    if aspect == "16:9":
        vf = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"
    elif aspect == "4:3":
        vf = "scale=960:720:force_original_aspect_ratio=decrease,pad=960:720:(ow-iw)/2:(oh-ih)/2"
    else:
        vf = "scale=1280:720"

    subprocess.run([
        "ffmpeg", "-y", "-i", looped_path,
        "-t", str(duration),
        "-vf", vf,
        "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-an", output_path
    ], check=True)

    os.remove(looped_path)
    os.remove(list_path)

def stitch_clips(clips, total_duration, aspect):
    final_clips = []
    each_duration = total_duration / len(clips)
    txt_path = os.path.join(TEMP, "concat_list.txt")
    safe_print(f"Total: {total_duration}s, Clips: {len(clips)}, Each: {each_duration}s")

    with open(txt_path, "w") as f:
        for i, clip in enumerate(clips):
            norm_path = os.path.join(TEMP, f"norm_{i+1}.mp4")
            safe_print(f"Normalizing clip {i+1}/{len(clips)} to {each_duration:.2f} seconds")
            normalize_clip(clip, norm_path, each_duration, aspect)
            if os.path.exists(norm_path):
                norm_path_abs = os.path.abspath(norm_path).replace("\\", "/")
                f.write(f"file '{norm_path_abs}'\n")
                final_clips.append(norm_path)
            else:
                safe_print(f"❌ Failed to create normalized clip: {norm_path}")

    safe_print(f"🧾 Final concat list contains {len(final_clips)} files")

    final = os.path.join(OUTPUT, "stitched.mp4")
    result = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", txt_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
        final
    ], capture_output=True, text=True)

    if result.returncode != 0:
        safe_print("❌ FFmpeg concat failed:")
        safe_print(result.stderr)
    else:
        probe = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", final
        ], capture_output=True, text=True)
        safe_print(f"🕒 Final stitched video duration (according to ffprobe): {probe.stdout.strip()} seconds")

    return final
