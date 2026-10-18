import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN & DESAIN MINIMALIS
# ==========================================
st.set_page_config(page_title="AI Petty Cash & Kebijakan", page_icon="✨", layout="centered")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            color: #333333;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            border-color: #0056b3;
            color: #0056b3;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        }
        .stChatInputContainer {
            padding-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (PANEL SAMPING PROFESIONAL)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/2942/2942813.png" width="70" style="margin-bottom: 10px;">
            <h2 style="margin: 0; color: #1E1E1E; font-size: 22px;">Finance AI</h2>
            <p style="color: #666666; font-size: 13px;">Sistem Asisten Operasional</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Informasi Sistem:**\nDatabase membaca seluruh baris data secara cerdas menggunakan pencarian otomatis.")
    
    st.divider()
    
    if st.button("🔄 Bersihkan Obrolan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    
    st.markdown("""
        <div style="text-align: center; margin-top: 40px; padding: 15px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #eeeeee;">
            <p style="font-size: 11px; color: #888888; margin: 0; text-transform: uppercase; letter-spacing: 1px;">Developed By</p>
            <p style="font-size: 16px; font-weight: bold; color: #2c3e50; margin: 5px 0 2px 0;">M Khadafi Zainal</p>
            <p style="font-size: 12px; font-weight: 600; color: #0056b3; margin: 0;">Finance Representative</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HEADER UTAMA
# ==========================================
st.markdown("""
    <div style="background-color: #f4f7f6; padding: 20px 25px; border-radius: 12px; margin-bottom: 30px; border-left: 5px solid #0056b3;">
        <h3 style="margin: 0; color: #1a1a1a; font-size: 24px;">✨ AI Petty Cash dan Kebijakan Lainnya</h3>
        <p style="margin: 8px 0 0 0; color: #555555; font-size: 15px;">Dapatkan panduan kode COA dan aturan operasional secara instan & akurat.</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. AUTENTIKASI API KEY
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("API Key belum dimasukkan di menu Secrets Streamlit!")
    st.stop()

# ==========================================
# 5. FUNGSI TARIK DATA (PENCARIAN CERDAS PANDAS)
# ==========================================
def buat_link_csv(url):
    if "/d/" in url and "/edit" in url:
        return f"https://docs.google.com/spreadsheets/d/{url.split('/d/')[1].split('/edit')[0]}/export?format=csv"
    return None

@st.cache_data(ttl=3600) 
def tarik_data_mentah():
    try:
        r = requests.get("https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt")
        aturan = r.text.strip() if r.status_code == 200 else "Gagal baca aturan."
        
        l1 = buat_link_csv("https://docs.google.com/spreadsheets/d/1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c/edit?usp=sharing")
        l2 = buat_link_csv("https://docs.google.com/spreadsheets/d/1jCvhYPqyTDJkpismwkPmz3z-wMDs2nE7xC0Doh4cEBI/edit?usp=sharing")
        l3 = buat_link_csv("https://docs.google.com/spreadsheets/d/1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4/edit?usp=sharing")
        
        df1 = pd.read_csv(l1).dropna(how='all').dropna(axis=1, how='all').fillna("") if l1 else pd.DataFrame()
        df2 = pd.read_csv(l2).dropna(how='all').dropna(axis=1, how='all').fillna("") if l2 else pd.DataFrame()
        df3 = pd.read_csv(l3).dropna(how='all').dropna(axis=1, how='all').fillna("") if l3 else pd.DataFrame()
        
        return aturan, df1, df2, df3
    except Exception:
        return "", pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

data_aturan, df1, df2, df3 = tarik_data_mentah()

# ==========================================
# 6. INISIALISASI MODEL AI (PERSONA)
# ==========================================
instruksi_dasar = f"""
IDENTITAS ANDA:
Jika pengguna bertanya "kamu siapa", "siapa namamu", "siapa anda", atau tentang identitas Anda, Anda WAJIB menjawab persis dengan kalimat ini:
"Aku adalah AI asisten M Khadafi Zainal yang akan membantu permasalahan Anda yang berhubungan dengan Accounting Operational."

TUGAS UTAMA:
Anda adalah Asisten AI untuk membantu operasional toko mengidentifikasi COA dan aturan Petty Cash.
- Jawab SANGAT SINGKAT, rapi, dan langsung ke inti jawaban.
- HANYA gunakan data referensi yang diberikan di bawah ini. Dilarang keras mengarang kode COA.
- Jika data tidak ditemukan, katakan: "Maaf, data tersebut tidak ditemukan di sistem."

ATURAN PERUSAHAAN:\n{data_aturan}
"""

model = genai.GenerativeModel(model_name="gemini-3.8-flash", system_instruction=instruksi_dasar)

# ==========================================
# 7. ANTARMUKA OBROLAN & PENCARIAN DINAMIS
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Halo! Saya adalah AI Asisten Anda. Ada yang bisa saya bantu terkait *Petty Cash* dan Kebijakan Operasional?"}
    ]

for msg in st.session_state.messages:
    ikon = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=ikon):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ketikkan pencarian Anda di sini (misal: nama barang atau transaksi)..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model", avatar="✨"):
        tunggu = st.empty()
        tunggu.markdown("⏳ *Memindai ribuan baris database...*")
        
        try:
            # FUNGSI PENCARIAN CERDAS (PANDAS FILTERING)
            # Mencari baris di Google Sheet yang mengandung kata kunci dari pertanyaan kasir
            keyword = prompt.lower()
            
            def cari_data_relevan(df):
                if df.empty: return ""
                # Mengubah seluruh dataframe menjadi string lowercase untuk dicari kecocokannya
                mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)
                hasil_filter = df[mask]
                if not hasil_filter.empty:
                    # Ambil maksimal 15 baris yang paling cocok untuk dikirim ke AI
                    return hasil_filter.head(15).to_csv(index=False)
                return ""

            s1_relevan = cari_data_relevan(df1)
            s2_relevan = cari_data_relevan(df2)
            s3_relevan = cari_data_relevan(df3)
            
            # Jika kata kunci tidak ditemukan lewat pencarian, ambil sampel teratas sebagai cadangan
            if not s1_relevan and not s2_relevan and not s3_relevan:
                s1_relevan = df1.head(20).to_csv(index=False)
                s2_relevan = df2.head(20).to_csv(index=False)
                s3_relevan = df3.head(20).to_csv(index=False)

            # Susun konteks khusus untuk pertanyaan ini saja
            konteks_dinamis = f"""
            DATA KAMUS 1 (HASIL PENCARIAN):\n{s1_relevan}
            DATA MASTER 1 (HASIL PENCARIAN):\n{s2_relevan}
            DATA MASTER 2 (HASIL PENCARIAN):\n{s3_relevan}
            """
            
            # Kirim pertanyaan beserta data spesifik yang sudah difilter ke AI
            chat_session = model.start_chat(history=[])
            respon_lengkap = chat_session.send_message(f"{konteks_dinamis}\n\nPertanyaan Kasir: {prompt}")
            
            tunggu.markdown(respon_lengkap.text)
            st.session_state.messages.append({"role": "model", "content": respon_lengkap.text})
            
        except Exception as e:
            if "429" in str(e):
                tunggu.error("⚠️ Batas limit kuota per menit tercapai. Mohon tunggu sekitar 1 menit lalu coba ketik ulang.")
            else:
                tunggu.error(f"Koneksi terganggu: {e}")
