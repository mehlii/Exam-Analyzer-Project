import pandas as pd
import re

def clean_dataframe(df):
    """
    Bu fonksiyon o çirkin, NaN dolu PDF verisinin içine dalar,
    sadece ders isimlerini bulur ve yanındaki sayıları cımbızla çeker.
    """
    if df is None or df.empty:
        return None

    print("\n[!] Veri temizleniyor, çöpler atılıyor...")

    # Aradığımız derslerin listesi
    dersler = ["Türkçe", "Tarih", "Din K.ve A.B.", "İngilizce", "Matematik", "Fen"]
    temiz_satirlar = []

    # 1. Tablodaki tüm NaN (boş) değerleri sil ve her şeyi metne (string) çevir
    df = df.fillna("")
    df = df.astype(str)

    # 2. Satır satır gezip avlanmaya başla
    for index, row in df.iterrows():
        # Satırdaki tüm parçaları birleştirip tek bir uzun cümle yapıyoruz
        satir_metni = " ".join(row.values)
        
        for ders in dersler:
            if ders in satir_metni:
                # Dersi bulduk! Şimdi içindeki çöpleri (\n, .., virgüller) temizle
                temiz_metin = satir_metni.replace("\\n", " ").replace("..", " ").replace("\n", " ").replace(",", ".")
                
                # Sadece sayıları avla (virgüllü veya tam sayılar)
                sayilar = re.findall(r'\b\d+(?:\.\d+)?\b', temiz_metin)
                
                # O satırda Soru, Doğru, Yanlış, Net sayılarını yakaladıysak listeye ekle
                if len(sayilar) >= 4:
                    temiz_satirlar.append({
                        "Ders": ders,
                        "Doğru": float(sayilar[1]), # 2. sayı genelde Doğrudur
                        "Yanlış": float(sayilar[2]), # 3. sayı genelde Yanlıştır
                        "Net": float(sayilar[3])  # 4. sayı genelde Nettir
                    })
                break # Bu satırın işi bitti, diğerine geç
                
    # 3. Temiz satırlardan pırıl pırıl yeni bir tablo oluştur
    temiz_df = pd.DataFrame(temiz_satirlar)
    
    print("[✓] VERİ TEMİZLİĞİ TAMAMLANDI\n")
    return temiz_df

# === TEST ALANI ===
if __name__ == "__main__":
    from pdf_reader import extract_exam_data
    
    # 1. Veriyi çek (Dosya adını düzelttik!)
    ham_veri = extract_exam_data("kayra_test.pdf") 
    
    if ham_veri is not None:
        # 2. Veriyi temizle
        temiz_veri = clean_dataframe(ham_veri)
        print("--- İŞTE PIRIL PIRIL TEMİZLENMİŞ VERİ ---")
        print(temiz_veri)