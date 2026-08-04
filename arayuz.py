# ==============================================================================
# PROJE: AI Destekli Akıllı Tarım Platformu (AI ZİRAAT ASİSTANI EKLENDİ)
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
        "depo_yonetimi": "📦 Depo ve Stok Yönetimi",
        "ai_asistan": "🤖 AI Ziraat Asistanı",
        "yeni_tarla_ekle": "➕ Yeni Arazi / Tarla Ekle",
        "tarla_ayarlari": "⚙️ Tarla Bilgilerini Düzenle / Ayarlar",
        "finans_ayarlari": "📈 Finansal Parametreler & Kredi Ayarları",
        "degisiklik_kaydet": "💾 Değişiklikleri Kaydet",
        "guncelleme_basarili": "🎉 Bilgiler başarıyla güncellendi!"
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
        "depo_yonetimi": "📦 Warehouse & Stock Mgmt",
        "ai_asistan": "🤖 AI Agri Assistant",
        "yeni_tarla_ekle": "➕ Add New Field / Land",
        "tarla_ayarlari": "⚙️ Edit Field Information / Settings",
        "finans_ayarlari": "📈 Financial Parameters & Loan Settings",
        "degisiklik_kaydet": "💾 Save Changes",
        "guncelleme_basarili": "🎉 Information successfully updated!"
    }
}

st.sidebar.title("🌍 Language / Dil")
secilen_dil = st.sidebar.radio("Select Interface Language:", ["TR", "EN"])

def _t(anahtar, **kwargs):
    metin = dil_sozlugu[secilen_dil].get(anahtar, anahtar)
    if kwargs: return metin.format(**kwargs)
    return metin

# --- API FONKSİYONLARI ---
def koordinat_bul(il, ilce):
    try:
        adres = f"{ilce}, {il}, Turkey"
        url = f"https://nominatim.openstreetmap.org/search?q={adres}&format=json&limit=1"
        headers = {'User-Agent': 'AkilliTarimProjesi/1.0'} 
        cevap = requests.get(url, headers=headers, timeout=5)
        veri = cevap.json()
        if len(veri) > 0: return float(veri[0]['lat']), float(veri[0]['lon'])
        else: return 39.0, 35.0
    except: return 39.0, 35.0

def gercek_hava_durumu_getir(enlem, boylam):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={enlem}&longitude={boylam}&current_weather=true"
        cevap = requests.get(url, timeout=5)
        return cevap.json()["current_weather"]["temperature"]
    except: return None 

def akilli_nem_simulasyonu():
    saat = datetime.now().hour
    if 6 <= saat < 12: return random.randint(40, 70)
    elif 12 <= saat < 18: return random.randint(15, 35)
    elif 18 <= saat < 22: return random.randint(30, 50)
    else: return random.randint(50, 75)

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

# --- YENİ: AI SOHBET BOTU MANTIĞI ---
def ai_sohbet_cevabi_uret(mesaj, dil="TR"):
    mesaj = mesaj.lower()
    
    if dil == "TR":
        if "pamuk" in mesaj and ("örümcek" in mesaj or "böcek" in mesaj):
            return "Pamukta kırmızı örümcek (Tetranychus urticae) ciddi verim kaybı yapar. Abamectin veya Spiromesifen etken maddeli akarisitler kullanmanızı öneririm. İlaçlamayı sabah erken veya akşam serinliğinde yapmalısınız."
        elif "pas" in mesaj or "sarı" in mesaj or "buğday" in mesaj:
            return "Buğdayda pas hastalığı genelde yüksek nemde ortaya çıkar. Tebuconazole veya Epoxiconazole içeren sistemik fungisitler etkilidir. Lütfen tarlada homojen bir ilaçlama yapın."
        elif "gübre" in mesaj or "azot" in mesaj:
            return "Gübreleme bitkinin fenolojik evresine göre değişir. Genel kural olarak; fosfor ve potasyumu taban gübresi olarak ekim öncesi, azotlu gübreleri ise bitkinin büyüme döneminde parçalar halinde vermelisiniz."
        elif "zeytin" in mesaj and "sinek" in mesaj:
            return "Zeytin sineğine karşı vuruk oranını kontrol edin. Eğer %1-2'yi geçmişse Spinosad veya Deltamethrin içeren spesifik ilaçlarla zehirli yem kısmi dal ilaçlaması yapabilirsiniz."
        elif "merhaba" in mesaj or "selam" in mesaj:
            return "Merhaba! Ben yapay zeka destekli ziraat asistanınızım. Size hastalıklar, gübreleme, ilaçlama veya bütçe konularında nasıl yardımcı olabilirim?"
        else:
            return "Bu harika bir soru. Sistemimizdeki zirai veritabanına göre, arazinizin spesifik toprak yapısını göz önünde bulundurarak lokal bir uzmana danışmanız veya sistem üzerinden toprak analizi görevini ajandaya eklemeniz en doğrusu olacaktır. Başka bir konuda yardımcı olabilir miyim?"
    else:
        if "cotton" in mesaj and ("mite" in mesaj or "spider" in mesaj):
            return "For spider mites in cotton, I recommend acaricides with Abamectin or Spiromesifen. Apply during the cool hours of early morning or evening."
        elif "rust" in mesaj or "wheat" in mesaj:
            return "Wheat rust disease thrives in high humidity. Systemic fungicides containing Tebuconazole or Epoxiconazole are very effective. Ensure uniform spraying."
        elif "fertilizer" in mesaj or "nitrogen" in mesaj:
            return "Fertilization depends on the crop's phenological stage. Generally, apply phosphorus and potassium as base fertilizer before planting, and split nitrogen applications during the growing season."
        elif "hello" in mesaj or "hi" in mesaj:
            return "Hello! I am your AI-powered agricultural assistant. How can I help you today with crop diseases, fertilizers, or budget planning?"
        else:
            return "That's a great question. Based on our agricultural database, I recommend adding a 'Soil Analysis' task to your agenda for precise answers. Is there anything else I can help with?"

# --- VERİTABANI KURULUMU VE FONKSİYONLARI ---
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
    
    for kolon in ["alan_m2", "rekolte_kg", "birim_fiyat", "devlet_destegi", "kredi_anapara", "kredi_faiz"]:
        try: kursor.execute(f"ALTER TABLE kullanicilar ADD COLUMN {kolon} REAL DEFAULT 0.0"); baglanti.commit()
        except: pass
    try: kursor.execute("ALTER TABLE tarim_takvimi ADD COLUMN tarla_adi TEXT DEFAULT 'Genel Tarla'"); baglanti.commit()
    except: pass
    try: kursor.execute("ALTER TABLE tarim_takvimi ADD COLUMN maliyet REAL DEFAULT 0.0"); baglanti.commit()
    except: pass 
    try: kursor.execute("ALTER TABLE tarim_takvimi ADD COLUMN maliyet_kategorisi TEXT DEFAULT 'Diğer'"); baglanti.commit()
    except: pass 
    try: kursor.execute("ALTER TABLE tarla_gunlukleri ADD COLUMN tarla_adi TEXT DEFAULT 'Genel Tarla'"); baglanti.commit()
    except: pass
        
    kursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE kullanici_adi = 'yunus'")
    if kursor.fetchone()[0] == 0:
        kursor.execute("""INSERT INTO kullanicilar 
        (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("yunus", "12345", "Yunus Beyin Pamuk Tarlası (Adana)", 37.00, 35.32, "yonetici_yunus@example.com", "Pamuk", "Admin", "104", "12", 50000.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        baglanti.commit()
    baglanti.close()

veritabani_otomatik_kur()

def sql_kullanici_kontrol(k_adi, sifre):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("SELECT tarla_adi FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (k_adi, sifre))
    sonuc = kursor.fetchone()
    baglanti.close()
    return True if sonuc else False

def sql_kullanicinin_tarlalarini_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("SELECT tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz FROM kullanicilar WHERE kullanici_adi = ?", (k_adi,))
    tarlalar = kursor.fetchall()
    baglanti.close()
    return tarlalar

def sql_yeni_tarla_ekle(k_adi, sifre, tarla, il, ilce, email, urun, ada, parsel, alan_m2):
    try:
        baglanti = sqlite3.connect("akilli_tarim.db")
        kursor = baglanti.cursor()
        tam_tarla_adi = f"{tarla} ({il.capitalize()} / {ilce.capitalize()})"
        v_enlem, v_boylam = koordinat_bul(il, ilce)
        kursor.execute("""INSERT INTO kullanicilar 
        (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0.0, 0.0, 0.0, 0.0)""",
        (k_adi, sifre, tam_tarla_adi, v_enlem, v_boylam, email, urun, "Müşteri/Çiftçi", ada, parsel, alan_m2))
        baglanti.commit(); baglanti.close()
        return True
    except: return False 

def sql_tarla_guncelle(k_adi, e_tarla, y_tarla, y_urun, y_ada, y_parsel, y_alan, y_enlem, y_boylam, y_rekolte, y_fiyat, y_destek, y_kanapara, y_kfaiz):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("""UPDATE kullanicilar 
        SET tarla_adi=?, urun_turu=?, ada=?, parsel=?, alan_m2=?, enlem=?, boylam=?, rekolte_kg=?, birim_fiyat=?, devlet_destegi=?, kredi_anapara=?, kredi_faiz=?
        WHERE kullanici_adi=? AND tarla_adi=?""", (y_tarla, y_urun, y_ada, y_parsel, y_alan, y_enlem, y_boylam, y_rekolte, y_fiyat, y_destek, y_kanapara, y_kfaiz, k_adi, e_tarla))
    if e_tarla != y_tarla:
        kursor.execute("UPDATE tarim_takvimi SET tarla_adi=? WHERE kullanici_adi=? AND tarla_adi=?", (y_tarla, k_adi, e_tarla))
        kursor.execute("UPDATE tarla_gunlukleri SET tarla_adi=? WHERE kullanici_adi=? AND tarla_adi=?", (y_tarla, k_adi, e_tarla))
    baglanti.commit(); baglanti.close(); return True

def sql_takvim_etkinlik_ekle(k_adi, tarla, islem, tarih, notlar, maliyet, kat):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("INSERT INTO tarim_takvimi (kullanici_adi, tarla_adi, islem_turu, tarih, notlar, maliyet, maliyet_kategorisi) VALUES (?, ?, ?, ?, ?, ?, ?)", (k_adi, tarla, islem, tarih, notlar, maliyet, kat))
    baglanti.commit(); baglanti.close()

def sql_takvim_etkinlik_sil(gorev_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("DELETE FROM tarim_takvimi WHERE id = ?", (gorev_id,))
    baglanti.commit(); baglanti.close()

def sql_takvim_verileri_getir_ham(k_adi, tarla):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, islem_turu, maliyet_kategorisi, tarih, notlar, maliyet FROM tarim_takvimi WHERE kullanici_adi = ? AND tarla_adi = ? ORDER BY id DESC", baglanti, params=(k_adi, tarla))
    baglanti.close(); return df

def sql_analiz_kaydet(k_adi, tarla, nem, sicaklik, karar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("INSERT INTO tarla_gunlukleri (kullanici_adi, tarla_adi, nem, sicaklik, karar) VALUES (?, ?, ?, ?, ?)", (k_adi, tarla, nem, sicaklik, karar))
    baglanti.commit(); baglanti.close()

def sql_analizleri_getir(k_adi, tarla):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT nem, sicaklik, karar, tarih FROM tarla_gunlukleri WHERE kullanici_adi = ? AND tarla_adi = ? ORDER BY id DESC LIMIT 50", baglanti, params=(k_adi, tarla))
    baglanti.close(); return df

def sql_depo_urun_ekle(k_adi, urun_adi, kategori, miktar, birim, kritik):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("INSERT INTO depo_envanter (kullanici_adi, urun_adi, kategori, miktar, birim, kritik_esik) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, urun_adi, kategori, miktar, birim, kritik))
    baglanti.commit(); baglanti.close()

def sql_depo_urun_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, urun_adi, kategori, miktar, birim, kritik_esik FROM depo_envanter WHERE kullanici_adi = ? ORDER BY kategori ASC", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_depo_miktar_guncelle(urun_id, yeni_miktar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("UPDATE depo_envanter SET miktar = ? WHERE id = ?", (yeni_miktar, urun_id))
    baglanti.commit(); baglanti.close()

def sql_depo_urun_tam_guncelle(urun_id, y_ad, y_kat, y_mik, y_birim, y_kritik):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("UPDATE depo_envanter SET urun_adi=?, kategori=?, miktar=?, birim=?, kritik_esik=? WHERE id=?", (y_ad, y_kat, y_mik, y_birim, y_kritik, urun_id))
    baglanti.commit(); baglanti.close()

def sql_depo_urun_sil(urun_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("DELETE FROM depo_envanter WHERE id = ?", (urun_id,))
    baglanti.commit(); baglanti.close()

# --- OTURUM KONTROLÜ ---
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["aktif_kullanici"] = ""

# --- GİRİŞ EKRANI ---
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

# --- ANA PANEL VE ÇOKLU MENÜ ---
else:
    kullanici = st.session_state["aktif_kullanici"]
    tarlalar_listesi = sql_kullanicinin_tarlalarini_getir(kullanici)
    
    st.sidebar.markdown(f"👤 **{kullanici.upper()}**")
    st.sidebar.markdown("---")
    
    # YENİ MENÜ DÜZENİ: AI Asistan eklendi!
    menu_secenekleri = [_t("genel_merkez"), _t("depo_yonetimi"), _t("ai_asistan")] + [t[0] for t in tarlalar_listesi] + [_t("yeni_tarla_ekle")]
    aktif_secim = st.sidebar.radio("📌 Menü / Menu", menu_secenekleri)
    
    st.sidebar.markdown("---")
    if st.sidebar.button(_t("cikis_yap"), type="primary", use_container_width=True):
        st.session_state["giris_yapildi"] = False
        st.session_state["aktif_kullanici"] = ""
        st.rerun()

    # ==========================================
    # 1. YENİ MODÜL: AI ZİRAAT ASİSTANI (CHATBOT)
    # ==========================================
    if aktif_secim == _t("ai_asistan"):
        st.subheader("🤖 Yapay Zeka Destekli Ziraat Mühendisi")
        st.caption("Mahsulünüzdeki hastalıklar, gübreleme takvimi veya verimlilik hakkında tüm sorularınızı sorabilirsiniz." if secilen_dil == "TR" else "Ask any questions about crop diseases, fertilization schedule, or yield efficiency.")
        st.markdown("---")

        # Chat geçmişini oturumda tut
        if "chat_gecmisi" not in st.session_state:
            karsilama = "Merhaba! Tarlalarınızın dijital ziraat mühendisiyim. Hastalıklar veya ilaçlama ile ilgili ne öğrenmek istersiniz?" if secilen_dil == "TR" else "Hello! I'm your digital agricultural engineer. What would you like to know about diseases or treatments?"
            st.session_state["chat_gecmisi"] = [{"rol": "asistan", "icerik": karsilama}]

        # Geçmişi Ekrana Çiz
        for mesaj in st.session_state["chat_gecmisi"]:
            if mesaj["rol"] == "asistan":
                with st.chat_message("assistant", avatar="🤖"): st.markdown(mesaj["icerik"])
            else:
                with st.chat_message("user", avatar="👤"): st.markdown(mesaj["icerik"])

        # Chat Girdi Kutusu (Input)
        mesaj_kutusu = "Sorunuzu buraya yazın... (Örn: Pamukta kırmızı örümcek için ne yapmalıyım?)" if secilen_dil == "TR" else "Type your question here... (e.g. What should I do for spider mites in cotton?)"
        
        if prompt := st.chat_input(mesaj_kutusu):
            # Kullanıcı mesajını ekle
            st.session_state["chat_gecmisi"].append({"rol": "kullanici", "icerik": prompt})
            with st.chat_message("user", avatar="👤"): st.markdown(prompt)

            # Yapay Zeka Cevabını Simüle Et
            with st.chat_message("assistant", avatar="🤖"):
                mesaj_alani = st.empty()
                mesaj_alani.markdown("Yazıyor... ⏳" if secilen_dil == "TR" else "Typing... ⏳")
                time.sleep(1.0) # İnternetten çekiyormuş gibi 1 saniye bekle
                
                # Cevabı al ve ekrana bas
                ai_cevabi = ai_sohbet_cevabi_uret(prompt, secilen_dil)
                mesaj_alani.markdown(ai_cevabi)
                
            st.session_state["chat_gecmisi"].append({"rol": "asistan", "icerik": ai_cevabi})

    # ==========================================
    # 2. DEPO VE STOK YÖNETİMİ
    # ==========================================
    elif aktif_secim == _t("depo_yonetimi"):
        st.subheader(f"📦 Depo ve Envanter Kontrol Merkezi")
        st.caption("Tüm arazilerinizde kullandığınız zirai ilaç, gübre, tohum ve yakıt stoklarınızı buradan yönetin.")
        st.markdown("---")
        
        df_depo = sql_depo_urun_getir(kullanici)
        if not df_depo.empty:
            kritik_urunler = df_depo[df_depo['miktar'] <= df_depo['kritik_esik']]
            if not kritik_urunler.empty:
                st.error("🚨 **KRİTİK STOK UYARISI:** Aşağıdaki ürünlerin stoğu tükenmek üzere, acil tedarik planlayın!")
                for index, row in kritik_urunler.iterrows():
                    st.warning(f"⚠️ {row['urun_adi']} ({row['kategori']}) - Kalan: {row['miktar']} {row['birim']}")
                st.markdown("---")

        col_d1, col_d2 = st.columns([1, 2.5])
        with col_d1:
            with st.form("yeni_stok_formu"):
                st.write("**Yeni Ürün / Stok Ekle**")
                d_urun_adi = st.text_input("Ürün Markası / Adı:")
                d_kategori = st.selectbox("Kategori:", ["Zirai İlaç", "Gübre", "Tohum/Fide", "Mazot/Yakıt", "Ambalaj", "Diğer"])
                c_d_1, c_d_2 = st.columns(2)
                with c_d_1: d_miktar = st.number_input("Miktar:", min_value=0.0, value=0.0)
                with c_d_2: d_birim = st.selectbox("Birim:", ["kg", "Litre", "Torba", "Adet", "Ton"])
                d_kritik = st.number_input("Kritik Eşik (Uyarı Ver):", min_value=0.0, value=10.0)
                
                if st.form_submit_button("📦 Depoya Ekle", use_container_width=True):
                    if d_urun_adi:
                        sql_depo_urun_ekle(kullanici, d_urun_adi, d_kategori, float(d_miktar), d_birim, float(d_kritik))
                        st.rerun()

        with col_d2:
            st.write("**Mevcut Depo Durumu**")
            if not df_depo.empty:
                df_gosterim = df_depo.rename(columns={"urun_adi":"Ürün Adı", "kategori":"Kategori", "miktar":"Kalan Miktar", "birim":"Birim", "kritik_esik":"Uyarı Eşiği"})
                st.dataframe(df_gosterim[["Ürün Adı", "Kategori", "Kalan Miktar", "Birim", "Uyarı Eşiği"]], use_container_width=True, hide_index=True)
                
                with st.expander("⚙️ Stok Bilgilerini Düzenle / Güncelle", expanded=False):
                    stok_secenekleri = df_depo.apply(lambda r: f"ID:{r['id']} | {r['urun_adi']}", axis=1).tolist()
                    guncellenecek_stok = st.selectbox("Düzenlenecek Ürünü Seçin:", stok_secenekleri, key="guncelle_stok_box")
                    if guncellenecek_stok:
                        s_id = int(guncellenecek_stok.split("|")[0].replace("ID:", "").strip())
                        secilen_urun = df_depo[df_depo['id'] == s_id].iloc[0]
                        with st.form("stok_guncelleme_formu"):
                            col_g1, col_g2 = st.columns(2)
                            with col_g1:
                                yeni_ad = st.text_input("Yeni Ürün Adı:", value=secilen_urun['urun_adi'])
                                yeni_miktar = st.number_input("Yeni Miktar:", value=float(secilen_urun['miktar']), min_value=0.0)
                            with col_g2:
                                kategoriler = ["Zirai İlaç", "Gübre", "Tohum/Fide", "Mazot/Yakıt", "Ambalaj", "Diğer"]
                                yeni_kat = st.selectbox("Yeni Kategori:", kategoriler, index=kategoriler.index(secilen_urun['kategori']) if secilen_urun['kategori'] in kategoriler else 0)
                                birimler = ["kg", "Litre", "Torba", "Adet", "Ton"]
                                yeni_birim = st.selectbox("Yeni Birim:", birimler, index=birimler.index(secilen_urun['birim']) if secilen_urun['birim'] in birimler else 0)
                            yeni_kritik = st.number_input("Yeni Kritik Eşik:", value=float(secilen_urun['kritik_esik']), min_value=0.0)
                            if st.form_submit_button("💾 Bilgileri Güncelle", use_container_width=True):
                                sql_depo_urun_tam_guncelle(s_id, yeni_ad, yeni_kat, yeni_miktar, yeni_birim, yeni_kritik)
                                st.rerun()

                with st.expander("Gelişmiş Seçenekler: Ürünü Depodan Sil", expanded=False):
                    sil_stok = st.selectbox("Tamamen Silinecek Ürünü Seçin:", stok_secenekleri, key="sil_stok_box")
                    if st.button("🗑️ Ürünü Kalıcı Olarak Sil", type="primary"):
                        if sil_stok:
                            sql_depo_urun_sil(int(sil_stok.split("|")[0].replace("ID:", "").strip()))
                            st.rerun()
            else:
                st.info("Deponuz şu an boş.")

    # ==========================================
    # 3. YENİ TARLA EKLEME EKRANI
    # ==========================================
    elif aktif_secim == _t("yeni_tarla_ekle"):
        st.subheader(f"➕ İşletmenize Yeni Bir Arazi / Tarla Ekleyin")
        st.markdown("---")
        with st.form("yeni_tarla_ekleme_formu"):
            col_y1, col_y2 = st.columns(2)
            with col_y1:
                y_il = st.text_input("İl / State (*)")
                y_ada = st.text_input("Ada No / Block")
                y_alan = st.number_input("Alan / Size (m²)", min_value=0.0, step=100.0, value=1000.0)
            with col_y2:
                y_ilce = st.text_input("İlçe / City (*)")
                y_parsel = st.text_input("Parsel No / Parcel")
                y_tarla_adi = st.text_input("Tarla Adı (Örn: Kuzey Parsel) (*)")
            urunler = ["Pamuk", "Zeytin", "Buğday", "Mısır", "Ayçiçeği", "Narenciye", "Domates", "Diğer"] if secilen_dil == "TR" else ["Cotton", "Olive", "Wheat", "Corn", "Sunflower", "Citrus", "Tomato", "Other"]
            y_urun = st.selectbox("Mahsul / Crop", urunler)
            if st.form_submit_button("🚀 Tarlayı Ekle", use_container_width=True):
                if y_il and y_ilce and y_tarla_adi:
                    sql_yeni_tarla_ekle(kullanici, "12345", y_tarla_adi, y_il, y_ilce, tarlalar_listesi[0][3], y_urun, y_ada, y_parsel, float(y_alan))
                    st.rerun()

    # ==========================================
    # 4. GENEL TARLA RAPOR MERKEZİ (ÖZET)
    # ==========================================
    elif aktif_secim == _t("genel_merkez"):
        st.subheader(f"🏠 ERP Genel Rapor Merkezi | İşletme Özeti")
        st.markdown("---")
        
        toplam_sirket_gideri = 0.0
        toplam_tahmini_gelir = 0.0
        toplam_destek = 0.0
        toplam_kredi_odeme = 0.0
        
        for t in tarlalar_listesi:
            toplam_tahmini_gelir += (t[9] * t[10])
            toplam_destek += t[11]
            toplam_kredi_odeme += (t[12] + (t[12] * t[13] / 100))
            df_g = sql_takvim_verileri_getir_ham(kullanici, t[0])
            if not df_g.empty: toplam_sirket_gideri += df_g['maliyet'].sum()
                
        genel_net_kar = toplam_tahmini_gelir + toplam_destek - toplam_sirket_gideri - toplam_kredi_odeme

        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric(label="Toplam Gelir + Destek", value=f"₺ {(toplam_tahmini_gelir + toplam_destek):,.2f}")
        rc2.metric(label="Operasyonel Gider", value=f"₺ {toplam_sirket_gideri:,.2f}")
        rc3.metric(label="Banka/Kredi Ödemeleri", value=f"₺ {toplam_kredi_odeme:,.2f}")
        rc4.metric(label="İşletme Net Kârı", value=f"₺ {genel_net_kar:,.2f}", delta="Kârlı" if genel_net_kar > 0 else "Zarar")

        st.write("---")
        tarlalar_df = pd.DataFrame(tarlalar_listesi, columns=["Tarla Adı", "En", "Boy", "Mail", "Mahsul", "Rol", "Ada", "Parsel", "Alan(m²)", "Hasat(kg)", "Fiyat(TL)", "Destek(TL)", "Kredi Ana", "Kredi Faiz"])
        st.dataframe(tarlalar_df[["Tarla Adı", "Mahsul", "Alan(m²)", "Hasat(kg)", "Fiyat(TL)", "Destek(TL)"]], use_container_width=True, hide_index=True)

    # ==========================================
    # 5. TARLA DETAY VE FİNANS (ERP) PANELİ
    # ==========================================
    else:
        aktif_tarla_verisi = next((t for t in tarlalar_listesi if t[0] == aktif_secim), None)
        if aktif_tarla_verisi:
            tarla_adi, t_enlem, t_boylam, m_email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz = aktif_tarla_verisi
            
            st.subheader(f"{_t('baslik')} | {tarla_adi.upper()}")
            st.caption(f"Yönetici: {kullanici.upper()} | Ada/Parsel: {ada}/{parsel} | Büyüklük: {alan_m2:,.0f} m² | Mahsul: {urun_turu}")
            
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
                        
                        if st.form_submit_button(_t("degisiklik_kaydet"), use_container_width=True):
                            sql_tarla_guncelle(kullanici, tarla_adi, g_tarla_adi, g_urun, g_ada, g_parsel, float(g_alan), t_enlem, t_boylam, float(rekolte_kg), float(birim_fiyat), float(devlet_destegi), float(kredi_anapara), float(kredi_faiz))
                            st.rerun()

            with col_finans:
                with st.expander(_t("finans_ayarlari"), expanded=False):
                    with st.form(f"g_finans_{tarla_adi}"):
                        c_f1, c_f2 = st.columns(2)
                        with c_f1: g_rekolte = st.number_input("Hasat Beklentisi (kg):", value=float(rekolte_kg), min_value=0.0)
                        with c_f2: g_fiyat = st.number_input("Satış Fiyatı (TL/kg):", value=float(birim_fiyat), min_value=0.0)
                        g_destek = st.number_input("Devlet Desteği / Hibe (TL):", value=float(devlet_destegi), min_value=0.0)
                        
                        st.write("---")
                        c_k1, c_k2 = st.columns(2)
                        with c_k1: g_kanapara = st.number_input("Çekilen Kredi (TL):", value=float(kredi_anapara), min_value=0.0)
                        with c_k2: g_kfaiz = st.number_input("Faiz Oranı (%):", value=float(kredi_faiz), min_value=0.0)
                        
                        if st.form_submit_button(_t("degisiklik_kaydet"), use_container_width=True):
                            sql_tarla_guncelle(kullanici, tarla_adi, tarla_adi, urun_turu, ada, parsel, float(alan_m2), t_enlem, t_boylam, float(g_rekolte), float(g_fiyat), float(g_destek), float(g_kanapara), float(g_kfaiz))
                            st.rerun()

            st.markdown("---")
            if "aktif_tarla_nemi" not in st.session_state or st.session_state.get("secili_tarla") != tarla_adi:
                st.session_state["aktif_tarla_nemi"] = akilli_nem_simulasyonu()
                st.session_state["aktif_tarla_sicaklik"] = gercek_hava_durumu_getir(t_enlem, t_boylam) or random.randint(22, 38)
                st.session_state["secili_tarla"] = tarla_adi
                
            tn, ts = st.session_state["aktif_tarla_nemi"], st.session_state["aktif_tarla_sicaklik"]

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.subheader(_t("canli_metrikler"), divider="blue")
                st.write(f"🌡️ Sıcaklık: **{ts} °C** | 💧 Toprak Nemi: **%{tn}**")
                ai_mesaj = _t("ai_kuru") if tn < 30 and ts > 30 else _t("ai_uyari") if tn < 30 else _t("ai_normal")
                st.info(f"**AI VANA:** {ai_mesaj}")
                
            with col_s2:
                h_adi, h_skor, h_mesaj = ai_hastalik_risk_analizi(urun_turu, ts, tn, secilen_dil)
                st.subheader(f"🦠 {_t('hastalik_riski')}", divider="red")
                st.progress(h_skor / 100)
                if h_skor >= 75: st.error(f"**{h_adi} (%{h_skor}):** {h_mesaj}")
                elif h_skor >= 40: st.warning(f"**{h_adi} (%{h_skor}):** {h_mesaj}")
                else: st.success(f"**{h_adi} (%{h_skor}):** {h_mesaj}")

            st.markdown("---")
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
            cm3.metric("Toplam Gider", f"₺ {toplam_gider:,.0f}")
            cm4.metric("Kredi Geri Ödeme", f"₺ {toplam_kredi_maliyeti:,.0f}")
            cm5.metric("Net Kâr", f"₺ {net_kar:,.0f}", delta="Kârlı" if net_kar > 0 else "Zarar")
            
            st.write(" ")
            col_f_sol, col_f_sag = st.columns([1, 1])
            
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
                st.write("---")
                if birim_fiyat > 0:
                    sim_fiyat = st.slider("Borsada Satış Fiyatı Değişimi:", 0.0, float(birim_fiyat*2), float(birim_fiyat), step=0.5)
                    sim_kar = (rekolte_kg * sim_fiyat) + devlet_destegi - toplam_gider - toplam_kredi_maliyeti
                    st.success(f"Piyasa fiyatı **{sim_fiyat} TL** olursa, net kâr: **{sim_kar:,.0f} TL**")

            st.markdown("---")
            st.subheader(_t("ajanda_baslik"), divider="gray")
            
            df_depo_anlik = sql_depo_urun_getir(kullanici)
            depo_secenekleri = ["-- Depodan Ürün Kullanma --"]
            if not df_depo_anlik.empty:
                depo_secenekleri += df_depo_anlik.apply(lambda r: f"ID:{r['id']} | {r['urun_adi']} (Kalan: {r['miktar']} {r['birim']})", axis=1).tolist()
            
            ca1, ca2 = st.columns([1, 2])
            with ca1:
                with st.form(f"f_gorev_{tarla_adi}"):
                    y_kat = st.selectbox("Maliyet Kategorisi:", ["Mazot/Yakıt", "Gübre", "Zirai İlaç", "İşçi Yevmiyesi", "Tohum/Fide", "Su/Elektrik", "Amortisman", "Diğer"])
                    y_islem = st.text_input("Yapılan İşlem Özeti (*):")
                    
                    st.write("---")
                    st.write("📦 **Depo Kullanımı (İsteğe Bağlı)**")
                    y_depo_secim = st.selectbox("Stoktan Düşülecek Ürün:", depo_secenekleri)
                    y_depo_miktar = st.number_input("Kullanılan Miktar:", min_value=0.0, step=1.0)
                    st.write("---")
                    
                    y_tarih = st.date_input("Tarih:")
                    y_maliyet = st.number_input("Ek Maliyet/Tutar (TL):", min_value=0.0, step=100.0)
                    y_not = st.text_input("Durum Notu:", value="Tamamlandı")
                    
                    if st.form_submit_button("🗓️ Gideri İşle ve Stoktan Düş", use_container_width=True):
                        if y_islem:
                            if y_depo_secim != "-- Depodan Ürün Kullanma --" and y_depo_miktar > 0:
                                s_id = int(y_depo_secim.split("|")[0].replace("ID:", "").strip())
                                mevcut_stok = df_depo_anlik[df_depo_anlik['id'] == s_id].iloc[0]['miktar']
                                urun_isim = df_depo_anlik[df_depo_anlik['id'] == s_id].iloc[0]['urun_adi']
                                u_birim = df_depo_anlik[df_depo_anlik['id'] == s_id].iloc[0]['birim']
                                
                                yeni_miktar = max(0.0, mevcut_stok - y_depo_miktar)
                                sql_depo_miktar_guncelle(s_id, yeni_miktar)
                                
                                ek_not = f"[Depodan {y_depo_miktar} {u_birim} {urun_isim} kullanıldı]"
                                y_not = f"{y_not} - {ek_not}" if y_not else ek_not
                                
                            sql_takvim_etkinlik_ekle(kullanici, tarla_adi, y_islem, str(y_tarih), y_not, float(y_maliyet), y_kat)
                            st.rerun()
                        else:
                            st.warning("Lütfen işlem özeti giriniz.")
                            
            with ca2:
                if not df_takvim_ham.empty:
                    df_g = df_takvim_ham.rename(columns={"maliyet_kategorisi":"Kategori", "islem_turu":"İşlem", "tarih":"Tarih", "maliyet":"Tutar (TL)", "notlar":"Durum"})
                    st.dataframe(df_g[["Kategori", "İşlem", "Tarih", "Tutar (TL)", "Durum"]], use_container_width=True, hide_index=True)
                    
                    sildi_id = st.selectbox("Silinecek Kaydı Seçin:", df_takvim_ham.apply(lambda r: f"ID:{r['id']} | {r['islem_turu']} ({r['maliyet']} TL)", axis=1).tolist())
                    if st.button("🗑️ Seçili Kaydı Sil", use_container_width=True):
                        if sildi_id:
                            sql_takvim_etkinlik_sil(int(sildi_id.split("|")[0].replace("ID:", "").strip()))
                            st.rerun()
