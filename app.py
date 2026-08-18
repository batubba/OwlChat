import base64
import html
import time
import streamlit as st
from google import genai
from google.genai import types

# OWLCHAT - TEK DOSYA SÜRÜMÜ
st.set_page_config(
    page_title="OwlChat",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_NAME = "gemini-2.5-flash"

# API ANAHTARI
API_KEY = "AQ.Ab8RN6LQwSWgll3qRysfwDgZLJfbxWpx9IkNdfBCWWX8I0R6hA"

if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    API_KEY = st.secrets["GEMINI_API_KEY"]

# GÖMÜLÜ BAYKUŞ LOGOSU (Ekran görüntündeki logonun tam base64 verisi)
LOGO_B64 = """/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQAAABtbnRyUkdCIFhZWiAHsAABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAADcAA2LcZXNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0ZXh0AAAAAENvcHlyaWdodCBBcHBsZSBJbmMuLCAyMDI2AABYWVogAAAAAAAAYpkAALeFAAAY2lhZXogAAAAAAAAAAAAAABXWVogAAAAAAAAYpkAALeFAAAY2lhZXogAAAAAAAAAAAAAABXWVogAAAAAAAAYpkAALeFAAAY2lhZXogAAAAAAAAAAAAAABWWVogAAAAAAAAb6AAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjnA"""
LOGO_DATA = "data:image/jpeg;base64," + LOGO_B64

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

# ARAYÜZ VE YAN MENÜ
with st.sidebar:
    st.image(LOGO_DATA, width=100)
    st.title("OwlChat")

    # API Key koda yazılmadıysa kenar çubuğunda giriş alanı gösterir
    if not API_KEY:
        API_KEY = st.text_input(
            "Gemini API Key girin:", type="password", key="api_key_input"
        )

    if st.button("+ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("Geçmiş Sohbetler")
    st.caption("Bu oturumdaki mesajlar saklanır.")

# CLIENT OLUŞTURMA
client = genai.Client(api_key=API_KEY) if API_KEY else None

# SOHBET AKIŞI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Kullanıcı girdisi
user_input = st.chat_input("OwlChat'e sorun...")

if user_input:
    if not API_KEY or not client:
        st.error("Lütfen sol menüden geçerli bir Gemini API Key girin!")
    else:
        # Kullanıcı mesajını ekle ve göster
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Gemini yanıtını al ve akışlı (stream) olarak göster
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                response = client.models.generate_content_stream(
                    model=MODEL_NAME,
                    contents=user_input,
                )
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
