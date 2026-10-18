import streamlit as st
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN & DESAIN CHAT
# ==========================================
st.set_page_config(page_title="AI Petty Cash (Mode Gratis)", page_icon="✨", layout="centered")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stChatInputContainer { padding-bottom: 20px; }
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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (PANEL SAMPING)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #1E1E1E; font-size: 22px;">Finance Asisten</h2>
            <p style="color: #0056b3; font-size: 13px; font-weight:bold;">⚡ Mode Bebas Kuota (100% Gratis)</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Tips Pencarian:**\nKetik kata kunci lebih dari satu untuk hasil spesifik. (Contoh: *BBM Mobil* atau *Sewa Gedung*).")
    
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
    <div style="background-color: #f4f7f6; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid #0056b3;">
        <h3 style="margin: 0; color: #1a1a1a; font-size: 22px;">✨ Chat Operasional Petty Cash</h3>
        <p style="margin: 5px 0 0 0; color: #555; font-size: 14px;">Sistem pencarian cerdas berbasis data langsung.</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. TARIK DATA DARI GOOGLE SHEETS & DOCS
# ==========================================
def buat_link_csv(url):
    if "/d/" in url and "/edit" in url:
        return f"https://docs.google.com/spreadsheets/d/{url.split('/d/')[1].split('/edit')[0]}/export?format=csv"
    return None

@st.cache_data(ttl=3600) 
def tarik_data_mentah():
    try:
        r = requests.get("https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt")
        aturan = r.text.strip() if r.status_code == 200 else ""
        
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
# 5. INISIALISASI CHAT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Halo! Saya Asisten Finance M Khadafi Zainal. Apa yang ingin Anda cari hari ini? (Ketik nama transaksi atau barang)"}
    ]

for msg in st.session_state.messages:
    ikon = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=ikon):
        st.markdown(msg["content"])

# ==========================================
# 6. LOGIK PENCARIAN & DESAIN DAFTAR (ANTI-UNNAMED & ANTI-ERROR)
# ==========================================
if prompt := st.chat_input("Tulis kata kunci pencarian di sini..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model", avatar="✨"):
        keyword = prompt.lower().strip()
        jawaban_bot = ""
        ditemukan = False
        
        def rangkai_kartu(df, nama_sumber):
            if df.empty: return ""
            
            keywords = keyword.split()
            mask = pd.Series([True] * len(df), index=df.index)
            
            for k in keywords:
                # PERBAIKAN BUG PYARROW: Menggunakan pencarian teks Python asli yang jauh lebih aman
                mask = mask & df.apply(lambda row: k in " ".join(row.astype(str)).lower(), axis=1)
                
            hasil = df[mask]
            
            if not hasil.empty:
                hasil = hasil.head(15) 
                kolom = list(hasil.columns)
                
                teks = f"### 📂 {nama_sumber} ({len(hasil)} Kecocokan)\n\n"
                
                for i, (_, row) in enumerate(hasil.iterrows(), 1):
                    teks += f"🔹 **Pilihan {i}**\n"
                    for col in kolom:
                        val = str(row[col]).replace("\n", " ").strip()
                        
                        if val and val.lower() != "nan" and val != "-":
                            if "unnamed" in str(col).lower():
                                teks += f"   ▪️ {val}\n"  
                            else:
                                teks += f"   ▪️ **{col}:** {val}\n" 
                    teks += "\n---\n\n"
                    
                return teks
            return ""

        hasil_1 = rangkai_kartu(df1, "Kamus COA")
        hasil_2 = rangkai_kartu(df2, "Master Data 1")
        hasil_3 = rangkai_kartu(df3, "Master Data 2")
        
        if hasil_1 or hasil_2 or hasil_3:
            jawaban_bot += "Berikut adalah hasil pencarian yang sudah dirapikan:\n\n"
            jawaban_bot += hasil_1 + hasil_2 + hasil_3
            ditemukan = True
            
        if keyword in data_aturan.lower():
            kalimat_aturan = [baris.strip() for baris in data_aturan.split('\n') if keyword in baris.lower()]
            if kalimat_aturan:
                jawaban_bot += "### 📜 Kebijakan Operasional Terkait:\n"
                for k in kalimat_aturan[:3]: 
                    jawaban_bot += f"> *\"{k}\"*\n\n"
                ditemukan = True

        if not ditemukan:
            jawaban_bot = f"Maaf, saya tidak dapat menemukan informasi terkait '{prompt}'. Coba gunakan kata kunci yang lebih umum (misal: Bensin, Solar, atau Transport)."
            
        st.markdown(jawaban_bot)
        st.session_state.messages.append({"role": "model", "content": jawaban_bot})
