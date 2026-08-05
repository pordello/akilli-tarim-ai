# ==============================================================================
# PROJE: AI Destekli Akıllı Tarım Platformu (TAM SÜRÜM + İK, CARİ & MUHASEBE)
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
        "genel_muhasebe": "📊 Genel Muhasebe & İK",
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
        "genel_muhasebe": "📊 Gen. Accounting & HR",
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
    risk_skoru = 10; h_adi = "Mantar ve Bakteri Riski"; d_mesaj = "Hava şartları uygun."
    if urun in ["Pamuk", "Cotton"]:
        h_adi = "Pamukta Solgunluk & Kırmızı Örümcek"
        if sicaklik > 32 and nem < 30: risk_skoru, d_mesaj = 85, "🚨 Yüksek sıcaklık Kırmızı Örümcek riskini tetikler!"
        elif sicaklik > 25 and nem > 60: risk_skoru, d_mesaj = 60, "⚠️ Nemli ve sıcak hava mantarı tetikler."
    elif urun in ["Zeytin", "Olive"]:
        h_adi = "Zeytin Halkalı Leke Hastalığı"
        if 15 <= sicaklik <= 22 and nem > 70: risk_skoru, d_mesaj = 90, "🚨 Mantar için üreme sıcaklığı!"
    elif urun in ["Buğday", "Wheat"]:
        h_adi = "Buğdayda Pas Hastalığı"
        if 10 <= sicaklik <= 20 and nem > 65: risk_skoru, d_mesaj = 75, "⚠️ Serin ve nemli hava pas yapar."
    return h_adi, risk_skoru, d_mesaj

def ai_sohbet_cevabi_uret(mesaj, dil="TR"):
    m = mesaj.lower()
    if "pamuk" in m and "örümcek" in m: return "Pamukta kırmızı örümceğe karşı Abamectin etken maddeli ilaçları sabah uygulayın."
    elif "pas" in m or "buğday" in m: return "Buğday pas hastalığı için Tebuconazole içerikli sistemik fungisitler tavsiye edilir."
    elif "merhaba" in m or "selam" in m: return "Merhaba! Ben yapay zeka tarım asistanınızım. Nasıl yardımcı olabilirim?"
    else: return "Arazinize en uygun çözüm için lütfen ajandanıza bir 'Toprak Analizi' görevi ekleyin."

# --- VERİTABANI KURULUMU ---
def veritabani_otomatik_kur():
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    
    # Mevcut Tablolar
    kursor.execute("""CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, sifre TEXT NOT NULL, tarla_adi TEXT NOT NULL, enlem REAL NOT NULL, boylam REAL NOT NULL, email TEXT NOT NULL, urun_turu TEXT DEFAULT 'Genel', rol TEXT DEFAULT 'SHA', ada TEXT DEFAULT '-', parsel TEXT DEFAULT '-', alan_m2 REAL DEFAULT 0.0, rekolte_kg REAL DEFAULT 0.0, birim_fiyat REAL DEFAULT 0.0, devlet_destegi REAL DEFAULT 0.0, kredi_anapara REAL DEFAULT 0.0, kredi_faiz REAL DEFAULT 0.0)""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS tarim_takvimi (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, tarla_adi TEXT NOT NULL, islem_turu TEXT NOT NULL, tarih TEXT NOT NULL, notlar TEXT, maliyet REAL DEFAULT 0.0, maliyet_kategorisi TEXT DEFAULT 'Diğer')""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS tarla_gunlukleri (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, tarla_adi TEXT NOT NULL, nem INTEGER NOT NULL, sicaklik INTEGER NOT NULL, karar TEXT NOT NULL, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS depo_envanter (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, urun_adi TEXT NOT NULL, kategori TEXT NOT NULL, miktar REAL NOT NULL, birim TEXT NOT NULL, kritik_esik REAL NOT NULL)""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS makine_garaji (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, makine_adi TEXT NOT NULL, plaka TEXT NOT NULL, son_bakim_saati REAL NOT NULL, guncel_saat REAL NOT NULL, bakim_periyodu REAL NOT NULL, muayene_tarihi TEXT DEFAULT '2026-12-31')""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS depo_alimlari (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, urun_adi TEXT NOT NULL, miktar REAL NOT NULL, birim_fiyat REAL NOT NULL, toplam_tutar REAL NOT NULL, tedarikci TEXT NOT NULL, tarih TEXT NOT NULL, odeme_durumu TEXT DEFAULT 'Peşin / Ödendi', vade_tarihi TEXT DEFAULT '-', taksit_sayisi INTEGER DEFAULT 1)""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS makine_yakit_gecmisi (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, makine_id INTEGER NOT NULL, makine_adi TEXT NOT NULL, tarih TEXT NOT NULL, miktar_litre REAL NOT NULL, islem_notu TEXT)""")
    
    # YENİ TABLOLAR (Cari, Personel, İzin, Genel Gider)
    kursor.execute("""CREATE TABLE IF NOT EXISTS cari_hesaplar (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, unvan TEXT NOT NULL, tip TEXT NOT NULL, tel TEXT, bakiye REAL DEFAULT 0.0, aciklama TEXT)""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS personeller (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, ad_soyad TEXT NOT NULL, gorev TEXT NOT NULL, maas REAL NOT NULL, tel TEXT, baslama_tarihi TEXT)""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS personel_izinleri (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, personel_ad TEXT NOT NULL, baslangic TEXT NOT NULL, bitis TEXT NOT NULL, tur TEXT NOT NULL, aciklama TEXT)""")
    kursor.execute("""CREATE TABLE IF NOT EXISTS genel_giderler (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT NOT NULL, tarih TEXT NOT NULL, kategori TEXT NOT NULL, tutar REAL NOT NULL, aciklama TEXT)""")
    
    # Sütun Güvenlik Kontrolleri
    for kolon in ["alan_m2", "rekolte_kg", "birim_fiyat", "devlet_destegi", "kredi_anapara", "kredi_faiz"]:
        try: kursor.execute(f"ALTER TABLE kullanicilar ADD COLUMN {kolon} REAL DEFAULT 0.0"); baglanti.commit()
        except: pass
    for t_kolon in ["tarla_adi", "maliyet", "maliyet_kategorisi"]:
        try: kursor.execute(f"ALTER TABLE tarim_takvimi ADD COLUMN {t_kolon} TEXT DEFAULT 'Diğer'"); baglanti.commit()
        except: pass
        
    kursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE kullanici_adi = 'yunus'")
    if kursor.fetchone()[0] == 0:
        kursor.execute("""INSERT INTO kullanicilar (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("yunus", "12345", "Yunus Beyin Pamuk Tarlası (Adana)", 37.00, 35.32, "yonetici_yunus@example.com", "Pamuk", "Admin", "104", "12", 50000.0))
        baglanti.commit()
    baglanti.close()

veritabani_otomatik_kur()

# --- TEMEL SQL FONKSİYONLARI ---
def sql_kullanici_kontrol(k_adi, sifre):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("SELECT tarla_adi FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (k_adi, sifre))
    sonuc = kursor.fetchone(); baglanti.close()
    return True if sonuc else False

def sql_kullanicinin_tarlalarini_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz FROM kullanicilar WHERE kullanici_adi = ?", baglanti, params=(k_adi,))
    baglanti.close(); return df.values.tolist()

def sql_yeni_tarla_ekle(k_adi, sifre, tarla, il, ilce, email, urun, ada, parsel, alan_m2):
    try:
        baglanti = sqlite3.connect("akilli_tarim.db")
        t_ad = f"{tarla} ({il.capitalize()} / {ilce.capitalize()})"
        y_en, y_boy = koordinat_bul(il, ilce)
        baglanti.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, tarla_adi, enlem, boylam, email, urun_turu, rol, ada, parsel, alan_m2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (k_adi, sifre, t_ad, y_en, y_boy, email, urun, "Müşteri/Çiftçi", ada, parsel, alan_m2))
        baglanti.commit(); baglanti.close(); return True
    except: return False 

def sql_tarla_guncelle(k_adi, e_tarla, y_tarla, y_urun, y_ada, y_parsel, y_alan, y_enlem, y_boylam, y_rek, y_fiyat, y_des, y_kana, y_kfaiz):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("UPDATE kullanicilar SET tarla_adi=?, urun_turu=?, ada=?, parsel=?, alan_m2=?, enlem=?, boylam=?, rekolte_kg=?, birim_fiyat=?, devlet_destegi=?, kredi_anapara=?, kredi_faiz=? WHERE kullanici_adi=? AND tarla_adi=?", (y_tarla, y_urun, y_ada, y_parsel, y_alan, y_enlem, y_boylam, y_rek, y_fiyat, y_des, y_kana, y_kfaiz, k_adi, e_tarla))
    if e_tarla != y_tarla:
        baglanti.execute("UPDATE tarim_takvimi SET tarla_adi=? WHERE kullanici_adi=? AND tarla_adi=?", (y_tarla, k_adi, e_tarla))
        baglanti.execute("UPDATE tarla_gunlukleri SET tarla_adi=? WHERE kullanici_adi=? AND tarla_adi=?", (y_tarla, k_adi, e_tarla))
    baglanti.commit(); baglanti.close(); return True

# --- TAKVİM & GİDERLER ---
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

# --- YENİ EKLENEN İK VE GENEL GİDER FONKSİYONLARI ---
def sql_cari_ekle(k_adi, unvan, tip, tel, bakiye, aciklama):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO cari_hesaplar (kullanici_adi, unvan, tip, tel, bakiye, aciklama) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, unvan, tip, tel, bakiye, aciklama))
    baglanti.commit(); baglanti.close()

def sql_cari_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, unvan, tip, tel, bakiye, aciklama FROM cari_hesaplar WHERE kullanici_adi = ?", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_cari_sil(c_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM cari_hesaplar WHERE id = ?", (c_id,))
    baglanti.commit(); baglanti.close()

def sql_personel_ekle(k_adi, ad, gorev, maas, tel, baslama):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO personeller (kullanici_adi, ad_soyad, gorev, maas, tel, baslama_tarihi) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, ad, gorev, maas, tel, baslama))
    baglanti.commit(); baglanti.close()

def sql_personel_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, ad_soyad, gorev, maas, tel, baslama_tarihi FROM personeller WHERE kullanici_adi = ?", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_personel_sil(p_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM personeller WHERE id = ?", (p_id,))
    baglanti.commit(); baglanti.close()

def sql_izin_ekle(k_adi, personel, bas, bit, tur, aciklama):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO personel_izinleri (kullanici_adi, personel_ad, baslangic, bitis, tur, aciklama) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, personel, bas, bit, tur, aciklama))
    baglanti.commit(); baglanti.close()

def sql_izin_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, personel_ad, baslangic, bitis, tur, aciklama FROM personel_izinleri WHERE kullanici_adi = ? ORDER BY id DESC", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_izin_sil(i_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM personel_izinleri WHERE id = ?", (i_id,))
    baglanti.commit(); baglanti.close()

def sql_genel_gider_ekle(k_adi, tarih, kat, tutar, aciklama):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO genel_giderler (kullanici_adi, tarih, kategori, tutar, aciklama) VALUES (?, ?, ?, ?, ?)", (k_adi, tarih, kat, tutar, aciklama))
    # Genel gider aynı zamanda şirketin toplam faturasına eklensin (tarim_takvimi üzerinden)
    islem = f"Genel Gider: {kat}"
    baglanti.execute("INSERT INTO tarim_takvimi (kullanici_adi, tarla_adi, islem_turu, tarih, notlar, maliyet, maliyet_kategorisi) VALUES (?, ?, ?, ?, ?, ?, ?)", (k_adi, 'İşletme / Ofis', islem, str(tarih), aciklama, tutar, 'Diğer'))
    baglanti.commit(); baglanti.close()

def sql_genel_gider_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, tarih, kategori, tutar, aciklama FROM genel_giderler WHERE kullanici_adi = ? ORDER BY id DESC", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_genel_gider_sil(g_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM genel_giderler WHERE id = ?", (g_id,))
    baglanti.commit(); baglanti.close()

# --- DEPO & DİĞERLERİ ---
def sql_depo_urun_ekle(k_adi, urun_adi, kategori, miktar, birim, kritik):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO depo_envanter (kullanici_adi, urun_adi, kategori, miktar, birim, kritik_esik) VALUES (?, ?, ?, ?, ?, ?)", (k_adi, urun_adi, kategori, miktar, birim, kritik))
    baglanti.commit(); baglanti.close()

def sql_depo_alim_kaydet(k_adi, urun_adi, miktar, b_fiyat, tedarikci, tarih, kategori, durum, vade, taksit):
    baglanti = sqlite3.connect("akilli_tarim.db")
    toplam = miktar * b_fiyat
    baglanti.execute("INSERT INTO depo_alimlari (kullanici_adi, urun_adi, miktar, birim_fiyat, toplam_tutar, tedarikci, tarih, odeme_durumu, vade_tarihi, taksit_sayisi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (k_adi, urun_adi, miktar, b_fiyat, toplam, tedarikci, tarih, durum, vade, taksit))
    notlar = f"Tedarikçi: {tedarikci} | Durum: {durum}"
    baglanti.execute("INSERT INTO tarim_takvimi (kullanici_adi, tarla_adi, islem_turu, tarih, notlar, maliyet, maliyet_kategorisi) VALUES (?, ?, ?, ?, ?, ?, ?)", (k_adi, 'Merkezi Depo', f"Mal Alımı: {urun_adi}", tarih, notlar, toplam, kategori))
    baglanti.commit(); baglanti.close()

def sql_depo_alimlari_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, urun_adi, miktar, birim_fiyat, toplam_tutar, tedarikci, tarih, odeme_durumu, vade_tarihi, taksit_sayisi FROM depo_alimlari WHERE kullanici_adi = ? ORDER BY tarih DESC", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_depo_urun_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, urun_adi, kategori, miktar, birim, kritik_esik FROM depo_envanter WHERE kullanici_adi = ? ORDER BY kategori ASC", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_depo_miktar_guncelle(urun_id, yeni_miktar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("UPDATE depo_envanter SET miktar = ? WHERE id = ?", (yeni_miktar, urun_id))
    baglanti.commit(); baglanti.close()

def sql_depo_urun_sil(urun_id):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("DELETE FROM depo_envanter WHERE id = ?", (urun_id,))
    baglanti.commit(); baglanti.close()

def sql_kullanici_tedarikcileri_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    try:
        df = pd.read_sql_query("SELECT DISTINCT tedarikci FROM depo_alimlari WHERE kullanici_adi = ? AND tedarikci != '' AND tedarikci IS NOT NULL", baglanti, params=(k_adi,))
        baglanti.close(); return df['tedarikci'].tolist()
    except: baglanti.close(); return []

def sql_makine_getir(k_adi):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT id, makine_adi, plaka, son_bakim_saati, guncel_saat, bakim_periyodu, muayene_tarihi FROM makine_garaji WHERE kullanici_adi = ?", baglanti, params=(k_adi,))
    baglanti.close(); return df

def sql_analizleri_getir(k_adi, tarla):
    baglanti = sqlite3.connect("akilli_tarim.db")
    df = pd.read_sql_query("SELECT nem, sicaklik, karar, tarih FROM tarla_gunlukleri WHERE kullanici_adi = ? AND tarla_adi = ? ORDER BY id DESC LIMIT 50", baglanti, params=(k_adi, tarla))
    baglanti.close(); return df

def sql_analiz_kaydet(k_adi, tarla, nem, sicaklik, karar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    baglanti.execute("INSERT INTO tarla_gunlukleri (kullanici_adi, tarla_adi, nem, sicaklik, karar) VALUES (?, ?, ?, ?, ?)", (k_adi, tarla, nem, sicaklik, karar))
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
    
    # YENİ MENÜ DÜZENİ
    menu_secenekleri = [
        _t("genel_merkez"),
        _t("genel_muhasebe"),
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
    # MODÜL 1: GENEL MUHASEBE, CARİ VE İK (YENİ DEV MODÜL)
    # ==========================================
    if aktif_secim == _t("genel_muhasebe"):
        st.subheader("📊 Genel Muhasebe, Cari Hesap ve İnsan Kaynakları (İK)")
        st.caption("İşletmenizin cari hesaplarını, personel izinlerini, maaşları ve genel ofis giderlerini buradan yönetin.")
        st.markdown("---")
        
        tab_cari, tab_personel, tab_gider, tab_fatura = st.tabs([
            "💳 Cari Hesaplar", "👥 Personel & İzinler", "💸 Diğer Genel Giderler", "🧾 Satın Alma & Borçlar"
        ])
        
        # --- CARİ HESAPLAR ---
        with tab_cari:
            col_c1, col_c2 = st.columns([1, 2])
            with col_c1:
                with st.form("cari_ekle_form"):
                    st.write("**Yeni Cari Kart Aç**")
                    c_unvan = st.text_input("Cari Unvanı / Adı (*):")
                    c_tip = st.selectbox("Cari Tipi:", ["Alıcı (Müşteri)", "Satıcı (Tedarikçi)", "Personel", "Diğer"])
                    c_tel = st.text_input("Telefon:")
                    c_bakiye = st.number_input("Açılış Bakiyesi (TL):", help="+ Alacak, - Borç", value=0.0)
                    c_acik = st.text_input("Açıklama:")
                    if st.form_submit_button("💳 Cariyi Kaydet", use_container_width=True):
                        if c_unvan:
                            sql_cari_ekle(kullanici, c_unvan, c_tip, c_tel, c_bakiye, c_acik)
                            st.success("Cari eklendi!"); st.rerun()
                        else: st.warning("Unvan zorunludur.")
            with col_c2:
                df_cari = sql_cari_getir(kullanici)
                if not df_cari.empty:
                    st.write("**Mevcut Cari Hesaplar**")
                    st.dataframe(df_cari.rename(columns={"unvan":"Unvan", "tip":"Tip", "tel":"Telefon", "bakiye":"Bakiye(TL)", "aciklama":"Not"})[["Unvan", "Tip", "Telefon", "Bakiye(TL)", "Not"]], use_container_width=True, hide_index=True)
                    sil_cari_id = st.selectbox("Cari Sil:", df_cari.apply(lambda r: f"ID:{r['id']} | {r['unvan']}", axis=1).tolist())
                    if st.button("🗑️ Seçili Cariyi Sil", use_container_width=True):
                        sql_cari_sil(int(sil_cari_id.split("|")[0].replace("ID:", "").strip())); st.rerun()
                else: st.info("Sistemde kayıtlı cari hesap bulunmuyor.")

        # --- PERSONEL VE İK ---
        with tab_personel:
            col_p1, col_p2 = st.columns([1.2, 2])
            with col_p1:
                with st.form("per_ekle"):
                    st.write("**Yeni Personel İşe Alım**")
                    p_ad = st.text_input("Ad Soyad (*):")
                    p_gorev = st.text_input("Görevi (Örn: Traktör Şoförü):")
                    p_maas = st.number_input("Aylık Net Maaş (TL):", min_value=0.0, step=500.0)
                    p_tel = st.text_input("Telefon:")
                    p_bas = st.date_input("İşe Başlama Tarihi:")
                    if st.form_submit_button("👥 Personeli Kaydet", use_container_width=True):
                        if p_ad:
                            sql_personel_ekle(kullanici, p_ad, p_gorev, float(p_maas), p_tel, str(p_bas))
                            sql_cari_ekle(kullanici, p_ad, "Personel", p_tel, 0.0, "Personel Carisi otomatik açıldı.")
                            st.rerun()
            with col_p2:
                df_per = sql_personel_getir(kullanici)
                if not df_per.empty:
                    st.write("**Mevcut Personel Listesi**")
                    for idx, per in df_per.iterrows():
                        with st.expander(f"👷 {per['ad_soyad']} | {per['gorev']} - Maaş: {per['maas']} TL", expanded=False):
                            st.write(f"**Tel:** {per['tel']} | **İşe Giriş:** {per['baslama_tarihi']}")
                            c_p1, c_p2 = st.columns(2)
                            with c_p1:
                                if st.button(f"💸 Bu Ayki Maaşı Öde ({per['maas']} TL)", key=f"mp_{per['id']}", use_container_width=True):
                                    sql_genel_gider_ekle(kullanici, str(datetime.now().date()), "Personel Maaşı", per['maas'], f"{per['ad_soyad']} - Aylık Maaş Ödemesi")
                                    st.success("Maaş şirket giderlerine işlendi!"); st.rerun()
                            with c_p2:
                                if st.button("🗑️ İşten Çıkar (Sil)", key=f"sp_{per['id']}", use_container_width=True, type="primary"):
                                    sql_personel_sil(per['id']); st.rerun()
                    
                    st.write("---")
                    st.write("**✈️ İzin Yönetimi (Yıllık / Rapor)**")
                    with st.form("izin_form"):
                        i_per = st.selectbox("İzne Çıkacak Personel:", df_per['ad_soyad'].tolist())
                        i_tur = st.selectbox("İzin Türü:", ["Yıllık İzin", "Mazeret İzni", "Hastalık / Rapor", "Ücretsiz İzin"])
                        c_i1, c_i2 = st.columns(2)
                        with c_i1: i_bas = st.date_input("Başlangıç:")
                        with c_i2: i_bit = st.date_input("Bitiş:")
                        i_not = st.text_input("Açıklama:")
                        if st.form_submit_button("✈️ İzni İşle"):
                            sql_izin_ekle(kullanici, i_per, str(i_bas), str(i_bit), i_tur, i_not); st.rerun()
                    
                    df_izin = sql_izin_getir(kullanici)
                    if not df_izin.empty:
                        st.dataframe(df_izin.rename(columns={"personel_ad":"Personel", "baslangic":"Başlangıç", "bitis":"Bitiş", "tur":"Tür", "aciklama":"Not"})[["Personel", "Tür", "Başlangıç", "Bitiş", "Not"]], use_container_width=True, hide_index=True)
                else: st.info("Sistemde personel bulunmuyor.")

        # --- DİĞER GENEL GİDERLER ---
        with tab_gider:
            st.caption("Kira, Elektrik, Ofis malzemesi, Muhasebe ücreti gibi tarlaya ait olmayan işletme giderlerinizi buradan girin.")
            col_g1, col_g2 = st.columns([1, 2])
            with col_g1:
                with st.form("gider_form"):
                    g_kat = st.selectbox("Gider Kategorisi:", ["Ofis Kirası", "Fatura (Elektrik/Su/İnternet)", "Muhasebe / Mali Müşavir", "Çay/Kahve/Mutfak", "Vergi/Harç", "Bakım/Onarım", "Diğer"])
                    g_tutar = st.number_input("Tutar (TL):", min_value=0.0, step=100.0)
                    g_tarih = st.date_input("Fatura/Ödeme Tarihi:")
                    g_not = st.text_input("Açıklama (*):")
                    if st.form_submit_button("💸 Gideri İşle", use_container_width=True):
                        if g_not and g_tutar > 0:
                            sql_genel_gider_ekle(kullanici, str(g_tarih), g_kat, float(g_tutar), g_not)
                            st.success("İşletme gideri eklendi!"); st.rerun()
                        else: st.warning("Tutar ve Açıklama zorunludur.")
            with col_g2:
                df_giderler = sql_genel_gider_getir(kullanici)
                if not df_giderler.empty:
                    st.write("**Geçmiş Genel Giderler**")
                    st.dataframe(df_giderler.rename(columns={"tarih":"Tarih", "kategori":"Kategori", "tutar":"Tutar(TL)", "aciklama":"Açıklama"})[["Tarih", "Kategori", "Tutar(TL)", "Açıklama"]], use_container_width=True, hide_index=True)
                    s_gider_id = st.selectbox("Gider Sil:", df_giderler.apply(lambda r: f"ID:{r['id']} | {r['aciklama']} ({r['tutar']} TL)", axis=1).tolist())
                    if st.button("🗑️ Seçili Gideri Sil", use_container_width=True):
                        sql_genel_gider_sil(int(s_gider_id.split("|")[0].replace("ID:", "").strip())); st.rerun()
                else: st.info("Genel gider bulunmuyor.")

        # --- SATIN ALMA VE FATURALAR (ESKİ DEPODAN TAŞINAN) ---
        with tab_fatura:
            df_alim_ham = sql_depo_alimlari_getir(kullanici)
            if not df_alim_ham.empty:
                df_borclar = df_alim_ham[df_alim_ham['odeme_durumu'] == 'Vadeli / Ödenmedi']
                if not df_borclar.empty:
                    st.error("⏳ **GELECEK ÖDEMELER VE BORÇLAR (Cari Durum)**")
                    for idx, borc in df_borclar.iterrows():
                        st.warning(f"**Tedarikçi:** {borc['tedarikci']} | **Ürün:** {borc['urun_adi']} | **Borç:** {borc['toplam_tutar']:,.2f} TL | **Vade:** {borc['vade_tarihi']} | **Taksit:** {borc['taksit_sayisi']}")
                    st.write("---")

                st.write("**📅 Tarih Aralığına Göre Fatura Raporu Al**")
                df_alim_ham['tarih_dt'] = pd.to_datetime(df_alim_ham['tarih']).dt.date
                c_t1, c_t2, c_t3 = st.columns([1, 1, 1])
                with c_t1: baslangic_tarihi = st.date_input("Başlangıç:", value=df_alim_ham['tarih_dt'].min())
                with c_t2: bitis_tarihi = st.date_input("Bitiş:", value=datetime.now().date())
                
                df_filtreli = df_alim_ham[(df_alim_ham['tarih_dt'] >= baslangic_tarihi) & (df_alim_ham['tarih_dt'] <= bitis_tarihi)]
                with c_t3: st.metric("Aralık Toplam Fatura", f"₺ {df_filtreli['toplam_tutar'].sum():,.2f}")
                
                if not df_filtreli.empty:
                    st.dataframe(df_filtreli.rename(columns={"urun_adi":"Ürün", "miktar":"Miktar", "toplam_tutar":"Tutar(TL)", "tedarikci":"Tedarikçi", "tarih":"Tarih", "odeme_durumu":"Durum", "vade_tarihi":"Vade"})[["Tarih", "Ürün", "Miktar", "Tedarikçi", "Tutar(TL)", "Durum", "Vade"]], use_container_width=True, hide_index=True)
            else: st.info("Sistemde satın alma (mal girişi) faturası bulunmuyor. Depo bölümünden alım yapın.")

    # ==========================================
    # MODÜL 2: CANLI BORSA EKRANI
    # ==========================================
    elif aktif_secim == _t("borsa_ekrani"):
        st.subheader("📈 Canlı Tarım Borsası & Piyasa Analizi")
        st.markdown("---")
        borsa_verileri = {"Pamuk": {"fiyat": 64.50, "degisim": 1.2}, "Zeytinyağı": {"fiyat": 285.00, "degisim": -2.5}, "Buğday": {"fiyat": 10.20, "degisim": 0.4}, "Mısır": {"fiyat": 9.40, "degisim": -0.1}}
        k1, k2, k3, k4 = st.columns(4); sutunlar = [k1, k2, k3, k4]; idx = 0
        for urun, veri in borsa_verileri.items():
            sutunlar[idx % 4].metric(label=urun, value=f"₺ {veri['fiyat']:.2f}", delta=f"{veri['degisim']}%"); idx += 1
        st.write("---"); st.write("**Borsa Grafiği (Son 7 Günlük Trend)**")
        tarihler = pd.date_range(end=datetime.today(), periods=7).strftime('%Y-%m-%d')
        st.line_chart(pd.DataFrame({'Tarih': tarihler, 'Pamuk': [60, 61.5, 61, 62, 63.5, 63, 64.5]}).set_index('Tarih'))

    # ==========================================
    # MODÜL 3: MAKİNE VE EKİPMAN GARAJI
    # ==========================================
    elif aktif_secim == _t("makine_garaji"):
        st.subheader("🚜 Makine Garajı, Yakıt ve Muayene Takibi")
        st.markdown("---")
        df_makine = sql_makine_getir(kullanici)
        col_m1, col_m2 = st.columns([1.2, 2.5])
        with col_m1:
            with st.form("yeni_makine_form"):
                st.write("**Yeni Makine Ekle**")
                m_adi = st.text_input("Makine Adı:"); m_plaka = st.text_input("Plaka:")
                m_son_bakim = st.number_input("Son Bakım:", step=10.0); m_guncel = st.number_input("Güncel Saat:", step=10.0)
                m_periyot = st.number_input("Periyot:", value=250.0); m_muayene = st.date_input("Muayene Tarihi:")
                if st.form_submit_button("🚜 Garaja Ekle", use_container_width=True) and m_adi:
                    sql_makine_ekle(kullanici, m_adi, m_plaka, float(m_son_bakim), float(m_guncel), float(m_periyot), str(m_muayene)); st.rerun()
        with col_m2:
            if not df_makine.empty:
                for idx, r in df_makine.iterrows():
                    with st.expander(f"⚙️ {r['makine_adi']} | {r['plaka']} ({r['guncel_saat']} Saat)", expanded=False):
                        st.write(f"Muayene: {r['muayene_tarihi']}")
            else: st.info("Garajınız boş.")

    # ==========================================
    # MODÜL 4: AKILLI DEPO (SADECE STOK GİRİŞİ)
    # ==========================================
    elif aktif_secim == _t("depo_yonetimi"):
        st.subheader(f"📦 Merkezi Depo ve Envanter Kontrolü")
        st.caption("Faturalar ve cari borçlar 'Genel Muhasebe' sekmesine taşındı. Buradan sadece fiziksel stok girişi yapılır.")
        st.markdown("---")
        df_depo = sql_depo_urun_getir(kullanici)
        kayitli_tedarikciler = sql_kullanici_tedarikcileri_getir(kullanici)
        tedarikci_secenekleri_ana = ["-- Yeni Tedarikçi Ekle --"] + kayitli_tedarikciler
        
        col_d1, col_d2 = st.columns([1.2, 2])
        with col_d1:
            sekme_mevcut, sekme_yeni = st.tabs(["📥 Mevcut Ürüne Stok Ekle", "🆕 Yeni Ürün Tanımla"])
            with sekme_yeni:
                with st.form("yeni_stok_formu"):
                    d_urun_adi = st.text_input("Ürün Adı (*):")
                    d_kategori = st.selectbox("Kategori:", ["Zirai İlaç", "Gübre", "Tohum/Fide", "Mazot/Yakıt", "Diğer"])
                    d_miktar = st.number_input("Alınan Miktar:", min_value=0.0); d_birim = st.selectbox("Birim:", ["kg", "Litre", "Adet", "Ton"])
                    d_kritik = st.number_input("Kritik Eşik:", value=10.0)
                    st.write("---")
                    d_fiyat = st.number_input("Birim Alış Fiyatı (TL):", step=10.0)
                    sec_ted_d = st.selectbox("Tedarikçi:", tedarikci_secenekleri_ana)
                    d_tedarikci = st.text_input("Yeni Tedarikçi:") if sec_ted_d == "-- Yeni Tedarikçi Ekle --" else sec_ted_d
                    d_odeme = st.selectbox("Ödeme:", ["Peşin / Ödendi", "Vadeli / Ödenmedi"])
                    d_vade = st.date_input("İlk Vade Tarihi:"); d_tarih = st.date_input("Alım Tarihi:")
                    
                    if st.form_submit_button("📦 Depoya ve Muhasebeye İşle", use_container_width=True) and d_urun_adi:
                        vade_str = str(d_vade) if d_odeme == "Vadeli / Ödenmedi" else "-"
                        sql_depo_urun_ekle(kullanici, d_urun_adi, d_kategori, float(d_miktar), d_birim, float(d_kritik))
                        if d_miktar > 0: sql_depo_alim_kaydet(kullanici, d_urun_adi, float(d_miktar), float(d_fiyat), d_tedarikci, str(d_tarih), d_kategori, d_odeme, vade_str, 1)
                        st.rerun()
                        
            with sekme_mevcut:
                if not df_depo.empty:
                    with st.form("mevcut_stok_ekle_formu"):
                        stok_secenekleri = df_depo.apply(lambda r: f"ID:{r['id']} | {r['urun_adi']} (Kalan: {r['miktar']} {r['birim']})", axis=1).tolist()
                        secili_stok = st.selectbox("Stoğu Artacak Ürün:", stok_secenekleri)
                        m_miktar = st.number_input("Alınan Ek Miktar:", min_value=0.1, step=1.0)
                        m_fiyat = st.number_input("Birim Alış Fiyatı (TL):", step=10.0)
                        sec_ted_m = st.selectbox("Tedarikçi:", tedarikci_secenekleri_ana)
                        m_tedarikci = st.text_input("Yeni Tedarikçi:", key="ym") if sec_ted_m == "-- Yeni Tedarikçi Ekle --" else sec_ted_m
                        m_odeme = st.selectbox("Ödeme:", ["Peşin / Ödendi", "Vadeli / Ödenmedi"], key="mo")
                        m_vade = st.date_input("Vade Tarihi:", key="mv"); m_tarih = st.date_input("Alım Tarihi:", key="mtar")
                        
                        if st.form_submit_button("📥 Stok Artır ve Muhasebeye İşle", use_container_width=True) and secili_stok:
                            s_id = int(secili_stok.split("|")[0].replace("ID:", "").strip())
                            s_eski = float(df_depo[df_depo['id'] == s_id].iloc[0]['miktar'])
                            sql_depo_miktar_guncelle(s_id, s_eski + float(m_miktar))
                            sql_depo_alim_kaydet(kullanici, df_depo[df_depo['id'] == s_id].iloc[0]['urun_adi'], float(m_miktar), float(m_fiyat), m_tedarikci, str(m_tarih), df_depo[df_depo['id'] == s_id].iloc[0]['kategori'], m_odeme, str(m_vade) if m_odeme == "Vadeli / Ödenmedi" else "-", 1)
                            st.rerun()

        with col_d2:
            st.write("**📊 Mevcut Depo Envanteri**")
            if not df_depo.empty:
                st.dataframe(df_depo.rename(columns={"urun_adi":"Ürün", "kategori":"Kategori", "miktar":"Miktar", "birim":"Birim"})[["Ürün", "Kategori", "Miktar", "Birim"]], use_container_width=True, hide_index=True)
            else: st.info("Deponuz boş.")

    # ==========================================
    # 5. AI ASİSTAN, YENİ TARLA & MERKEZ
    # ==========================================
    elif aktif_secim == _t("ai_asistan"):
        st.subheader("🤖 AI Ziraat Asistanı")
        if "chat_gecmisi" not in st.session_state: st.session_state["chat_gecmisi"] = [{"rol": "asistan", "icerik": "Merhaba! Nasıl yardımcı olabilirim?"}]
        for msj in st.session_state["chat_gecmisi"]:
            with st.chat_message(msj["rol"]): st.markdown(msj["icerik"])
        if prompt := st.chat_input("Yazın..."):
            st.session_state["chat_gecmisi"].append({"rol": "user", "icerik": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("asistan"):
                cvp = ai_sohbet_cevabi_uret(prompt, secilen_dil)
                st.markdown(cvp)
                st.session_state["chat_gecmisi"].append({"rol": "asistan", "icerik": cvp})

    elif aktif_secim == _t("genel_merkez"):
        st.subheader(f"🏠 ERP Genel Rapor Merkezi")
        st.markdown("---")
        t_gider = t_gelir = t_destek = t_kredi = 0.0
        df_tum_gider = sql_tum_tarlalarin_takvimini_getir(kullanici)
        if not df_tum_gider.empty: t_gider = df_tum_gider['maliyet'].sum()
        for t in tarlalar_listesi: t_gelir += (t[9] * t[10]); t_destek += t[11]; t_kredi += (t[12] + (t[12] * t[13] / 100))
        net = t_gelir + t_destek - t_gider - t_kredi
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("Toplam Gelir+Destek", f"₺ {(t_gelir + t_destek):,.2f}")
        rc2.metric("Toplam Şirket Gideri", f"₺ {t_gider:,.2f}", help="Tarlalar + Merkezi Depo + Personel + Genel Gider")
        rc3.metric("Banka Ödemeleri", f"₺ {t_kredi:,.2f}")
        rc4.metric("İşletme Net Kârı", f"₺ {net:,.2f}", delta="Kârlı" if net > 0 else "Zarar")

    elif aktif_secim == _t("yeni_tarla_ekle"):
        st.subheader("➕ Yeni Arazi Ekle")
        with st.form("yeni_tarla"):
            il = st.text_input("İl (*)"); ilce = st.text_input("İlçe (*)"); tarla_ad = st.text_input("Tarla Adı (*)")
            if st.form_submit_button("Ekle", use_container_width=True) and tarla_ad:
                sql_yeni_tarla_ekle(kullanici, "123", tarla_ad, il, ilce, "x@x.com", "Pamuk", "", "", 1000.0); st.rerun()

    # ==========================================
    # 6. TARLA DETAY
    # ==========================================
    else:
        aktif_t = next((t for t in tarlalar_listesi if t[0] == aktif_secim), None)
        if aktif_t:
            tarla_adi, t_enlem, t_boylam, m_email, urun_turu, rol, ada, parsel, alan_m2, rekolte_kg, birim_fiyat, devlet_destegi, kredi_anapara, kredi_faiz = aktif_t
            st.subheader(f"🌾 {tarla_adi.upper()}")
            st.caption(f"Yönetici: {kullanici.upper()} | Ada/Parsel: {ada}/{parsel} | Büyüklük: {alan_m2:,.0f} m² | Mahsul: {urun_turu}")
            
            # --- SADECE AJANDA KISMI GÖSTERİLDİ ---
            st.markdown("---")
            st.subheader(_t("ajanda_baslik"), divider="gray")
            df_depo_anlik = sql_depo_urun_getir(kullanici)
            depo_secenekleri = ["-- Depodan Ürün Kullanma --"] + (df_depo_anlik.apply(lambda r: f"ID:{r['id']} | {r['urun_adi']} (Kalan: {r['miktar']})", axis=1).tolist() if not df_depo_anlik.empty else [])
            
            ca1, ca2 = st.columns([1, 2])
            with ca1:
                with st.form(f"f_gorev_{tarla_adi}"):
                    y_kat = st.selectbox("Kategori:", ["Mazot/Yakıt", "Gübre", "Zirai İlaç", "İşçi", "Diğer"])
                    y_islem = st.text_input("İşlem Özeti (*):")
                    y_depo_secim = st.selectbox("Depodan Düş:", depo_secenekleri)
                    y_depo_miktar = st.number_input("Düşülecek Miktar:", min_value=0.0)
                    y_maliyet = st.number_input("İşçilik Tutar (TL):", min_value=0.0)
                    if st.form_submit_button("🗓️ Gideri İşle", use_container_width=True) and y_islem:
                        if y_depo_secim != "-- Depodan Ürün Kullanma --" and y_depo_miktar > 0:
                            s_id = int(y_depo_secim.split("|")[0].replace("ID:", "").strip())
                            mevcut = float(df_depo_anlik[df_depo_anlik['id'] == s_id].iloc[0]['miktar'])
                            sql_depo_miktar_guncelle(s_id, max(0.0, mevcut - y_depo_miktar))
                        sql_takvim_etkinlik_ekle(kullanici, tarla_adi, y_islem, str(datetime.now().date()), "Tamamlandı", float(y_maliyet), y_kat)
                        st.rerun()
            with ca2:
                df_takvim_ham = sql_takvim_verileri_getir_ham(kullanici, tarla_adi)
                if not df_takvim_ham.empty:
                    st.dataframe(df_takvim_ham[["maliyet_kategorisi", "islem_turu", "tarih", "maliyet"]], use_container_width=True, hide_index=True)
