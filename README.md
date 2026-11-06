LINK STREIMLIT : https://case-3-zbf3mogh8nsg3he3wq6vhe.streamlit.app/
# Panduan Eksekusi Bedah Kasus 3: Dataset Pengamatan Cuaca

## 📁 Struktur Direktori
```text
bedah_kasus_cuaca/
├── generate_weather_data.py          # Generator 1.000 data sintesis pengamatan cuaca
├── dataset_pengamatan_cuaca_1000.csv # File CSV 1.000 baris record pengamatan cuaca
├── eda_weather_analysis.py           # Analisis mendalam meteorologi (Pandas/NumPy)
├── app3.py                           # Aplikasi Web Dashboard Interaktif Streamlit
├── requirements.txt                  # Dependensi pustaka Python
└── README.md                         # Dokumentasi & panduan
```

## 🚀 Perintah Menjalankan Aplikasi di Terminal

1. **Masuk ke folder proyek:**
   ```bash
   cd "C:\Users\User_PC\.gemini\antigravity\scratch\bedah_kasus_cuaca"
   ```

2. **Install dependensi pustaka:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate data cuaca (1.000 records):**
   ```bash
   python generate_weather_data.py
   ```

4. **Jalankan analisis data mendalam (EDA):**
   ```bash
   python eda_weather_analysis.py
   ```

5. **Jalankan aplikasi web Streamlit:**
   ```bash
   streamlit run app3.py
   ```

## 🌐 Tautan Akses Lokal:
Setelah perintah dijalankan, akses dashboard di browser melalui:
- **Local URL:** `http://localhost:8501`
- **Network URL:** `http://<ip-lokal-anda>:8501`
