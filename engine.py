import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN STREAMLIT
# ==========================================
st.set_page_config(page_title="Asisten Petty Cash", page_icon="🤖", layout="wide")
st.title("🤖 Asisten AI Petty Cash & COA")
st.caption("Tanyakan aturan Petty Cash, kode COA, atau riwayat klaim di sini.")

# ==========================================
# 2. AUTENTIKASI API KEY GEMINI
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("API Key belum dimasukkan di menu Secrets Streamlit!")
    st.stop()

# ==========================================
# 3. FUNGSI TARIK DATA DATABASE (DOCS & SHEETS)
# ==========================================
# Fungsi untuk mengubah link Google Sheets menjadi format unduhan CSV
def buat_link_csv(url_asli):
    # Mengambil ID dari link Google Sheets
    if "/d/" in url_asli and "/edit" in url_asli:
        id_sheet = url_asli.split("/d/")[1].split("/edit")[0]
        # Mengubah link menjadi format CSV
        return f"https://docs.google.com/spreadsheets/d/{id_sheet}/export?format=csv"
    return None

@st.cache_data(ttl=3600) 
def tarik_data_database():
    try:
        # A. TARIK DATA ATURAN PETTY CASH (Dari Google Docs Anda)
        url_aturan = "https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt"
        respon_aturan = requests.get(url_aturan)
        aturan = respon_aturan.text if respon_aturan.status_code == 200 else "Gagal membaca Aturan Petty Cash."

        # B. TARIK DATA DARI TIGA GOOGLE SHEETS ANDA
        link_sheet_1 = "https://docs.google.com/spreadsheets/d/1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c/edit?usp=sharing"
        link_sheet_2 = "https://docs.google.com/spreadsheets/d/1jCvhYPqyTDJkpismwkPmz3z-wMDs2nE7xC0Doh4cEBI/edit?usp=sharing"
        link_sheet_3 = "https://docs.google.com/spreadsheets/d/1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4/edit?usp=sharing"

        # Mengubah link ke format CSV
        csv_1 = buat_link_csv(link_sheet_1)
        csv_2 = buat_link_csv(link_sheet_2)
        csv_3 = buat_link_csv(link_sheet_3)

        # Membaca data menggunakan Pandas (maksimal 200 baris agar tidak berat)
        data_sheet_1 = pd.read_csv(csv_1).head(200).to_string(index=False) if csv_1 else "Data Sheet 1 Kosong"
        data_sheet_2 = pd.read_csv(csv_2).head(200).to_string(index=False) if csv_2 else "Data Sheet 2 Kosong"
        data_sheet_3 = pd.read_csv(csv_3).head(200).to_string(index=False) if csv_3 else "Data Sheet 3 Kosong"

        return aturan, data_sheet_1, data_sheet_2, data_sheet_3
    
    except Exception as e:
        return f"Error mengambil data: {e}", "", "", ""

# Jalankan fungsi tarik data
data_aturan, sheet_1, sheet_2, sheet_3 = tarik_data_database()

# ==========================================
# 4. PENGATURAN INSTRUKSI AI & MODEL
# ==========================================
system_instruction = f"""
Anda adalah Asisten AI yang bertugas membantu kasir toko mengidentifikasi kode COA (Chart of Account) 
dan aturan klaim Petty Cash perusahaan berdasarkan dokumen-dokumen berikut:

1. ATURAN PENTING PETTY CASH:
{data_aturan}

2. KAMUS PETTY CASH & HISTORY (Sheet 1):
{sheet_1}

3. MASTER COA 1 (Sheet 2):
{sheet_2}

4. MASTER COA 2 (Sheet 3):
{sheet_3}

Jawab dengan ramah, ringkas, dan langsung pada intinya. 
Tugas utama Anda adalah menemukan COA/Keterangan yang tepat berdasarkan kata kunci dari Kasir.
Jika data tidak ada, katakan Anda tidak dapat menemukannya.
"""

# Inisialisasi model AI
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    system_instruction=system_instruction
)

# ==========================================
# 5. FITUR OBROLAN (CHAT INTERFACE)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tombol untuk menghapus obrolan
if st.button("🗑️ Hapus Riwayat Chat & Mulai Baru"):
    st.session_state.messages = []
    st.rerun()

# Menampilkan chat di layar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 6. LOGIK TANYA JAWAB (SUDAH DIPERBAIKI := )
# ==========================================
if prompt := st.chat_input("Ketik pertanyaan kasir di sini (misal: 'COA untuk beli galon?')..."):
    
    # Tampilkan pertanyaan kasir
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Proses jawaban AI
    with st.chat_message("model"):
        pesan_tunggu = st.empty()
        pesan_tunggu.markdown("⏳ *Sedang mencari COA dan Aturan Perusahaan...*")
        
        try:
            # Kirim ke Gemini
            response = model.generate_content(prompt)
            pesan_tunggu.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
            
        except Exception as e:
            pesan_tunggu.error(f"Maaf, terjadi gangguan pada server: {e}")
