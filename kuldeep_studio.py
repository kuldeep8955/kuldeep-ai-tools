import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from google import genai
import requests, urllib.parse, time

st.set_page_config(page_title="Kuldeep AI Tools", layout="wide")
st.title("Kuldeep AI - Gemini Powered Studio (v5.1 SAFE)")

HEADERS = {"User-Agent": "Mozilla/5.0"}

tool = st.sidebar.selectbox("Apna AI Tool Chunein:", [
    "1. Kuldeep AI Chat (Gemini Style)",
    "2. Auto-AI Video Maker",
    "3. AI Image Generator",
    "4. Hindi/English Voice Maker",
    "5. AI Photo Editor"
])

from google.genai import types

from google.genai import types

def ask_free_ai(prompt):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                max_output_tokens=400
            )
        )
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"

def get_free_image(prompt, width=768, height=768):
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + f"?width={width}&height={height}&nologo=true"
    return requests.get(url, headers=HEADERS, timeout=35)

def add_caption(img, text):
    draw = ImageDraw.Draw(img)
    draw.rectangle([(40, 610), (1240, 690)], fill=(0, 0, 0))
    draw.text((60, 640), text[:85], fill=(255, 255, 0))
    return img
if tool == "1. Kuldeep AI Chat (Gemini Style)":
    st.subheader("Kuldeep AI se Kuch Bhi Puchein ya Kahani Likhwaiye")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_q = st.chat_input("Yahan apna sawal likhein...")
    if user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            with st.spinner("Kuldeep AI soch raha hai..."):
                try:
                    api_key = st.secrets["GEMINI_API_KEY"]
                    url = f"https://googleapis.com{api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": user_q}]}],
                        "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}}
                    }
                    res = requests.post(url, json=payload, timeout=15)
                    data = res.json()
                    if "candidates" in data:
                        ans = data["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        ans = f"Server Message: {data}"
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except Exception as e:
                    st.error(f"Error: {e}")

                def stream_jawab():
                    for chunk in client.models.generate_content_stream(
                        model="gemini-3.8-flash",
                        contents=user_q,
                        config=types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=0)
                        )
                    ):
                        if chunk.text:
                            yield chunk.text
                ans = st.write_stream(stream_jawab())
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"Error: {e}")

elif tool == "2. Auto-AI Video Maker":
    st.subheader("AI se Kahani Likhwakar Video Banayein")
    topic = st.text_input("Kahani ka Topic likhein:", "A brave lion and a little mouse in Hindi")
    if st.button("AI se Script Likhwaiye"):
        with st.spinner("Gemini script likh raha hai..."):
            st.session_state.auto_script = ask_free_ai(
                f"Write a short 4-sentence story about {topic}. End every sentence with a full stop. Do not use bullet points."
            )
    default_script = st.session_state.get(
        "auto_script",
        "The sun is shining as Leo walks in the park. He finds a cute little brown puppy."
    )
    title = st.text_input("Video Title:", "Leo_Story")
    bhasha = st.selectbox("Bhasha:", ["hi", "en"])
    style = st.selectbox("Image Style:", ["3D Pixar cartoon style", "realistic cinematic photo", "anime art"])
    kahani = st.text_area("Kahani (har line ke baad . lagayein):", default_script)
    captions_on = st.checkbox("Video par Subtitles dikhayein", value=True)
    if st.button("Pro AI Video Banayein"):
        with st.spinner("Video ban raha hai (har scene ke liye AI photo banayi ja rahi hai)..."):
            scenes = [s.strip() for s in kahani.split(".") if s.strip()]
            clips = []
            rang = [(25, 45, 90), (80, 20, 50), (20, 80, 60), (90, 60, 20)]
            for i, line in enumerate(scenes):
                if i > 0:
                    time.sleep(5)
                af, imf = f"a_{i}.mp3", f"i_{i}.jpg"
                gTTS(line, lang=bhasha).save(af)
                try:
                    clean_p = "".join(c for c in line if c.isalnum() or c == " ")[:80]
                    resp = get_free_image(f"{clean_p}, {style}", width=768, height=512)
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        with open(imf, "wb") as f:
                            f.write(resp.content)
                        img = Image.open(imf).convert("RGB").resize((1280, 720))
                    else:
                        raise Exception("Fallback")
                except Exception:
                    img = Image.new("RGB", (1280, 720), color=rang[i % len(rang)])
                if captions_on:
                    img = add_caption(img, line)
                img.save(imf)
                aud = AudioFileClip(af)
                clips.append(ImageClip(imf).with_duration(aud.duration).with_audio(aud))
            fv = concatenate_videoclips(clips)
            fn = "".join(c for c in title if c.isalnum() or c == " ").replace(" ", "_") + ".mp4"
            fv.write_videofile(fn, fps=24)
            st.video(fn)
            with open(fn, "rb") as f:
                st.download_button("Download Video (.mp4)", f, file_name=fn)

elif tool == "3. AI Image Generator":
    st.subheader("Likhe hue Text se AI Photo Banayein")
    img_prompt = st.text_input("Kaisi photo banani hai? (English mein likhein):", "A futuristic Indian city at night with flying cars, 3D render")
    if st.button("AI Photo Banayein"):
        with st.spinner("AI photo bana raha hai..."):
            try:
                resp = get_free_image(img_prompt, width=768, height=768)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    with open("gen_img.jpg", "wb") as f:
                        f.write(resp.content)
                    st.image("gen_img.jpg", caption=img_prompt, width=500)
                    with open("gen_img.jpg", "rb") as f:
                        st.download_button("Download Photo", f, file_name="kuldeep_ai_art.jpg")
                elif resp.status_code == 402:
                    st.warning("Free limit ke karan kripya 45 second ruk kar dobara koshish karein.")
                else:
                    st.error("Photo generate nahi ho payi, dobara try karein.")
            except Exception as e:
                st.error(f"Network error: {e}")

elif tool == "4. Hindi/English Voice Maker":
    st.subheader("Text se AI Awaaz Banayein")
    txt = st.text_area("Bolne ke liye text likhein:", "Namaste Kuldeep, aapka AI Studio shandar kaam kar raha hai!")
    lang = st.selectbox("Language:", ["hi", "en"])
    if st.button("Awaaz Banayein"):
        gTTS(txt, lang=lang).save("voice_out.mp3")
        st.audio("voice_out.mp3")
        with open("voice_out.mp3", "rb") as f:
            st.download_button("Download Audio (.mp3)", f, file_name="kuldeep_voice.mp3")

elif tool == "5. AI Photo Editor":
    st.subheader("Photo Filter aur Watermark Tool")
    up_img = st.file_uploader("Koi bhi Photo chunein:", type=["jpg", "png", "jpeg"])
    effect = st.selectbox("Effect Chunein:", ["Original + Text", "Black & White", "Blur Effect"])
    w_text = st.text_input("Photo par likhne ke liye text:", "Kuldeep AI Tools")
    if up_img:
        im = Image.open(up_img).convert("RGB")
        if effect == "Black & White":
            im = ImageOps.grayscale(im).convert("RGB")
        elif effect == "Blur Effect":
            im = im.filter(ImageFilter.GaussianBlur(5))
        if w_text:
            ImageDraw.Draw(im).text((30, 30), w_text, fill=(255, 255, 0))
        st.image(im, caption="Edited Photo", width=500)
        im.save("edited_photo.png")
        with open("edited_photo.png", "rb") as f:
            st.download_button("Download Edited Photo", f, file_name="kuldeep_edited.png")
