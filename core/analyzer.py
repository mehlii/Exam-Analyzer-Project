import pandas as pd

def compute_summary(df):
    """
    Sınav verilerini analiz eder (Ortalama, Standart Sapma vb.)
    Mehlika'dan gelen temizlenmiş tabloyu (df) kullanır.
    """
    # Eğer tablo boşsa hata vermemesi için boş bir sözlük dönüyoruz
    if df.empty:
        return {}

    summary = {
        # Genel ortalamayı hesaplar
        "average": round(df['score'].mean(), 2),
        
        # En yüksek ve en düşük notları bulur
        "max_score": int(df['score'].max()),
        "min_score": int(df['score'].min()),
        
        # Ders bazlı ortalamaları hesaplar (Sema bu veriyi grafik yapacak)
        "subject_averages": df.groupby('subject')['score'].mean().to_dict()
    }
    
    return summary