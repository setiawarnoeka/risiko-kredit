
# Analisis Risiko Gagal Bayar Kartu Kredit

Proyek analisis data dan pemodelan risiko kredit pada 29.965 nasabah kartu kredit (dataset UCI *Default of Credit Card Clients*, Taiwan 2005).

**Dashboard interaktif:** https://risiko-kredit-setiawarnoeka.streamlit.app/

## Pertanyaan bisnis

Nasabah seperti apa yang paling berisiko gagal bayar bulan depan, seberapa akurat risikonya bisa diprediksi, dan tindakan apa yang sebaiknya diambil bank?

## Temuan utama

- Tingkat gagal bayar keseluruhan 22,13% (6.630 dari 29.965 nasabah).
- Riwayat telat bayar adalah sinyal terkuat: nasabah yang telat 1 bulan gagal bayar 34,0%, dan yang telat 2 bulan 69,1%.
- Segmen risiko Tinggi hanya 16,4% dari nasabah tetapi menyumbang 45,1% dari seluruh kasus gagal bayar, dengan tingkat gagal bayar 60,7%.
- Nasabah yang memakai 80% limit atau lebih gagal bayar sekitar 32%, dibanding rata-rata 22%.
- Nasabah dengan limit terkecil (10% terbawah) gagal bayar 35,7%, dibanding 12,5% pada limit terbesar.

## Model

Logistic Regression dan Gradient Boosting dibandingkan dengan validasi silang 5-lipat (ROC-AUC 0,760 dan 0,785), lalu Gradient Boosting disetel dan dievaluasi pada data uji (20% data, stratifikasi).

| Model                     | ROC-AUC | Recall | Precision |
| ------------------------- | ------- | ------ | --------- |
| Logistic Regression       | 0,755   | 60,5%  | 44,4%     |
| Gradient Boosting (tuned) | 0,778   | 64,2%  | 45,7%     |

Hasil di atas pada ambang keputusan 0,5. Akurasi tidak dipakai sebagai metrik utama karena tebakan "semua nasabah aman" sudah 77,9% akurat tetapi tidak menangkap satu pun kasus gagal bayar.

Faktor paling berpengaruh (permutation importance): keterlambatan terparah, status bayar bulan terakhir, utilisasi limit, dan jumlah bulan telat.

**Ambang berbasis biaya.** Dengan asumsi gagal bayar yang lolos lima kali lebih mahal daripada salah tandai, ambang optimal adalah 0,35 dan menurunkan total biaya 49,8% dibanding tanpa model (1,9% dibanding ambang 0,5). Ambang optimal sensitif terhadap asumsi: 0,65 pada rasio biaya 2x dan 0,25 pada 10x.

## Rekomendasi

1. Pantau segmen Tinggi (16% nasabah, 45% kasus gagal bayar) dengan prioritas tertinggi.
2. Hubungi nasabah yang telat 1 bulan sebelum mereka telat bulan kedua, karena tingkat gagal bayar melonjak dari 34% ke 69%.
3. Beri peringatan dini pada nasabah dengan utilisasi limit 80% ke atas, dan gunakan limit kecil sebagai sinyal tambahan bersama riwayat telat bayar, bukan satu-satunya dasar pemantauan.

## Teknologi

Python, pandas, DuckDB (SQL), scikit-learn, Streamlit

## Cara menjalankan

    pip install -r requirements.txt
    streamlit run app.py

Analisis lengkap ada di `Analisis_Risiko_Kredit.ipynb`.

## Keterbatasan

- Data satu bank di Taiwan tahun 2005, sehingga pola belum tentu berlaku di tempat dan waktu lain.
- Biaya kesalahan adalah asumsi, bukan angka kerugian riil.
- Ambang keputusan dipilih menggunakan data uji, sehingga penghematan biaya yang dilaporkan cenderung sedikit optimistis.
- Skor model dipakai untuk mengurutkan risiko, bukan sebagai peluang yang terkalibrasi.
- Hubungan antara faktor (misalnya limit kecil) dan gagal bayar adalah korelasi, bukan sebab-akibat.
- Model belum diuji pada periode waktu yang berbeda.
