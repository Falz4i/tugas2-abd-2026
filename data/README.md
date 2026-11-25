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

## Membuat ulang dari data Tugas 1

1. Jika Parquet bersih sudah tersedia dari Tugas 1, langsung gunakan berkas tersebut pada langkah 3.
2. Untuk memulai dari data mentah, unduh arsip Kaggle di atas, ekstrak ketiga CSV ke `data/raw/archive/` di repositori Tugas 1, lalu jalankan notebook `notebooks/01_data_profiling.ipynb` dan `notebooks/02_data_cleaning.ipynb` sesuai panduan repositori tersebut. Hasilnya tersimpan di `data/processed/indonesia_news_clean.parquet`.
3. Dari direktori utama repositori **Tugas 2**, jalankan blok Python berikut dengan PyArrow dari `requirements.txt`. Jalur sumber mengikuti susunan folder proyek lokal. Sesuaikan `src` jika repositori Tugas 1 berada di lokasi lain.

```python
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

src = Path("../../tugas1-abd-2026/data/processed/indonesia_news_clean.parquet")
out = Path("data/processed/jejak_liputan.parquet")
out.parent.mkdir(parents=True, exist_ok=True)

data = pq.read_table(src, columns=["source", "published_at", "title"])
month = pc.floor_temporal(data["published_at"], unit="month").cast(pa.date32())
data = data.append_column("month", month)
pq.write_table(data, out, compression="zstd")

saved = pq.read_table(out)
assert saved.equals(data)
assert saved.num_rows == 848_028
print(pc.value_counts(saved["source"]).to_pylist())
```

Git mengabaikan folder `data/processed/`. Pada clone baru atau saat menyiapkan deployment, hasilkan kembali Parquet ringkas dengan langkah di atas atau salin berkas yang sudah diverifikasi ke jalur yang sama.
