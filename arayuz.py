# ==============================================================================
# PROJE: AI Destekli Akıllı Tarım Platformu (HASTALIK RİSK ANALİZ MODÜLÜ ENTEGRELİ)
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

# --- YENİ: YAPAY ZEKA HASTALIK RİSK TAHMİN MOTORU ---
def ai_hastalik_risk_analizi(urun, sicaklik, nem):
    """Hava durumu verilerine göre ürüne özel hastalık riskini hesaplar."""
    risk_skoru = 10 # Başlangıç baz risk skoru (%)
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
            
    else: # Diğer genel ürünler için kök çürüklüğü riski
        hastalik_adi = "Kök Çürüklüğü & Mantar"
        if nem > 75:
            risk_skoru = 80
            detay_mesaj = "🚨 Aşırı toprak nemi köklerin nefes almasını engelliyor ve çürüme mantarlarını besliyor!"

    return hastalik_adi, risk_skoru, detay_mesaj

# --- VERİTABANI KURULUMU ---
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

def sql_takvim_etkinlik_ekle(k_adi, islem, tarih, notlar):
    baglanti = sqlite3.connect("akilli_tarim.db")
    kursor = baglanti.cursor()
    kursor.execute("INSERT INTO tarim_takvimi (kullanici_adi, islem_turu, tarih, notlar) VALUES (?, ?, ?, ?)", (k_adi, islem, tarih, notlar))
    baglanti.commit()
    baglanti.close()

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

    if "toprak_nemi" not in st.session_state:
        st.session_state["toprak_nemi"] = akilli_nem_simulasyonu()
        gercek_isi = gercek_hava_durumu_getir(t_enlem, t_boylam)
        st.session_state["canli_sicaklik"] = gercek_isi if gercek_isi is not None else random.randint(22, 38)
        
    toprak_nemi = st.session_state["toprak_nemi"]
    canli_sicaklik = st.session_state["canli_sicaklik"]

    with col_top_right:
        with st.expander("🖨️ RAPORLAMA ÇIKTI İSTASYON MERKEZİ", expanded=False):
            st.caption("Yapay zeka analiz raporunu resmi kurumsal evrak olarak hemen indirebilirsiniz.")
            
            rapor_icerigi = f"""============================================================
AI AKILLI TARIM PLATFORMU - RESMİ TARLA DURUM RAPORU
============================================================
Mülk Sahibi: {kullanici.upper()} | Konum: {tarla_adi.upper()}
Ada / Parsel No: {ada} / {parsel} | Mahsul Türü: {urun_turu}
------------------------------------------------------------
ANLIK ANALİZ VERİLERİ (Tarih: {datetime.now().strftime("%Y-%m-%d %H:%M")}):
Hava Sıcaklığı (Canlı API): {canli_sicaklik} °C | Toprak Nemi: %{toprak_nemi}
============================================================
"""
            st.download_button(
                label="📄 Kurumsal Tarla Raporunu İndir (.txt)",
                data=rapor_icerigi,
                file_name=f"{kullanici}_tarla_raporu.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.markdown("---")

    col_yenile, _ = st.columns([2, 8])
    with col_yenile:
        if st.button("🔄 Sensörleri Oku (Canlı API Veri Al)", use_container_width=True):
            guncel_isi = gercek_hava_durumu_getir(t_enlem, t_boylam)
            if guncel_isi is not None:
                st.session_state["canli_sicaklik"] = guncel_isi
                st.toast(f"☁️ Gerçek hava durumu verisi çekildi: {guncel_isi}°C")
            else:
                st.session_state["canli_sicaklik"] = random.randint(22, 38)
                st.toast("⚠️ API'ye ulaşılamadı, yedek simülasyon devrede.")
            st.session_state["toprak_nemi"] = akilli_nem_simulasyonu()
            st.rerun()

    if toprak_nemi < 30 and canli_sicaklik > 30:
        ai_mesaj = "🔥 KRİTİK: Toprak kuru, hava sıcak! Acil sulama başlatıldı."
        ai_durum = "error"
    elif toprak_nemi < 30:
        ai_mesaj = "💧 UYARI: Nem düşük, standart sulama açıldı."
        ai_durum = "warning"
    else:
        ai_mesaj = "✅ NORMAL: Nem yeterli, sulama kapalı. Su tasarrufu yapılıyor."
        ai_durum = "success"

    st.markdown(" ")

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
            
        # YENİ: HASTALIK RİSK ANALİZ GÖSTERİMİ
        st.write(" ")
        h_adi, h_skor, h_mesaj = ai_hastalik_risk_analizi(urun_turu, canli_sicaklik, toprak_nemi)
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

    st.markdown("---")

    with st.expander("📅 Dijital Tarım Ajandası & İş Planlama Faaliyetleri", expanded=False):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            islem = st.selectbox("İşlem:", ["Gübreleme", "İlaçlama", "Hasat"], key="task_ajanda")
        with col_t2:
            tarih = st.date_input("Tarih:", key="date_ajanda")
            if st.button("🗓️ Takvime İşle", use_container_width=True):
                sql_takvim_etkinlik_ekle(kullanici, islem, str(tarih), "Planlandı")
                st.success("İşlem başarıyla takvime kaydedildi.")
