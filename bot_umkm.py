import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. KONFIGURASI API (AMBIL DARI SECRETS) ---
# Pastikan sudah diset di Streamlit Cloud Settings -> Secrets
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception:
    st.error("⚠️ API Key belum disetting di Secrets!")
    st.stop()

# --- 2. CONFIG HALAMAN (MODERN LOOK) ---
st.set_page_config(
    page_title="Ibat AI Vision", 
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed" # Sidebar otomatis nutup biar bersih
)

# --- 3. CSS INJECTION (MAKEUP TOTAL) ---
st.markdown("""
<style>
    /* Sembunyikan elemen bawaan Streamlit yang mengganggu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Kustomisasi area input chat biar lebih bulat modern */
    .stChatInput input {
        border-radius: 25px !important;
        border: 1px solid #ddd !important;
        padding: 10px 15px !important;
    }
    
    /* Sedikit merapikan padding atas */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. OTAK AI ---
sys_prompt = """
Kamu adalah Ibat AI, asisten virtual yang cerdas, ramah, dan modern.
Tugasmu: Membantu pengguna menganalisis gambar atau menjawab pertanyaan bisnis/umum.
Gaya bicara: Santai tapi profesional, gunakan emoji sesekali agar ramah.
WAJIB: Jawab dalam Bahasa Indonesia.
"""
model = genai.GenerativeModel('gemini-flash-latest', system_instruction=sys_prompt)

# --- 5. HEADER MODERN (HEADER BOT) ---
col1, col2 = st.columns([1, 5])
with col1:
    # Ganti URL ini dengan gambar robot lain jika mau
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=60)
with col2:
    st.title("Ibat AI Assistant")
    st.caption("Online | Siap membantu menganalisis foto & bisnis Anda.")

st.divider() # Garis pemisah tipis

# --- 6. FITUR UPLOAD YANG LEBIH MUDAH (DI TENGAH) ---
# Tidak di sidebar lagi, tapi pakai Expander di area utama
with st.expander("📸 Klik di sini untuk Mengirim Gambar/Foto"):
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    image_data = None
    if uploaded_file is not None:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Preview Gambar", width=300)
        st.info("✅ Gambar siap dikirim! Ketik pertanyaanmu di bawah.")

# Tombol Reset di pojok kanan atas (pakai kolom biar rapi)
col_reset_space, col_reset_btn = st.columns([4, 1])
with col_reset_btn:
    if st.button("🗑️ Reset", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 7. LOGIKA CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan History dengan Avatar Keren
for message in st.session_state.messages:
    # Pilih avatar berdasarkan role
    avatar_icon = "🧑‍💼" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# Input Chat
if prompt := st.chat_input("Ketik pesan atau pertanyaan tentang gambar..."):
    # 1. Tampilkan pesan user
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Proses Jawaban
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        try:
            prompt_paksa = f"{prompt}\n\n(Jawab santai & ramah dalam Bahasa Indonesia)"
            
            if image_data:
                # Mode Vision (Gambar + Teks)
                with st.spinner("Sedang melihat gambar..."):
                    response = model.generate_content([prompt_paksa, image_data])
            else:
                # Mode Teks Biasa
                with st.spinner("Sedang mengetik..."):
                    chat = model.start_chat(history=[])
                    response = chat.send_message(prompt_paksa)
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Waduh error: {e}")
