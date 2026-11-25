# Data Jejak Liputan Indonesia

Dashboard membandingkan porsi judul berita yang memuat kata atau frasa tertentu pada arsip CNN Indonesia dan Tempo. Satu baris mewakili satu artikel yang lolos pembersihan Tugas 1.

## Sumber dan cakupan

Dataset **Indonesia News** dihimpun oleh azizainunnajib. Tiga berkas sumbernya adalah `cnn.csv`, `tempo.csv`, dan `tempo010619310520.csv`. [Unduh dataset di Kaggle](https://www.kaggle.com/datasets/azizainunnajib/indonesia-news).

| Tahap | Format | Jumlah artikel | Ukuran |
|---|---|---:|---:|
| Arsip awal | 3 CSV | 988.814 | 2,16 GB |
| Hasil pembersihan Tugas 1 | Parquet | 848.028 | 639,60 MB |
| Input dashboard, `data/processed/jejak_liputan.parquet` | Parquet, kompresi Zstandard | 848.028 | sekitar 26 MB |

Arsip mencakup **4 Agustus 2014 sampai 31 Mei 2020** dengan interpretasi waktu UTC. Tahun 2014 dan 2020 hanya tercakup sebagian. Jumlah artikel setelah pembersihan adalah **332.444 untuk CNN Indonesia** dan **515.584 untuk Tempo**. Saat membandingkan media, gunakan total artikel masing-masing media dalam bulan yang dipilih sebagai penyebut.

## Skema Parquet dashboard

| Kolom | Tipe | Arti |
|---|---|---|
| `source` | String | Nama media untuk pengelompokan dan perbandingan. |
| `published_at` | Timestamp, mikrodetik | Waktu terbit yang diinterpretasikan sebagai UTC. Berkas menyimpannya tanpa penanda zona waktu. |
| `title` | String | Judul artikel untuk pencarian frasa dan pemeriksaan konteks. |
| `month` | Date | Tanggal pertama bulan terbit, diturunkan dari `published_at` untuk agregasi bulanan. |

## Unduh data siap pakai

Simpan berkas sebagai `data/processed/jejak_liputan.parquet` di repositori Tugas 2. Tautan unduhan menunjuk revisi yang dipakai tim agar hasil analisis dapat direproduksi. [Halaman dataset Hugging Face](https://huggingface.co/datasets/Falzz/jejak-liputan-indonesia) · [Unduh Parquet, 26,04 MB](https://huggingface.co/datasets/Falzz/jejak-liputan-indonesia/resolve/0404d9dd52f052b23340c9afd73c7a97072be1e0/jejak_liputan.parquet?download=true).

Dari direktori utama Tugas 2, pasang dependensi proyek lalu unduh rilis dengan perintah berikut. Skrip memeriksa SHA-256 sebelum menempatkan berkas di jalur dashboard.

```powershell
python -m pip install -r requirements.txt
python -m src.prepare_data
```

## Membuat ulang dari data Tugas 1

Untuk memakai sumber lokal, gunakan Parquet bersih yang dihasilkan notebook pembersihan Tugas 1. Skrip memilih kolom, membentuk bulan UTC, dan memeriksa jumlah artikel per media sebelum mengganti berkas keluaran.

```powershell
python -m src.prepare_data --source "../../tugas1-abd-2026/data/processed/indonesia_news_clean.parquet"
```

## Menggunakan kueri dari Streamlit

```python
from datetime import date
from src.queries import monthly_summary, sample_titles

awal = akhir = date(2014, 8, 1)
tren = monthly_summary(awal, akhir, keyword="pemilu")
contoh = sample_titles(awal, akhir, sources=["CNN Indonesia"], keyword="pemilu")
```

Kedua fungsi mengembalikan DataFrame Polars. Rentang mencakup bulan awal dan akhir. Ringkasan menghasilkan kolom `month`, `source`, `total`, `hits`, dan `pct` (0–100). Kata kunci kosong menampilkan volume dengan `hits` dan `pct` kosong. Bulan tanpa arsip memiliki `total=0` dan `pct` kosong. Untuk ringkasan lintas bulan, hitung ulang persentase dari jumlah seluruh kecocokan dibagi jumlah seluruh artikel. Kueri judul mengembalikan hingga 100 baris.
Uji penerimaan backend menggunakan data lokal dapat dijalankan dari akar repositori dengan `python -m unittest discover -s tests`.
