from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

def predict_next_score(df):
    """
    Lineer regresyon kullanarak bir sonraki sınav notunu tahmin eder.
    """
    # Tahmin yapabilmek için en az 2 sınav verisi gerekir
    if len(df) < 2:
        return 0.0, 0.0

    # 1. Hazırlık: Tarihleri sayısal bir formata (ordinal) çeviriyoruz
    # Makine öğrenmesi modeli tarihleri doğrudan okuyamaz, sayıya ihtiyaç duyar.
    df['date_ordinal'] = df['exam_date'].map(pd.Timestamp.toordinal)
    
    X = df[['date_ordinal']].values  # Bağımsız değişken (Tarih)
    y = df['score'].values           # Bağımlı değişken (Not)

    # 2. Modeli Oluştur ve Eğit
    model = LinearRegression()
    model.fit(X, y)

    # 3. Tahmin Yap: Son sınav tarihinden 30 gün sonrası için tahmin üret
    last_date = df['date_ordinal'].max()
    next_exam_date = np.array([[last_date + 30]]) 
    predicted_score = model.predict(next_exam_date)[0]

    # 4. Model Başarısı (R² Skoru): Tahminin ne kadar güvenilir olduğunu gösterir
    r2 = model.score(X, y)

    # Nisa'nın beklediği iki değeri (tahmin notu ve başarı oranı) döndürüyoruz
    return round(float(predicted_score), 2), round(float(r2), 2)