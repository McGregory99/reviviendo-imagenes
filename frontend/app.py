import requests
import streamlit as st
from supabase import create_client

BACKEND_URL = st.secrets["BACKEND_URL"]
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


# --- Estado de sesión ---
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "colorized_url" not in st.session_state:
    st.session_state.colorized_url = None
if "video_url" not in st.session_state:
    st.session_state.video_url = None
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "show_history" not in st.session_state:
    st.session_state.show_history = False


if st.session_state.user is None:
    st.title("Reviviendo Imágenes")
    tab_login, tab_register = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_password")
        if st.button("Entrar"):
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = response.user
                st.session_state.access_token = response.session.access_token
                st.rerun()
            except Exception as e:
                st.error("Email o contraseña incorrectos")

    with tab_register:
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Contraseña", type="password", key="register_password")
        if st.button("Crear cuenta"):
            try:
                response = supabase.auth.sign_up({"email": email, "password": password})
                st.success("Cuenta creada :)")
            except Exception as e:
                st.error(f"Error al crear la cuenta: {e}")
    st.stop()



# barra lateral
st.sidebar.text(st.session_state.user.email)
st.sidebar.code(st.session_state.access_token)
if st.sidebar.button("Mi Historial"):
    st.session_state.show_history = not st.session_state.show_history
    st.rerun()
if st.sidebar.button("Cerrar Sesión"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.colorized_url = None
    st.session_state.video_url = None
    st.session_state.uploaded_file_data = None
    st.session_state.show_history = False
    st.rerun()

# ── PANTALLA DE HISTORIAL ────────────────────────────────────────────────────
if st.session_state.show_history:
    st.header("Historial de transformaciones")
    response = requests.get(f"{BACKEND_URL}/transformations", headers={"Authorization": f"Bearer {st.session_state.access_token}"})
    transformations = response.json() if response.status_code == 200 else []

    if not transformations:
        st.info("Todavía no has hecho ninguna transformación.")
    else:
        for i, t in enumerate(transformations):
            col1, col2 = st.columns(2)
            with col1:
                st.image(t["colorized_url"], use_container_width=True)
            with col2:
                if t["video_url"]:
                    st.video(t["video_url"])
            if i < len(transformations) - 1:
                st.divider()
    st.stop()

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
        st.image(f"{st.session_state.colorized_url}", use_container_width=True)
    else:
        st.markdown("Esperando colorización...")

with tab_vid:
    st.header("Video")
    if step2_done:
        st.video(f"{st.session_state.video_url}")
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
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
        if response.status_code == 200:
            st.session_state.colorized_url = response.json()["image_url"]

        st.rerun()

with col2:
    prompt = st.text_input("Prompt", placeholder="Describe el video a generar...", disabled=not step1_done)

    if st.button("Generar Video", disabled=not step1_done or not prompt):
        response = requests.post(
            f"{BACKEND_URL}/generate-video", 
            data={"colorized_url": st.session_state.colorized_url, "prompt": prompt},
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
        if response.status_code == 200:
            st.session_state.video_url = response.json()["video_url"]

        st.rerun()

with col3:
    if step1_done:
        image_bytes = requests.get(f"{st.session_state.colorized_url}").content
        st.download_button(
            "Descargar imagen",
            data=image_bytes,
            file_name="colorizada.jpg",
            mime="image/jpeg",
        )    

    if step2_done:
        video_bytes = requests.get(f"{st.session_state.video_url}").content
        st.download_button(
            "Descargar video",
            data=video_bytes,
            file_name="video.mp4",
            mime="video/mp4",
        )    