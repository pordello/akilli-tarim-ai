# ==============================================================================
# PROJE: AI Destekli Akıllı Tarım Platformu (TAM SÜRÜM + FATURA DÜZENLEME)
# ==============================================================================

import streamlit as st
import random
import requests
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import altair as alt
import time

st.set_page_config(page_title="AI Akıllı Tarım Paneli", page_icon="🌾", layout="wide")

# --- ÇOKLU DİL SÖZLÜĞÜ VE ÇEVİRİ MOTORU ---
dil_sozlugu = {
    "TR": {
        "baslik": "🌾 AI Akıllı Tarım ERP Kontrol Merkezi",
        "cikis_yap": "🚪 Çıkış Yap",
        "genel_merkez": "🏠 Genel Tarla Rapor Merkezi",
        "borsa_ekrani": "📈 Canlı Tarım Borsası",
        "depo_yonetimi": "📦 Depo ve Satın Alma Yönetimi",
        "makine_garaji": "🚜 Makine ve Ekipman Garajı",
        "ai_asistan": "🤖 AI Ziraat Asistanı",
        "yeni_tarla_ekle": "➕ Yeni Arazi / Tarla Ekle",
        "tarla_ayarlari": "⚙️ Tarla Bilgilerini Düzenle",
        "finans_ayarlari": "📈 Finansal Parametreler",
        "degisiklik_kaydet": "💾 Değişiklikleri Kaydet",
        "canli_metrikler": "📉 Canlı Metrikler & AI Vana",
        "hastalik_riski": "🦠 AI Hastalık Risk Analizi",
        "verimlilik_raporu": "📊 Verimlilik Raporu",
        "ajanda_baslik": "📅 Dijital Tarım Ajandası & Maliyet Takibi",
        "rapor_indir": "📄 Kurumsal PDF/Web Raporunu İndir"
    },
    "EN": {
        "baslik": "🌾 AI Smart Agri ERP Control Center",
        "cikis_yap": "🚪 Logout",
        "genel_merkez": "🏠 General Field Report Center",
        "borsa_ekrani": "📈 Live Agri Market",
        "depo_yonetimi": "📦 Warehouse & Purchase Mgmt",
        "makine_garaji": "🚜 Machine & Equipment Garage",
        "ai_asistan": "🤖 AI Agri Assistant",
        "yeni_tarla_ekle": "➕ Add New Field / Land",
        "tarla_ayarlari": "⚙️ Edit Field Information",
        "finans_ayarlari": "📈 Financial Parameters",
        "degisiklik_kaydet": "💾 Save Changes",
        "canli_metrikler": "📉 Live Metrics & AI Valve",
        "hastalik_riski": "🦠 AI Disease Risk Analysis",
        "verimlilik_raporu": "📊 Efficiency Report",
        "ajanda_baslik": "📅 Digital Ag-Agenda & Cost Tracking",
        "rapor_indir": "📄 Download Corporate Report"
    }
}

st.sidebar.title("🌍 Language / Dil")
secilen_dil = st.sidebar.radio("Select Interface Language:", ["TR", "EN"])

def _t(anahtar, **kwargs):
    metin = dil_sozlugu[secilen_dil].get(anahtar, anahtar)
    if kwargs: return metin.format(**kwargs)
    return metin

# --- API VE AI FONKSİYONLARI ---
def koordinat_bul(il, ilce):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={ilce},{il},Turkey&format=json&limit=1"
        cevap = requests.get(url, headers={'User-Agent': 'AkilliTarim/1.0'}, timeout=5)
        if cevap.json(): return float(cevap.json()[0]['lat']), float(cevap.json()[0]['lon'])
    except: pass
    return 39.0, 35.0

def gercek_hava_durumu_getir(enlem, boylam):
    try: return requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={enlem}&longitude={boylam}&current_weather=true", timeout=5).json()["current_weather"]["temperature"]
    except: return None 

def akilli_nem_simulasyonu():
    saat = datetime.now().hour
    if 6 <= saat < 12: return random.randint(40, 70)
    elif 12 <= saat < 18: return random.randint(15, 35)
    elif 18 <= saat < 22: return random.randint(30, 50)
    else: return random.randint(50, 75)

def ai_hastalik_risk_analizi(urun, sicaklik, nem, dil="TR"):
    risk_skoru = 10 
    h_adi = "Mantar ve Bakteri Riski" if dil == "TR" else "Fungal Risk"
    d_mesaj = "Hava şartları uygun." if dil == "TR" else "Conditions favorable."
    if urun in ["Pamuk", "Cotton"]:
        h_adi = "Pamukta Solgunluk & Kırmızı Örümcek" if dil == "TR" else "Cotton Wilt & Spider Mites"
        if sicaklik > 32 and nem < 30: risk_skoru, d_mesaj = 85, "🚨 Yüksek sıcaklık Kırmızı Örümcek riskini tetikler!" if dil=="TR" else "🚨 High temp triggers Spider Mites!"
        elif sicaklik > 25 and nem > 60: risk_skoru, d_mesaj = 60, "⚠️ Nemli ve sıcak hava mantarı tetikler." if dil=="TR" else "⚠️ Humid weather triggers fungus."
    elif urun in ["Zeytin", "Olive"]:
        h_adi = "Zeytin Halkalı Leke Hastalığı" if dil == "TR" else "Olive Peacock Spot"
        if 15 <= sicaklik <= 22 and nem > 70: risk_skoru, d_mesaj = 90, "🚨 Mantar için üreme sıcaklığı!" if dil=="TR" else "🚨 Perfect breeding temp for fungus!"
    elif urun in ["Buğday", "Wheat"]:
        h_adi = "Buğdayda Pas Hastalığı" if dil == "TR" else "Wheat Rust Disease"
        if 10 <= sicaklik <= 20 and nem > 65: risk_skoru, d_mesaj = 75, "⚠️ Serin ve nemli hava pas yapar." if dil=="TR" else "⚠️ Cool & humid weather creates rust."
    return h_adi, risk_skoru, d_mesaj

def ai_sohbet_cevabi_uret(mesaj, dil="TR"):
    m = mesaj.lower()
    if dil == "TR":
        if "pamuk" in m and "örümcek" in m: return "Pamukta kırmızı örümceğe karşı Abamectin etken maddeli ilaçları sabah erken saatlerde uygulayın."
        elif "pas" in m or "buğday" in m: return "Buğday pas hastalığı için Tebuconazole içerikli sistemik fungisitler tavsiye edilir."
        elif "merhaba" in m or "selam" in m: return "Merhaba! Ben yapay zeka tarım asistanınızım. Tarım, gübreleme veya bütçe konusunda nasıl yardımcı olabilirim?"
        else: return "Arazinize en uygun çözüm için lütfen ajandanıza bir 'Toprak Analizi' görevi ekleyin. Başka bir sorunuz var mı?"
    else:
        if "hello" in m or "hi" in m: return "Hello! I am your AI agricultural assistant. How can I help you today?"
        else: return "Based on our data, I recommend adding a 'Soil Analysis' task to your agenda for precise solutions."

# --- VERİTABANI KURULUMU ---
def veritabani_otomatik_kur():
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    
    kursor.execute("""CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, sifre TEXT NOT NULL,
        tarla_adi TEXT NOT NULL, enlem REAL NOT NULL, boylam REAL NOT NULL, email TEXT NOT NULL,
        urun_turu TEXT DEFAULT 'Genel', rol TEXT DEFAULT 'SHA', ada TEXT DEFAULT '-', parsel TEXT DEFAULT '-',
        alan_m2 REAL DEFAULT 0.0, rekolte_kg REAL DEFAULT 0.0, birim_fiyat REAL DEFAULT 0.0,
        devlet_destegi REAL DEFAULT 0.0, kredi_anapara REAL DEFAULT 0.0, kredi_faiz REAL DEFAULT 0.0)""")
        
    kursor.execute("""CREATE TABLE IF NOT EXISTS tarim_takvimi (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, tarla_adi TEXT NOT NULL, 
        islem_turu TEXT NOT NULL, tarih TEXT NOT NULL, notlar TEXT, maliyet REAL DEFAULT 0.0,
        maliyet_kategorisi TEXT DEFAULT 'Diğer')""")
        
    kursor.execute("""CREATE TABLE IF NOT EXISTS tarla_gunlukleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, tarla_adi TEXT NOT NULL, nem INTEGER NOT NULL,
        sicaklik INTEGER NOT NULL, karar TEXT NOT NULL, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        
    kursor.execute("""CREATE TABLE IF NOT EXISTS depo_envanter (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, 
        urun_adi TEXT NOT NULL, kategori TEXT NOT NULL, miktar REAL NOT NULL, 
        birim TEXT NOT NULL, kritik_esik REAL NOT NULL)""")
        
    kursor.execute("""CREATE TABLE IF NOT EXISTS makine_garaji (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, 
        makine_adi TEXT NOT NULL, plaka TEXT NOT NULL, 
        son_bakim_saati REAL NOT NULL, guncel_saat REAL NOT NULL, bakim_periyodu REAL NOT NULL)""")
        
    kursor.execute("""CREATE TABLE IF NOT EXISTS depo_alimlari (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, 
        urun_adi TEXT NOT NULL, miktar REAL NOT NULL, birim_fiyat REAL NOT NULL, 
        toplam_tutar REAL NOT NULL, tedarikci TEXT NOT NULL, tarih TEXT NOT NULL)""")
    
    # Eksik Sütun Kontrolleri (Güvenlik Amaçlı)
    for kolon in ["alan_m2", "rekolte_kg", "birim_fiyat", "devlet_destegi", "kredi_anapara", "kredi_faiz"]:
        try: kursor.execute(f"ALTER TABLE kullanicilar ADD COLUMN {kolon} REAL DEFAULT 0.0"); baglanti.commit()
        except: pass
    for t_kolon in ["tarla_adi", "maliyet", "maliyet_kategorisi"]:
        try: kursor.execute(f"ALTER TABLE tarim_takvimi ADD COLUMN {t_kolon} TEXT DEFAULT 'Diğer'"); baglanti.commit()
        except: pass
    try: kursor.execute("ALTER TABLE tarla_gunlukleri ADD COLUMN tarla_adi TEXT DEFAULT 'Genel Tarla'"); baglanti.commit()
    except: pass
        
    kursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE kullanici_adi = 'yunus'")
    if kursor.fetchone()[0] == 0:
        kursor.execute("""INSERT INTO kullanicilar 
        (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("yunus", "12345", "Yunus Beyin Pamuk Tarlası (Adana)", 37.00, 35.32, "yonetici_yunus@example.com", "Pamuk", "Admin", "104", "12", 50000.0))
        baglanti.commit()
    baglanti.close()

veritabani_otomatik_kur()

# --- SQL FONKSİYONLARI ---
def sql_kullanici_kontrol(k_adi, sifre):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("SELECT tarla_adi FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (k_adi, sifre))
    sonuc = kursor.fetchone(); baglanti.close()
    return True if sonuc else False

def sql_kullanicinin_tarlalarini_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("SELECT tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz FROM kullanicilar WHERE kullanici_adi = ?", (k_adi,))
    tarlalar = kursor.fetchall(); baglanti.close(); return tarlalar

def sql_yeni_tarla_ekle(k_adi, sifre, tarla, il, ilce, email, urun, ada, parsel, alan_m2):
    try:
        baglanti = sqlite3.connect("akilli_tarim.db")
        kursor = baglanti.cursor()
        t_ad = f"{tarla} ({il.capitalize()} / {ilce.capitalize()})"
        y_en, y_boy = koordinat_bul(il, ilce)
        kursor.execute("""INSERT INTO kullanicilar 
        (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0.0, 0.0, 0.0, 0.0)""",
        (k_adi, sifre, t_ad, y_en, y_boy, email, urun, "Müşteri/Çiftçi", ada, parsel, alan_m2))
        baglanti.commit(); baglanti.close(); return True
    except: return False 

def sql_tarla_guncelle(k_adi, e_tarla, y_tarla, y_urun, y_ada, y_parsel, y_alan, y_enlem, y_boylam, y_rek, y_fiyat, y_des, y_kana, y_kfaiz):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("""UPDATE kullanicilar 
        SET tarla_adi=?, urun_turu=?, ada=?, parsel=?, alan_m2=?, enlem=?, boylam=?, rekolte_kg=?, birim_fiyat=?, devlet_destegi=?, kredi_anapara=?, kredi_faiz=?
        WHERE kullanici_adi=? AND tarla_adi=?""", (y_tarla, y_urun, y_ada, y_parsel, y_alan, y_enlem, y_boylam, y_rek, y_fiyat, y_des, y_kana, y_kfaiz, k_adi, e_tarla))
    if e_tarla != y_tarla:
        kursor.execute("UPDATE tarim_takvimi SET tarla_adi=? WHERE kullanici_adi=? AND tarla_adi=?", (y_tarla, k_adi, e_tarla))
        kursor.execute("UPDATE tarla_gunlukleri SET tarla_adi=? WHERE kullanici_adi=? AND tarla_adi=?", (y_tarla, k_adi, e_tarla))
    baglanti.commit(); baglanti.close(); return True

def sql_takvim_etkinlik_ekle(k_adi, tarla, islem, tarih, notlar, maliyet, kat):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO tarim_takvimi (kullanici_adi, tarla_adi, islem_turu, tarih, notlar, maliyet, maliyet_kategorisi) VALUES (?, ?, ?, ?, ?, ?, ?)", (k_adi, tarla, islem, tarih, notlar, maliyet, kat))
    baglanti.commit(); baglanti.close()

def sql_takvim_verileri_getir_ham(k_adi, tarla):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, islem_turu, maliyet_kategorisi, tarih, notlar, maliyet FROM tarim_takvimi WHERE kullanici_adi = ? AND tarla_adi = ? ORDER BY id DESC", baglanti, params=(k_adi, tarla))
    baglanti.close(); return df

def sql_tum_tarlalarin_takvimini_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, maliyet FROM tarim_takvimi WHERE kullanici_adi = ?", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_takvim_etkinlik_sil(gorev_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM tarim_takvimi WHERE id = ?", (gorev_id,))
    baglanti.commit(); baglanti.close()

def sql_analiz_kaydet(k_adi, tarla, nem, sicaklik, karar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO tarla_gunlukleri (kullanici_adi, tarla_adi, nem, sicaklik, karar) VALUES (?, ?, ?, ?, ?)", (k_adi, tarla, nem, sicaklik, karar))
    baglanti.commit(); baglanti.close()

def sql_analizleri_getir(k_adi, tarla):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT nem, sicaklik, karar, tarih FROM tarla_gunlukleri WHERE kullanici_adi = ? AND tarla_adi = ? ORDER BY id DESC LIMIT 50", baglanti, params=(k_adi, tarla))
    baglanti.close(); return df

# YENİ DEPO SATIN ALMA FONKSİYONLARI
def sql_depo_urun_ekle(k_adi, urun_adi, kategori, miktar, birim, kritik):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO depo_envanter (kullanici_adi, urun_adi, kategori, miktar, birim, kritik_esik) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, urun_adi, kategori, miktar, birim, kritik))
    baglanti.commit(); baglanti.close()

def sql_depo_alim_kaydet(k_adi, urun_adi, miktar, b_fiyat, tedarikci, tarih, kategori):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    toplam = miktar * b_fiyat
    kursor.execute("INSERT INTO depo_alimlari (kullanici_adi, urun_adi, miktar, birim_fiyat, toplam_tutar, tedarikci, tarih) VALUES (?, ?, ?, ?, ?, ?, ?)", (k_adi, urun_adi, miktar, b_fiyat, toplam, tedarikci, tarih))
    notlar = f"Tedarikçi: {tedarikci} | Depoya {miktar} birim giriş yapıldı."
    islem_turu = f"Mal Alımı: {urun_adi}"
    kursor.execute("INSERT INTO tarim_takvimi (kullanici_adi, tarla_adi, islem_turu, tarih, notlar, maliyet, maliyet_kategorisi) VALUES (?, ?, ?, ?, ?, ?, ?)", (k_adi, 'Merkezi Depo', islem_turu, tarih, notlar, toplam, kategori))
    baglanti.commit(); baglanti.close()

def sql_depo_alimlari_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    # YENİ: id değerini de ekledik ki silebilelim veya düzenleyebilelim
    df = pd.read_sql_query("SELECT id, urun_adi, miktar, birim_fiyat, toplam_tutar, tedarikci, tarih FROM depo_alimlari WHERE kullanici_adi = ? ORDER BY id DESC LIMIT 50", baglanti, params=(k_adi,))
    baglanti.close(); return df

# YENİ: SATIN ALMA (FATURA) DÜZENLEME VE SİLME FONKSİYONLARI
def sql_depo_alim_guncelle(alim_id, miktar, b_fiyat, tedarikci, tarih):
    baglanti = sqlite3.connect("akilli_tarim.db")
    toplam = miktar * b_fiyat
    baglanti.execute("UPDATE depo_alimlari SET miktar=?, birim_fiyat=?, toplam_tutar=?, tedarikci=?, tarih=? WHERE id=?", (miktar, b_fiyat, toplam, tedarikci, tarih, alim_id))
    baglanti.commit(); baglanti.close()

def sql_depo_alim_sil(alim_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM depo_alimlari WHERE id = ?", (alim_id,))
    baglanti.commit(); baglanti.close()

def sql_depo_urun_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, urun_adi, kategori, miktar, birim, kritik_esik FROM depo_envanter WHERE kullanici_adi = ? ORDER BY kategori ASC", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_depo_miktar_guncelle(urun_id, yeni_miktar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("UPDATE depo_envanter SET miktar = ? WHERE id = ?", (yeni_miktar, urun_id))
    baglanti.commit(); baglanti.close()

def sql_depo_urun_tam_guncelle(urun_id, y_ad, y_kat, y_mik, y_birim, y_kritik):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("UPDATE depo_envanter SET urun_adi=?, kategori=?, miktar=?, birim=?, kritik_esik=? WHERE id=?", (y_ad, y_kat, y_mik, y_birim, y_kritik, urun_id))
    baglanti.commit(); baglanti.close()

def sql_depo_urun_sil(urun_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM depo_envanter WHERE id = ?", (urun_id,))
    baglanti.commit(); baglanti.close()

def sql_makine_ekle(k_adi, makine, plaka, s_bakim, g_saat, periyot):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO makine_garaji (kullanici_adi, makine_adi, plaka, son_bakim_saati, guncel_saat, bakim_periyodu) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, makine, plaka, s_bakim, g_saat, periyot))
    baglanti.commit(); baglanti.close()

def sql_makine_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, makine_adi, plaka, son_bakim_saati, guncel_saat, bakim_periyodu FROM makine_garaji WHERE kullanici_adi = ?", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_makine_saat_guncelle(m_id, y_saat):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("UPDATE makine_garaji SET guncel_saat = ? WHERE id = ?", (y_saat, m_id))
    baglanti.commit(); baglanti.close()

def sql_makine_bakim_yap(m_id, yeni_son_bakim):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("UPDATE makine_garaji SET son_bakim_saati = ?, guncel_saat = ? WHERE id = ?", (yeni_son_bakim, yeni_son_bakim, m_id))
    baglanti.commit(); baglanti.close()

def sql_makine_sil(m_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM makine_garaji WHERE id = ?", (m_id,))
    baglanti.commit(); baglanti.close()

# --- OTURUM VE GİRİŞ EKRANI ---
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["aktif_kullanici"] = ""

if not st.session_state["giris_yapildi"]:
    bosluk_sol, icerik_orta, bosluk_sag = st.columns([1.5, 2.5, 1.5])
    with icerik_orta:
        st.markdown(f"<h2 style='text-align: center; color: #2ecc71;'>{_t('baslik')}</h2>", unsafe_allow_html=True)
        st.write("")
        tab_names = ["🔑 Sisteme Giriş", "📝 Yeni Kayıt Ol"] if secilen_dil == "TR" else ["🔑 Login", "📝 Register"]
        sekme_giris, sekme_kayit = st.tabs(tab_names)
        
        with sekme_giris:
            kullanici_adi = st.text_input("Kullanıcı Adı / Username:", key="login_kadi")
            sifre = st.text_input("Şifre / Password:", type="password", key="login_sifre")
            if st.button("🚀 Giriş Yap / Login", use_container_width=True, type="primary"):
                if sql_kullanici_kontrol(kullanici_adi, sifre):
                    st.session_state["giris_yapildi"] = True
                    st.session_state["aktif_kullanici"] = kullanici_adi
                    st.rerun()
                else: st.error("Hatalı Giriş! / Invalid Login!")
                    
        with sekme_kayit:
            with st.form("yeni_kayit_formu"):
                k_adi = st.text_input("Kullanıcı Adı / Username (*)")
                k_sifre = st.text_input("Şifre / Password (*)", type="password")
                k_email = st.text_input("E-Posta / Email (*)")
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    k_il = st.text_input("İl / State (*)"); k_ada = st.text_input("Ada No / Block"); k_alan = st.number_input("Alan / Area (m²)", min_value=0.0, step=100.0, value=1000.0)
                with col_k2:
                    k_ilce = st.text_input("İlçe / City (*)"); k_parsel = st.text_input("Parsel No / Parcel"); k_tarla = st.text_input("Tarla Adı / Farm Name (*)")
                urunler = ["Pamuk", "Zeytin", "Buğday", "Mısır", "Ayçiçeği", "Narenciye", "Domates", "Diğer"] if secilen_dil == "TR" else ["Cotton", "Olive", "Wheat", "Corn", "Sunflower", "Citrus", "Tomato", "Other"]
                k_urun = st.selectbox("Mahsul / Crop", urunler)
                if st.form_submit_button("✅ Hesabı Oluştur", use_container_width=True):
                    if k_adi and k_sifre and k_email and k_il and k_ilce and k_tarla:
                        if sql_yeni_tarla_ekle(k_adi, k_sifre, k_tarla, k_il, k_ilce, k_email, k_urun, k_ada, k_parsel, float(k_alan)):
                            st.success("🎉 Başarılı! Giriş yapabilirsiniz.")
                        else: st.error("⚠️ Kayıt Hatası! Kullanıcı adı alınmış olabilir.")
                    else: st.warning("Lütfen (*) alanları doldurun.")

# --- ANA SİSTEM (ERP) ---
else:
    kullanici = st.session_state["aktif_kullanici"]
    tarlalar_listesi = sql_kullanicinin_tarlalarini_getir(kullanici)
    
    st.sidebar.markdown(f"👤 **{kullanici.upper()}**")
    st.sidebar.markdown("---")
    
    menu_secenekleri = [
        _t("genel_merkez"), 
        _t("borsa_ekrani"), 
        _t("depo_yonetimi"), 
        _t("makine_garaji"), 
        _t("ai_asistan")
    ] + [t[0] for t in tarlalar_listesi] + [_t("yeni_tarla_ekle")]
    
    aktif_secim = st.sidebar.radio("📌 Menü / Menu", menu_secenekleri)
    st.sidebar.markdown("---")
    if st.sidebar.button(_t("cikis_yap"), type="primary", use_container_width=True):
        st.session_state["giris_yapildi"] = False; st.session_state["aktif_kullanici"] = ""; st.rerun()

    # ==========================================
    # MODÜL 1: CANLI BORSA EKRANI
    # ==========================================
    if aktif_secim == _t("borsa_ekrani"):
        st.subheader("📈 Canlı Tarım Borsası & Piyasa Analizi")
        st.caption("Piyasadaki güncel ürün fiyatları ve günlük değişim grafikleri (Simülasyon Verisi)")
        st.markdown("---")
        borsa_verileri = {
            "Pamuk (Ege Standart 1)": {"fiyat": 64.50, "degisim": 1.2},
            "Zeytinyağı (Sızma)": {"fiyat": 285.00, "degisim": -2.5},
            "Buğday (Ekmeklik)": {"fiyat": 10.20, "degisim": 0.4},
            "Mısır (1. Sınıf)": {"fiyat": 9.40, "degisim": -0.1},
            "Ayçiçeği (Yağlık)": {"fiyat": 17.80, "degisim": 0.8},
            "Domates (Salçalık)": {"fiyat": 4.50, "degisim": 0.2},
            "Narenciye (Portakal)": {"fiyat": 12.00, "degisim": -0.5}
        }
        k1, k2, k3, k4 = st.columns(4)
        sutunlar = [k1, k2, k3, k4]
        idx = 0
        for urun, veri in borsa_verileri.items():
            sutunlar[idx % 4].metric(label=urun, value=f"₺ {veri['fiyat']:.2f}", delta=f"{veri['degisim']}%")
            idx += 1
        st.write("---")
        st.write("**Borsa Grafiği (Son 7 Günlük Trend)**")
        tarihler = pd.date_range(end=datetime.today(), periods=7).strftime('%Y-%m-%d')
        df_trend = pd.DataFrame({'Tarih': tarihler, 'Pamuk': [60, 61.5, 61, 62, 63.5, 63, 64.5], 'Buğday': [9.5, 9.6, 9.8, 9.7, 10.0, 10.1, 10.2]})
        st.line_chart(df_trend.set_index('Tarih'))

    # ==========================================
    # MODÜL 2: MAKİNE VE EKİPMAN GARAJI
    # ==========================================
    elif aktif_secim == _t("makine_garaji"):
        st.subheader("🚜 Makine ve Ekipman Garajı (Bakım Takibi)")
        st.markdown("---")
        df_makine = sql_makine_getir(kullanici)
        if not df_makine.empty:
            for index, r in df_makine.iterrows():
                fark = r['guncel_saat'] - r['son_bakim_saati']
                kalan_saat = r['bakim_periyodu'] - fark
                if kalan_saat <= 0: st.error(f"🚨 **BAKIM ZAMANI GELDİ:** {r['makine_adi']} ({r['plaka']}) periyodu aşıldı!")
                elif kalan_saat <= 20: st.warning(f"⚠️ **YAKLAŞAN BAKIM:** {r['makine_adi']} ({r['plaka']}) bakımına **{kalan_saat} saat** kaldı.")
            st.markdown("---")
            
        col_m1, col_m2 = st.columns([1.2, 2])
        with col_m1:
            with st.form("yeni_makine_form"):
                st.write("**Yeni Makine/Araç Ekle**")
                m_adi = st.text_input("Makine Adı (Örn: John Deere):")
                m_plaka = st.text_input("Plaka / Demir No:")
                m_son_bakim = st.number_input("Son Bakım Saati:", min_value=0.0, step=10.0)
                m_guncel = st.number_input("Şu An Motor Saati:", min_value=0.0, step=10.0)
                m_periyot = st.number_input("Bakım Periyodu (Saat):", min_value=10.0, value=250.0, step=50.0)
                if st.form_submit_button("🚜 Garaja Ekle", use_container_width=True):
                    if m_adi and m_plaka:
                        sql_makine_ekle(kullanici, m_adi, m_plaka, float(m_son_bakim), float(m_guncel), float(m_periyot))
                        st.rerun()
                    else: st.warning("Ad ve Plaka zorunludur.")
                        
        with col_m2:
            st.write("**Garajdaki Araçlar ve Çalışma Durumları**")
            if not df_makine.empty:
                for idx, r in df_makine.iterrows():
                    fark = r['guncel_saat'] - r['son_bakim_saati']
                    yuzde = min(fark / r['bakim_periyodu'], 1.0)
                    with st.expander(f"⚙️ {r['makine_adi']} | {r['plaka']} (Güncel: {r['guncel_saat']} Saat)", expanded=False):
                        st.write(f"**Son Bakım:** {r['son_bakim_saati']} Saat | **Periyot:** {r['bakim_periyodu']} Saat")
                        st.progress(yuzde)
                        st.caption(f"Bakıma Kalan Süre: {max(0, r['bakim_periyodu'] - fark)} saat")
                        cm1, cm2, cm3 = st.columns(3)
                        with cm1:
                            yeni_s = st.number_input("Saati Güncelle:", value=float(r['guncel_saat']), key=f"s_{r['id']}")
                            if st.button("⏱️ Kaydet", key=f"b1_{r['id']}"):
                                sql_makine_saat_guncelle(r['id'], yeni_s); st.rerun()
                        with cm2:
                            if st.button("🔧 Bakım Yapıldı", key=f"b2_{r['id']}"):
                                sql_makine_bakim_yap(r['id'], r['guncel_saat']); st.rerun()
                        with cm3:
                            if st.button("🗑️ Sil", key=f"b3_{r['id']}"):
                                sql_makine_sil(r['id']); st.rerun()
            else: st.info("Garajınız boş.")

    # ==========================================
    # MODÜL 3: AI SOHBET BOTU
    # ==========================================
    elif aktif_secim == _t("ai_asistan"):
        st.subheader(_t("ai_asistan"))
        st.markdown("---")
        if "chat_gecmisi" not in st.session_state:
            st.session_state["chat_gecmisi"] = [{"rol": "asistan", "icerik": "Merhaba! Tarım, gübreleme veya bütçe ile ilgili sorularınızı sorabilirsiniz." if secilen_dil == "TR" else "Hello! Ask me anything about agriculture."}]

        for msj in st.session_state["chat_gecmisi"]:
            if msj["rol"] == "asistan":
                with st.chat_message("assistant", avatar="🤖"): st.markdown(msj["icerik"])
            else:
                with st.chat_message("user", avatar="👤"): st.markdown(msj["icerik"])

        if prompt := st.chat_input("Sorunuzu yazın... / Type here..."):
            st.session_state["chat_gecmisi"].append({"rol": "kullanici", "icerik": prompt})
            with st.chat_message("user", avatar="👤"): st.markdown(prompt)
            with st.chat_message("assistant", avatar="🤖"):
                mesaj_alani = st.empty()
                mesaj_alani.markdown("Yazıyor... ⏳" if secilen_dil == "TR" else "Typing... ⏳")
                time.sleep(1.0) 
                ai_cevabi = ai_sohbet_cevabi_uret(prompt, secilen_dil)
                mesaj_alani.markdown(ai_cevabi)
            st.session_state["chat_gecmisi"].append({"rol": "asistan", "icerik": ai_cevabi})

    # ==========================================
    # MODÜL 4: AKILLI DEPO VE SATIN ALMA (MUHASEBE)
    # ==========================================
    elif aktif_secim == _t("depo_yonetimi"):
        st.subheader(f"📦 Akıllı Depo, Satın Alma ve Muhasebe Entegrasyonu")
        st.markdown("---")
        df_depo = sql_depo_urun_getir(kullanici)
        
        if not df_depo.empty:
            kritik_urunler = df_depo[df_depo['miktar'] <= df_depo['kritik_esik']]
            if not kritik_urunler.empty:
                st.error("🚨 **KRİTİK STOK UYARISI:**")
                for index, row in kritik_urunler.iterrows():
                    st.warning(f"⚠️ {row['urun_adi']} - Kalan: {row['miktar']} {row['birim']}")
                st.markdown("---")

        col_d1, col_d2 = st.columns([1, 2.5])
        
        with col_d1:
            sekme_mevcut, sekme_yeni = st.tabs(["📥 Mevcut Ürüne Stok Ekle", "🆕 Yeni Ürün Tanımla"])
            
            with sekme_yeni:
                with st.form("yeni_stok_formu"):
                    st.write("**Yeni Ürün Tanımla ve Alım Yap**")
                    d_urun_adi = st.text_input("Ürün Markası / Adı (*):")
                    d_kategori = st.selectbox("Kategori:", ["Zirai İlaç", "Gübre", "Tohum/Fide", "Mazot/Yakıt", "Ambalaj", "Diğer"])
                    c_d_1, c_d_2 = st.columns(2)
                    with c_d_1: d_miktar = st.number_input("Alınan Miktar:", min_value=0.0, value=0.0)
                    with c_d_2: d_birim = st.selectbox("Birim:", ["kg", "Litre", "Torba", "Adet", "Ton"])
                    d_kritik = st.number_input("Kritik Eşik (Uyarı Ver):", min_value=0.0, value=10.0)
                    
                    st.write("---")
                    st.write("💰 **Muhasebe & Satın Alma Bilgileri**")
                    d_fiyat = st.number_input("Birim Alış Fiyatı (TL):", min_value=0.0, step=10.0)
                    d_tedarikci = st.text_input("Tedarikçi Firma (Örn: Tarım Kredi):")
                    d_tarih = st.date_input("Alım Tarihi:")
                    
                    if st.form_submit_button("📦 Depoya ve Muhasebeye İşle", use_container_width=True):
                        if d_urun_adi:
                            sql_depo_urun_ekle(kullanici, d_urun_adi, d_kategori, float(d_miktar), d_birim, float(d_kritik))
                            if d_miktar > 0 and d_tedarikci:
                                sql_depo_alim_kaydet(kullanici, d_urun_adi, float(d_miktar), float(d_fiyat), d_tedarikci, str(d_tarih), d_kategori)
                            st.rerun()
                        else:
                            st.warning("Ürün adı zorunludur.")
                            
            with sekme_mevcut:
                if not df_depo.empty:
                    with st.form("mevcut_stok_ekle_formu"):
                        st.write("**Mevcut Ürüne Mal Girişi Yap**")
                        stok_secenekleri = df_depo.apply(lambda r: f"ID:{r['id']} | {r['urun_adi']} (Kalan: {r['miktar']} {r['birim']})", axis=1).tolist()
                        secili_stok = st.selectbox("Stoğu Artacak Ürün:", stok_secenekleri)
                        m_miktar = st.number_input("Alınan Ek Miktar:", min_value=0.1, step=1.0)
                        
                        st.write("---")
                        st.write("💰 **Muhasebe & Satın Alma Bilgileri**")
                        m_fiyat = st.number_input("Güncel Birim Alış Fiyatı (TL):", min_value=0.0, step=10.0)
                        m_tedarikci = st.text_input("Tedarikçi Firma (*):")
                        m_tarih = st.date_input("Alım Tarihi: ", key="mtarih")
                        
                        if st.form_submit_button("📥 Stok Artır ve Muhasebeye İşle", use_container_width=True):
                            if m_tedarikci and secili_stok:
                                s_id = int(secili_stok.split("|")[0].replace("ID:", "").strip())
                                s_eski_miktar = float(df_depo[df_depo['id'] == s_id].iloc[0]['miktar'])
                                s_urun_adi = df_depo[df_depo['id'] == s_id].iloc[0]['urun_adi']
                                s_kategori = df_depo[df_depo['id'] == s_id].iloc[0]['kategori']
                                
                                yeni_miktar = s_eski_miktar + float(m_miktar)
                                sql_depo_miktar_guncelle(s_id, yeni_miktar)
                                sql_depo_alim_kaydet(kullanici, s_urun_adi, float(m_miktar), float(m_fiyat), m_tedarikci, str(m_tarih), s_kategori)
                                st.rerun()
                            else:
                                st.warning("Tedarikçi firma adı zorunludur.")
                else:
                    st.info("Önce 'Yeni Ürün Tanımla' sekmesinden ürün ekleyin.")

        with col_d2:
            tab_stok, tab_alim = st.tabs(["📊 Mevcut Depo Envanteri", "💳 Satın Alma ve Fiyat Geçmişi"])
            
            with tab_stok:
                if not df_depo.empty:
                    st.dataframe(df_depo.rename(columns={"urun_adi":"Ürün", "kategori":"Kategori", "miktar":"Miktar", "birim":"Birim"})[["Ürün", "Kategori", "Miktar", "Birim"]], use_container_width=True, hide_index=True)
                    
                    with st.expander("⚙️ Stok Bilgilerini Düzenle / Sil", expanded=False):
                        stok_sec = df_depo.apply(lambda r: f"ID:{r['id']} | {r['urun_adi']}", axis=1).tolist()
                        g_stok = st.selectbox("Ürün Seçin:", stok_sec, key="gbox")
                        if g_stok:
                            s_id = int(g_stok.split("|")[0].replace("ID:", "").strip())
                            s_urun = df_depo[df_depo['id'] == s_id].iloc[0]
                            with st.form("st_guncelle"):
                                c1, c2 = st.columns(2)
                                with c1:
                                    y_ad = st.text_input("Adı:", value=s_urun['urun_adi'])
                                    y_mik = st.number_input("Miktar:", value=float(s_urun['miktar']))
                                with c2:
                                    y_kat = st.selectbox("Kategori:", ["Zirai İlaç", "Gübre", "Tohum/Fide", "Mazot/Yakıt", "Ambalaj", "Diğer"], index=0)
                                    y_birim = st.selectbox("Birim:", ["kg", "Litre", "Torba", "Adet", "Ton"], index=0)
                                y_kritik = st.number_input("Kritik Eşik:", value=float(s_urun['kritik_esik']))
                                if st.form_submit_button("💾 Kaydet", use_container_width=True):
                                    sql_depo_urun_tam_guncelle(s_id, y_ad, y_kat, y_mik, y_birim, y_kritik); st.rerun()
                                    
                            if st.button("🗑️ Ürünü Kalıcı Olarak Sil", type="primary", use_container_width=True):
                                sql_depo_urun_sil(s_id); st.rerun()
                else: st.info("Deponuz boş.")
                
            # YENİ EKLENEN: FATURA (SATIN ALMA) DÜZENLEME MODÜLÜ
            with tab_alim:
                df_alim = sql_depo_alimlari_getir(kullanici)
                if not df_alim.empty:
                    df_g_alim = df_alim.rename(columns={"urun_adi":"Ürün", "miktar":"Miktar", "birim_fiyat":"Birim Fiyat(TL)", "toplam_tutar":"Toplam Fatura", "tedarikci":"Tedarikçi", "tarih":"Tarih"})
                    st.dataframe(df_g_alim[["Ürün", "Miktar", "Birim Fiyat(TL)", "Toplam Fatura", "Tedarikçi", "Tarih"]], use_container_width=True, hide_index=True)
                    
                    with st.expander("⚙️ Fatura (Alım Kaydını) Düzenle veya Sil", expanded=False):
                        st.caption("Not: Buradaki değişiklik faturayı günceller. Eğer bu alım Merkez Ajandasına gider olarak işlendiyse, ajandadan da manuel düzeltmeniz gerekir.")
                        alim_secenekleri = df_alim.apply(lambda r: f"ID:{r['id']} | {r['urun_adi']} ({r['tarih']} - {r['toplam_tutar']} TL)", axis=1).tolist()
                        secili_fatura = st.selectbox("Düzenlenecek Faturayı Seçin:", alim_secenekleri, key="fatura_guncelle_box")
                        
                        if secili_fatura:
                            f_id = int(secili_fatura.split("|")[0].replace("ID:", "").strip())
                            fatura_kaydi = df_alim[df_alim['id'] == f_id].iloc[0]
                            
                            with st.form("fatura_guncelleme_formu"):
                                st.write(f"**Güncellenen Ürün:** {fatura_kaydi['urun_adi']}")
                                col_f1, col_f2 = st.columns(2)
                                with col_f1:
                                    y_alim_mik = st.number_input("Miktar:", value=float(fatura_kaydi['miktar']), min_value=0.0)
                                    y_alim_fiyat = st.number_input("Birim Fiyat (TL):", value=float(fatura_kaydi['birim_fiyat']), min_value=0.0)
                                with col_f2:
                                    y_alim_ted = st.text_input("Tedarikçi:", value=fatura_kaydi['tedarikci'])
                                    try: parsed_tarih = datetime.strptime(fatura_kaydi['tarih'], "%Y-%m-%d").date()
                                    except: parsed_tarih = datetime.now().date()
                                    y_alim_tar = st.date_input("Alım Tarihi:", value=parsed_tarih)
                                    
                                if st.form_submit_button("💾 Faturayı Güncelle", use_container_width=True):
                                    sql_depo_alim_guncelle(f_id, y_alim_mik, y_alim_fiyat, y_alim_ted, str(y_alim_tar))
                                    st.success("Fatura güncellendi!")
                                    st.rerun()
                                    
                            if st.button("🗑️ Faturayı Kalıcı Olarak Sil", type="primary", use_container_width=True):
                                sql_depo_alim_sil(f_id)
                                st.rerun()
                else:
                    st.info("Henüz sisteme kaydedilmiş bir satın alma faturası bulunmuyor.")

    # ==========================================
    # 5. YENİ TARLA EKLEME EKRANI
    # ==========================================
    elif aktif_secim == _t("yeni_tarla_ekle"):
        st.subheader("➕ Yeni Arazi Ekle")
        with st.form("yeni_tarla"):
            col1, col2 = st.columns(2)
            with col1: il = st.text_input("İl (*)"); ada = st.text_input("Ada"); alan = st.number_input("Alan (m²)", min_value=0.0)
            with col2: ilce = st.text_input("İlçe (*)"); parsel = st.text_input("Parsel"); tarla_ad = st.text_input("Tarla Adı (*)")
            urun = st.selectbox("Mahsul", ["Pamuk", "Zeytin", "Buğday", "Mısır", "Diğer"])
            if st.form_submit_button("Ekle", use_container_width=True):
                if il and ilce and tarla_ad:
                    sql_yeni_tarla_ekle(kullanici, "12345", tarla_ad, il, ilce, "x@x.com", urun, ada, parsel, float(alan))
                    st.rerun()

    # ==========================================
    # 6. GENEL MERKEZ
    # ==========================================
    elif aktif_secim == _t("genel_merkez"):
        st.subheader(f"🏠 ERP Genel Rapor Merkezi")
        st.markdown("---")
        t_gider = t_gelir = t_destek = t_kredi = 0.0
        
        df_tum_gider = sql_tum_tarlalarin_takvimini_getir(kullanici)
        if not df_tum_gider.empty:
            t_gider = df_tum_gider['maliyet'].sum()
            
        for t in tarlalar_listesi:
            t_gelir += (t[9] * t[10]); t_destek += t[11]; t_kredi += (t[12] + (t[12] * t[13] / 100))
            
        net = t_gelir + t_destek - t_gider - t_kredi
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("Toplam Gelir+Destek", f"₺ {(t_gelir + t_destek):,.2f}")
        rc2.metric("Toplam Şirket Gideri", f"₺ {t_gider:,.2f}", help="Tarlalar + Merkezi Depo Mal Alımları")
        rc3.metric("Banka Ödemeleri", f"₺ {t_kredi:,.2f}")
        rc4.metric("İşletme Net Kârı", f"₺ {net:,.2f}", delta="Kârlı" if net > 0 else "Zarar")

        st.write("---")
        st.write("📋 **Tarlalarınızın Finansal Özeti**")
        tarlalar_df = pd.DataFrame(tarlalar_listesi, columns=["Tarla Adı", "En", "Boy", "Mail", "Mahsul", "Rol", "Ada", "Parsel", "Alan(m²)", "Hasat(kg)", "Fiyat(TL)", "Destek(TL)", "Kredi Ana", "Kredi Faiz"])
        st.dataframe(tarlalar_df[["Tarla Adı", "Mahsul", "Alan(m²)", "Hasat(kg)", "Fiyat(TL)", "Destek(TL)"]], use_container_width=True, hide_index=True)

    # ==========================================
    # 7. TARLA DETAY PANELİ (TÜM ÖZELLİKLERİYLE EKSİKSİZ)
    # ==========================================
    else:
        aktif_t = next((t for t in tarlalar_listesi if t[0] == aktif_secim), None)
        if aktif_t:
            tarla_adi, t_enlem, t_boylam, m_email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz = aktif_t
            
            st.subheader(f"{_t('baslik')} | {tarla_adi.upper()}")
            st.caption(f"Yönetici: {kullanici.upper()} | Ada/Parsel: {ada}/{parsel} | Büyüklük: {alan_m2:,.0f} m² | Mahsul: {urun_turu}")
            
            # --- 1. AYARLAR VE FİNANS EXPANDERLARI ---
            col_ayarlar, col_finans = st.columns(2)
            with col_ayarlar:
                with st.expander(_t("tarla_ayarlari"), expanded=False):
                    with st.form(f"g_kimlik_{tarla_adi}"):
                        g_tarla_adi = st.text_input("Tarla Adı:", value=tarla_adi)
                        urunler = ["Pamuk", "Zeytin", "Buğday", "Mısır", "Ayçiçeği", "Narenciye", "Domates", "Diğer"] if secilen_dil == "TR" else ["Cotton", "Olive", "Wheat", "Corn", "Sunflower", "Citrus", "Tomato", "Other"]
                        g_urun = st.selectbox("Mahsul:", urunler, index=urunler.index(urun_turu) if urun_turu in urunler else 0)
                        g_alan = st.number_input("Alan (m²):", value=float(alan_m2), min_value=0.0, step=100.0)
                        col_ap1, col_ap2 = st.columns(2)
                        with col_ap1: g_ada = st.text_input("Ada:", value=ada)
                        with col_ap2: g_parsel = st.text_input("Parsel:", value=parsel)
                        
                        st.caption("Lokasyon değiştirmek için (İsteğe bağlı):")
                        col_il1, col_il2 = st.columns(2)
                        with col_il1: g_il = st.text_input("Yeni İl:")
                        with col_il2: g_ilce = st.text_input("Yeni İlçe:")
                        
                        if st.form_submit_button(_t("degisiklik_kaydet"), use_container_width=True):
                            y_en, y_boy = (koordinat_bul(g_il, g_ilce) if g_il and g_ilce else (t_enlem, t_boylam))
                            sql_tarla_guncelle(kullanici, tarla_adi, g_tarla_adi, g_urun, g_ada, g_parsel, float(g_alan), y_en, y_boy, float(rekolte_kg), float(birim_fiyat), float(devlet_destegi), float(kredi_anapara), float(kredi_faiz))
                            st.rerun()

            with col_finans:
                with st.expander(_t("finans_ayarlari"), expanded=False):
                    with st.form(f"g_finans_{tarla_adi}"):
                        c_f1, c_f2 = st.columns(2)
                        with c_f1: g_rekolte = st.number_input("Hasat Beklentisi (kg):", value=float(rekolte_kg), min_value=0.0)
                        with c_f2: g_fiyat = st.number_input("Satış Fiyatı (TL/kg):", value=float(birim_fiyat), min_value=0.0)
                        g_destek = st.number_input("Devlet Desteği / Hibe (TL):", value=float(devlet_destegi), min_value=0.0)
                        c_k1, c_k2 = st.columns(2)
                        with c_k1: g_kanapara = st.number_input("Çekilen Kredi (TL):", value=float(kredi_anapara), min_value=0.0)
                        with c_k2: g_kfaiz = st.number_input("Faiz Oranı (%):", value=float(kredi_faiz), min_value=0.0)
                        
                        if st.form_submit_button(_t("degisiklik_kaydet"), use_container_width=True):
                            sql_tarla_guncelle(kullanici, tarla_adi, tarla_adi, urun_turu, ada, parsel, float(alan_m2), t_enlem, t_boylam, float(g_rekolte), float(g_fiyat), float(g_destek), float(g_kanapara), float(g_kfaiz))
                            st.rerun()

            st.markdown("---")

            # --- 2. CANLI METRİKLER, HARİTA VE VERİMLİLİK ---
            if "aktif_tarla_nemi" not in st.session_state or st.session_state.get("secili_tarla") != tarla_adi:
                st.session_state["aktif_tarla_nemi"] = akilli_nem_simulasyonu()
                st.session_state["aktif_tarla_sicaklik"] = gercek_hava_durumu_getir(t_enlem, t_boylam) or random.randint(22, 38)
                st.session_state["secili_tarla"] = tarla_adi
                
            tn, ts = st.session_state["aktif_tarla_nemi"], st.session_state["aktif_tarla_sicaklik"]
            h_adi, h_skor, h_mesaj = ai_hastalik_risk_analizi(urun_turu, ts, tn, secilen_dil)
            
            html_rapor = f"""
            <!DOCTYPE html><html><head><meta charset="UTF-8"><style>
            body {{ font-family: sans-serif; padding: 40px; color: #2c3e50; }}
            .header {{ text-align: center; border-bottom: 3px solid #2ecc71; padding-bottom: 20px; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            .info-table th, .info-table td {{ border: 1px solid #e0e0e0; padding: 12px; text-align: left; }}
            </style></head><body>
            <div class="header"><h2>AI Smart Agri Platform Report</h2><p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p></div>
            <table class="info-table"><tr><th>User</th><td>{kullanici.upper()}</td></tr><tr><th>Field</th><td>{tarla_adi.upper()}</td></tr><tr><th>Area</th><td>{alan_m2:,.0f} m²</td></tr><tr><th>Crop</th><td>{urun_turu}</td></tr><tr><th>Temp</th><td>{ts} °C</td></tr><tr><th>Moisture</th><td>%{tn}</td></tr></table>
            </body></html>"""
            
            col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
            with col_b1:
                st.subheader(_t("canli_metrikler"), divider="blue")
                st.write(f"🌡️ Sıcaklık: **{ts} °C** | 💧 Toprak Nemi: **%{tn}**")
                st.info(f"**AI VANA:** {_t('ai_kuru') if tn < 30 and ts > 30 else _t('ai_uyari') if tn < 30 else _t('ai_normal')}")
                st.write(f"🦠 **{_t('hastalik_riski')} ({h_adi})**")
                st.progress(h_skor / 100)
                if st.button(_t("analizi_gunlukle"), key=f"btn_g_{tarla_adi}", use_container_width=True):
                    sql_analiz_kaydet(kullanici, tarla_adi, int(tn), float(ts), "Kaydedildi")
                    st.rerun()

            with col_b2:
                st.subheader("🗺️ Harita Lokasyonu", divider="green")
                st.map(pd.DataFrame({'lat': [t_enlem], 'lon': [t_boylam]}), size=14, zoom=11)
                st.download_button(_t("rapor_indir"), data=html_rapor, file_name=f"{tarla_adi}_rapor.html", mime="text/html", use_container_width=True)

            with col_b3:
                df_kayitlar = sql_analizleri_getir(kullanici, tarla_adi)
                tasarruf_orani = (df_kayitlar['karar'].str.contains("NORMAL").sum() / len(df_kayitlar)) if not df_kayitlar.empty else 0.0
                st.subheader(_t("verimlilik_raporu"), divider="orange")
                st.write(_t("su_tasarrufu"))
                st.progress(tasarruf_orani)
                if not df_kayitlar.empty:
                    st.line_chart(df_kayitlar.iloc[::-1].reset_index()['nem'])

            st.markdown("---")

            # --- 3. ERP BÜTÇE, PASTA GRAFİK VE SİMÜLATÖR ---
            st.subheader(f"💼 Dijital Finans & Risk Yönetimi", divider="orange")
            df_takvim_ham = sql_takvim_verileri_getir_ham(kullanici, tarla_adi)
            toplam_gider = df_takvim_ham['maliyet'].sum() if not df_takvim_ham.empty else 0.0
            tahmini_gelir = rekolte_kg * birim_fiyat
            toplam_kredi_maliyeti = kredi_anapara + (kredi_anapara * kredi_faiz / 100)
            net_kar = tahmini_gelir + devlet_destegi - toplam_gider - toplam_kredi_maliyeti
            
            birim_maliyet = (toplam_gider / rekolte_kg) if rekolte_kg > 0 else 0.0
            basabas = ((toplam_gider - devlet_destegi + toplam_kredi_maliyeti) / rekolte_kg) if rekolte_kg > 0 else 0.0

            cm1, cm2, cm3, cm4, cm5 = st.columns(5)
            cm1.metric("Brüt Gelir", f"₺ {tahmini_gelir:,.0f}")
            cm2.metric("Devlet Desteği", f"₺ {devlet_destegi:,.0f}")
            cm3.metric("Tarlanın Gideri", f"₺ {toplam_gider:,.0f}")
            cm4.metric("Kredi Ödeme", f"₺ {toplam_kredi_maliyeti:,.0f}")
            cm5.metric("Net Kâr", f"₺ {net_kar:,.0f}", delta="Kârlı" if net_kar > 0 else "Zarar Riski")
            
            col_f_sol, col_f_sag = st.columns(2)
            with col_f_sol:
                st.write("**📊 Operasyonel Gider Dağılımı**")
                if not df_takvim_ham.empty and toplam_gider > 0:
                    df_gider = df_takvim_ham.groupby('maliyet_kategorisi')['maliyet'].sum().reset_index()
                    fig = alt.Chart(df_gider).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="maliyet", type="quantitative"),
                        color=alt.Color(field="maliyet_kategorisi", type="nominal", title="Kategori"),
                        tooltip=['maliyet_kategorisi', 'maliyet']
                    ).properties(height=250)
                    st.altair_chart(fig, use_container_width=True)
                else: st.info("Gider bulunmuyor.")
                    
            with col_f_sag:
                st.write("**🎯 Birim Maliyet & Risk Analizi**")
                st.info(f"💡 **1 Kg Ürünün Size Maliyeti:** {birim_maliyet:.2f} TL")
                st.warning(f"⚖️ **Başabaş Noktası:** Zarar etmemek için ürün en az **{basabas:.2f} TL**'ye satılmalıdır.")
                st.write("**🔮 Fiyat Dalgalanma Simülatörü**")
                if birim_fiyat > 0:
                    sim_fiyat = st.slider("Satış Fiyatı Düşer/Artarsa:", 0.0, float(birim_fiyat*2), float(birim_fiyat), step=0.5)
                    st.success(f"Fiyat **{sim_fiyat} TL** olursa net kâr: **{((rekolte_kg * sim_fiyat) + devlet_destegi - toplam_gider - toplam_kredi_maliyeti):,.0f} TL**")

            st.markdown("---")

            # --- 4. AJANDA VE DEPO ENTEGRASYONU ---
            st.subheader(_t("ajanda_baslik"), divider="gray")
            df_depo_anlik = sql_depo_urun_getir(kullanici)
            depo_secenekleri = ["-- Depodan Ürün Kullanma --"] + (df_depo_anlik.apply(lambda r: f"ID:{r['id']} | {r['urun_adi']} (Kalan: {r['miktar']} {r['birim']})", axis=1).tolist() if not df_depo_anlik.empty else [])
            
            ca1, ca2 = st.columns([1, 2])
            with ca1:
                with st.form(f"f_gorev_{tarla_adi}"):
                    y_kat = st.selectbox("Kategori:", ["Mazot/Yakıt", "Gübre", "Zirai İlaç", "İşçi Yevmiyesi", "Tohum/Fide", "Su/Elektrik", "Amortisman", "Diğer"])
                    y_islem = st.text_input("İşlem Özeti (*):")
                    
                    st.write("---")
                    st.write("📦 **Depo Kullanımı (İsteğe Bağlı)**")
                    y_depo_secim = st.selectbox("Stoktan Düşülecek Ürün:", depo_secenekleri)
                    y_depo_miktar = st.number_input("Kullanılan Miktar:", min_value=0.0, step=1.0)
                    
                    st.write("---")
                    y_tarih = st.date_input("Tarih:")
                    y_maliyet = st.number_input("İşçilik Tutar (Malzeme depodansa 0 girin) (TL):", min_value=0.0, step=100.0)
                    y_not = st.text_input("Not:", value="Tamamlandı")
                    
                    if st.form_submit_button("🗓️ Gideri İşle ve Stoktan Düş", use_container_width=True):
                        if y_islem:
                            if y_depo_secim != "-- Depodan Ürün Kullanma --" and y_depo_miktar > 0:
                                s_id = int(y_depo_secim.split("|")[0].replace("ID:", "").strip())
                                mevcut_stok = df_depo_anlik[df_depo_anlik['id'] == s_id].iloc[0]['miktar']
                                urun_isim = df_depo_anlik[df_depo_anlik['id'] == s_id].iloc[0]['urun_adi']
                                u_birim = df_depo_anlik[df_depo_anlik['id'] == s_id].iloc[0]['birim']
                                sql_depo_miktar_guncelle(s_id, max(0.0, mevcut_stok - y_depo_miktar))
                                ek_not = f"[Depodan {y_depo_miktar} {u_birim} {urun_isim} kullanıldı]"
                                y_not = f"{y_not} - {ek_not}" if y_not else ek_not
                            sql_takvim_etkinlik_ekle(kullanici, tarla_adi, y_islem, str(y_tarih), y_not, float(y_maliyet), y_kat)
                            st.rerun()
                        else: st.warning("Lütfen işlem özeti giriniz.")
                            
            with ca2:
                if not df_takvim_ham.empty:
                    df_g = df_takvim_ham.rename(columns={"maliyet_kategorisi":"Kategori", "islem_turu":"İşlem", "tarih":"Tarih", "maliyet":"Tutar(TL)", "notlar":"Durum"})
                    st.dataframe(df_g[["Kategori", "İşlem", "Tarih", "Tutar(TL)", "Durum"]], use_container_width=True, hide_index=True)
                    sildi_id = st.selectbox("Silinecek Kayıt:", df_takvim_ham.apply(lambda r: f"ID:{r['id']} | {r['islem_turu']} ({r['maliyet']} TL)", axis=1).tolist())
                    if st.button("🗑️ Kaydı Sil", use_container_width=True):
                        if sildi_id:
                            sql_takvim_etkinlik_sil(int(sildi_id.split("|")[0].replace("ID:", "").strip()))
                            st.rerun()
