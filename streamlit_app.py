
import streamlit as st
import os
from broll_stitcher_core import make_video

st.set_page_config(page_title="101 VideoShort Generator", page_icon="🎬", layout="centered")
st.title("🎬 101 VideoShort Generator")

topic = st.text_input("Enter topic")
duration = st.number_input("Duration (seconds)", min_value=1, step=1)
clips = st.number_input("Number of clips", min_value=1, step=1)
aspect = st.selectbox("Aspect Ratio", ["16:9", "9:16", "4:3"])

if st.button("Generate Video"):
    with st.spinner("Building your highlight video..."):
        output_path = make_video(topic, int(duration), int(clips), aspect)
        if output_path and os.path.exists(output_path):
            st.success("✅ Done! Download your video below:")
            st.video(output_path)
            st.download_button("Download Video", open(output_path, "rb"), file_name="final_output.mp4")
        else:
            st.error("❌ Something went wrong generating the video.")
