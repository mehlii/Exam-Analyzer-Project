import pdfplumber
import pandas as pd
import os

def extract_exam_data(pdf_path):
    if not os.path.isabs(pdf_path):
        pdf_path = os.path.join(os.getcwd(), pdf_path)

    all_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_data.append(df)
        
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            print("\n[✓] PDF BAŞARIYLA OKUNDU (Tablo Bulundu)\n")
            return final_df
        else:
             print("\n[!] DİKKAT: PDF içinde belirgin bir tablo bulunamadı.\n")
             return None
             
    except FileNotFoundError:
        print(f"\n[X] HATA: '{pdf_path}' adlı dosya bulunamadı. Lütfen klasörü kontrol edin.\n")
        return None
    except Exception as e:
        print(f"\n[X] HATA: Okuma sırasında bir sorun oluştu -> {e}\n")
        return None


if __name__ == "__main__":
    test_df = extract_exam_data("kayra_test.pdf") # Dosya adını güncelledik
    if test_df is not None:
         print(test_df)