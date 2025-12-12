import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. KONFIGURASI API (WAJIB DARI SECRETS) ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception:
    st.error("⚠️ API Key belum disetting!")
    st.stop()

# --- 2. CONFIG HALAMAN ---
st.set_page_config(
    page_title="Ibat AI", 
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 3. CSS "FLYPERPLEX" STYLE ---
st.markdown("""
<style>
    /* Paksa Mode Terang & Font Bersih */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    
    /* Hilangkan Elemen Bawaan */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Style Kartu Saran (Buttons) */
    .stButton button {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        color: #495057;
        font-weight: 600;
        padding: 1rem;
        transition: all 0.2s;
    }
    .stButton button:hover {
        border-color: #228be6;
        color: #228be6;
        background-color: #e7f5ff;
        transform: translateY(-2px);
    }
    
    /* Input Chat Bulat */
    .stChatInput input {
        border-radius: 30px !important;
        border: 1px solid #ced4da !important;
    }
    
    /* Judul Besar */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. OTAK AI ---
sys_prompt = """
Kamu adalah Ibat AI, asisten bisnis profesional.
Gaya bicara: Cerdas, Ringkas, Solutif (seperti konsultan top tier).
Bahasa: Indonesia Formal & Santai (seimbang).
"""
model = genai.GenerativeModel('gemini-flash-latest', system_instruction=sys_prompt)

# --- 5. LOGIKA SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fungsi untuk menambah chat dari tombol kartu
def klik_kartu(prompt_text):
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    # Kita tidak rerun manual, biarkan flow di bawah menangkapnya

# --- 6. TAMPILAN UTAMA (LANDING PAGE VS CHAT MODE) ---

# Jika chat masih kosong, tampilkan Landing Page ala "FlyPerplex"
if not st.session_state.messages:
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True) # Spacer
    st.title("Selamat Datang di Ibat AI ✨")
    st.markdown("### *Asisten Pribadi untuk Bisnis & Produktivitas Anda.*")
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # 3 KARTU SARAN (GRID)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Ide Bisnis", use_container_width=True, help="Cari ide usaha modal kecil"):
            klik_kartu("Berikan saya 3 ide bisnis modal 1 juta yang lagi tren di 2025.")
            st.rerun()
            
    with col2:
        if st.button("📈 Strategi Marketing", use_container_width=True, help="Tips promosi di sosmed"):
            klik_kartu("Buatkan strategi konten Instagram untuk jualan makanan selama seminggu.")
            st.rerun()
            
    with col3:
        if st.button("💪 Motivasi Sukses", use_container_width=True, help="Kata-kata penyemangat"):
            klik_kartu("Berikan saya motivasi ala triliuner agar semangat kerja hari ini.")
            st.rerun()

# --- 7. AREA CHAT ---
# Tampilkan history jika ada
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "✨"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 8. INPUT AREA DENGAN UPLOAD GAMBAR ---
# Kita pakai container kosong di bawah biar rapi
bottom_container = st.container()

with bottom_container:
    # 1. Fitur Upload Gambar (Pakai Popover biar rapi kayak menu attach)
    with st.popover("📎 Upload Gambar (Klik Disini)", use_container_width=True):
        st.caption("Kirim foto untuk dianalisa AI")
        uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
    image_data = None
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.toast("✅ Gambar berhasil diupload!", icon="📸")
        # Tampilkan preview kecil di chat biar user tau
        with st.expander("Lihat Gambar Terupload"):
            st.image(image_data, width=200)

    # 2. Chat Input
    if prompt := st.chat_input("Ketik pesan Anda di sini..."):
        # Tampilkan pesan user
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Proses Jawaban
        with st.chat_message("assistant", avatar="✨"):
            message_placeholder = st.empty()
            try:
                prompt_paksa = f"{prompt}\n\n(Jawab Bahasa Indonesia)"
                
                # Cek apakah ada gambar di sesi ini
                if image_data:
                    with st.spinner("Menganalisis gambar... 👁️"):
                        response = model.generate_content([prompt_paksa, image_data])
                else:
                    with st.spinner("Berpikir... ✨"):
                        chat = model.start_chat(history=[])
                        response = chat.send_message(prompt_paksa)
                
                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- 9. TOMBOL RESET DI SIDEBAR (BIAR BERSIH) ---
with st.sidebar:
    st.header("Pengaturan")
    if st.button("🗑️ Hapus Chat", type="primary"):
        st.session_state.messages = []
        st.rerun()
