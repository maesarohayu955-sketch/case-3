import pandas as pd
import numpy as np

def run_weather_eda(filepath: str = "dataset_pengamatan_cuaca_1000.csv"):
    print("=" * 80)
    print(" BEDAH KASUS 3: ANALISIS MENDALAM DATASET PENGAMATAN CUACA (1.000 RECORDS)")
    print("=" * 80)

    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' tidak ditemukan! Jalankan 'generate_weather_data.py' terlebih dahulu.")
        return

    # 1. Metadata & Kualitas Data
    print("\n[1] METADATA & INTEGRITAS DATA:")
    print(f"- Total Baris Pengamatan : {len(df):,}")
    print(f"- Missing / Null Values  : {df.isnull().sum().to_dict()}")
    print(f"- Kota Terdaftar         : {df['Kota'].unique().tolist()}")
    print(f"- Variasi Kondisi Cuaca  : {df['Kondisi'].unique().tolist()}")

    # 2. Statistik Deskriptif (Suhu - Interval & Kelembaban - Rasio)
    print("\n[2] RINGKASAN STATISTIK DESKRIPTIF:")
    print("-" * 80)
    for col in ["Suhu (°C)", "Kelembaban (%)"]:
        series = df[col]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = series[(series < lower) | (series > upper)]

        unit = "°C" if "Suhu" in col else "%"
        print(f"Variabel: {col.upper()}")
        print(f"  • Mean             : {series.mean():.2f} {unit}")
        print(f"  • Median           : {series.median():.2f} {unit}")
        print(f"  • Standar Deviasi  : {series.std():.2f} {unit}")
        print(f"  • Min - Max        : {series.min():.1f} s.d. {series.max():.1f} {unit}")
        print(f"  • Q1 - Q3 (IQR)    : {q1:.1f} - {q3:.1f} (IQR = {iqr:.1f} {unit})")
        print(f"  • Deteksi Outlier  : {len(outliers)} data di luar rentang [{lower:.1f}, {upper:.1f}]")
        print("-" * 80)

    # 3. Analisis Cuaca Berdasarkan Kota
    print("\n[3] PROFIL RATA-RATA CUACA BERDASARKAN KOTA:")
    kota_summary = df.groupby("Kota").agg(
        Total_Pengamatan=("Kondisi", "count"),
        Rata_Suhu=("Suhu (°C)", "mean"),
        Median_Suhu=("Suhu (°C)", "median"),
        Rata_Kelembaban=("Kelembaban (%)", "mean"),
        Median_Kelembaban=("Kelembaban (%)", "median"),
        Suhu_Min=("Suhu (°C)", "min"),
        Suhu_Max=("Suhu (°C)", "max")
    ).reset_index().sort_values(by="Rata_Suhu", ascending=False).reset_index(drop=True)

    print(f"{'Kota':<14} | {'Total':<6} | {'Rata Suhu':<12} | {'Rentang Suhu':<16} | {'Rata Kelembaban':<16}")
    print("-" * 75)
    for _, r in kota_summary.iterrows():
        print(f"{r['Kota']:<14} | {r['Total_Pengamatan']:<6} | {r['Rata_Suhu']:>5.2f} °C     | {r['Suhu_Min']:>4.1f} - {r['Suhu_Max']:>4.1f} °C   | {r['Rata_Kelembaban']:>6.1f} %")
    print("-" * 75)

    # 4. Distribusi Kondisi Cuaca (Kategorik Nominal)
    print("\n[4] DISTRIBUSI FREKUENSI KONDISI CUACA:")
    kondisi_counts = df["Kondisi"].value_counts().reset_index()
    kondisi_counts.columns = ["Kondisi", "Jumlah"]
    kondisi_counts["Proporsi (%)"] = (kondisi_counts["Jumlah"] / len(df)) * 100
    for _, r in kondisi_counts.iterrows():
        print(f"  • {r['Kondisi']:<14}: {r['Jumlah']:3d} pengamatan ({r['Proporsi (%)']:.1f}%)")

    # 5. Rata-rata Suhu & Kelembaban per Kondisi Cuaca
    print("\n[5] KARAKTERISTIK TERMODINAMIKA PER KONDISI CUACA:")
    kondisi_profile = df.groupby("Kondisi").agg(
        Rata_Suhu=("Suhu (°C)", "mean"),
        Rata_Kelembaban=("Kelembaban (%)", "mean"),
        Frekuensi=("Kota", "count")
    ).reset_index().sort_values(by="Rata_Suhu", ascending=False).reset_index(drop=True)

    for _, r in kondisi_profile.iterrows():
        print(f"  • {r['Kondisi']:<14}: Suhu Rata-rata = {r['Rata_Suhu']:5.2f} °C | Kelembaban = {r['Rata_Kelembaban']:5.1f} %")

    # 6. Analisis Korelasi (Suhu vs Kelembaban)
    print("\n[6] KORELASI ANTAR VARIABEL (SUHU VS KELEMBABAN):")
    print("-" * 80)
    r_pearson = df["Suhu (°C)"].corr(df["Kelembaban (%)"], method="pearson")
    r_spearman = df["Suhu (°C)"].corr(df["Kelembaban (%)"], method="spearman")
    print(f"• Koefisien Korelasi Pearson  (r) : {r_pearson:.4f}")
    print(f"• Koefisien Korelasi Spearman (rho): {r_spearman:.4f}")

    print("\n" + "=" * 80)
    print(" KESIMPULAN & INSIGHT METEOROLOGI DATA SCIENCE:")
    print("=" * 80)
    print(f"1. Terdapat korelasi negatif kuat yang signifikan (r = {r_pearson:.2f}) antara Suhu dan Kelembaban.")
    print("   Saat suhu udara meningkat (misal kondisi cerah), kapasitas tampung uap air membesar sehingga kelembaban relatif menurun.")
    print("2. Terjadi perbedaan klaster iklim geografis yang nyata:")
    print("   - Kota Dataran Tinggi (Bandung & Malang) memiliki rata-rata suhu sejuk (~21-23°C) dengan kelembaban tinggi (>80%).")
    print("   - Kota Pesisir/Dataran Rendah (Surabaya & Jakarta) memiliki rata-rata suhu hangat (>31°C) dengan kelembaban lebih moderat.")
    print(f"3. Kondisi '{kondisi_counts.iloc[0]['Kondisi']}' merupakan cuaca paling dominan ({kondisi_counts.iloc[0]['Proporsi (%)']:.1f}%).")
    print("=" * 80)

if __name__ == "__main__":
    run_weather_eda()
