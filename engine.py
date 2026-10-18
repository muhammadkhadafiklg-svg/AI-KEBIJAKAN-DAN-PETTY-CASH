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
        url_aturan = "https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt"
        respon_aturan = requests.get(url_aturan)
        aturan = respon_aturan.text if respon_aturan.status_code == 200 else "Gagal membaca Aturan Petty Cash."

        link_sheet_1 = "https://docs.google.com/spreadsheets/d/1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c/edit?usp=sharing"
        link_sheet_2 = "https://docs.google.com/spreadsheets/d/1jCvhYPqyTDJkpismwkPmz3z-wMDs2nE7xC0Doh4cEBI/edit?usp=sharing"
        link_sheet_3 = "https://docs.google.com/spreadsheets/d/1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4/edit?usp=sharing"

        csv_1 = buat_link_csv(link_sheet_1)
        csv_2 = buat_link_csv(link_sheet_2)
        csv_3 = buat_link_csv(link_sheet_3)

        data_sheet_1 = pd.read_csv(csv_1).head(200).to_string(index=False) if csv_1 else "Data Sheet 1 Kosong"
        data_sheet_2 = pd.read_csv(csv_2).head(200).to_string(index=False) if csv_2 else "Data Sheet 2 Kosong"
        data_sheet_3 = pd.read_csv(csv_3).head(200).to_string(index=False) if csv_3 else "Data Sheet 3 Kosong"

        return aturan, data_sheet_1, data_sheet_2, data_sheet_3
    
    except Exception as e:
        return f"Error mengambil data: {e}", "", "", ""

data_aturan, sheet_1, sheet_2, sheet_3 = tarik_data_database()

# ==========================================
# 4. PENGATURAN INSTRUKSI AI
# ==========================================
system_instruction = f"""
Anda adalah Asisten AI yang bertugas membantu kasir toko mengidentifikasi kode COA (Chart of Account) 
dan aturan klaim Petty Cash perusahaan berdasarkan dokumen-dokumen berikut:

1. ATURAN PENTING PETTY CASH:
{data_aturan}

2. KAMUS PETTY CASH (Sheet 1):
{sheet_1}

3. MASTER COA 1 (Sheet 2):
{sheet_2}

4. MASTER COA 2 (Sheet 3):
{sheet_3}

Jawab dengan ramah, ringkas, dan langsung pada intinya. 
Jika data tidak ada, katakan Anda tidak dapat menemukannya.
"""

# ==========================================
# 5. FITUR OBROLAN (CHAT INTERFACE)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🗑️ Hapus Riwayat Chat & Mulai Baru"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 6. LOGIK TANYA JAWAB DENGAN AUTO-FALLBACK
# ==========================================
if prompt := st.chat_input("Ketik pertanyaan kasir di sini (misal: 'COA untuk beli galon?')..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model"):
        pesan_tunggu = st.empty()
        pesan_tunggu.markdown("⏳ *Sedang mencari COA dan Aturan Perusahaan...*")
        
        try:
            # Percobaan 1: Menggunakan Gemini 1.5 Pro (Model paling canggih)
            model = genai.GenerativeModel(model_name="gemini-1.5-pro", system_instruction=system_instruction)
            response = model.generate_content(prompt)
            pesan_tunggu.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
            
        except Exception:
            try:
                # Percobaan 2: Menggunakan Gemini 1.5 Flash (Model cepat)
                model2 = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
                response = model2.generate_content(prompt)
                pesan_tunggu.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
                
            except Exception:
                try:
                    # Percobaan 3: Menggunakan Gemini Pro 1.0 (Model stabil lama yang pasti ada)
                    model3 = genai.GenerativeModel(model_name="gemini-pro")
                    prompt_lengkap = f"{system_instruction}\n\nPertanyaan Kasir: {prompt}"
                    response = model3.generate_content(prompt_lengkap)
                    pesan_tunggu.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                    
                except Exception as e3:
                    pesan_tunggu.error(f"Maaf, semua server AI sedang sibuk. Detail Error: {e3}")
