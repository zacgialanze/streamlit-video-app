import tkinter as tk
from tkinter import messagebox
from broll_stitcher_core import download_pexels_videos, download_giphy_videos, stitch_clips


def start_process():
    query = topic_entry.get()
    try:
        duration = int(duration_entry.get())
        clip_count = int(clips_entry.get())
        aspect_ratio = aspect_var.get()
    except ValueError:
        messagebox.showerror("Invalid Input", "Duration and Clip Count must be numbers.")
        return

    status_label.config(text="Downloading clips...")
    window.update()

    clips = download_pexels_videos(query, clip_count)
    if len(clips) < clip_count:
        status_label.config(text="Pulling extra clips from Giphy...")
        window.update()
        clips += download_giphy_videos(query, clip_count - len(clips))

    if not clips:
        messagebox.showerror("Error", "No clips found. Try a different topic.")
        return

    status_label.config(text="Stitching clips...")
    window.update()
    final_path = stitch_clips(clips, duration, aspect_ratio)

    status_label.config(text=f"Done! Saved to: {final_path}")
    messagebox.showinfo("Success", f"Video saved to: {final_path}")


# GUI setup
window = tk.Tk()
window.title("101 VideoShort Generator 1.0")
window.geometry("400x400")
window.configure(bg="#0a0a0a")

header = tk.Label(window, text="🌀 101 VideoShort Generator", fg="white", bg="#0a0a0a", font=("Arial", 16, "bold"))
header.pack(pady=10)

topic_label = tk.Label(window, text="Enter topic:", fg="white", bg="#0a0a0a")
topic_label.pack()
topic_entry = tk.Entry(window, width=40)
topic_entry.pack(pady=5)

duration_label = tk.Label(window, text="Duration (seconds):", fg="white", bg="#0a0a0a")
duration_label.pack()
duration_entry = tk.Entry(window, width=40)
duration_entry.pack(pady=5)

clips_label = tk.Label(window, text="Number of clips:", fg="white", bg="#0a0a0a")
clips_label.pack()
clips_entry = tk.Entry(window, width=40)
clips_entry.pack(pady=5)

aspect_label = tk.Label(window, text="Aspect Ratio:", fg="white", bg="#0a0a0a")
aspect_label.pack()
aspect_var = tk.StringVar(window)
aspect_var.set("16:9")
tk.OptionMenu(window, aspect_var, "16:9", "4:3").pack(pady=5)

start_btn = tk.Button(window, text="Generate Video", command=start_process, bg="#4444ff", fg="white", font=("Arial", 12, "bold"))
start_btn.pack(pady=20)

status_label = tk.Label(window, text="", fg="lime", bg="#0a0a0a")
status_label.pack(pady=10)

window.mainloop()
