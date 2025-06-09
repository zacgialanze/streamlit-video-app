import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import subprocess

# Set up main window
root = tk.Tk()
root.title("101 VideoShort Generator")
root.geometry("480x720")
root.configure(bg='#0e1a2b')

# Load background image
background_path = os.path.join("assets", "splash.png")
if os.path.exists(background_path):
    bg_img = Image.open(background_path).resize((480, 720))
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Title directly on window, no frame box
form_y_offset = 0.14  # lowered slightly for better balance

title = tk.Label(root, text="\U0001F3AC 101 VideoShort Generator", font=("Helvetica", 16, 'bold'), fg="white", bg=root['bg'])
title.place(relx=0.5, rely=form_y_offset, anchor='n')

# Input fields
fields = ["Enter topic:", "Duration (seconds):", "Number of clips:"]
entries = []
for i, field in enumerate(fields):
    lbl = tk.Label(root, text=field, font=("Helvetica", 12), fg="white", bg=root['bg'])
    lbl.place(relx=0.39, rely=form_y_offset + 0.08 + i*0.07, anchor='e')
    ent = tk.Entry(root, font=("Helvetica", 12), width=27)
    ent.place(relx=0.39, rely=form_y_offset + 0.08 + i*0.07, anchor='w')
    entries.append(ent)

# Aspect Ratio dropdown
aspect_lbl = tk.Label(root, text="Aspect Ratio:", font=("Helvetica", 12), fg="white", bg=root['bg'])
aspect_lbl.place(relx=0.39, rely=form_y_offset + 0.29, anchor='e')
aspect_option = ttk.Combobox(root, values=["16:9", "9:16", "4:3"], font=("Helvetica", 12), width=24)
aspect_option.set("16:9")
aspect_option.place(relx=0.39, rely=form_y_offset + 0.29, anchor='w')

# ✅ Define the generate button function
def generate_video():
    topic = entries[0].get()
    duration = entries[1].get()
    clips = entries[2].get()
    aspect = aspect_option.get()

    print("Generating video with:")
    print("Topic:", topic)
    print("Duration:", duration)
    print("Clips:", clips)
    print("Aspect Ratio:", aspect)

    try:
        subprocess.run([
            "python",
            "broll_stitcher.py",
            topic,
            duration,
            clips,
            aspect
        ])
    except Exception as e:
        print("Error running broll_stitcher.py:", e)

# Generate button
generate_btn = tk.Button(root, text="Generate Video", font=("Helvetica", 12, 'bold'), bg="#4267F6", fg="white", command=generate_video)
generate_btn.place(relx=0.5, rely=form_y_offset + 0.39, anchor='n')

# Run the app
root.mainloop()
