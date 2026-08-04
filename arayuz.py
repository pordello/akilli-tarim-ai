# ==============================================================================
# PROJE: AI Destekli Akıllı Tarım Platformu (GELİŞMİŞ KURUMSAL RAPORLAMA EKLENDİ)
# ==============================================================================

import streamlit as st
import random
import requests
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="AI Akıllı Tarım Paneli", page_icon="🌾", layout="wide")

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
def ai_hastalik_risk_analizi(urun, sicaklik, nem):
    risk_skoru = 10 
    detay_mesaj = "Hava şartları mahsul sağlığı için elverişli görünüyor."
    hastalik_adi = "Mantar ve Bakteri Riski"

    if urun == "Pamuk":
        hastalik_adi = "Pamukta Solgunluk & Kırmızı Örümcek"
        if sicaklik > 32 and nem < 30:
            risk_skoru = 85
            detay_mesaj = "🚨 Yüksek sıcaklık ve düşük nem Kırmızı Örümcek zararlısını tetikler! Sahayı kontrol edin."
        elif sicaklik > 25 and nem > 60:
            risk_skoru = 60
            detay_mesaj = "⚠️ Nemli ve sıcak hava Verticillium Solgunluğu mantarını tetikleyebilir."
    elif urun == "Zeytin":
        hastalik_adi = "Zeytin Halkalı Leke Hastalığı"
        if 15 <= sicaklik <= 22 and nem > 70:
            risk_skoru = 90
            detay_mesaj = "🚨 Tam Halkalı Leke mantarının üreme sıcaklığı! Aşırı nem riski maksimuma çıkardı."
        elif sicaklik > 28:
            risk_skoru = 20
            detay_mesaj = "✅ Yüksek sıcaklık zeytin sineği ve mantar faaliyetlerini yavaşlatıyor."
    elif urun == "Buğday":
        hastalik_adi = "Buğdayda Pas Hastalığı (Küf)"
        if 10 <= sicaklik <= 20 and nem > 65:
            risk_skoru = 75
            detay_mesaj = "⚠️ Serin ve nemli hava pas (püskül) hastalığı için ideal ortam oluşturuyor."
    else: 
        hastalik_adi = "Kök Çürüklüğü & Mantar"
        if nem > 75:
            risk_skoru = 80
            detay_mesaj = "🚨 Aşırı toprak nemi köklerin nefes almasını engelliyor ve çürüme mantarlarını besliyor!"

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
        tarih TEXT NOT NULL, notlar TEXT
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
        st.markdown("<h2 style='text-align: center; color: #2ecc71;'>🌾 AI Akıllı Tarım Ağı</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Sisteme giriş yapın veya yeni bir çiftçi hesabı oluşturun.</p>", unsafe_allow_html=True)
        st.write("")
        
        sekme_giris, sekme_kayit = st.tabs(["🔑 Sisteme Giriş", "📝 Yeni Kayıt Ol"])
        
        with sekme_giris:
            st.write("")
            kullanici_adi = st.text_input("Kullanıcı Adı:", key="login_kadi")
            sifre = st.text_input("Şifre:", type="password", key="login_sifre")
            if st.button("🚀 Sisteme Bağlan", use_container_width=True, type="primary"):
                kullanici_verisi = sql_kullanici_kontrol(kullanici_adi, sifre)
                if kullanici_verisi:
                    st.session_state["giris_yapildi"] = True
                    st.session_state["aktif_kullanici"] = kullanici_adi
                    st.session_state["kullanici_bilgileri"] = kullanici_verisi
                    st.rerun()
                else:
                    st.error("Hatalı Kullanıcı Adı veya Şifre!")
                    
        with sekme_kayit:
            with st.form("yeni_kayit_formu"):
                st.subheader("Yeni Tarla / Çiftçi Kaydı")
                st.caption("Lütfen hesap ve lokasyon bilgilerinizi eksiksiz doldurun.")
                
                k_adi = st.text_input("Kullanıcı Adı (*)")
                k_sifre = st.text_input("Şifre (*)", type="password")
                k_email = st.text_input("E-Posta Adresi (*)")
                
                st.write("---")
                st.write("**📍 Lokasyon ve Parsel Bilgileri**")
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    k_il = st.text_input("İl (*) - Örn: Antalya")
                    k_ada = st.text_input("Ada No (*)")
                with col_k2:
                    k_ilce = st.text_input("İlçe (*) - Örn: Alanya")
                    k_parsel = st.text_input("Parsel No (*)")
                    
                k_tarla = st.text_input("Tarlanıza Vermek İstediğiniz İsim (Örn: Kuzey Yamacı)")
                k_urun = st.selectbox("Yetiştirilen Ana Mahsul", ["Pamuk", "Zeytin", "Buğday", "Mısır", "Ayçiçeği", "Narenciye", "Domates", "Diğer"])
                
                kayit_buton = st.form_submit_button("✅ Hesabı Oluştur", use_container_width=True)
                
                if kayit_buton:
                    if k_adi and k_sifre and k_email and k_il and k_ilce and k_ada and k_parsel:
                        with st.spinner("🗺️ Harita koordinatları bulunuyor..."):
                            sonuc = sql_yeni_musteri_kayit(k_adi, k_sifre, k_tarla, k_il, k_ilce, k_email, k_urun, k_ada, k_parsel)
                        if sonuc:
                            st.success("🎉 Kayıt başarıyla tamamlandı! Giriş sekmesinden bağlanabilirsiniz.")
                        else:
                            st.error("⚠️ Bu kullanıcı adı zaten sistemde kayıtlı!")
                    else:
                        st.warning("Lütfen (*) ile işaretli tüm zorunlu alanları doldurun.")

# --- ANA PANEL ---
else:
    kullanici = st.session_state["aktif_kullanici"]
    tarla_adi, t_enlem, t_boylam, m_email, urun_turu, rol, ada, parsel = st.session_state["kullanici_bilgileri"]

    # --- DEĞERLERİN ÖNCEDEN HESAPLANMASI (RAPOR İÇİN GEREKLİ) ---
    if "toprak_nemi" not in st.session_state:
        st.session_state["toprak_nemi"] = akilli_nem_simulasyonu()
        gercek_isi = gercek_hava_durumu_getir(t_enlem, t_boylam)
        st.session_state["canli_sicaklik"] = gercek_isi if gercek_isi is not None else random.randint(22, 38)
        
    toprak_nemi = st.session_state["toprak_nemi"]
    canli_sicaklik = st.session_state["canli_sicaklik"]

    # AI Sulama Kararı
    if toprak_nemi < 30 and canli_sicaklik > 30:
        ai_mesaj = "🔥 KRİTİK: Toprak kuru, hava sıcak! Acil sulama başlatıldı."
        ai_durum = "error"
        css_durum = "box-danger"
    elif toprak_nemi < 30:
        ai_mesaj = "💧 UYARI: Nem düşük, standart sulama açıldı."
        ai_durum = "warning"
        css_durum = "box-warning"
    else:
        ai_mesaj = "✅ NORMAL: Nem yeterli, sulama kapalı. Su tasarrufu yapılıyor."
        ai_durum = "success"
        css_durum = "box-success"

    # AI Hastalık Kararı
    h_adi, h_skor, h_mesaj = ai_hastalik_risk_analizi(urun_turu, canli_sicaklik, toprak_nemi)
    h_css = "box-danger" if h_skor >= 75 else "box-warning" if h_skor >= 40 else "box-success"

    # Finans Hesaplamaları
    df_takvim_ham = sql_takvim_verileri_getir_ham(kullanici)
    toplam_gider = 0.0
    if not df_takvim_ham.empty and 'maliyet' in df_takvim_ham.columns:
        toplam_gider = df_takvim_ham['maliyet'].sum()
        
    baz_getiri = {"Pamuk": 150000, "Zeytin": 200000, "Buğday": 80000, "Mısır": 120000, "Ayçiçeği": 95000, "Narenciye": 180000, "Domates": 110000}
    tahmini_gelir = baz_getiri.get(urun_turu, 100000)
    beklenen_kar = tahmini_gelir - toplam_gider

    # --- ARAYÜZ YÜKLEMESİ BAŞLIYOR ---
    col_header_text, col_header_logout_btn = st.columns([8.5, 1.5])
    with col_header_text:
        st.subheader(f"🌾 AI Akıllı Tarım Kontrol Merkezi | {tarla_adi.upper()}")
        st.caption(f"Yönetici: {kullanici.upper()} ({rol}) | Ada/Parsel: {ada}/{parsel}")
    with col_header_logout_btn:
        st.write("") 
        if st.button("🚪 Çıkış Yap", type="primary", use_container_width=True):
            st.session_state["giris_yapildi"] = False
            st.session_state["aktif_kullanici"] = ""
            st.rerun()

    st.markdown(" ")

    # BİLDİRİM VE ALARM MERKEZİ
    if ai_durum == "error" or h_skor >= 75:
        st.error(f"🚨 **KRİTİK ALARM:** Yapay zeka tarlada risk tespit etti! Eylem planı **{m_email}** adresinize ve cep telefonunuza iletilmiştir.")
        if "alarm_gosterildi" not in st.session_state or not st.session_state["alarm_gosterildi"]:
            st.toast("📲 SMS İLETİLDİ: Sayın Çiftçimiz, tarlanızda kritik durum tespit edildi!", icon="🚨")
            st.session_state["alarm_gosterildi"] = True
    elif ai_durum == "warning" or h_skor >= 40:
        st.warning(f"⚠️ **SİSTEM UYARISI:** Tarlada dikkat edilmesi gereken durumlar var. Detaylar **{m_email}** adresinize iletilmiştir.")
        if "alarm_gosterildi" not in st.session_state or not st.session_state["alarm_gosterildi"]:
            st.toast("📧 E-Posta İLETİLDİ: Rutin dışı hava durumu tespit edildi.", icon="⚠️")
            st.session_state["alarm_gosterildi"] = True
    else:
        st.info(f"✅ **BİLDİRİM MERKEZİ:** Her şey yolunda. Sistem günlük olağan raporu **{m_email}** adresinize gönderdi.")
        st.session_state["alarm_gosterildi"] = False

    st.markdown("---")

    col_top_left, col_top_right = st.columns(2) 
    
    with col_top_left:
        if str(rol).strip().lower() == "admin":
            with st.expander("👥 ADMIN PERSONEL YETKİLENDİRME BÖLGESİ", expanded=False):
                p_kadi = st.text_input("Personel Kullanıcı Adı:", key="pk_admin")
                p_sifre = st.text_input("Personel Giriş Şifresi:", type="password", key="ps_admin")
                p_rol = st.selectbox("Atanacak Unvan:", ["Ziraat Mühendisi", "Saha Personeli", "Traktör Operatörü"], key="prole_admin")
                
                if st.button("🚀 Personel Atamasını Onayla", use_container_width=True):
                    if p_kadi and p_sifre:
                        sql_calisan_ekle(p_kadi, p_sifre, tarla_adi, t_enlem, t_boylam, "kurumsal@tarim.com", urun_turu, p_rol, ada, parsel)
                        st.success(f"🎉 {p_kadi} isimli personel atandı.")
                    else:
                        st.warning("Lütfen alanları doldurun.")
        else:
            st.info("Personel yetkilendirme alanı yalnızca Admin rolüne açıktır.")

    with col_top_right:
        with st.expander("🖨️ GELİŞMİŞ ÇIKTI VE RAPORLAMA MERKEZİ", expanded=False):
            st.caption("Yapay zeka analiz raporunuzu kurumsal formatta PDF olarak yazdırılmak üzere indirebilirsiniz.")
            
            # YENİ NESİL HTML KURUMSAL RAPOR OLUŞTURUCU
            html_rapor = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <title>Akıllı Tarım Raporu</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #2c3e50; background-color: #ffffff; }}
                .header {{ text-align: center; border-bottom: 3px solid #2ecc71; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #27ae60; margin: 0; font-size: 28px; }}
                .header p {{ color: #7f8c8d; font-size: 14px; margin-top: 5px; }}
                .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                .info-table th, .info-table td {{ border: 1px solid #e0e0e0; padding: 12px; text-align: left; }}
                .info-table th {{ background-color: #f8f9fa; width: 35%; font-weight: 600; color: #34495e; }}
                .section-title {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-top: 30px; font-size: 18px; }}
                .box {{ padding: 15px; border-radius: 8px; margin-bottom: 15px; font-weight: bold; }}
                .box-success {{ background-color: #eaeded; color: #27ae60; border-left: 5px solid #27ae60; }}
                .box-warning {{ background-color: #fef9e7; color: #d35400; border-left: 5px solid #f39c12; }}
                .box-danger {{ background-color: #fdedec; color: #c0392b; border-left: 5px solid #e74c3c; }}
            </style>
            </head>
            <body>
                <div class="header">
                    <h1>🌾 AI Akıllı Tarım Platformu</h1>
                    <h2 style="color:#2c3e50; margin-top: 10px;">Resmi Saha ve Finans Raporu</h2>
                    <p>Oluşturulma Tarihi: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>

                <h3 class="section-title">📍 Müşteri ve Tesis Bilgileri</h3>
                <table class="info-table">
                    <tr><th>Mülk Sahibi</th><td>{kullanici.upper()}</td></tr>
                    <tr><th>Tesis Adı</th><td>{tarla_adi.upper()}</td></tr>
                    <tr><th>Ada / Parsel</th><td>{ada} / {parsel}</td></tr>
                    <tr><th>Yetiştirilen Mahsul</th><td>{urun_turu}</td></tr>
                </table>

                <h3 class="section-title">📊 Anlık Çevresel Metrikler</h3>
                <table class="info-table">
                    <tr><th>Hava Sıcaklığı (Bölgesel)</th><td>{canli_sicaklik} °C</td></tr>
                    <tr><th>Sensör Toprak Nemi</th><td>%{toprak_nemi}</td></tr>
                </table>

                <h3 class="section-title">🤖 Yapay Zeka Karar Merkezi</h3>
                <div class="box {css_durum}">
                    💧 Sulama Kararı: {ai_mesaj}
                </div>
                <div class="box {h_css}">
                    🦠 Hastalık Riski ({h_adi}): %{h_skor} <br><br> Tespit: {h_mesaj}
                </div>

                <h3 class="section-title">💰 Finansal Analiz ve Bütçe (Sezonluk)</h3>
                <table class="info-table">
                    <tr><th>Toplam Operasyonel Gider</th><td>₺ {toplam_gider:,.2f}</td></tr>
                    <tr><th>Tahmini Hasat Geliri</th><td>₺ {tahmini_gelir:,.2f}</td></tr>
                    <tr><th>Beklenen Net Kâr / Zarar Durumu</th><td>₺ {beklenen_kar:,.2f}</td></tr>
                </table>
                
                <p style="text-align: center; color: #95a5a6; font-size: 11px; margin-top: 50px;">
                    Bu belge AI Akıllı Tarım Platformu algoritmaları tarafından otomatik olarak üretilmiş resmi bir analiz raporudur.<br>
                    Yazdır (Ctrl + P) kısayolunu kullanarak PDF olarak arşivleyebilirsiniz.
                </p>
            </body>
            </html>
            """
            
            st.download_button(
                label="📄 Kurumsal Web Raporunu İndir (.html / PDF'e Uygun)",
                data=html_rapor,
                file_name=f"{kullanici}_resmi_rapor.html",
                mime="text/html",
                use_container_width=True
            )

    st.markdown("---")

    col_yenile, _ = st.columns([2, 8])
    with col_yenile:
        if st.button("🔄 Sensörleri Oku (Canlı API Veri Al)", use_container_width=True):
            guncel_isi = gercek_hava_durumu_getir(t_enlem, t_boylam)
            if guncel_isi is not None:
                st.session_state["canli_sicaklik"] = guncel_isi
            else:
                st.session_state["canli_sicaklik"] = random.randint(22, 38)
            st.session_state["toprak_nemi"] = akilli_nem_simulasyonu()
            st.session_state["alarm_gosterildi"] = False 
            st.rerun()

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
        st.subheader("📉 Canlı Metrikler & AI Vana", divider="blue")
        st.write("Hava Sıcaklığı (Canlı API) / Mahsul")
        st.subheader(f"{canli_sicaklik} °C")
        st.caption(f"⬆️ {urun_turu}")
        
        st.write("Anlık Toprak Nemi")
        st.subheader(f"%{toprak_nemi}")
        st.caption("⬆️ Hedef: %40-%70")
        
        if ai_durum == "error":
            st.error(f"**AI SULAMA KARARI:**\n\n{ai_mesaj}")
        elif ai_durum == "warning":
            st.warning(f"**AI SULAMA KARARI:**\n\n{ai_mesaj}")
        else:
            st.success(f"**AI SULAMA KARARI:**\n\n{ai_mesaj}")
            
        st.write(" ")
        st.write(f"🦠 **AI Hastalık Risk Analizi ({h_adi})**")
        st.progress(h_skor / 100)
        if h_skor >= 75:
            st.error(f"Risk Oranı: %{h_skor}\n\n{h_mesaj}")
        elif h_skor >= 40:
            st.warning(f"Risk Oranı: %{h_skor}\n\n{h_mesaj}")
        else:
            st.success(f"Risk Oranı: %{h_skor}\n\n{h_mesaj}")

        st.write(" ")
        if st.button("💾 Analizi Günlükle", use_container_width=True):
            su_anki_zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql_analiz_kaydet(kullanici, int(toprak_nemi), float(canli_sicaklik), ai_mesaj)
            st.toast("Veriler veritabanına başarıyla işlendi!")
            st.rerun()

    with col_box2:
        st.subheader("🗺️ Tarlanın Coğrafi Konumu", divider="green")
        tarla_df = pd.DataFrame({'lat': [t_enlem], 'lon': [t_boylam]})
        st.map(tarla_df, size=14, zoom=11)
        st.caption(f"📍 Enlem: {t_enlem} | Boylam: {t_boylam} (Harita Lokasyonu)")

    with col_box3:
        st.subheader("📊 Verimlilik & Tasarruf Raporu", divider="orange")
        st.write("AI Su Tasarruf Başarısı")
        st.subheader(f"%{int(tasarruf_orani * 100)}")
        st.progress(tasarruf_orani)
        st.caption(f"Sistem üzerinden toplam {toplam_kayit} adet AI optimizasyon kaydı doğrulandı.")
        
        st.write("---")
        st.caption("📈 **Son Günlüklenen Toprak Nem Geçmişi (%)**")
        
        if not df_kayitlar.empty:
            df_grafik = df_kayitlar.iloc[::-1].reset_index()
            st.line_chart(df_grafik['nem'])
        else:
            st.write("Henüz veri bulunmuyor.")

        st.markdown(" ")
        df_tum_veri = sql_tum_veriyi_getir(kullanici)
        if not df_tum_veri.empty:
            csv_veri = df_tum_veri.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Yapay Zeka İçin Veri Setini İndir (.csv)",
                data=csv_veri,
                file_name=f"{kullanici}_ml_veri_seti.csv",
                mime="text/csv",
                use_container_width=True
            )

    # --- FİNANSAL ANALİZ PANOSU ---
    st.markdown("---")
    st.subheader("💰 Finansal Analiz & Sezonluk Bütçe Raporu", divider="red")
    
    col_fin1, col_fin2, col_fin3 = st.columns(3)
    col_fin1.metric(label="Toplam Operasyonel Gider (TL)", value=f"₺ {toplam_gider:,.2f}")
    col_fin2.metric(label=f"Tahmini Hasat Geliri ({urun_turu})", value=f"₺ {tahmini_gelir:,.2f}")
    col_fin3.metric(label="Beklenen Net Kâr (TL)", value=f"₺ {beklenen_kar:,.2f}", delta=f"{'Kârlı' if beklenen_kar > 0 else 'Zarar Riski'}")

    # --- CANLI TARIM AJANDASI VE GÜNCELLEME ALANI ---
    st.markdown("---")
    st.subheader("📅 Dijital Tarım Ajandası & Görev Takibi", divider="gray")
    
    col_ajanda1, col_ajanda2 = st.columns([1, 2.5])
    
    with col_ajanda1:
        with st.form("yeni_gorev_formu"):
            st.write("**Yeni Faaliyet Planla**")
            yeni_islem = st.selectbox("İşlem Türü:", ["Gübreleme", "İlaçlama", "Hasat", "Toprak Analizi", "Budama", "Sulama (Manuel)", "İşçi Maliyeti", "Diğer"])
            yeni_tarih = st.date_input("Planlanan Tarih:")
            yeni_maliyet = st.number_input("Tahmini Maliyet / Gider (TL):", min_value=0.0, step=100.0)
            yeni_not = st.text_input("Durum / Notlar:", value="Planlandı")
            
            if st.form_submit_button("🗓️ Takvime İşle", use_container_width=True):
                sql_takvim_etkinlik_ekle(kullanici, yeni_islem, str(yeni_tarih), yeni_not, float(yeni_maliyet))
                st.success("Faaliyet başarıyla kaydedildi!")
                st.rerun()
                
    with col_ajanda2:
        st.write("**Planlanan ve Geçmiş Görevleriniz**")
        
        if not df_takvim_ham.empty:
            df_gosterim = df_takvim_ham.copy()
            if 'maliyet' not in df_gosterim.columns:
                df_gosterim['maliyet'] = 0.0
            
            df_gosterim = df_gosterim.rename(columns={"islem_turu": "Faaliyet Türü", "tarih": "Planlanan Tarih", "notlar": "Durum / Notlar", "maliyet": "Maliyet (TL)"})
            st.dataframe(df_gosterim[["Faaliyet Türü", "Planlanan Tarih", "Maliyet (TL)", "Durum / Notlar"]], use_container_width=True, hide_index=True)
            
            st.write("---")
            st.write("**✏️ Mevcut Bir Görevi Güncelle veya Sil**")
            
            gorev_secenekleri = df_takvim_ham.apply(lambda row: f"ID:{row['id']} | {row['islem_turu']} ({row['tarih']})", axis=1).tolist()
            secilen_gorev_metin = st.selectbox("Düzenlemek istediğiniz görevi seçin:", gorev_secenekleri)
            
            if secilen_gorev_metin:
                secilen_id = int(secilen_gorev_metin.split("|")[0].replace("ID:", "").strip())
                secilen_satir = df_takvim_ham[df_takvim_ham['id'] == secilen_id].iloc[0]
                
                c1, c2, c3, c4 = st.columns([1, 1, 1, 1.5])
                with c1:
                    mevcut_tarih_str = secilen_satir['tarih']
                    try:
                        mevcut_tarih = datetime.strptime(mevcut_tarih_str, "%Y-%m-%d").date()
                    except:
                        mevcut_tarih = datetime.now().date()
                    yeni_guncel_tarih = st.date_input("Yeni Tarih:", value=mevcut_tarih, key=f"date_{secilen_id}")
                
                with c2:
                    eski_maliyet = float(secilen_satir['maliyet']) if 'maliyet' in secilen_satir else 0.0
                    yeni_guncel_maliyet = st.number_input("Maliyet (TL):", value=eski_maliyet, key=f"mal_{secilen_id}", step=100.0)

                with c3:
                    yeni_guncel_not = st.text_input("Yeni Not / Durum:", value=secilen_satir['notlar'], key=f"not_{secilen_id}")
                    
                with c4:
                    st.write(" ")
                    st.write(" ")
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("🔄 Güncelle", key=f"btn_guncelle_{secilen_id}", use_container_width=True):
                            sql_takvim_etkinlik_guncelle(secilen_id, str(yeni_guncel_tarih), yeni_guncel_not, float(yeni_guncel_maliyet))
                            st.success("Görev başarıyla güncellendi!")
                            st.rerun()
                    with col_btn2:
                        if st.button("🗑️ Sil", key=f"btn_sil_{secilen_id}", use_container_width=True):
                            sql_takvim_etkinlik_sil(secilen_id)
                            st.error("Görev tablodan tamamen silindi!")
                            st.rerun()
        else:
            st.info("Henüz planlanmış bir tarımsal faaliyetiniz bulunmuyor. Sol taraftaki paneli kullanarak yeni bir görev ekleyebilirsiniz.")
