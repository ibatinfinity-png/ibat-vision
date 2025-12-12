import streamlit as st
import google.generativeai as genai
from PIL import Image # Library pengolah gambar

# --- 1. KONFIGURASI API ---
# Mengambil kunci dari Brankas Streamlit
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. CONFIG HALAMAN ---
st.set_page_config(page_title="IbatGPT Vision", page_icon="👁️", layout="centered")

# --- 3. CSS (TAMPILAN BERSIH) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stChatInput {border-radius: 20px;}
</style>
""", unsafe_allow_html=True)

# --- 4. OTAK AI ---
sys_prompt = """
Kamu adalah IbatGPT, asisten visual cerdas.
Kemampuanmu: Bisa melihat gambar dan menganalisisnya secara mendalam.
Gaya bicara: Profesional, Cerdas, Bahasa Indonesia.
"""
model = genai.GenerativeModel('gemini-flash-latest', system_instruction=sys_prompt)

# --- 5. SIDEBAR (UPLOAD GAMBAR) ---
with st.sidebar:
    st.title("👁️ Ibat Vision")
    
    # Fitur Mata (Upload)
    uploaded_file = st.file_uploader("Upload Gambar/Foto:", type=["jpg", "png", "jpeg"])
    
    image_data = None
    if uploaded_file is not None:
        # Tampilkan gambar di sidebar
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Gambar Terupload", use_container_width=True)
        st.success("Mata AI Aktif! Tanyakan sesuatu soal gambar ini.")

    st.markdown("---")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. LOGIKA CHAT ---
st.title("IbatGPT Vision 👁️")
st.caption("Kirim foto di menu kiri, lalu tanya saya apa saja.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Chat
if prompt := st.chat_input("Analisa gambar ini atau tanya sesuatu..."):
    # Tampilkan pesan user
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Proses Jawaban
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # LOGIKA VISION:
            # Jika ada gambar, kirim [Prompt + Gambar]
            # Jika tidak ada, kirim [Prompt] saja
            
            prompt_paksa = f"{prompt}\n\n(Jawab HANYA Bahasa Indonesia)"
            
            if image_data:
                # Mode Vision (Lihat Gambar)
                response = model.generate_content([prompt_paksa, image_data])
            else:
                # Mode Teks Biasa (Chat)
                chat = model.start_chat(history=[]) # Stateless untuk simplifikasi
                response = chat.send_message(prompt_paksa)
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:

            st.error(f"Error Vision: {e}")
