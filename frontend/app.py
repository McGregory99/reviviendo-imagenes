import requests
import streamlit as st
from PIL import Image

BACKEND_URL = "http://localhost:8000"

# --- Sidebar ---
st.sidebar.text("USER")
st.sidebar.button("Logout")

# --- Estado de sesión ---
if "colorized_url" not in st.session_state:
    st.session_state.colorized_url = None
if "video_url" not in st.session_state:
    st.session_state.video_url = None

# --- Área principal ---
col1, col2, col3 = st.columns([1, 1, 1])

# Columna 1 — Imagen B&N
with col1:
    st.subheader("Imagen B&N")
    uploaded_file = st.file_uploader("Sube imagen B&N", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

    if st.button("Colorize", disabled=uploaded_file is None):
        uploaded_file.seek(0)
        response = requests.post(
            f"{BACKEND_URL}/colorize",
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
        )
        st.session_state.colorized_url = response.json()["image_url"]
        st.session_state.video_url = None

# Columna 2 — Imagen Color
with col2:
    st.subheader("Imagen Color")

    if st.session_state.colorized_url:
        st.image(f"{BACKEND_URL}{st.session_state.colorized_url}", use_container_width=True)
    else:
        st.empty()

    prompt = st.text_input("Prompt", placeholder="Describe el video a generar...")

    if st.button("Generate Video", disabled=st.session_state.colorized_url is None):
        response = requests.post(
            f"{BACKEND_URL}/generate-video",
            data={
                "colorized_url": st.session_state.colorized_url,
                "prompt": prompt,
            },
        )
        st.session_state.video_url = response.json()["video_url"]

# Columna 3 — Video
with col3:
    st.subheader("Video")

    if st.session_state.video_url:
        st.video(f"{BACKEND_URL}{st.session_state.video_url}")
    else:
        st.empty()
