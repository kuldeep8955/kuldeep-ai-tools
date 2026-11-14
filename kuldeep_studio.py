import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
import requests, urllib.parse, os

st.set_page_config(page_title="Kuldeep AI Tools", layout="wide")
st.title("Kuldeep AI Master Studio (Pro 3.0)")

tool = st.sidebar.selectbox("Apna AI Tool Chunein:", ["1. Auto-AI Video Maker", "2. Photo se Video Maker", "3. Hindi/English Voice Maker", "4. AI Photo Editor"])

def add_caption(img, text):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 620, 1280, 720], fill=(0, 0, 0))
    d.text((50, 655), text[:95], fill=(255, 255, 0))
    return img

if tool == "1. Auto-AI Video Maker":
    st.subheader("Auto-AI Video + Subtitles + Music")
    title = st.text_input("Video Title:", "Leo_Pro_Story")
    bhasha = st.selectbox("Bhasha:", ["hi", "en"])
    style = st.selectbox("Image Style:", ["3D Pixar cartoon style", "realistic cinematic photo", "anime art"])
    kahani = st.text_area("Kahani likhein (har line ke baad . lagayein):", "The sun is shining as Leo walks in the park. He finds a cute little brown puppy.")
    bg_music = st.file_uploader("Background Music chunein (Optional .mp3):", type=["mp3"])
    if st.button("Pro AI Video Banayein"):
        with st.spinner("Subtitles aur AI tasveeron ke saath video ban raha hai..."):
            scenes = [s.strip() for s in kahani.split(".") if s.strip()]
            clips = []
            rang = [(25, 45, 90), (80, 20, 50), (20, 80, 60), (90, 60, 20)]
            for i, line in enumerate(scenes):
                af, imf = f"a_{i}.mp3", f"i_{i}.jpg"
                gTTS(line, lang=bhasha).save(af)
                try:
                    clean_p = "".join(c for c in line if c.isalnum() or c == " ")[:80]
                    url = f"https://pollinations.ai{urllib.parse.quote(clean_p + ", " + style)}?width=1280&height=720&nologo=true"
                    resp = requests.get(url, timeout=15)
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        open(imf, "wb").write(resp.content)
                        img = Image.open(imf).convert("RGB").resize((1280, 720))
                    else:
                        raise Exception("Fallback")
                except:
                    img = Image.new("RGB", (1280, 720), color=rang[i % len(rang)])
                img = add_caption(img, line)
                img.save(imf)
                aud = AudioFileClip(af)
                clips.append(ImageClip(imf).with_duration(aud.duration).with_audio(aud))
            fv = concatenate_videoclips(clips)
            if bg_music:
                open("bg.mp3", "wb").write(bg_music.read())
                bgm = AudioFileClip("bg.mp3").with_volume_scaled(0.15).with_duration(fv.duration)
                fv = fv.with_audio(CompositeAudioClip([fv.audio, bgm]))
            fn = "".join(c for c in title if c.isalnum() or c == " ").replace(" ", "_") + ".mp4"
            fv.write_videofile(fn, fps=24)
            st.success("Pro Video Taiyar Hai!")
            st.video(fn)
            st.download_button("Download Video", open(fn, "rb"), file_name=fn)

elif tool == "2. Photo se Video Maker":
    st.subheader("Apni Photos + Subtitles se Video Banayein")
    title = st.text_input("Title:", "Mera_Photo_Video")
    bhasha = st.selectbox("Awaaz ki Bhasha:", ["hi", "en"])
    kahani = st.text_area("Script likhein (har line ke baad . lagayein):", "Namaste dosto. Yeh mera naya video hai.")
    photos = st.file_uploader("Photos chunein:", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if st.button("Photo Video Banayein") and photos:
        with st.spinner("Video ban raha hai..."):
            scenes = [s.strip() for s in kahani.split(".") if s.strip()]
            clips = []
            for i, line in enumerate(scenes):
                af, imf = f"pa_{i}.mp3", f"pi_{i}.png"
                gTTS(line, lang=bhasha).save(af)
                img = Image.open(photos[i % len(photos)]).convert("RGB").resize((1280, 720))
                img = add_caption(img, line)
                img.save(imf)
                aud = AudioFileClip(af)
                clips.append(ImageClip(imf).with_duration(aud.duration).with_audio(aud))
            fv = concatenate_videoclips(clips)
            fn = "".join(c for c in title if c.isalnum() or c == " ").replace(" ", "_") + ".mp4"
            fv.write_videofile(fn, fps=24)
            st.video(fn)
            st.download_button("Download Video", open(fn, "rb"), file_name=fn)

elif tool == "3. Hindi/English Voice Maker":
    st.subheader("Text se AI Awaaz Banayein")
    txt = st.text_area("Bolne ke liye text likhein:", "Namaste Kuldeep, aapka AI Studio shandar kaam kar raha hai!")
    lang = st.selectbox("Language:", ["hi", "en"])
    if st.button("Awaaz Banayein"):
        gTTS(txt, lang=lang).save("voice_out.mp3")
        st.audio("voice_out.mp3")
        st.download_button("Download Audio (.mp3)", open("voice_out.mp3", "rb"), file_name="kuldeep_voice.mp3")

elif tool == "4. AI Photo Editor":
    st.subheader("Apni Photo ko Edit Karein")
    up_img = st.file_uploader("Photo upload karein:", type=["jpg", "png", "jpeg"])
    effect = st.selectbox("Filter chunein:", ["Black and White", "Blur Effect", "Extra Sharp", "High Brightness"])
    if up_img:
        im = Image.open(up_img).convert("RGB")
        if effect == "Black and White": im = im.convert("L")
        elif effect == "Blur Effect": im = im.filter(ImageFilter.GaussianBlur(5))
        elif effect == "Extra Sharp": im = im.filter(ImageFilter.SHARPEN)
        elif effect == "High Brightness": im = ImageEnhance.Brightness(im).enhance(1.5)
        im.save("edited_photo.png")
        st.image("edited_photo.png", caption="Edited Photo")
        st.download_button("Download Photo", open("edited_photo.png", "rb"), file_name="kuldeep_edited.png")
