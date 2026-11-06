import os
import warnings
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Mengabaikan warning deprecation agar terminal dan UI bersih sempurna
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ==============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Pengamatan Cuaca 2024",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. HELPER UNTUK MENCEGAH WARNING 'use_container_width' (STANDAR TERBARU)
# ==============================================================================
def render_plotly(fig, **kwargs):
    """Menampilkan grafik Plotly dengan standar terbaru (width='stretch') tanpa warning."""
    fig.update_layout(autosize=True)
    try:
        st.plotly_chart(fig, width="stretch", theme="streamlit", **kwargs)
    except TypeError:
        try:
            st.plotly_chart(fig, use_container_width=True, theme="streamlit", **kwargs)
        except Exception:
            st.plotly_chart(fig, **kwargs)

def render_dataframe(df_data, **kwargs):
    """Menampilkan dataframe dengan standar terbaru (width='stretch') tanpa warning."""
    try:
        st.dataframe(df_data, width="stretch", **kwargs)
    except TypeError:
        try:
            st.dataframe(df_data, use_container_width=True, **kwargs)
        except Exception:
            st.dataframe(df_data, **kwargs)

# ==============================================================================
# 3. CUSTOM CSS: MODERN, ELEGAN, & HARMONIS (SKY BLUE / CYAN / NAVY)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Creator Badge di Sidebar (Minimalis, Halus, & Elegan) */
    .creator-badge {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .creator-badge-icon {
        font-size: 1.25rem;
    }
    .creator-badge-text {
        font-size: 0.86rem;
        color: #14532d;
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    .creator-badge-nim {
        color: #0284c7;
        font-weight: 700;
    }

    /* Hero Header: Sky / Cyan / Deep Navy Gradien Profesional */
    .hero-container {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 45%, #0f172a 100%);
        border-radius: 16px;
        padding: 24px 30px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 10px 20px -5px rgba(2, 132, 199, 0.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #e0f2fe;
        margin: 6px 0 0 0;
        font-weight: 500;
    }
    .hero-pill {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 8px 16px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #ffffff;
        backdrop-filter: blur(8px);
    }

    /* KPI Cards Layout & Responsive Typography */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    @media (max-width: 1200px) {
        .kpi-container { grid-template-columns: repeat(3, 1fr); }
    }
    @media (max-width: 768px) {
        .kpi-container { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 500px) {
        .kpi-container { grid-template-columns: 1fr; }
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 18px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        border-top: 4px solid #0284c7;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    }
    .kpi-card.sky    { border-top-color: #0284c7; }
    .kpi-card.teal   { border-top-color: #0d9488; }
    .kpi-card.amber  { border-top-color: #ea580c; }
    .kpi-card.blue   { border-top-color: #3b82f6; }
    .kpi-card.violet { border-top-color: #7c3aed; }

    .kpi-label {
        font-size: 0.76rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 4. PENJANAAN DATA SINTESIS (1.000 BARIS) & CACHING DATASET
# ==============================================================================
def create_weather_dataset(num_records: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Menghasilkan 1.000 data pengamatan cuaca sintetik yang realistis dan konsisten secara meteorologi."""
    np.random.seed(seed)

    city_profiles = {
        "Jakarta": {"base_temp": 31.5, "temp_std": 1.8, "base_humidity": 74, "weight": 0.18, "tipe": "Pesisir"},
        "Surabaya": {"base_temp": 32.2, "temp_std": 1.9, "base_humidity": 70, "weight": 0.16, "tipe": "Pesisir"},
        "Bandung": {"base_temp": 22.8, "temp_std": 1.6, "base_humidity": 82, "weight": 0.16, "tipe": "Dataran Tinggi"},
        "Yogyakarta": {"base_temp": 28.5, "temp_std": 1.7, "base_humidity": 78, "weight": 0.14, "tipe": "Dataran Rendah"},
        "Medan": {"base_temp": 29.8, "temp_std": 1.8, "base_humidity": 80, "weight": 0.14, "tipe": "Dataran Rendah"},
        "Makassar": {"base_temp": 30.5, "temp_std": 1.7, "base_humidity": 76, "weight": 0.12, "tipe": "Pesisir"},
        "Malang": {"base_temp": 21.5, "temp_std": 1.5, "base_humidity": 84, "weight": 0.10, "tipe": "Dataran Tinggi"}
    }

    cities = list(city_profiles.keys())
    city_weights = [city_profiles[c]["weight"] for c in cities]

    weather_conditions = ["Cerah", "Berawan", "Hujan Ringan", "Hujan Lebat", "Badai Petir"]
    condition_probs = [0.35, 0.30, 0.20, 0.10, 0.05]

    condition_effects = {
        "Cerah": (+2.2, -12.0),
        "Berawan": (+0.2, -2.0),
        "Hujan Ringan": (-1.8, +8.0),
        "Hujan Lebat": (-3.5, +14.0),
        "Badai Petir": (-4.2, +16.0)
    }

    records = []
    for _ in range(num_records):
        kota = np.random.choice(cities, p=city_weights)
        prof = city_profiles[kota]
        kondisi = np.random.choice(weather_conditions, p=condition_probs)
        temp_delta, hum_delta = condition_effects[kondisi]

        # Suhu (°C) - Skala Interval
        raw_temp = prof["base_temp"] + temp_delta + np.random.normal(0, prof["temp_std"])
        suhu = float(np.round(np.clip(raw_temp, 16.0, 37.5), 1))

        # Kelembaban (%) - Skala Rasio (Korelasi negatif dengan suhu)
        temp_dev = suhu - prof["base_temp"]
        raw_hum = prof["base_humidity"] + hum_delta - (temp_dev * 2.2) + np.random.normal(0, 3.5)
        kelembaban = int(np.clip(np.round(raw_hum), 45, 99))

        records.append({
            "Kota": kota,
            "Suhu (°C)": suhu,
            "Kelembaban (%)": kelembaban,
            "Kondisi Cuaca": kondisi,
            "Tipe Wilayah": prof["tipe"]
        })

    return pd.DataFrame(records).sort_values(by=["Kota", "Kondisi Cuaca"]).reset_index(drop=True)


@st.cache_data
def load_weather_dataset(filepath: str = "dataset_pengamatan_cuaca_1000.csv") -> pd.DataFrame:
    """Membaca dataset cuaca atau membuatnya otomatis jika belum ada / kurang dari 1.000 baris."""
    need_create = False
    if not os.path.exists(filepath):
        need_create = True
    else:
        try:
            df_exist = pd.read_csv(filepath)
            if len(df_exist) < 1000:
                need_create = True
        except Exception:
            need_create = True

    if need_create:
        df = create_weather_dataset(1000, seed=42)
        df.to_csv(filepath, index=False)
    else:
        df = pd.read_csv(filepath)
        if "Kondisi Cuaca" not in df.columns and "Kondisi" in df.columns:
            df["Kondisi Cuaca"] = df["Kondisi"]
        if "Tipe Wilayah" not in df.columns:
            highland = ["Bandung", "Malang"]
            df["Tipe Wilayah"] = df["Kota"].apply(lambda x: "Dataran Tinggi" if x in highland else "Pesisir / Dataran Rendah")
            df.to_csv(filepath, index=False)

    return df


df_raw = load_weather_dataset()


# ==============================================================================
# 5. SIDEBAR: IDENTITAS PEMBUAT (MINIMALIS & ELEGAN) & FILTER INTERAKTIF
# ==============================================================================
with st.sidebar:
    # 🎓 CUKUP TAMPILKAN SATU KALI SAJA: Badge Profil Minimalis & Elegan
    st.markdown("""
    <div class="creator-badge">
        <span class="creator-badge-icon">🎓</span>
        <span class="creator-badge-text">
            <strong>Ayu Maesaroh</strong> • <span class="creator-badge-nim">NIM 241041010</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎛️ Parameter Filter Cuaca")
    st.caption("Gunakan panel ini untuk menyaring pengamatan iklim:")

    # Tombol Reset Filter
    if st.button("🔄 Reset Semua Filter"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")

    # Filter 1: Pilihan Kota (Kategorik Nominal)
    all_cities = sorted(df_raw["Kota"].unique().tolist())
    pilih_semua_kota = st.checkbox("Pilih Semua Kota", value=True)

    if pilih_semua_kota:
        selected_cities = st.multiselect("Stasiun Kota:", options=all_cities, default=all_cities)
    else:
        selected_cities = st.multiselect("Stasiun Kota:", options=all_cities, default=[all_cities[0]])

    # Filter 2: Rentang Suhu (°C) - Skala Interval
    min_temp = float(df_raw["Suhu (°C)"].min())
    max_temp = float(df_raw["Suhu (°C)"].max())
    selected_temp = st.slider("Rentang Suhu (°C):", min_value=15.0, max_value=40.0, value=(min_temp, max_temp), step=0.5)

    st.markdown("---")
    st.markdown("### 📌 Ringkasan Basis Data")
    st.caption(f"• **Total Pengamatan:** {len(df_raw):,} Record")
    st.caption("• **Jumlah Stasiun:** 7 Kota Indonesia")
    st.caption("• **Variabel:** Suhu, Kelembaban, Kondisi")


# ==============================================================================
# 6. FILTERING LOGIC
# ==============================================================================
df_filtered = df_raw[
    (df_raw["Kota"].isin(selected_cities)) &
    (df_raw["Suhu (°C)"] >= selected_temp[0]) &
    (df_raw["Suhu (°C)"] <= selected_temp[1])
].copy()

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data pengamatan cuaca yang cocok dengan parameter filter. Silakan sesuaikan kembali filter di sidebar.")
    st.stop()


# ==============================================================================
# 7. HERO HEADER (RINGKAS & PROFESIONAL)
# ==============================================================================
st.markdown(f"""
<div class="hero-container">
    <div>
        <h1 class="hero-title">🌦️ Executive Weather Observation Analytics</h1>
        <p class="hero-subtitle">Bedah Kasus 3: Pemantauan Klimatologi, Distribusi Suhu, Kelembaban, dan Kondisi Cuaca Antar Wilayah</p>
    </div>
    <div class="hero-pill">
        📍 {len(df_filtered):,} Pengamatan di {len(selected_cities)} Kota Terpilih
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 8. ANALISIS DATA MENDALAM DENGAN PANDAS/NUMPY & KPI CARDS
# ==============================================================================
mean_temp = df_filtered["Suhu (°C)"].mean()
mean_hum = df_filtered["Kelembaban (%)"].mean()

# Kota dengan rata-rata suhu tertinggi & terendah
kota_temp_stats = df_filtered.groupby("Kota")["Suhu (°C)"].mean()
hottest_city = kota_temp_stats.idxmax()
hottest_temp = kota_temp_stats.max()

coolest_city = kota_temp_stats.idxmin()
coolest_temp = kota_temp_stats.min()

dominant_condition = df_filtered["Kondisi Cuaca"].mode().iloc[0]
condition_icons = {
    "Cerah": "☀️ Cerah",
    "Berawan": "⛅ Berawan",
    "Hujan Ringan": "🌦️ Hujan Ringan",
    "Hujan Lebat": "🌧️ Hujan Lebat",
    "Badai Petir": "⛈️ Badai Petir"
}
icon_condition = condition_icons.get(dominant_condition, dominant_condition)

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card sky">
        <div class="kpi-label">🌡️ Rata-Rata Suhu</div>
        <div class="kpi-value">{mean_temp:.1f} °C</div>
        <div class="kpi-sub">Rentang {df_filtered['Suhu (°C)'].min():.1f} – {df_filtered['Suhu (°C)'].max():.1f} °C</div>
    </div>
    <div class="kpi-card teal">
        <div class="kpi-label">💧 Rata-Rata Kelembaban</div>
        <div class="kpi-value">{mean_hum:.1f}%</div>
        <div class="kpi-sub">Kelembaban relatif atmosfer</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-label">🔥 Kota Terpanas</div>
        <div class="kpi-value">{hottest_city}</div>
        <div class="kpi-sub">Rata-rata {hottest_temp:.1f} °C</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-label">❄️ Kota Tersejuk</div>
        <div class="kpi-value">{coolest_city}</div>
        <div class="kpi-sub">Rata-rata {coolest_temp:.1f} °C</div>
    </div>
    <div class="kpi-card violet">
        <div class="kpi-label">🌤️ Kondisi Dominan</div>
        <div class="kpi-value">{icon_condition}</div>
        <div class="kpi-sub">Frekuensi kemunculan tertinggi</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 9. TAB VISUALISASI INTERAKTIF (PLOTLY MODERN & HARMONIS)
# ==============================================================================
tab_nominal, tab_interval, tab_rasio, tab_table = st.tabs([
    "🌤️ 1. Kondisi Cuaca & Kota (Nominal)",
    "🌡️ 2. Sebaran Suhu (°C) (Interval)",
    "💧 3. Hubungan Suhu vs Kelembaban (Rasio)",
    "📋 4. Data Pengamatan & Export"
])

palette_weather = {
    "Cerah": "#f59e0b",
    "Berawan": "#64748b",
    "Hujan Ringan": "#38bdf8",
    "Hujan Lebat": "#0284c7",
    "Badai Petir": "#312e81"
}

# ------------------------------------------------------------------------------
# TAB 1: KATEGORIK NOMINAL (KONDISI CUACA & KOTA)
# ------------------------------------------------------------------------------
with tab_nominal:
    st.markdown("#### Analisis Variabel Kategorik Nominal: Kondisi Cuaca & Kota")
    st.caption("Distribusi proporsi kondisi atmosfer dan perbandingan frekuensi pengamatan di masing-masing stasiun kota.")

    col_w1, col_w2 = st.columns(2)

    with col_w1:
        st.markdown("**A. Proporsi Kondisi Cuaca (Donut Chart)**")
        cond_counts = df_filtered["Kondisi Cuaca"].value_counts().reset_index()
        cond_counts.columns = ["Kondisi Cuaca", "Total"]

        fig_pie = px.pie(
            cond_counts,
            names="Kondisi Cuaca",
            values="Total",
            hole=0.48,
            color="Kondisi Cuaca",
            color_discrete_map=palette_weather
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Pengamatan: %{value:,} Record (%{percent})<extra></extra>"
        )
        fig_pie.update_layout(
            height=400,
            autosize=True,
            showlegend=True,
            legend=dict(orientation="h", y=-0.15),
            margin=dict(l=15, r=15, t=20, b=30),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        render_plotly(fig_pie)

    with col_w2:
        st.markdown("**B. Frekuensi Kondisi per Stasiun Kota (Grouped Bar Chart)**")
        fig_city_cond = px.histogram(
            df_filtered,
            x="Kota",
            color="Kondisi Cuaca",
            barmode="group",
            color_discrete_map=palette_weather,
            labels={"Kota": "Stasiun Kota", "count": "Jumlah Pengamatan"}
        )
        fig_city_cond.update_layout(
            height=400,
            autosize=True,
            xaxis_title="Stasiun Pengamatan Kota",
            yaxis_title="Frekuensi Pengamatan",
            legend=dict(orientation="h", y=-0.25),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=15, r=15, t=20, b=45)
        )
        render_plotly(fig_city_cond)


# ------------------------------------------------------------------------------
# TAB 2: NUMERIK INTERVAL (SUHU °C)
# ------------------------------------------------------------------------------
with tab_interval:
    st.markdown("#### Analisis Variabel Numerik Interval: Sebaran Suhu (°C)")
    st.caption("Suhu udara diukur dalam derajat Celsius (°C) yang merupakan skala interval (titik 0°C adalah titik beku air, bukan ketiadaan kalor mutlak).")

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("**A. Histogram Distribusi Nilai Suhu (°C)**")
        fig_hist_temp = px.histogram(
            df_filtered,
            x="Suhu (°C)",
            nbins=30,
            marginal="box",
            color_discrete_sequence=["#0284c7"],
            labels={"Suhu (°C)": "Suhu Udara (°C)", "count": "Jumlah"}
        )
        fig_hist_temp.update_layout(
            height=410,
            autosize=True,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=15, r=15, t=20, b=20)
        )
        render_plotly(fig_hist_temp)
        st.caption("ℹ️ *Distribusi memperlihatkan dua puncak (bimodal) merefleksikan klaster dataran tinggi (~22°C) dan pesisir (~31°C).*")

    with col_t2:
        st.markdown("**B. Box Plot Komparasi Suhu per Kota (Deteksi Outlier)**")
        fig_box_temp = px.box(
            df_filtered,
            x="Kota",
            y="Suhu (°C)",
            color="Tipe Wilayah",
            points="outliers",
            color_discrete_map={"Dataran Tinggi": "#0d9488", "Dataran Rendah": "#0284c7", "Pesisir": "#f59e0b"},
            labels={"Suhu (°C)": "Suhu Udara (°C)"}
        )
        fig_box_temp.update_layout(
            height=410,
            autosize=True,
            legend=dict(orientation="h", y=-0.2),
            plot_bgcolor="rgba(248, 250, 252, 0.6)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=15, r=15, t=20, b=40)
        )
        render_plotly(fig_box_temp)
        st.caption("ℹ️ *Box plot menunjukkan disparitas suhu yang signifikan antara kota pegunungan sejuk vs kota pesisir.*")


# ------------------------------------------------------------------------------
# TAB 3: NUMERIK RASIO (SUHU VS KELEMBABAN %)
# ------------------------------------------------------------------------------
with tab_rasio:
    st.markdown("#### Analisis Variabel Numerik Rasio: Hubungan Suhu vs Kelembaban (%)")
    st.caption("Kelembaban relatif (%) adalah skala rasio dengan nilai nol absolut. Grafik di bawah menguji hubungan fisika atmosfer.")

    col_r1, col_r2 = st.columns([3, 2])

    with col_r1:
        st.markdown("**A. Scatter Plot: Hubungan Suhu vs Kelembaban (Garis Tren OLS)**")
        fig_scatter_w = px.scatter(
            df_filtered,
            x="Suhu (°C)",
            y="Kelembaban (%)",
            color="Kondisi Cuaca",
            trendline="ols",
            hover_data=["Kota", "Tipe Wilayah"],
            color_discrete_map=palette_weather,
            labels={"Suhu (°C)": "Suhu Udara (°C)", "Kelembaban (%)": "Kelembaban Relatif (%)"}
        )
        fig_scatter_w.update_layout(
            height=430,
            autosize=True,
            legend=dict(orientation="h", y=-0.2),
            plot_bgcolor="rgba(248, 250, 252, 0.6)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=15, r=15, t=15, b=45)
        )
        render_plotly(fig_scatter_w)
        r_corr = df_filtered["Suhu (°C)"].corr(df_filtered["Kelembaban (%)"])
        st.caption(f"ℹ️ *Garis tren OLS mengonfirmasi korelasi negatif kuat (r = {r_corr:.2f}): semakin tinggi suhu, kelembaban relatif menurun tajam.*")

    with col_r2:
        st.markdown("**B. Histogram Distribusi Nilai Kelembaban (%)**")
        fig_hist_hum = px.histogram(
            df_filtered,
            x="Kelembaban (%)",
            nbins=25,
            marginal="box",
            color_discrete_sequence=["#0d9488"],
            labels={"Kelembaban (%)": "Kelembaban Relatif (%)"}
        )
        fig_hist_hum.update_layout(
            height=430,
            autosize=True,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=15, r=15, t=15, b=20)
        )
        render_plotly(fig_hist_hum)


# ------------------------------------------------------------------------------
# TAB 4: DATA PENGAMATAN & EXPORT CSV
# ------------------------------------------------------------------------------
with tab_table:
    st.markdown("#### Basis Data Pengamatan Cuaca Terfilter")
    st.caption(f"Menampilkan {len(df_filtered):,} record observasi cuaca yang memenuhi kriteria aktif.")

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input("🔍 Cari Cepat (Kota / Kondisi Cuaca):", placeholder="Ketik nama kota atau cuaca...")
    with col_s2:
        st.write("")
        st.write("")
        csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Unduh Data CSV",
            data=csv_bytes,
            file_name=f"pengamatan_cuaca_filtered_{len(df_filtered)}_records.csv",
            mime="text/csv"
        )

    if search_query:
        df_display = df_filtered[
            df_filtered["Kota"].str.contains(search_query, case=False, na=False) |
            df_filtered["Kondisi Cuaca"].str.contains(search_query, case=False, na=False)
        ]
    else:
        df_display = df_filtered

    tabel_view = df_display[["Kota", "Tipe Wilayah", "Suhu (°C)", "Kelembaban (%)", "Kondisi Cuaca"]].copy()
    render_dataframe(
        tabel_view.style.format({
            "Suhu (°C)": "{:.1f} °C",
            "Kelembaban (%)": "{:d}%"
        }),
        height=420
    )

# ==============================================================================
# 10. FOOTER BERSIH & FORMAL
# ==============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.85rem; padding-bottom: 15px;'>"
    "Bedah Kasus 3: Dataset Pengamatan Cuaca 2024 • Sistem Analisis Data & Visualisasi Klimatologi"
    "</div>",
    unsafe_allow_html=True
)
