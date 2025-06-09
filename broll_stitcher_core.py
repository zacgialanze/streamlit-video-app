import os, requests, shutil, sys
from moviepy.editor import VideoFileClip, concatenate_videoclips

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

def normalize_clip(input_path, duration):
    clip = VideoFileClip(input_path)
    loop_count = int(duration // clip.duration) + 1
    looped_clips = [clip] * loop_count
    final_clip = concatenate_videoclips(looped_clips).subclip(0, duration)
    return final_clip

def stitch_clips(clips, total_duration, aspect):
    each_duration = total_duration / len(clips)
    final_clips = []

    for i, clip_path in enumerate(clips):
        safe_print(f"Normalizing clip {i+1}/{len(clips)} to {each_duration:.2f} seconds")
        try:
            norm_clip = normalize_clip(clip_path, each_duration)
            final_clips.append(norm_clip)
        except Exception as e:
            safe_print(f"❌ Failed to load or trim: {clip_path} ({e})")

    if not final_clips:
        return None

    stitched = concatenate_videoclips(final_clips, method="compose")
    output_path = os.path.join(OUTPUT, "stitched.mp4")
    stitched.write_videofile(output_path, codec="libx264", fps=24)
    return output_path

def make_video(topic, duration, clips, aspect):
    downloaded = download_pexels_videos(topic, clips)
    if not downloaded:
        downloaded = download_giphy_videos(topic, clips)
    if not downloaded:
        return None
    return stitch_clips(downloaded, duration, aspect)
