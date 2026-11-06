import numpy as np
import pandas as pd

def generate_weather_dataset(num_records: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Menghasilkan dataset pengamatan cuaca sintetik yang realistis dan konsisten secara meteorologi.
    
    Variabel & Karakteristik Fisika Atmosfer:
    1. Kota: Kategorik Nominal (7 kota di Indonesia dengan variasi elevasi: Pesisir vs Dataran Tinggi)
    2. Suhu (°C): Numerik Interval (Suhu terpengaruh oleh elevasi kota & kondisi cuaca)
    3. Kelembaban (%): Numerik Rasio (Berkorelasi negatif dengan suhu; hujan menghasilkan kelembaban mendekati jenuh)
    4. Kondisi: Kategorik Nominal (Cerah, Berawan, Hujan Ringan, Hujan Lebat, Badai Petir)
    """
    np.random.seed(seed)

    # Profil dasar kota di Indonesia (Elevasi & Rata-rata Suhu Dasar)
    city_profiles = {
        "Jakarta": {"base_temp": 31.5, "temp_std": 1.8, "base_humidity": 74, "weight": 0.18},
        "Surabaya": {"base_temp": 32.2, "temp_std": 1.9, "base_humidity": 70, "weight": 0.16},
        "Bandung": {"base_temp": 22.8, "temp_std": 1.6, "base_humidity": 82, "weight": 0.16},
        "Yogyakarta": {"base_temp": 28.5, "temp_std": 1.7, "base_humidity": 78, "weight": 0.14},
        "Medan": {"base_temp": 29.8, "temp_std": 1.8, "base_humidity": 80, "weight": 0.14},
        "Makassar": {"base_temp": 30.5, "temp_std": 1.7, "base_humidity": 76, "weight": 0.12},
        "Malang": {"base_temp": 21.5, "temp_std": 1.5, "base_humidity": 84, "weight": 0.10}
    }

    cities = list(city_profiles.keys())
    city_weights = [city_profiles[c]["weight"] for c in cities]

    # Kondisi cuaca dengan dampak termodinamika (efek terhadap suhu & kelembaban)
    weather_conditions = ["Cerah", "Berawan", "Hujan Ringan", "Hujan Lebat", "Badai Petir"]
    condition_probs = [0.35, 0.30, 0.20, 0.10, 0.05]

    condition_effects = {
        # Format: (delta_suhu, delta_kelembaban)
        "Cerah": (+2.2, -12.0),
        "Berawan": (+0.2, -2.0),
        "Hujan Ringan": (-1.8, +8.0),
        "Hujan Lebat": (-3.5, +14.0),
        "Badai Petir": (-4.2, +16.0)
    }

    records = []

    for _ in range(num_records):
        # 1. Pilih Kota (Kategorik Nominal)
        kota = np.random.choice(cities, p=city_weights)
        prof = city_profiles[kota]

        # 2. Tentukan Kondisi Cuaca (Kategorik Nominal)
        kondisi = np.random.choice(weather_conditions, p=condition_probs)
        temp_delta, hum_delta = condition_effects[kondisi]

        # 3. Hitung Suhu (°C) - Numerik Interval
        raw_temp = prof["base_temp"] + temp_delta + np.random.normal(0, prof["temp_std"])
        # Suhu iklim tropis Indonesia realistis antara 16.0°C s.d. 37.0°C
        suhu = float(np.round(np.clip(raw_temp, 16.0, 37.5), 1))

        # 4. Hitung Kelembaban (%) - Numerik Rasio
        # Secara fisika atmosfer, saat suhu naik kelembaban relatif turun (korelasi negatif kuat)
        temp_deviation = (suhu - prof["base_temp"])
        raw_hum = prof["base_humidity"] + hum_delta - (temp_deviation * 2.2) + np.random.normal(0, 3.5)
        # Kelembaban relatif dibatasi 45% s.d. 99%
        kelembaban = int(np.clip(np.round(raw_hum), 45, 99))

        records.append({
            "Kota": kota,
            "Suhu (°C)": suhu,
            "Kelembaban (%)": kelembaban,
            "Kondisi": kondisi
        })

    df = pd.DataFrame(records)
    # Urutkan berdasarkan Kota lalu Kondisi untuk struktur data rapi
    df = df.sort_values(by=["Kota", "Kondisi"]).reset_index(drop=True)
    return df

if __name__ == "__main__":
    output_csv = "dataset_pengamatan_cuaca_1000.csv"
    print("Membuat 1.000 data sintesis pengamatan cuaca realistis...")
    df_weather = generate_weather_dataset(1000, seed=42)
    df_weather.to_csv(output_csv, index=False)
    print(f"[SUKSES] Dataset berhasil disimpan di: {output_csv}")
    print("\n--- 5 Baris Pertama ---")
    print(df_weather.head())
    print("\n--- Statistik Deskriptif ---")
    print(df_weather.describe())
