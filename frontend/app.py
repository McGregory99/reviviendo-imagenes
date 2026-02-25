import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

# barra lateral
st.sidebar.text("USUARIO")
st.sidebar.button("Cerrar Sesión")

# --- Estado de sesión ---
if "colorized_url" not in st.session_state:
    st.session_state.colorized_url = None
if "video_url" not in st.session_state:
    st.session_state.video_url = None
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None

step1_done = st.session_state.colorized_url is not None
step2_done = st.session_state.video_url is not None

# --- FILA SUPERIOR: visualización ---
tab_orig, tab_color, tab_vid = st.tabs(["Original", "Colorizado", "Video"])
with tab_orig:
    st.header("Imagen Original")
    if st.session_state.uploaded_file_data:
        st.image(st.session_state.uploaded_file_data, use_container_width=True)
    else:
        st.markdown("Sube una imagen")

with tab_color:
    st.header("Imagen Colorizada")
    if step1_done:
        st.image(f"{BACKEND_URL}{st.session_state.colorized_url}", use_container_width=True)
    else:
        st.markdown("Esperando colorización...")

with tab_vid:
    st.header("Video")
    if step2_done:
        st.video(f"{BACKEND_URL}{st.session_state.video_url}")
    else:
        st.markdown("Esperando video")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    uploaded_file = st.file_uploader("Sube imagen B&N", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.session_state.uploaded_file_data = uploaded_file.read()
        uploaded_file.seek(0)

    if st.button("Colorizar", disabled=uploaded_file is None):
        response = requests.post(
            f"{BACKEND_URL}/colorize", 
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            )
        if response.status_code == 200:
            st.session_state.colorized_url = response.json()["image_url"]

        st.rerun()

with col2:
    prompt = st.text_input("Prompt", placeholder="Describe el video a generar...", disabled=not step1_done)

    if st.button("Generar Video", disabled=not step1_done or not prompt):
        response = requests.post(
            f"{BACKEND_URL}/generate-video", 
            data={"colorized_url": st.session_state.colorized_url, "prompt": prompt}
            )
        if response.status_code == 200:
            st.session_state.video_url = response.json()["video_url"]

        st.rerun()

with col3:
    if step1_done:
        image_bytes = requests.get(f"{BACKEND_URL}{st.session_state.colorized_url}").content
        st.download_button(
            "Descargar imagen",
            data=image_bytes,
            file_name="colorizada.jpg",
            mime="image/jpeg",
        )    

    if step2_done:
        video_bytes = requests.get(f"{BACKEND_URL}{st.session_state.video_url}").content
        st.download_button(
            "Descargar video",
            data=video_bytes,
            file_name="video.mp4",
            mime="video/mp4",
        )    