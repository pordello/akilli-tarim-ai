# ==============================================================================
# PROJE: AI Destekli Akıllı Tarım Platformu (M² ALAN HESABI EKLENDİ)
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
        "hastalik_riski": "🦠 AI Hastalık Risk Analizi",
        "personel_yetki": "👥 ADMIN PERSONEL YETKİLENDİRME BÖLGESİ",
        "raporlama_merkezi": "🖨️ GELİŞMİŞ ÇIKTI VE RAPORLAMA MERKEZİ",
        "genel_merkez": "🏠 Genel Tarla Rapor Merkezi",
        "yeni_tarla_ekle": "➕ Yeni Arazi / Tarla Ekle",
        "alarm_kritik": "🚨 **KRİTİK ALARM:** Yapay zeka tarlada risk tespit etti! Eylem planı **{email}** adresinize iletildi.",
        "alarm_uyari": "⚠️ **SİSTEM UYARISI:** Tarlada dikkat edilmesi gereken durumlar var. Detaylar **{email}** adresine iletildi.",
        "alarm_normal": "✅ **BİLDİRİM MERKEZİ:** Her şey yolunda. Günlük olağan rapor **{email}** adresine gönderildi."
    },
    "EN": {
        "baslik": "🌾 AI Smart Agri Control Center",
        "cikis_yap": "🚪 Logout",
        "canli_metrikler": "📉 Live Metrics & AI Valve",
        "hava_sicakligi": "Air Temp (Live API) / Crop",
        "toprak_nemi": "Instant Soil Moisture",
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
        "hastalik_riski": "🦠 AI Disease Risk Analysis",
        "personel_yetki": "👥 ADMIN PERSONNEL AUTHORIZATION AREA",
        "raporlama_merkezi": "🖨️ ADVANCED REPORTING & EXPORT CENTER",
        "genel_merkez": "🏠 General Field Report Center",
        "yeni_tarla_ekle": "➕ Add New Field / Land",
        "alarm_kritik": "🚨 **CRITICAL ALARM:** AI detected field risks! Action plan sent to **{email}**.",
        "alarm_uyari": "⚠️ **SYSTEM WARNING:** Conditions require attention. Details sent to **{email}**.",
        "alarm_normal": "✅ **NOTIFICATION CENTER:** Everything is optimal. Daily report sent to **{email}**."
    }
}

st.sidebar.title("🌍 Language / Dil")
secilen_dil = st.sidebar.radio("Select Interface Language:", ["TR", "EN"])

def _t(anahtar, **kwargs):
    metin = dil_sozlugu[secilen_dil].get(anahtar, anahtar)
    if kwargs:
        return metin.format(**kwargs)
    return metin

# --- API FONKSİYONLARI ---
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

def gercek_hava_durumu_getir(enlem, boylam):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={enlem}&longitude={boylam}&current_weather=true"
        cevap = requests.get(url, timeout=5)
        veri = cevap.json()
        return veri["current_weather"]["temperature"]
    except:
        return None 

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

def ai_hastalik_risk_analizi(urun, sicaklik, nem, dil="TR"):
    risk_skoru = 10 
    hastalik_adi = "Mantar ve Bakteri Riski" if dil == "TR" else "Fungal and Bacterial Risk"
    detay_mesaj = "Hava şartları mahsul sağlığı için elverişli görünüyor." if dil == "TR" else "Weather conditions look favorable."

    if urun in ["Pamuk", "Cotton"]:
        hastalik_adi = "Pamukta Solgunluk & Kırmızı Örümcek" if dil == "TR" else "Cotton Wilt & Spider Mites"
        if sicaklik > 32 and nem < 30:
            risk_skoru = 85
            detay_mesaj = "🚨 Yüksek sıcaklık ve düşük nem Kırmızı Örümcek zararlısını tetikler!" if dil == "TR" else "🚨 High temp and low humidity trigger Spider Mites!"
        elif sicaklik > 25 and nem > 60:
            risk_skoru = 60
            detay_mesaj = "⚠️ Nemli ve sıcak hava Solgunluk mantarını tetikleyebilir." if dil == "TR" else "⚠️ Humid and warm weather can trigger Wilt fungus."
    elif urun in ["Zeytin", "Olive"]:
        hastalik_adi = "Zeytin Halkalı Leke Hastalığı" if dil == "TR" else "Olive Peacock Spot Disease"
        if 15 <= sicaklik <= 22 and nem > 70:
            risk_skoru = 90
            detay_mesaj = "🚨 Tam Halkalı Leke mantarının üreme sıcaklığı!" if dil == "TR" else "🚨 Perfect breeding temp for Peacock Spot fungus!"
    elif urun in ["Buğday", "Wheat"]:
        hastalik_adi = "Buğdayda Pas Hastalığı (Küf)" if dil == "TR" else "Wheat Rust Disease (Mold)"
        if 10 <= sicaklik <= 20 and nem > 65:
            risk_skoru = 75
            detay_mesaj = "⚠️ Serin ve nemli hava pas hastalığı için ideal ortam oluşturuyor." if dil == "TR" else "⚠️ Cool and humid weather creates ideal conditions."
    else: 
        hastalik_adi = "Kök Çürüklüğü & Mantar" if dil == "TR" else "Root Rot & Fungus"
        if nem > 75:
            risk_skoru = 80
            detay_mesaj = "🚨 Aşırı toprak nemi köklerin nefes almasını engelliyor!" if dil == "TR" else "🚨 Excessive soil moisture prevents roots from breathing!"

    return hastalik_adi, risk_skoru, detay_mesaj

# --- VERİTABANI KURULUMU (ALAN M² EKLENDİ) ---
def veritabani_otomatik_kur():
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    
    kursor.execute("""
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, sifre TEXT NOT NULL,
        tarla_adi TEXT NOT NULL, enlem REAL NOT NULL, boylam REAL NOT NULL, email TEXT NOT NULL,
        urun_turu TEXT DEFAULT 'Genel', rol TEXT DEFAULT 'SHA', ada TEXT DEFAULT '-', parsel TEXT DEFAULT '-',
        alan_m2 REAL DEFAULT 0.0
    )
    """)
    kursor.execute("""
    CREATE TABLE IF NOT EXISTS tarim_takvimi (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, tarla_adi TEXT NOT NULL, islem_turu TEXT NOT NULL,
        tarih TEXT NOT NULL, notlar TEXT, maliyet REAL DEFAULT 0.0
    )
    """)
    kursor.execute("""
    CREATE TABLE IF NOT EXISTS tarla_gunlukleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, tarla_adi TEXT NOT NULL, nem INTEGER NOT NULL,
        sicaklik INTEGER NOT NULL, karar TEXT NOT NULL, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Mevcut veritabanlarına zarar vermeden yeni sütunları ekliyoruz
    try:
        kursor.execute("ALTER TABLE kullanicilar ADD COLUMN alan_m2 REAL DEFAULT 0.0")
        baglanti.commit()
    except:
        pass
    try:
        kursor.execute("ALTER TABLE tarim_takvimi ADD COLUMN tarla_adi TEXT DEFAULT 'Genel Tarla'")
        baglanti.commit()
    except:
        pass
    try:
        kursor.execute("ALTER TABLE tarla_gunlukleri ADD COLUMN tarla_adi TEXT DEFAULT 'Genel Tarla'")
        baglanti.commit()
    except:
        pass
    try:
        kursor.execute("ALTER TABLE tarim_takvimi ADD COLUMN maliyet REAL DEFAULT 0.0")
        baglanti.commit()
    except:
        pass 
        
    kursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE kullanici_adi = 'yunus'")
    if kursor.fetchone()[0] == 0:
        kursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("yunus", "12345", "Yunus Beyin Pamuk Tarlası (Adana)", 37.00, 35.32, "yonetici_yunus@example.com", "Pamuk", "Admin", "104", "12", 50000.0))
        baglanti.commit()
        
    baglanti.close()

veritabani_otomatik_kur()

# --- SQL YARDIMCI FONKSİYONLARI ---
def sql_kullanici_kontrol(kullanici_adi, sifre):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("SELECT tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2 FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (kullanici_adi, sifre))
    sonuc = kursor.fetchone()
    baglanti.close()
    return sonuc

def sql_kullanicinin_tarlalarini_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("SELECT tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2 FROM kullanicilar WHERE kullanici_adi = ?", (k_adi,))
    tarlalar = kursor.fetchall()
    baglanti.close()
    return tarlalar

def sql_yeni_tarla_ekle(k_adi, sifre, tarla, il, ilce, email, urun, ada, parsel, alan_m2):
    try:
        baglanti = sqlite3.connect("akilli_tarim.db")
        kursor = baglanti.cursor()
        tam_tarla_adi = f"{tarla} ({il.capitalize()} / {ilce.capitalize()})"
        v_enlem, v_boylam = koordinat_bul(il, ilce)
        kursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (k_adi, sifre, tam_tarla_adi, v_enlem, v_boylam, email, urun, "Müşteri/Çiftçi", ada, parsel, alan_m2))
        baglanti.commit()
        baglanti.close()
        return True
    except:
        return False 

def sql_takvim_etkinlik_ekle(k_adi, tarla_adi, islem, tarih, notlar, maliyet):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("INSERT INTO tarim_takvimi (kullanici_adi, tarla_adi, islem_turu, tarih, notlar, maliyet) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, tarla_adi, islem, tarih, notlar, maliyet))
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

def sql_takvim_verileri_getir_ham(k_adi, tarla_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, islem_turu, tarih, notlar, maliyet FROM tarim_takvimi WHERE kullanici_adi = ? AND tarla_adi = ? ORDER BY id DESC", baglanti, params=(k_adi, tarla_adi))
    baglanti.close()
    return df

def sql_tum_tarlalarin_takvimini_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT tarla_adi as 'Tarla', islem_turu as 'Faaliyet', tarih as 'Tarih', maliyet as 'Maliyet (TL)', notlar as 'Durum' FROM tarim_takvimi WHERE kullanici_adi = ? ORDER BY id DESC", baglanti, params=(k_adi,))
    baglanti.close()
    return df

def sql_analiz_kaydet(k_adi, tarla_adi, nem, sicaklik, karar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("INSERT INTO tarla_gunlukleri (kullanici_adi, tarla_adi, nem, sicaklik, karar) VALUES (?, ?, ?, ?, ?)", (k_adi, tarla_adi, nem, sicaklik, karar))
    baglanti.commit()
    baglanti.close()

def sql_analizleri_getir(k_adi, tarla_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT nem, sicaklik, karar, tarih FROM tarla_gunlukleri WHERE kullanici_adi = ? AND tarla_adi = ? ORDER BY id DESC LIMIT 50", baglanti, params=(k_adi, tarla_adi))
    baglanti.close()
    return df

def sql_tum_tarlalarin_gunluklerini_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT tarla_adi as 'Tarla', nem as 'Nem (%)', sicaklik as 'Sıcaklık (°C)', karar as 'Karar', tarih as 'Tarih' FROM tarla_gunlukleri WHERE kullanici_adi = ? ORDER BY id DESC LIMIT 50", baglanti, params=(k_adi,))
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
            st.markdown("<p style='text-align: center; color: gray;'>Log in or create a new farmer account.</p>", unsafe_allow_html=True)
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
                    st.subheader("Yeni İşletme / Çiftçi Kaydı")
                    k_adi = st.text_input("Kullanıcı Adı (*)")
                    k_sifre = st.text_input("Şifre (*)", type="password")
                    k_email = st.text_input("E-Posta Adresi (*)")
                    st.write("**📍 İlk Tarlanızın Lokasyon ve Alan Bilgileri**")
                else:
                    st.subheader("New Enterprise / Farmer Registration")
                    k_adi = st.text_input("Username (*)")
                    k_sifre = st.text_input("Password (*)", type="password")
                    k_email = st.text_input("Email Address (*)")
                    st.write("**📍 First Field Location & Area Information**")
                
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    k_il = st.text_input("İl / State (*)")
                    k_ada = st.text_input("Ada No / Block (*)")
                    k_alan = st.number_input("Arazi Büyüklüğü / Field Size (m²)", min_value=0.0, step=100.0, value=1000.0)
                with col_k2:
                    k_ilce = st.text_input("İlçe / City (*)")
                    k_parsel = st.text_input("Parsel No / Parcel (*)")
                    k_tarla = st.text_input("Tarla Adı / Farm Name (Örn: Ova Parsel)")
                    
                urunler = ["Pamuk", "Zeytin", "Buğday", "Mısır", "Ayçiçeği", "Narenciye", "Domates", "Diğer"] if secilen_dil == "TR" else ["Cotton", "Olive", "Wheat", "Corn", "Sunflower", "Citrus", "Tomato", "Other"]
                k_urun = st.selectbox("Yetiştirilen Ana Mahsul / Main Crop", urunler)
                
                kayit_buton = st.form_submit_button("✅ Hesabı Oluştur", use_container_width=True)
                
                if kayit_buton:
                    if k_adi and k_sifre and k_email and k_il and k_ilce and k_ada and k_parsel and k_tarla:
                        with st.spinner("Kayıt oluşturuluyor..."):
                            sonuc = sql_yeni_tarla_ekle(k_adi, k_sifre, k_tarla, k_il, k_ilce, k_email, k_urun, k_ada, k_parsel, float(k_alan))
                        if sonuc:
                            st.success("🎉 Kayıt başarılı! Giriş yapabilirsiniz.")
                        else:
                            st.error("⚠️ Kayıt oluşturulamadı!")
                    else:
                        st.warning("Zorunlu alanları doldurun.")

# --- ANA PANEL VE ÇOKLU TARLA / GENEL RAPOR MENÜSÜ ---
else:
    kullanici = st.session_state["aktif_kullanici"]
    tarlalar_listesi = sql_kullanicinin_tarlalarini_getir(kullanici)
    
    st.sidebar.markdown(f"👤 **{kullanici.upper()}**")
    st.sidebar.markdown("---")
    
    menu_secenekleri = [_t("genel_merkez")] + [t[0] for t in tarlalar_listesi] + [_t("yeni_tarla_ekle")]
    aktif_secim = st.sidebar.radio("📌 Arazi / Rapor Yönetimi", menu_secenekleri)
    
    st.sidebar.markdown("---")
    if st.sidebar.button(_t("cikis_yap"), type="primary", use_container_width=True):
        st.session_state["giris_yapildi"] = False
        st.session_state["aktif_kullanici"] = ""
        st.session_state["kullanici_bilgileri"] = None
        st.rerun()

    # ==========================================
    # 1. SEÇENEK: GENEL TARLA RAPOR MERKEZİ
    # ==========================================
    if aktif_secim == _t("genel_merkez"):
        st.subheader(f"🏠 Genel Tarla Rapor Merkezi | Tüm Arazilerin Özeti")
        
        toplam_alan = sum(t[8] for t in tarlalar_listesi) if tarlalar_listesi else 0.0
        
        st.caption(f"İşletme Sahibi: {kullanici.upper()} | Toplam Kayıtlı Arazi: {len(tarlalar_listesi)} | Toplam Alan: {toplam_alan:,.0f} m²")
        st.markdown("---")
        
        tum_takvim = sql_tum_tarlalarin_takvimini_getir(kullanici)
        toplam_sirket_gideri = tum_takvim['Maliyet (TL)'].sum() if not tum_takvim.empty else 0.0
        
        baz_getiri = {"Pamuk": 150000, "Zeytin": 200000, "Buğday": 80000, "Mısır": 120000, "Ayçiçeği": 95000, "Narenciye": 180000, "Domates": 110000, "Cotton": 150000, "Olive": 200000, "Wheat": 80000, "Corn": 120000, "Sunflower": 95000, "Citrus": 180000, "Tomato": 110000}
        
        toplam_tahmini_gelir = sum(baz_getiri.get(t[4], 100000) for t in tarlalar_listesi)
        genel_net_kar = toplam_tahmini_gelir - toplam_sirket_gideri

        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric(label="Toplam Arazi", value=f"{len(tarlalar_listesi)} Adet")
        rc2.metric(label="Toplam İşletme Gideri", value=f"₺ {toplam_sirket_gideri:,.2f}")
        rc3.metric(label="Toplam Tahmini Gelir", value=f"₺ {toplam_tahmini_gelir:,.2f}")
        rc4.metric(label="Genel Beklenen Kâr", value=f"₺ {genel_net_kar:,.2f}", delta="Kârlı" if genel_net_kar > 0 else "Risk")

        st.markdown("---")
        st.subheader("📋 Kayıtlı Tüm Arazilerinizin Listesi")
        tarlalar_df = pd.DataFrame(tarlalar_listesi, columns=["Tarla Adı", "Enlem", "Boylam", "E-posta", "Mahsul", "Rol", "Ada", "Parsel", "Alan (m²)"])
        st.dataframe(tarlalar_df[["Tarla Adı", "Mahsul", "Alan (m²)", "Ada", "Parsel"]], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📈 Tüm Arazilerden Son Sensör Akışı")
        tum_gunlukler = sql_tum_tarlalarin_gunluklerini_getir(kullanici)
        if not tum_gunlukler.empty:
            st.dataframe(tum_gunlukler, use_container_width=True, hide_index=True)
        else:
            st.info("Kayıtlı analiz bulunmuyor.")

    # ==========================================
    # 2. SEÇENEK: YENİ TARLA EKLEME EKRANI
    # ==========================================
    elif aktif_secim == _t("yeni_tarla_ekle"):
        st.subheader(f"➕ İşletmenize Yeni Bir Arazi / Tarla Ekleyin")
        st.caption("Yeni tarlanızın konumunu ve mahsul türünü girerek anında akıllı takibe başlayın.")
        st.markdown("---")
        
        with st.form("yeni_tarla_ekleme_formu"):
            col_y1, col_y2 = st.columns(2)
            with col_y1:
                y_il = st.text_input("İl / State (*)")
                y_ada = st.text_input("Ada No / Block (*)")
                y_alan = st.number_input("Arazi Büyüklüğü / Field Size (m²)", min_value=0.0, step=100.0, value=1000.0)
            with col_y2:
                y_ilce = st.text_input("İlçe / City (*)")
                y_parsel = st.text_input("Parsel No / Parcel (*)")
                y_tarla_adi = st.text_input("Tarla Adı (Örn: Güney Çorak) (*)")
                
            urunler = ["Pamuk", "Zeytin", "Buğday", "Mısır", "Ayçiçeği", "Narenciye", "Domates", "Diğer"] if secilen_dil == "TR" else ["Cotton", "Olive", "Wheat", "Corn", "Sunflower", "Citrus", "Tomato", "Other"]
            y_urun = st.selectbox("Yetiştirilen Mahsul", urunler)
                
            y_email = tarlalar_listesi[0][3] if tarlalar_listesi else "kurumsal@tarim.com"
            y_sifre = "12345" 
            
            if st.form_submit_button("🚀 Yeni Tarlayı Sisteme Kaydet", use_container_width=True):
                if y_il and y_ilce and y_ada and y_parsel and y_tarla_adi:
                    with st.spinner("Yeni arazi koordinatları hesaplanıyor..."):
                        sonuc = sql_yeni_tarla_ekle(kullanici, y_sifre, y_tarla_adi, y_il, y_ilce, y_email, y_urun, y_ada, y_parsel, float(y_alan))
                    if sonuc:
                        st.success("🎉 Yeni tarla başarıyla eklendi! Sol menüden seçerek yönetebilirsiniz.")
                        st.rerun()
                    else:
                        st.error("Tarla eklenirken bir hata oluştu.")
                else:
                    st.warning("Lütfen tüm zorunlu alanları doldurun.")

    # ==========================================
    # 3. SEÇENEK: BELİRLİ BİR TARLANIN DETAY PANELİ
    # ==========================================
    else:
        aktif_tarla_verisi = next((t for t in tarlalar_listesi if t[0] == aktif_secim), None)
        
        if aktif_tarla_verisi:
            tarla_adi, t_enlem, t_boylam, m_email, urun_turu, rol, ada, parsel, alan_m2 = aktif_tarla_verisi
            
            st.subheader(f"🌾 Arazi Kontrol Merkezi | {tarla_adi.upper()}")
            st.caption(f"Yönetici: {kullanici.upper()} | Ada/Parsel: {ada}/{parsel} | Büyüklük: {alan_m2:,.0f} m² | Mahsul: {urun_turu}")
            st.markdown("---")

            if "aktif_tarla_nemi" not in st.session_state or st.session_state.get("secili_tarla") != tarla_adi:
                st.session_state["aktif_tarla_nemi"] = akilli_nem_simulasyonu()
                gercek_isi = gercek_hava_durumu_getir(t_enlem, t_boylam)
                st.session_state["aktif_tarla_sicaklik"] = gercek_isi if gercek_isi is not None else random.randint(22, 38)
                st.session_state["secili_tarla"] = tarla_adi
                
            toprak_nemi = st.session_state["aktif_tarla_nemi"]
            canli_sicaklik = st.session_state["aktif_tarla_sicaklik"]

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

            # Alarm
            if ai_durum == "error" or h_skor >= 75:
                st.error(_t("alarm_kritik", email=m_email))
                if "alarm_gosterildi" not in st.session_state or not st.session_state["alarm_gosterildi"]:
                    st.toast("📲 SMS İLETİLDİ", icon="🚨")
                    st.session_state["alarm_gosterildi"] = True
            elif ai_durum == "warning" or h_skor >= 40:
                st.warning(_t("alarm_uyari", email=m_email))
                if "alarm_gosterildi" not in st.session_state or not st.session_state["alarm_gosterildi"]:
                    st.toast("📧 E-Posta İLETİLDİ", icon="⚠️")
                    st.session_state["alarm_gosterildi"] = True
            else:
                st.info(_t("alarm_normal", email=m_email))
                st.session_state["alarm_gosterildi"] = False

            # HTML Rapor ve Buton
            col_rp_bos, col_rp_buton = st.columns([7, 3])
            with col_rp_buton:
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
                </style>
                </head>
                <body>
                    <div class="header">
                        <h2>AI Smart Agri Platform Report</h2>
                        <p>Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    </div>
                    <table class="info-table">
                        <tr><th>User / Sahibi</th><td>{kullanici.upper()}</td></tr>
                        <tr><th>Field / Tarla</th><td>{tarla_adi.upper()}</td></tr>
                        <tr><th>Area / Alan</th><td>{alan_m2:,.0f} m²</td></tr>
                        <tr><th>Crop / Mahsul</th><td>{urun_turu}</td></tr>
                        <tr><th>Temp / Sıcaklık</th><td>{canli_sicaklik} °C</td></tr>
                        <tr><th>Moisture / Nem</th><td>%{toprak_nemi}</td></tr>
                    </table>
                </body>
                </html>
                """
                st.download_button(_t("rapor_indir"), data=html_rapor, file_name=f"{tarla_adi}_rapor.html", mime="text/html", use_container_width=True)

            st.markdown("---")
            
            # Finansal
            df_takvim_ham = sql_takvim_verileri_getir_ham(kullanici, tarla_adi)
            toplam_gider = df_takvim_ham['maliyet'].sum() if not df_takvim_ham.empty and 'maliyet' in df_takvim_ham.columns else 0.0
            baz_getiri = {"Pamuk": 150000, "Zeytin": 200000, "Buğday": 80000, "Mısır": 120000, "Ayçiçeği": 95000, "Narenciye": 180000, "Domates": 110000, "Cotton": 150000, "Olive": 200000, "Wheat": 80000, "Corn": 120000, "Sunflower": 95000, "Citrus": 180000, "Tomato": 110000}
            tahmini_gelir = baz_getiri.get(urun_turu, 100000)
            beklenen_kar = tahmini_gelir - toplam_gider

            col_box1, col_box2, col_box3 = st.columns(3)
            with col_box1:
                st.subheader(_t("canli_metrikler"), divider="blue")
                st.write(_t("hava_sicakligi"))
                st.subheader(f"{canli_sicaklik} °C")
                st.write(_t("toprak_nemi"))
                st.subheader(f"%{toprak_nemi}")
                
                if ai_durum == "error": st.error(f"{ai_mesaj}")
                elif ai_durum == "warning": st.warning(f"{ai_mesaj}")
                else: st.success(f"{ai_mesaj}")
                    
                st.write(f"🦠 **{_t('hastalik_riski')} ({h_adi})**")
                st.progress(h_skor / 100)
                
                if st.button(_t("analizi_gunlukle"), key=f"btn_gunluk_{tarla_adi}", use_container_width=True):
                    sql_analiz_kaydet(kullanici, tarla_adi, int(toprak_nemi), float(canli_sicaklik), ai_mesaj)
                    st.rerun()

            with col_box2:
                st.subheader(_t("cografi_konum"), divider="green")
                st.map(pd.DataFrame({'lat': [t_enlem], 'lon': [t_boylam]}), size=14, zoom=11)
                st.caption(f"📍 Enlem: {t_enlem} | Boylam: {t_boylam} ({tarla_adi})")

            with col_box3:
                df_kayitlar = sql_analizleri_getir(kullanici, tarla_adi)
                tasarruf_orani = (df_kayitlar['karar'].str.contains("NORMAL").sum() / len(df_kayitlar)) if not df_kayitlar.empty else 0.0
                
                st.subheader(_t("verimlilik_raporu"), divider="orange")
                st.write(_t("su_tasarrufu"))
                st.subheader(f"%{int(tasarruf_orani * 100)}")
                st.progress(tasarruf_orani)
                
                if not df_kayitlar.empty:
                    st.line_chart(df_kayitlar.iloc[::-1].reset_index()['nem'])

            st.markdown("---")
            st.subheader(f"💰 {tarla_adi} - Finansal Analiz & Bütçe", divider="red")
            fc1, fc2, fc3 = st.columns(3)
            fc1.metric(label=_t("toplam_gider"), value=f"₺ {toplam_gider:,.2f}")
            fc2.metric(label=f"{_t('tahmini_gelir')} ({urun_turu})", value=f"₺ {tahmini_gelir:,.2f}")
            fc3.metric(label=_t("net_kar"), value=f"₺ {beklenen_kar:,.2f}", delta="Kârlı" if beklenen_kar > 0 else "Zarar")

            st.markdown("---")
            st.subheader(f"📅 {tarla_adi} - Dijital Tarım Ajandası", divider="gray")
            
            ac1, ac2 = st.columns([1, 2.5])
            with ac1:
                with st.form(f"form_gorev_{tarla_adi}"):
                    y_islem = st.selectbox("İşlem Türü:", ["Gübreleme", "İlaçlama", "Hasat", "Sulama", "İşçi Maliyeti", "Diğer"])
                    y_tarih = st.date_input("Tarih:")
                    y_maliyet = st.number_input("Maliyet (TL):", min_value=0.0, step=100.0)
                    y_not = st.text_input("Not:", value="Planlandı")
                    
                    if st.form_submit_button("🗓️ Tarlaya İşle", use_container_width=True):
                        sql_takvim_etkinlik_ekle(kullanici, tarla_adi, y_islem, str(y_tarih), y_not, float(y_maliyet))
                        st.rerun()
                        
            with ac2:
                if not df_takvim_ham.empty:
                    st.dataframe(df_takvim_ham[["islem_turu", "tarih", "maliyet", "notlar"]].rename(columns={"islem_turu":"Faaliyet", "tarih":"Tarih", "maliyet":"Maliyet", "notlar":"Durum"}), use_container_width=True, hide_index=True)
                    
                    g_secenekleri = df_takvim_ham.apply(lambda r: f"ID:{r['id']} | {r['islem_turu']} ({r['tarih']})", axis=1).tolist()
                    sec_g = st.selectbox("Düzenlenecek Görev:", g_secenekleri, key=f"sel_{tarla_adi}")
                    if sec_g:
                        s_id = int(sec_g.split("|")[0].replace("ID:", "").strip())
                        if st.button("🗑️ Bu Görevi Sil", key=f"del_{s_id}", use_container_width=True):
                            sql_takvim_etkinlik_sil(s_id)
                            st.rerun()
