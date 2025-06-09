from broll_stitcher_core import download_pexels_videos, download_giphy_videos, stitch_clips
import sys

if __name__ == '__main__':
    print("🌀 Welcome to 101 VideoShort Generator 1.0")
    print("✨ The ultimate auto-stitching tool for your stepdad’s cartoon madness!")
    print("------------------------------------------------------------")

    # ✅ Get inputs passed from the GUI (via subprocess in fancy_gui.py)
    if len(sys.argv) < 5:
        print("❌ Missing arguments. Expected: topic duration clip_count aspect_ratio")
        sys.exit(1)

    query = sys.argv[1]
    duration = int(sys.argv[2])
    clip_count = int(sys.argv[3])
    aspect_ratio = sys.argv[4].strip()

    print("⬇️ Downloading cool & wacky clips for:", query)
    clips = download_pexels_videos(query, clip_count)
    if len(clips) < clip_count:
        print("⚠️ Not enough from Pexels, pulling extra visuals from Giphy...")
        clips += download_giphy_videos(query, clip_count - len(clips))

    if not clips:
        print("❌ No clips downloaded. Maybe pick a different topic?")
        sys.exit(1)

    print("🛠️ Stitching your cartoonish masterpiece together...")
    final_path = stitch_clips(clips, duration, aspect_ratio)

    print("🎉 DONE! Your custom mashup is ready!")
    print(f"📂 Saved to: {final_path}")
    print("🚀 Launch it on your 101 VideoShort channel with style!")
