import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# --- 1. PENGATURAN TAMPILAN (UI/UX) ---
st.set_page_config(page_title="AI Asisten Petty Cash", page_icon="💼", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-title { font-size: 2.5rem; font-weight: 700; color: #0F4C81; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; color: #555555; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("💼 Finance AI")
    st.markdown("---")
    st.markdown("""
    **Selamat Datang!** 👋  
    AI ini tersambung langsung ke database Google Sheets operasional secara *real-time*.
    
    **Sumber Database Aktif:**
    🔗 Google Docs: Aturan Petty Cash
    🔗 Google Sheets: Master COA
    🔗 Google Sheets: Kamus Petty Cash
    """)
    st.markdown("---")
    st.caption("© 2026 Tim Finance - Internal Use Only")

st.markdown('<p class="main-title">Asisten Cerdas Petty Cash & COA</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Ketik pertanyaan Anda, AI akan menjawab berdasarkan Data Google Sheets.</p>', unsafe_allow_html=True)

# --- 2. SETUP GEMINI API ---
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# --- 3. FUNGSI TARIK DATA DARI GOOGLE SHEETS & DOCS ---
# Cache ini menyimpan data selama 1 jam (3600 detik). 
# Jika Anda mengubah Google Sheet, AI akan update ilmu barunya maksimal 1 jam kemudian.
@st.cache_data(ttl=3600, show_spinner="Menyinkronkan data dengan Google Sheets...")
def fetch_live_database():
    # 1. Ambil Aturan dari Google Docs (Format TXT Export)
    doc_url = "https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt"
    try:
        doc_resp = requests.get(doc_url)
        doc_text = doc_resp.text if doc_resp.status_code == 200 else "Gagal memuat aturan Google Docs."
    except:
        doc_text = "Gagal memuat aturan Google Docs."

    # 2. Ambil Master COA dari Google Sheets (Format CSV Export)
    sheet_coa_url = "https://docs.google.com/spreadsheets/d/1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4/export?format=csv"
    try:
        df_coa = pd.read_csv(sheet_coa_url)
        coa_text = df_coa.to_csv(index=False)
    except:
        coa_text = "Gagal memuat Master COA."

    # 3. Ambil Kamus Petty Cash dari Google Sheets (Format CSV Export)
    sheet_kamus_url = "https://docs.google.com/spreadsheets/d/1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c/export?format=csv"
    try:
        df_kamus = pd.read_csv(sheet_kamus_url)
        kamus_text = df_kamus.to_csv(index=False)
    except:
        kamus_text = "Gagal memuat Kamus Petty Cash."

    # Gabungkan semua data menjadi satu "buku panduan" raksasa untuk AI
    full_knowledge_base = f"""
    BERIKUT ADALAH DATABASE PERUSAHAAN (ATURAN DAN COA).
    Jadikan data di bawah ini sebagai SATU-SATUNYA referensi kamu dalam menjawab pertanyaan user.

    === DOKUMEN ATURAN PETTY CASH ===
    {doc_text}

    === DATABASE MASTER COA ===
    {coa_text}

    === KAMUS PETTY CASH (HISTORI KLAIM) ===
    {kamus_text}
    """
    return full_knowledge_base

# --- 4. INISIALISASI MODEL AI ---
@st.cache_resource(show_spinner=False)
def get_ai_chat_session(knowledge_base):
    system_instruction = f"""
    Kamu adalah Asisten Finance AI profesional untuk internal perusahaan ritel (Kawan Lama Group).
    Tugas utamamu adalah membantu kasir menentukan kode COA (Chart of Account) dan menjawab prosedur klaim Petty Cash.
    
    Database kamu telah diisi dengan data real-time dari Google Sheets perusahaan di bawah ini.
    {knowledge_base}
    
    Pedoman menjawab:
    1. Jawablah dengan struktur poin-poin yang rapi.
    2. Gunakan gaya bahasa profesional, solutif, dan ramah.
    3. Analisa kata kunci dari pertanyaan user dan cocokkan dengan 'Deskripsi', 'Kamus Petty Cash', atau 'Master COA' yang ada di database.
    4. Jika jawaban TIDAK ADA di database, mohon jujur dan sarankan pengguna untuk bertanya langsung ke atasan atau tim Finance (Jangan pernah menebak COA secara asal).
    5. Selalu ingatkan aturan penting (misal: nota harus print, aturan IT, dll) jika relevan dengan pertanyaan.
    """
    
    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    system_instruction=system_instruction
)
    return model.start_chat(history=[])

# Tarik data dari Google Sheets & mulai AI
database_text = fetch_live_database()
chat_session = get_ai_chat_session(database_text)

# --- 5. LOGIKA RUANG CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Database Google Sheets sudah berhasil disinkronisasi. Ada yang bisa saya bantu terkait COA atau aturan klaim?"}
    ]

for msg in st.session_state.messages:
    avatar_img = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(msg["content"])

if user_input := st.chat_input("Contoh: Beli air galon untuk karyawan masuk COA apa?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        with st.spinner("Mencari kecocokan di Google Sheets..."):
            try:
                response = chat_session.send_message(user_input)
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                message_placeholder.error(f"Koneksi terganggu. Silakan coba lagi. {e}")
