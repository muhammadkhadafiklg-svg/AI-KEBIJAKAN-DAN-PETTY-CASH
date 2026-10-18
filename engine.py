import streamlit as st
import pandas as pd
import requests
import json

# ==========================================
# 1. PENGATURAN HALAMAN STREAMLIT
# ==========================================
st.set_page_config(page_title="Asisten Petty Cash", page_icon="🤖", layout="wide")
st.title("🤖 Asisten AI Petty Cash & COA")
st.caption("Tanyakan aturan Petty Cash, kode COA, atau riwayat klaim di sini.")

# ==========================================
# 2. AUTENTIKASI API KEY
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key belum dimasukkan di menu Secrets Streamlit!")
    st.stop()

# ==========================================
# 3. FUNGSI TARIK DATA DATABASE
# ==========================================
def buat_link_csv(url_asli):
    if "/d/" in url_asli and "/edit" in url_asli:
        id_sheet = url_asli.split("/d/")[1].split("/edit")[0]
        return f"https://docs.google.com/spreadsheets/d/{id_sheet}/export?format=csv"
    return None

@st.cache_data(ttl=3600) 
def tarik_data_database():
    try:
        # A. Aturan Petty Cash
        url_aturan = "https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt"
        respon_aturan = requests.get(url_aturan)
        aturan = respon_aturan.text if respon_aturan.status_code == 200 else "Gagal membaca Aturan Petty Cash."

        # B. Tiga Master Data (Google Sheets)
        link_1 = "https://docs.google.com/spreadsheets/d/1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c/edit?usp=sharing"
        link_2 = "https://docs.google.com/spreadsheets/d/1jCvhYPqyTDJkpismwkPmz3z-wMDs2nE7xC0Doh4cEBI/edit?usp=sharing"
        link_3 = "https://docs.google.com/spreadsheets/d/1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4/edit?usp=sharing"

        csv_1, csv_2, csv_3 = buat_link_csv(link_1), buat_link_csv(link_2), buat_link_csv(link_3)

        data_1 = pd.read_csv(csv_1).head(200).to_string(index=False) if csv_1 else ""
        data_2 = pd.read_csv(csv_2).head(200).to_string(index=False) if csv_2 else ""
        data_3 = pd.read_csv(csv_3).head(200).to_string(index=False) if csv_3 else ""

        return aturan, data_1, data_2, data_3
    
    except Exception as e:
        return f"Error mengambil data: {e}", "", "", ""

data_aturan, sheet_1, sheet_2, sheet_3 = tarik_data_database()

# ==========================================
# 4. INSTRUKSI SISTEM AI
# ==========================================
system_instruction = f"""
Anda adalah Asisten AI yang bertugas membantu kasir toko mengidentifikasi kode COA (Chart of Account) 
dan aturan klaim Petty Cash perusahaan berdasarkan dokumen-dokumen berikut:
1. ATURAN: {data_aturan}
2. KAMUS & HISTORY: {sheet_1}
3. MASTER COA 1: {sheet_2}
4. MASTER COA 2: {sheet_3}

Jawab dengan ramah, ringkas, dan langsung pada intinya. Jika data tidak ada, katakan Anda tidak menemukannya.
"""

# ==========================================
# 5. FITUR OBROLAN (CHAT INTERFACE)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🗑️ Hapus Riwayat Chat"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 6. LOGIK JALUR LANGSUNG (BYPASS ERROR)
# ==========================================
if prompt := st.chat_input("Ketik pertanyaan kasir di sini (misal: 'COA untuk galon?')..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model"):
        pesan_tunggu = st.empty()
        pesan_tunggu.markdown("⏳ *Menghubungi server pusat perusahaan...*")
        
        # Menyusun riwayat percakapan untuk dikirim
        riwayat_pesan = []
        for msg in st.session_state.messages:
            riwayat_pesan.append({
                "role": "model" if msg["role"] == "model" else "user",
                "parts": [{"text": msg["content"]}]
            })

        # Tembak langsung ke API Google tanpa perantara library
        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": riwayat_pesan
        }
        
        try:
            response = requests.post(url_api, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            
            if response.status_code == 200:
                jawaban = response.json()['candidates'][0]['content']['parts'][0]['text']
                pesan_tunggu.markdown(jawaban)
                st.session_state.messages.append({"role": "model", "content": jawaban})
            else:
                # Jika masih error, sistem akan mencetak teks error asli dari Google agar kita tahu penyebab pastinya
                pesan_tunggu.error(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            pesan_tunggu.error(f"Gagal terhubung ke internet: {e}")
