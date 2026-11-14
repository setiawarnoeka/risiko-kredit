import pandas as pd
import streamlit as st

import joblib

@st.cache_resource
def load_model():
    return joblib.load("model.joblib")

art = load_model()
model, thr, fitur = art["model"], art["threshold"], art["features"]

pay_cols  = [f"PAY_{i}" for i in range(1, 7)]
bill_cols = [f"BILL_AMT{i}" for i in range(1, 7)]

st.set_page_config(page_title="Dashboard Risiko Kredit", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data_dashboard.csv")

df = load_data()

st.title("Dashboard Risiko Kredit")
tab1, tab2, tab3 = st.tabs(["Ringkasan", "Segmentasi", "Simulator"])

with tab1:
    c1, c2 = st.columns(2)
    c1.metric("Nasabah", f"{len(df):,}")
    c2.metric("Gagal bayar", f"{df['default'].mean():.1%}")
    st.subheader("Gagal bayar per segmen")
    st.bar_chart(df.groupby("segmen")["default"].mean())

with tab2:
    seg = df.groupby("segmen").agg(
        nasabah=("default", "size"),
        gagal_bayar=("default", "sum"),
        rate=("default", "mean"))
    seg["persen_nasabah"] = seg["nasabah"] / seg["nasabah"].sum()
    seg["persen_dari_semua_gagal_bayar"] = seg["gagal_bayar"] / seg["gagal_bayar"].sum()
    st.subheader("Tabel segmen risiko")
    st.dataframe(seg.style.format({"rate": "{:.1%}", "persen_nasabah": "{:.1%}",
                                   "persen_dari_semua_gagal_bayar": "{:.1%}"}))

    st.subheader("Filter nasabah")
    pilih = st.multiselect("Segmen", ["Rendah", "Sedang", "Tinggi"], default=["Tinggi"])
    sub = df[df["segmen"].isin(pilih)]
    if len(sub):
        st.write(f"{len(sub):,} nasabah, tingkat gagal bayar {sub['default'].mean():.1%}")
    else:
        st.write("Pilih minimal satu segmen.")
        
with tab3:
    st.subheader("Simulator skor risiko")
    st.write("Atur profil nasabah, lalu lihat skor risikonya. Ini simulasi, bukan keputusan kredit.")
    a, b, d = st.columns(3)
    limit = a.number_input("Limit kredit", 10000, 1000000, 100000, 10000)
    age   = a.slider("Usia", 21, 75, 35)
    sex   = a.selectbox("Jenis kelamin (1=pria, 2=wanita)", [1, 2])
    edu   = b.selectbox("Pendidikan (1=pascasarjana, 2=universitas, 3=SMA, 4=lainnya)", [1, 2, 3, 4], index=1)
    mar   = b.selectbox("Status (1=menikah, 2=lajang, 3=lainnya)", [1, 2, 3], index=1)
    util  = b.slider("Utilisasi limit (tagihan / limit)", 0.0, 1.5, 0.5, 0.05)
    pay1  = d.slider("Status bayar bulan lalu (-2 s.d. 8)", -2, 8, 0)
    lama  = d.slider("Status bayar 5 bulan sebelumnya", -2, 8, 0)
    ratio = d.slider("Rasio pembayaran (bayar / tagihan)", 0.0, 1.0, 0.2, 0.05)

    row = {"LIMIT_BAL": limit, "SEX": sex, "EDUCATION": edu, "MARRIAGE": mar, "AGE": age}
    for i in range(1, 7):
        row[f"PAY_{i}"] = pay1 if i == 1 else lama
        row[f"BILL_AMT{i}"] = util * limit
        row[f"PAY_AMT{i}"] = ratio * util * limit

    x = pd.DataFrame([row])
    x["n_delay"]   = (x[pay_cols] > 0).sum(axis=1)
    x["max_delay"] = x[pay_cols].max(axis=1)
    x["util_avg"]  = x[bill_cols].mean(axis=1) / x["LIMIT_BAL"]

    skor = model.predict_proba(x[fitur])[:, 1][0]
    m1, m2 = st.columns(2)
    m1.metric("Skor risiko", f"{skor:.1%}")
    m2.metric("Keputusan", "Tandai berisiko" if skor >= thr else "Aman")
    st.caption(f"Ambang keputusan {thr:.2f} (dari asumsi biaya). Skor dipakai untuk mengurutkan risiko, bukan peluang yang terkalibrasi.")