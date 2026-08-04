# ==============================================================================
# PROJE: AI Destekli Akıllı Tarım Platformu (GLOBAL ÇOKLU DİL SAAS SÜRÜMÜ)
# ==============================================================================

import streamlit as st
import random
import requests
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="AI Akıllı Tarım Paneli", page_icon="🌾", layout="wide")

# --- ÇOKLU DİL SÖZLÜĞÜ VE ÇEVİRİ MOTORU ---
dil_sozlugu = {
    "TR": {
        "baslik": "🌾 AI Akıllı Tarım Kontrol Merkezi",
        "cikis_yap": "🚪 Çıkış Yap",
        "canli_metrikler": "📉 Canlı Metrikler & AI Vana",
        "hava_sicakligi": "Hava Sıcaklığı (Canlı API) / Mahsul",
        "toprak_nemi": "Anlık Toprak Nemi",
        "hedef": "Hedef",
        "analizi_gunlukle": "💾 Analizi Günlükle",
        "cografi_konum": "🗺️ Tarlanın Coğrafi Konumu",
        "harita_lokasyonu": "Harita Lokasyonu",
        "verimlilik_raporu": "📊 Verimlilik & Tasarruf Raporu",
        "su_tasarrufu": "AI Su Tasarruf Başarısı",
        "nem_gecmisi": "📈 Son Günlüklenen Toprak Nem Geçmişi (%)",
        "finansal_analiz": "💰 Finansal Analiz & Sezonluk Bütçe Raporu",
        "toplam_gider": "Toplam Operasyonel Gider (TL)",
        "tahmini_gelir": "Tahmini Hasat Geliri",
        "net_kar": "Beklenen Net Kâr (TL)",
        "ajanda_baslik": "📅 Dijital Tarım Ajandası & Görev Takibi",
        "rapor_indir": "📄 Kurumsal Web Raporunu İndir (.html)",
        "veri_seti_indir": "📥 Yapay Zeka İçin Veri Setini İndir (.csv)",
        "ai_kuru": "🔥 KRİTİK: Toprak kuru, hava sıcak! Acil sulama başlatıldı.",
        "ai_uyari": "💧 UYARI: Nem düşük, standart sulama açıldı.",
        "ai_normal": "✅ NORMAL: Nem yeterli, sulama kapalı. Su tasarrufu yapılıyor.",
        "veri_isleme": "Veriler veritabanına başarıyla işlendi!",
        "hastalik_riski": "🦠 AI Hastalık Risk Analizi"
    },
    "EN": {
        "baslik": "🌾 AI Smart Agri Control Center",
        "cikis_yap": "🚪 Logout",
        "canli_metrikler": "📉 Live Metrics & AI Valve",
        "hava_sicakligi": "Air Temp (Live API) / Crop",
        "toprak_nemi": "Instant Soil Moisture",
        "hedef": "Target",
        "analizi_gunlukle": "💾 Log Analysis",
        "cografi_konum": "🗺️ Field Geographic Location",
        "harita_lokasyonu": "Map Location",
        "verimlilik_raporu": "📊 Efficiency & Savings Report",
        "su_tasarrufu": "AI Water Saving Success",
        "nem_gecmisi": "📈 Recently Logged Soil Moisture History (%)",
        "finansal_analiz": "💰 Financial Analysis & Seasonal Budget",
        "toplam_gider": "Total Operational Cost (TRY)",
        "tahmini_gelir": "Est. Harvest Revenue",
        "net_kar": "Expected Net Profit (TRY)",
        "ajanda_baslik": "📅 Digital Ag-Agenda & Task Tracking",
        "rapor_indir": "📄 Download Corporate Web Report (.html)",
        "veri_seti_indir": "📥 Download Dataset for AI (.csv)",
        "ai_kuru": "🔥 CRITICAL: Dry soil, hot weather! Emergency irrigation started.",
        "ai_uyari": "💧 WARNING: Low moisture, standard irrigation active.",
        "ai_normal": "✅ NORMAL: Moisture sufficient, irrigation off. Saving water.",
        "veri_isleme": "Data successfully logged to database!",
        "hastalik_riski": "🦠 AI Disease Risk Analysis"
    }
}

# Sidebar üzerinden dil seçimi
st.sidebar.title("🌍 Language / Dil")
secilen_dil = st.sidebar.radio("Select Interface Language:", ["TR", "EN"])

def _t(anahtar):
    """Seçili dile göre sözlükten kelimeyi getirir, bulamazsa anahtarı döndürür."""
    return dil_sozlugu[secilen_dil].get(anahtar, anahtar)

# --- ADRESTEN GERÇEK KOORDİNAT BULMA API'Sİ (Geocoding) ---
def koordinat_bul(il, ilce):
    try:
        adres = f"{ilce}, {il}, Turkey"
        url = f"https://nominatim.openstreetmap.org/search?q={adres}&format=json&limit=1"
        headers = {'User-Agent': 'AkilliTarimProjesi/1.0'} 
        cevap = requests.get(url, headers=headers, timeout=5)
        veri = cevap.json()
        if len(veri) > 0:
            return float(veri[0]['lat']), float(veri[0]['lon'])
        else:
            return 39.0, 35.0
    except:
        return 39.0, 35.0

# --- GERÇEK ZAMANLI HAVA DURUMU API FONKSİYONU ---
def gercek_hava_durumu_getir(enlem, boylam):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={enlem}&longitude={boylam}&current_weather=true"
        cevap = requests.get(url, timeout=5)
        veri = cevap.json()
        return veri["current_weather"]["temperature"]
    except:
        return None 

# --- ZAMAN BAZLI AKILLI NEM SİMÜLASYONU ---
def akilli_nem_simulasyonu():
    su_anki_saat = datetime.now().hour
    if 6 <= su_anki_saat < 12:
        return random.randint(40, 70)
    elif 12 <= su_anki_saat < 18:
        return random.randint(15, 35)
    elif 18 <= su_anki_saat < 22:
        return random.randint(30, 50)
    else:
        return random.randint(50, 75)

# --- YAPAY ZEKA HASTALIK RİSK TAHMİN MOTORU ---
def ai_hastalik_risk_analizi(urun, sicaklik, nem, dil="TR"):
    risk_skoru = 10 
    hastalik_adi = "Mantar ve Bakteri Riski" if dil == "TR" else "Fungal and Bacterial Risk"
    detay_mesaj = "Hava şartları mahsul sağlığı için elverişli görünüyor." if dil == "TR" else "Weather conditions look favorable for crop health."

    if urun == "Pamuk":
        hastalik_adi = "Pamukta Solgunluk & Kırmızı Örümcek" if dil == "TR" else "Cotton Wilt & Spider Mites"
        if sicaklik > 32 and nem < 30:
            risk_skoru = 85
            detay_mesaj = "🚨 Yüksek sıcaklık ve düşük nem Kırmızı Örümcek zararlısını tetikler!" if dil == "TR" else "🚨 High temp and low humidity trigger Spider Mites!"
        elif sicaklik > 25 and nem > 60:
            risk_skoru = 60
            detay_mesaj = "⚠️ Nemli ve sıcak hava Solgunluk mantarını tetikleyebilir." if dil == "TR" else "⚠️ Humid and warm weather can trigger Wilt fungus."
            
    elif urun == "Zeytin":
        hastalik_adi = "Zeytin Halkalı Leke Hastalığı" if dil == "TR" else "Olive Peacock Spot Disease"
        if 15 <= sicaklik <= 22 and nem > 70:
            risk_skoru = 90
            detay_mesaj = "🚨 Tam Halkalı Leke mantarının üreme sıcaklığı!" if dil == "TR" else "🚨 Perfect breeding temp for Peacock Spot fungus!"
        elif sicaklik > 28:
            risk_skoru = 20
            detay_mesaj = "✅ Yüksek sıcaklık faaliyetleri yavaşlatıyor." if dil == "TR" else "✅ High temperatures slow down disease activities."

    return hastalik_adi, risk_skoru, detay_mesaj

# --- VERİTABANI KURULUMU VE GÜNCELLEMESİ ---
def veritabani_otomatik_kur():
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("""
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT UNIQUE NOT NULL, sifre TEXT NOT NULL,
        tarla_adi TEXT NOT NULL, enlem REAL NOT NULL, boylam REAL NOT NULL, email TEXT NOT NULL,
        urun_turu TEXT DEFAULT 'Genel', rol TEXT DEFAULT 'SHA', ada TEXT DEFAULT '-', parsel TEXT DEFAULT '-'
    )
    """)
    kursor.execute("""
    CREATE TABLE IF NOT EXISTS tarim_takvimi (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, islem_turu TEXT NOT NULL,
        tarih TEXT NOT NULL, notlar TEXT, maliyet REAL DEFAULT 0.0
    )
    """)
    kursor.execute("""
    CREATE TABLE IF NOT EXISTS tarla_gunlukleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, nem INTEGER NOT NULL,
        sicaklik INTEGER NOT NULL, karar TEXT NOT NULL, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    try:
        kursor.execute("ALTER TABLE tarim_takvimi ADD COLUMN maliyet REAL DEFAULT 0.0")
        baglanti.commit()
    except:
        pass 
        
    try:
        kursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("yunus", "12345", "Yunus Beyin Pamuk Tarlası (Adana)", 37.00, 35.32, "yonetici_yunus@example.com", "Pamuk", "Admin", "104", "12"))
        baglanti.commit()
    except sqlite3.IntegrityError:
        pass
    baglanti.close()

veritabani_otomatik_kur()

# --- SQL YARDIMCI FONKSİYONLARI ---
def sql_kullanici_kontrol(kullanici_adi, sifre):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("SELECT tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (kullanici_adi, sifre))
    sonuc = kursor.fetchone()
    baglanti.close()
    return sonuc

def sql_calisan_ekle(k_adi, sifre, t_adi, enlem, boylam, email, urun, rol, ada, parsel):
    try:
        baglanti = sqlite3.connect("akilli_tarim.db")
        kursor = baglanti.cursor()
        kursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (k_adi, sifre, t_adi, enlem, boylam, email, urun, rol, ada, parsel))
        baglanti.commit()
        baglanti.close()
        return True
    except:
        return False

def sql_yeni_musteri_kayit(k_adi, sifre, tarla, il, ilce, email, urun, ada, parsel):
    try:
        baglanti = sqlite3.connect("akilli_tarim.db")
        kursor = baglanti.cursor()
        tam_tarla_adi = f"{tarla} ({il.capitalize()} / {ilce.capitalize()})"
        v_enlem, v_boylam = koordinat_bul(il, ilce)
        kursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (k_adi, sifre, tam_tarla_adi, v_enlem, v_boylam, email, urun, "Müşteri/Çiftçi", ada, parsel))
        baglanti.commit()
        baglanti.close()
        return True
    except sqlite3.IntegrityError:
        return False 

def sql_takvim_etkinlik_ekle(k_adi, islem, tarih, notlar, maliyet):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("INSERT INTO tarim_takvimi (kullanici_adi, islem_turu, tarih, notlar, maliyet) VALUES (?, ?, ?, ?, ?)", (k_adi, islem, tarih, notlar, maliyet))
    baglanti.commit()
    baglanti.close()

def sql_takvim_etkinlik_guncelle(gorev_id, yeni_tarih, yeni_not, yeni_maliyet):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("UPDATE tarim_takvimi SET tarih = ?, notlar = ?, maliyet = ? WHERE id = ?", (yeni_tarih, yeni_not, yeni_maliyet, gorev_id))
    baglanti.commit()
    baglanti.close()

def sql_takvim_etkinlik_sil(gorev_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("DELETE FROM tarim_takvimi WHERE id = ?", (gorev_id,))
    baglanti.commit()
    baglanti.close()

def sql_takvim_verileri_getir_ham(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, islem_turu, tarih, notlar, maliyet FROM tarim_takvimi WHERE kullanici_adi = ? ORDER BY id DESC", baglanti, params=(k_adi,))
    baglanti.close()
    return df

def sql_analiz_kaydet(k_adi, nem, sicaklik, karar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("INSERT INTO tarla_gunlukleri (kullanici_adi, nem, sicaklik, karar) VALUES (?, ?, ?, ?)", (k_adi, nem, sicaklik, karar))
    baglanti.commit()
    baglanti.close()

def sql_analizleri_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT nem, sicaklik, karar, tarih FROM tarla_gunlukleri WHERE kullanici_adi = ? ORDER BY id DESC LIMIT 50", baglanti, params=(k_adi,))
    baglanti.close()
    return df

def sql_tum_veriyi_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT nem, sicaklik, karar, tarih FROM tarla_gunlukleri WHERE kullanici_adi = ? ORDER BY id ASC", baglanti, params=(k_adi,))
    baglanti.close()
    return df

# --- OTURUM KONTROLÜ ---
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["aktif_kullanici"] = ""
    st.session_state["kullanici_bilgileri"] = None

# --- GİRİŞ VE YENİ KAYIT EKRANI ---
if not st.session_state["giris_yapildi"]:
    bosluk_sol, icerik_orta, bosluk_sag = st.columns([1.5, 2.5, 1.5])
    
    with icerik_orta:
        if secilen_dil == "TR":
            st.markdown("<h2 style='text-align: center; color: #2ecc71;'>🌾 AI Akıllı Tarım Ağı</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Sisteme giriş yapın veya yeni bir çiftçi hesabı oluşturun.</p>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align: center; color: #2ecc71;'>🌾 AI Smart Agri Network</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Log in to the system or create a new farmer account.</p>", unsafe_allow_html=True)
        st.write("")
        
        tab_names = ["🔑 Sisteme Giriş", "📝 Yeni Kayıt Ol"] if secilen_dil == "TR" else ["🔑 Login", "📝 Register New Account"]
        sekme_giris, sekme_kayit = st.tabs(tab_names)
        
        with sekme_giris:
            st.write("")
            kullanici_adi = st.text_input("Kullanıcı Adı / Username:", key="login_kadi")
            sifre = st.text_input("Şifre / Password:", type="password", key="login_sifre")
            btn_text = "🚀 Sisteme Bağlan" if secilen_dil == "TR" else "🚀 Login to System"
            if st.button(btn_text, use_container_width=True, type="primary"):
                kullanici_verisi = sql_kullanici_kontrol(kullanici_adi, sifre)
                if kullanici_verisi:
                    st.session_state["giris_yapildi"] = True
                    st.session_state["aktif_kullanici"] = kullanici_adi
                    st.session_state["kullanici_bilgileri"] = kullanici_verisi
                    st.rerun()
                else:
                    st.error("Hatalı Kullanıcı Adı veya Şifre!" if secilen_dil == "TR" else "Invalid Username or Password!")
                    
        with sekme_kayit:
            with st.form("yeni_kayit_formu"):
                if secilen_dil == "TR":
                    st.subheader("Yeni Tarla / Çiftçi Kaydı")
                    k_adi = st.text_input("Kullanıcı Adı (*)")
                    k_sifre = st.text_input("Şifre (*)", type="password")
                    k_email = st.text_input("E-Posta Adresi (*)")
                    st.write("**📍 Lokasyon ve Parsel Bilgileri**")
                else:
                    st.subheader("New Field / Farmer Registration")
                    k_adi = st.text_input("Username (*)")
                    k_sifre = st.text_input("Password (*)", type="password")
                    k_email = st.text_input("Email Address (*)")
                    st.write("**📍 Location and Parcel Information**")
                
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    k_il = st.text_input("İl / State (*)")
                    k_ada = st.text_input("Ada No / Block (*)")
                with col_k2:
                    k_ilce = st.text_input("İlçe / City (*)")
                    k_parsel = st.text_input("Parsel No / Parcel (*)")
                    
                k_tarla = st.text_input("Tarlanıza Vermek İstediğiniz İsim / Farm Name")
                
                urunler = ["Pamuk", "Zeytin", "Buğday", "Mısır", "Ayçiçeği", "Narenciye", "Domates", "Diğer"] if secilen_dil == "TR" else ["Cotton", "Olive", "Wheat", "Corn", "Sunflower", "Citrus", "Tomato", "Other"]
                k_urun = st.selectbox("Yetiştirilen Ana Mahsul / Main Crop", urunler)
                
                kayit_buton = st.form_submit_button("✅ Hesabı Oluştur / Create Account", use_container_width=True)
                
                if kayit_buton:
                    if k_adi and k_sifre and k_email and k_il and k_ilce and k_ada and k_parsel:
                        with st.spinner("Harita koordinatları bulunuyor... / Finding coordinates..."):
                            sonuc = sql_yeni_musteri_kayit(k_adi, k_sifre, k_tarla, k_il, k_ilce, k_email, k_urun, k_ada, k_parsel)
                        if sonuc:
                            st.success("🎉 Kayıt başarılı! / Registration successful!")
                        else:
                            st.error("⚠️ Bu kullanıcı adı kullanımda! / Username already taken!")
                    else:
                        st.warning("Zorunlu alanları doldurun. / Please fill required fields.")

# --- ANA PANEL ---
else:
    kullanici = st.session_state["aktif_kullanici"]
    tarla_adi, t_enlem, t_boylam, m_email, urun_turu, rol, ada, parsel = st.session_state["kullanici_bilgileri"]

    if "toprak_nemi" not in st.session_state:
        st.session_state["toprak_nemi"] = akilli_nem_simulasyonu()
        gercek_isi = gercek_hava_durumu_getir(t_enlem, t_boylam)
        st.session_state["canli_sicaklik"] = gercek_isi if gercek_isi is not None else random.randint(22, 38)
        
    toprak_nemi = st.session_state["toprak_nemi"]
    canli_sicaklik = st.session_state["canli_sicaklik"]

    if toprak_nemi < 30 and canli_sicaklik > 30:
        ai_mesaj = _t("ai_kuru")
        ai_durum = "error"
        css_durum = "box-danger"
    elif toprak_nemi < 30:
        ai_mesaj = _t("ai_uyari")
        ai_durum = "warning"
        css_durum = "box-warning"
    else:
        ai_mesaj = _t("ai_normal")
        ai_durum = "success"
        css_durum = "box-success"

    h_adi, h_skor, h_mesaj = ai_hastalik_risk_analizi(urun_turu, canli_sicaklik, toprak_nemi, secilen_dil)
    h_css = "box-danger" if h_skor >= 75 else "box-warning" if h_skor >= 40 else "box-success"

    df_takvim_ham = sql_takvim_verileri_getir_ham(kullanici)
    toplam_gider = 0.0
    if not df_takvim_ham.empty and 'maliyet' in df_takvim_ham.columns:
        toplam_gider = df_takvim_ham['maliyet'].sum()
        
    baz_getiri = {"Pamuk": 150000, "Zeytin": 200000, "Buğday": 80000, "Mısır": 120000, "Ayçiçeği": 95000, "Narenciye": 180000, "Domates": 110000}
    tahmini_gelir = baz_getiri.get(urun_turu, 100000)
    beklenen_kar = tahmini_gelir - toplam_gider

    col_header_text, col_header_logout_btn = st.columns([8.5, 1.5])
    with col_header_text:
        st.subheader(f"{_t('baslik')} | {tarla_adi.upper()}")
        st.caption(f"Admin: {kullanici.upper()} ({rol}) | {ada}/{parsel}")
    with col_header_logout_btn:
        st.write("") 
        if st.button(_t("cikis_yap"), type="primary", use_container_width=True):
            st.session_state["giris_yapildi"] = False
            st.session_state["aktif_kullanici"] = ""
            st.rerun()

    st.markdown(" ")

    col_top_left, col_top_right = st.columns(2) 
    with col_top_right:
        with st.expander("🖨️ " + ("GELİŞMİŞ ÇIKTI VE RAPORLAMA MERKEZİ" if secilen_dil == "TR" else "ADVANCED REPORTING CENTER"), expanded=False):
            html_rapor = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: sans-serif; padding: 40px; color: #2c3e50; }}
                .header {{ text-align: center; border-bottom: 3px solid #2ecc71; padding-bottom: 20px; }}
                .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
                .info-table th, .info-table td {{ border: 1px solid #e0e0e0; padding: 12px; text-align: left; }}
                .info-table th {{ background-color: #f8f9fa; width: 35%; }}
                .box {{ padding: 15px; border-radius: 8px; margin-bottom: 15px; font-weight: bold; background-color: #eaeded; }}
            </style>
            </head>
            <body>
                <div class="header">
                    <h2>AI Smart Agri Platform Report</h2>
                    <p>Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                <table class="info-table">
                    <tr><th>User / Mülk Sahibi</th><td>{kullanici.upper()}</td></tr>
                    <tr><th>Field / Tesis Adı</th><td>{tarla_adi.upper()}</td></tr>
                    <tr><th>Crop / Mahsul</th><td>{urun_turu}</td></tr>
                    <tr><th>Temp / Sıcaklık</th><td>{canli_sicaklik} °C</td></tr>
                    <tr><th>Moisture / Nem</th><td>%{toprak_nemi}</td></tr>
                </table>
            </body>
            </html>
            """
            st.download_button(
                label=_t("rapor_indir"),
                data=html_rapor,
                file_name=f"{kullanici}_report.html",
                mime="text/html",
                use_container_width=True
            )

    st.markdown("---")

    df_kayitlar = sql_analizleri_getir(kullanici)
    if not df_kayitlar.empty:
        toplam_kayit = len(df_kayitlar)
        tasarruf_kayitlari = df_kayitlar['karar'].str.contains("NORMAL").sum()
        tasarruf_orani = tasarruf_kayitlari / toplam_kayit
    else:
        tasarruf_orani = 0.0
        toplam_kayit = 0

    col_box1, col_box2, col_box3 = st.columns(3)
    
    with col_box1:
        st.subheader(_t("canli_metrikler"), divider="blue")
        st.write(_t("hava_sicakligi"))
        st.subheader(f"{canli_sicaklik} °C")
        
        st.write(_t("toprak_nemi"))
        st.subheader(f"%{toprak_nemi}")
        
        if ai_durum == "error":
            st.error(f"**AI KARARI:**\n\n{ai_mesaj}")
        elif ai_durum == "warning":
            st.warning(f"**AI KARARI:**\n\n{ai_mesaj}")
        else:
            st.success(f"**AI KARARI:**\n\n{ai_mesaj}")
            
        st.write(" ")
        st.write(f"🦠 **{_t('hastalik_riski')} ({h_adi})**")
        st.progress(h_skor / 100)
        
        st.write(" ")
        if st.button(_t("analizi_gunlukle"), use_container_width=True):
            sql_analiz_kaydet(kullanici, int(toprak_nemi), float(canli_sicaklik), ai_mesaj)
            st.toast(_t("veri_isleme"))
            st.rerun()

    with col_box2:
        st.subheader(_t("cografi_konum"), divider="green")
        tarla_df = pd.DataFrame({'lat': [t_enlem], 'lon': [t_boylam]})
        st.map(tarla_df, size=14, zoom=11)
        st.caption(f"📍 Enlem: {t_enlem} | Boylam: {t_boylam} ({_t('harita_lokasyonu')})")

    with col_box3:
        st.subheader(_t("verimlilik_raporu"), divider="orange")
        st.write(_t("su_tasarrufu"))
        st.subheader(f"%{int(tasarruf_orani * 100)}")
        st.progress(tasarruf_orani)
        
        st.write("---")
        st.caption(_t("nem_gecmisi"))
        
        if not df_kayitlar.empty:
            df_grafik = df_kayitlar.iloc[::-1].reset_index()
            st.line_chart(df_grafik['nem'])
        else:
            st.write("-")

        st.markdown(" ")
        df_tum_veri = sql_tum_veriyi_getir(kullanici)
        if not df_tum_veri.empty:
            csv_veri = df_tum_veri.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=_t("veri_seti_indir"),
                data=csv_veri,
                file_name=f"{kullanici}_ml_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.markdown("---")
    st.subheader(_t("finansal_analiz"), divider="red")
    
    col_fin1, col_fin2, col_fin3 = st.columns(3)
    col_fin1.metric(label=_t("toplam_gider"), value=f"₺ {toplam_gider:,.2f}")
    col_fin2.metric(label=f"{_t('tahmini_gelir')} ({urun_turu})", value=f"₺ {tahmini_gelir:,.2f}")
    
    durum_etiketi = "Kârlı / Profitable" if beklenen_kar > 0 else "Zarar Riski / Loss Risk"
    col_fin3.metric(label=_t("net_kar"), value=f"₺ {beklenen_kar:,.2f}", delta=durum_etiketi)

    st.markdown("---")
    st.subheader(_t("ajanda_baslik"), divider="gray")
    
    col_ajanda1, col_ajanda2 = st.columns([1, 2.5])
    
    with col_ajanda1:
        with st.form("yeni_gorev_formu"):
            st.write("**Yeni Faaliyet / New Task**")
            yeni_islem = st.selectbox("İşlem Türü / Task Type:", ["Gübreleme / Fertilizing", "İlaçlama / Spraying", "Hasat / Harvest", "Sulama / Irrigation", "Diğer / Other"])
            yeni_tarih = st.date_input("Tarih / Date:")
            yeni_maliyet = st.number_input("Tahmini Maliyet / Est. Cost:", min_value=0.0, step=100.0)
            yeni_not = st.text_input("Durum / Note:", value="Planlandı / Planned")
            
            if st.form_submit_button("🗓️ Takvime İşle / Save Task", use_container_width=True):
                sql_takvim_etkinlik_ekle(kullanici, yeni_islem, str(yeni_tarih), yeni_not, float(yeni_maliyet))
                st.rerun()
                
    with col_ajanda2:
        if not df_takvim_ham.empty:
            df_gosterim = df_takvim_ham.copy()
            if 'maliyet' not in df_gosterim.columns:
                df_gosterim['maliyet'] = 0.0
            
            df_gosterim = df_gosterim.rename(columns={"islem_turu": "Faaliyet / Task", "tarih": "Tarih / Date", "notlar": "Durum / Status", "maliyet": "Maliyet / Cost"})
            st.dataframe(df_gosterim[["Faaliyet / Task", "Tarih / Date", "Maliyet / Cost", "Durum / Status"]], use_container_width=True, hide_index=True)
            
            gorev_secenekleri = df_takvim_ham.apply(lambda row: f"ID:{row['id']} | {row['islem_turu']} ({row['tarih']})", axis=1).tolist()
            secilen_gorev_metin = st.selectbox("Görev Seç / Select Task to Edit:", gorev_secenekleri)
            
            if secilen_gorev_metin:
                secilen_id = int(secilen_gorev_metin.split("|")[0].replace("ID:", "").strip())
                if st.button("🗑️ Görevi Sil / Delete Task", key=f"btn_sil_{secilen_id}", use_container_width=True):
                    sql_takvim_etkinlik_sil(secilen_id)
                    st.rerun()
