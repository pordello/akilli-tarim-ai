# ==============================================================================
# PROJE: AI Destekli Akıllı Tarım Platformu (BORSA VE MAKİNE GARAJI EKLENDİ)
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
        "canli_metrikler": "📉 Canlı Metrikler & AI Vana",
        "hava_sicakligi": "Hava Sıcaklığı (Canlı API)",
        "toprak_nemi": "Anlık Toprak Nemi",
        "analizi_gunlukle": "💾 Analizi Günlükle",
        "cografi_konum": "🗺️ Tarlanın Coğrafi Konumu",
        "verimlilik_raporu": "📊 Verimlilik Raporu",
        "su_tasarrufu": "AI Su Tasarruf Başarısı",
        "finansal_analiz": "💰 Finans & Bütçe Yönetimi (ERP)",
        "toplam_gider": "Toplam Operasyonel Gider",
        "tahmini_gelir": "Brüt Hasat Geliri",
        "net_kar": "Net Kâr Durumu",
        "ajanda_baslik": "📅 Dijital Tarım Ajandası & Maliyet Takibi",
        "rapor_indir": "📄 Kurumsal PDF/Web Raporunu İndir",
        "ai_kuru": "🔥 KRİTİK: Toprak kuru, hava sıcak! Acil sulama başlatıldı.",
        "ai_uyari": "💧 UYARI: Nem düşük, standart sulama açıldı.",
        "ai_normal": "✅ NORMAL: Nem yeterli, sulama kapalı. Tasarruf yapılıyor.",
        "hastalik_riski": "🦠 AI Hastalık Risk Analizi",
        "genel_merkez": "🏠 Genel Tarla Rapor Merkezi",
        "borsa_ekrani": "📈 Canlı Tarım Borsası",
        "depo_yonetimi": "📦 Depo ve Stok Yönetimi",
        "makine_garaji": "🚜 Makine ve Ekipman Garajı",
        "ai_asistan": "🤖 AI Ziraat Asistanı",
        "yeni_tarla_ekle": "➕ Yeni Arazi / Tarla Ekle",
        "tarla_ayarlari": "⚙️ Tarla Bilgilerini Düzenle / Ayarlar",
        "finans_ayarlari": "📈 Finansal Parametreler & Kredi Ayarları",
        "degisiklik_kaydet": "💾 Değişiklikleri Kaydet"
    },
    "EN": {
        "baslik": "🌾 AI Smart Agri ERP Control Center",
        "cikis_yap": "🚪 Logout",
        "canli_metrikler": "📉 Live Metrics & AI Valve",
        "hava_sicakligi": "Air Temp (Live API)",
        "toprak_nemi": "Instant Soil Moisture",
        "analizi_gunlukle": "💾 Log Analysis",
        "cografi_konum": "🗺️ Field Geographic Location",
        "verimlilik_raporu": "📊 Efficiency Report",
        "su_tasarrufu": "AI Water Saving Success",
        "finansal_analiz": "💰 Finance & Budget Management (ERP)",
        "toplam_gider": "Total Operational Cost",
        "tahmini_gelir": "Gross Harvest Revenue",
        "net_kar": "Net Profit Status",
        "ajanda_baslik": "📅 Digital Ag-Agenda & Cost Tracking",
        "rapor_indir": "📄 Download Corporate PDF/Web Report",
        "ai_kuru": "🔥 CRITICAL: Dry soil, hot weather! Emergency irrigation started.",
        "ai_uyari": "💧 WARNING: Low moisture, standard irrigation active.",
        "ai_normal": "✅ NORMAL: Moisture sufficient, irrigation off.",
        "hastalik_riski": "🦠 AI Disease Risk Analysis",
        "genel_merkez": "🏠 General Field Report Center",
        "borsa_ekrani": "📈 Live Agri Market",
        "depo_yonetimi": "📦 Warehouse & Stock Mgmt",
        "makine_garaji": "🚜 Machine & Equipment Garage",
        "ai_asistan": "🤖 AI Agri Assistant",
        "yeni_tarla_ekle": "➕ Add New Field / Land",
        "tarla_ayarlari": "⚙️ Edit Field Information / Settings",
        "finans_ayarlari": "📈 Financial Parameters & Loan Settings",
        "degisiklik_kaydet": "💾 Save Changes"
    }
}

st.sidebar.title("🌍 Language / Dil")
secilen_dil = st.sidebar.radio("Select Interface Language:", ["TR", "EN"])

def _t(anahtar, **kwargs):
    metin = dil_sozlugu[secilen_dil].get(anahtar, anahtar)
    if kwargs: return metin.format(**kwargs)
    return metin

# --- API VE YARDIMCI FONKSİYONLAR ---
def koordinat_bul(il, ilce):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={ilce},{il},Turkey&format=json&limit=1"
        cevap = requests.get(url, headers={'User-Agent': 'AkilliTarim/1.0'}, timeout=5)
        veri = cevap.json()
        if veri: return float(veri[0]['lat']), float(veri[0]['lon'])
    except: pass
    return 39.0, 35.0

def gercek_hava_durumu_getir(enlem, boylam):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={enlem}&longitude={boylam}&current_weather=true"
        return requests.get(url, timeout=5).json()["current_weather"]["temperature"]
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
    d_mesaj = "Hava şartları uygun." if dil == "TR" else "Conditions are favorable."

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
        elif "merhaba" in m: return "Merhaba! Ben yapay zeka tarım asistanınızım. Tarım, gübreleme veya bütçe konusunda nasıl yardımcı olabilirim?"
        else: return "Arazinize en uygun çözüm için lütfen ajandanıza bir 'Toprak Analizi' görevi ekleyin. Başka bir sorunuz var mı?"
    else:
        if "hello" in m: return "Hello! I am your AI agricultural assistant. How can I help you today?"
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
        
    # YENİ EKLENEN: MAKİNE GARAJI TABLOSU
    kursor.execute("""CREATE TABLE IF NOT EXISTS makine_garaji (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, 
        makine_adi TEXT NOT NULL, plaka TEXT NOT NULL, 
        son_bakim_saati REAL NOT NULL, guncel_saat REAL NOT NULL, bakim_periyodu REAL NOT NULL)""")
    
    # Eksik Sütun Kontrolleri
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

# --- VERİTABANI YARDIMCI FONKSİYONLARI ---
# (Kullanıcı, Ajanda, Analiz, Depo...)
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

# Depo
def sql_depo_urun_ekle(k_adi, urun_adi, kategori, miktar, birim, kritik):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO depo_envanter (kullanici_adi, urun_adi, kategori, miktar, birim, kritik_esik) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, urun_adi, kategori, miktar, birim, kritik))
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

# YENİ: Garaj
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


# --- OTURUM VE ARAYÜZ BAŞLANGICI ---
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
                st.write("---")
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    k_il = st.text_input("İl / State (*)")
                    k_ada = st.text_input("Ada No / Block")
                    k_alan = st.number_input("Alan / Area (m²)", min_value=0.0, step=100.0, value=1000.0)
                with col_k2:
                    k_ilce = st.text_input("İlçe / City (*)")
                    k_parsel = st.text_input("Parsel No / Parcel")
                    k_tarla = st.text_input("Tarla Adı / Farm Name (*)")
                    
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
    
    # YENİ MENÜ DÜZENİ: Borsa ve Garaj Eklendi
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
        
        # Simüle Edilmiş Borsa Verileri
        borsa_verileri = {
            "Pamuk (Ege Standart 1)": {"fiyat": 64.50, "degisim": 1.2},
            "Zeytinyağı (Sızma)": {"fiyat": 285.00, "degisim": -2.5},
            "Buğday (Ekmeklik)": {"fiyat": 10.20, "degisim": 0.4},
            "Mısır (1. Sınıf)": {"fiyat": 9.40, "degisim": -0.1},
            "Ayçiçeği (Yağlık)": {"fiyat": 17.80, "degisim": 0.8},
            "Domates (Salçalık)": {"fiyat": 4.50, "degisim": 0.2},
            "Narenciye (Portakal)": {"fiyat": 12.00, "degisim": -0.5}
        }
        
        # Kartlar halinde gösterim
        k1, k2, k3, k4 = st.columns(4)
        sutunlar = [k1, k2, k3, k4]
        idx = 0
        for urun, veri in borsa_verileri.items():
            sutunlar[idx % 4].metric(label=urun, value=f"₺ {veri['fiyat']:.2f}", delta=f"{veri['degisim']}%")
            idx += 1
            
        st.write("---")
        st.write("**Borsa Grafiği (Son 7 Günlük Trend)**")
        # Simüle grafik verisi
        tarihler = pd.date_range(end=datetime.today(), periods=7).strftime('%Y-%m-%d')
        df_trend = pd.DataFrame({
            'Tarih': tarihler,
            'Pamuk': [60, 61.5, 61, 62, 63.5, 63, 64.5],
            'Buğday': [9.5, 9.6, 9.8, 9.7, 10.0, 10.1, 10.2]
        })
        st.line_chart(df_trend.set_index('Tarih'))

    # ==========================================
    # MODÜL 2: MAKİNE VE EKİPMAN GARAJI
    # ==========================================
    elif aktif_secim == _t("makine_garaji"):
        st.subheader("🚜 Makine ve Ekipman Garajı (Bakım Takibi)")
        st.caption("Traktör, biçerdöver ve su motorlarınızın çalışma saatlerini ve bakım periyotlarını takip edin.")
        st.markdown("---")
        
        df_makine = sql_makine_getir(kullanici)
        
        # Bakım Alarmları
        if not df_makine.empty:
            for index, r in df_makine.iterrows():
                fark = r['guncel_saat'] - r['son_bakim_saati']
                kalan_saat = r['bakim_periyodu'] - fark
                if kalan_saat <= 0:
                    st.error(f"🚨 **BAKIM ZAMANI GELDİ:** {r['makine_adi']} ({r['plaka']}) için bakım periyodu aşıldı! Lütfen servise götürün.")
                elif kalan_saat <= 20:
                    st.warning(f"⚠️ **YAKLAŞAN BAKIM:** {r['makine_adi']} ({r['plaka']}) bakımına sadece **{kalan_saat} saat** kaldı.")
            st.markdown("---")
            
        col_m1, col_m2 = st.columns([1.2, 2])
        
        with col_m1:
            with st.form("yeni_makine_form"):
                st.write("**Yeni Makine/Araç Ekle**")
                m_adi = st.text_input("Makine Adı (Örn: John Deere 5075E):")
                m_plaka = st.text_input("Plaka / Demirbaş No:")
                m_son_bakim = st.number_input("Son Bakım Saati:", min_value=0.0, step=10.0)
                m_guncel = st.number_input("Şu Anki Motor Saati:", min_value=0.0, step=10.0)
                m_periyot = st.number_input("Bakım Periyodu (Saat):", min_value=10.0, value=250.0, step=50.0)
                
                if st.form_submit_button("🚜 Garaja Ekle", use_container_width=True):
                    if m_adi and m_plaka:
                        sql_makine_ekle(kullanici, m_adi, m_plaka, float(m_son_bakim), float(m_guncel), float(m_periyot))
                        st.success("Araç garaja eklendi!")
                        st.rerun()
                    else: st.warning("Ad ve Plaka zorunludur.")
                        
        with col_m2:
            st.write("**Garajdaki Araçlar ve Çalışma Durumları**")
            if not df_makine.empty:
                # Durum çubuklu liste
                for idx, r in df_makine.iterrows():
                    fark = r['guncel_saat'] - r['son_bakim_saati']
                    yuzde = min(fark / r['bakim_periyodu'], 1.0)
                    renk = "green" if yuzde < 0.8 else "orange" if yuzde < 1.0 else "red"
                    
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
                            if st.button("🔧 Bakım Yapıldı", key=f"b2_{r['id']}", help="Son bakım saatini, güncel saate eşitler."):
                                sql_makine_bakim_yap(r['id'], r['guncel_saat']); st.rerun()
                        with cm3:
                            if st.button("🗑️ Sil", key=f"b3_{r['id']}"):
                                sql_makine_sil(r['id']); st.rerun()
            else:
                st.info("Garajınız boş. Sol taraftan traktör veya makinelerinizi ekleyin.")

    # ==========================================
    # MODÜL 3: AI SOHBET BOTU
    # ==========================================
    elif aktif_secim == _t("ai_asistan"):
        st.subheader(_t("ai_asistan"))
        st.markdown("---")
        if "chat_gecmisi" not in st.session_state:
            karsilama = "Merhaba! Tarım, gübreleme veya bütçe ile ilgili sorularınızı bana sorabilirsiniz." if secilen_dil == "TR" else "Hello! Ask me anything about agriculture, fertilization or budget."
            st.session_state["chat_gecmisi"] = [{"rol": "asistan", "icerik": karsilama}]

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
    # MODÜL 4: DEPO YÖNETİMİ
    # ==========================================
    elif aktif_secim == _t("depo_yonetimi"):
        st.subheader(f"📦 Depo ve Envanter Kontrol Merkezi")
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
            with st.form("yeni_stok_formu"):
                d_urun_adi = st.text_input("Ürün Markası / Adı:")
                d_kategori = st.selectbox("Kategori:", ["Zirai İlaç", "Gübre", "Tohum/Fide", "Mazot/Yakıt", "Ambalaj", "Diğer"])
                c_d_1, c_d_2 = st.columns(2)
                with c_d_1: d_miktar = st.number_input("Miktar:", min_value=0.0, value=0.0)
                with c_d_2: d_birim = st.selectbox("Birim:", ["kg", "Litre", "Torba", "Adet", "Ton"])
                d_kritik = st.number_input("Kritik Eşik:", min_value=0.0, value=10.0)
                if st.form_submit_button("📦 Depoya Ekle", use_container_width=True):
                    if d_urun_adi:
                        sql_depo_urun_ekle(kullanici, d_urun_adi, d_kategori, float(d_miktar), d_birim, float(d_kritik))
                        st.rerun()

        with col_d2:
            if not df_depo.empty:
                st.dataframe(df_depo.rename(columns={"urun_adi":"Ürün", "kategori":"Kategori", "miktar":"Miktar", "birim":"Birim"})[["Ürün", "Kategori", "Miktar", "Birim"]], use_container_width=True, hide_index=True)
                
                with st.expander("⚙️ Stok Bilgilerini Düzenle / Düş", expanded=False):
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
            else: st.info("Deponuz boş.")

    # ==========================================
    # 5. GENEL MERKEZ VE TARLA İŞLEMLERİ (Önceki Sürümle Birebir Aynı)
    # ==========================================
    elif aktif_secim == _t("genel_merkez"):
        st.subheader(f"🏠 ERP Genel Rapor Merkezi")
        st.markdown("---")
        t_gider = t_gelir = t_destek = t_kredi = 0.0
        for t in tarlalar_listesi:
            t_gelir += (t[9] * t[10]); t_destek += t[11]; t_kredi += (t[12] + (t[12] * t[13] / 100))
            df_g = sql_takvim_verileri_getir_ham(kullanici, t[0])
            if not df_g.empty: t_gider += df_g['maliyet'].sum()
        net = t_gelir + t_destek - t_gider - t_kredi
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("Toplam Gelir+Destek", f"₺ {(t_gelir + t_destek):,.2f}")
        rc2.metric("Toplam Gider", f"₺ {t_gider:,.2f}")
        rc3.metric("Banka Ödemeleri", f"₺ {t_kredi:,.2f}")
        rc4.metric("İşletme Net Kârı", f"₺ {net:,.2f}", delta="Kârlı" if net > 0 else "Zarar")

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

    else:
        # Seçili Tarlanın Detayları
        aktif_t = next((t for t in tarlalar_listesi if t[0] == aktif_secim), None)
        if aktif_t:
            tarla_adi, t_enlem, t_boylam, m_email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz = aktif_t
            st.subheader(f"🌾 {tarla_adi.upper()}")
            
            # Formlar vs. (Optimizasyon için finansal özet ve ajanda gösteriliyor)
            df_takvim_ham = sql_takvim_verileri_getir_ham(kullanici, tarla_adi)
            toplam_gider = df_takvim_ham['maliyet'].sum() if not df_takvim_ham.empty else 0.0
            
            cm1, cm2, cm3 = st.columns(3)
            cm1.metric("Brüt Gelir", f"₺ {(rekolte_kg*birim_fiyat):,.0f}")
            cm2.metric("Toplam Gider", f"₺ {toplam_gider:,.0f}")
            cm3.metric("Net Kâr", f"₺ {((rekolte_kg*birim_fiyat)+devlet_destegi-toplam_gider-(kredi_anapara*1.2)):,.0f}")

            st.write("---")
            st.write("**📅 Ajanda ve Depo Düşümü**")
            with st.form("ajanda"):
                c1, c2 = st.columns(2)
                with c1: 
                    y_islem = st.text_input("İşlem Özeti:")
                    y_mal = st.number_input("Tutar (TL):", min_value=0.0)
                with c2:
                    df_depo_a = sql_depo_urun_getir(kullanici)
                    sec_list = ["-- Ürün Kullanma --"] + df_depo_a.apply(lambda r: f"{r['id']} | {r['urun_adi']}", axis=1).tolist() if not df_depo_a.empty else ["-- Depo Boş --"]
                    depo_sec = st.selectbox("Stoktan Düş:", sec_list)
                    dep_mik = st.number_input("Düşülecek Miktar:", min_value=0.0)
                    
                if st.form_submit_button("Kaydet"):
                    sql_takvim_etkinlik_ekle(kullanici, tarla_adi, y_islem, str(datetime.now().date()), "Tamamlandı", y_mal, "Diğer")
                    if depo_sec != "-- Ürün Kullanma --" and depo_sec != "-- Depo Boş --" and dep_mik > 0:
                        s_id = int(depo_sec.split("|")[0])
                        eski_mik = df_depo_a[df_depo_a['id']==s_id].iloc[0]['miktar']
                        sql_depo_miktar_guncelle(s_id, max(0.0, eski_mik - dep_mik))
                    st.rerun()
