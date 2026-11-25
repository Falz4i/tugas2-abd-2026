"""Siapkan Parquet dashboard dari rilis publik atau Parquet bersih Tugas 1."""
import argparse
import hashlib
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

DATASET = Path(__file__).resolve().parents[1] / "data/processed/jejak_liputan.parquet"
REVISION = "0404d9dd52f052b23340c9afd73c7a97072be1e0"
URL = f"https://huggingface.co/datasets/Falzz/jejak-liputan-indonesia/resolve/{REVISION}/jejak_liputan.parquet"
SHA256 = "61bfbe612a654fc3b21250be0bda6b2b86addc59381cbdbf34efcf4bea1ce283"
COUNTS = {"CNN Indonesia": 332444, "Tempo": 515584}


def validate(path):
    data = pq.read_table(path)
    if data.column_names != ["source", "published_at", "title", "month"]:
        raise ValueError("Kolom Parquet tidak sesuai skema dashboard.")
    if any(col.null_count for col in data.columns):
        raise ValueError("Ada nilai kosong dalam data dashboard.")
    counts = {row["values"]: row["counts"] for row in pc.value_counts(data["source"]).to_pylist()}
    expected_month = pc.floor_temporal(data["published_at"], unit="month").cast(pa.date32())
    if counts != COUNTS or not expected_month.equals(data["month"]):
        raise ValueError("Jumlah artikel per media atau bulan terbit gagal divalidasi.")


def prepare(source, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=output.parent, delete=False) as tmp:
        staging = Path(tmp.name)
    try:
        if source is None:
            with urlopen(URL, timeout=60) as response, staging.open("wb") as target:
                shutil.copyfileobj(response, target)
            if hashlib.sha256(staging.read_bytes()).hexdigest() != SHA256:
                raise ValueError("Checksum unduhan berbeda dari rilis dataset.")
        else:
            data = pq.read_table(source, columns=["source", "published_at", "title"])
            month = pc.floor_temporal(data["published_at"], unit="month").cast(pa.date32())
            pq.write_table(data.append_column("month", month), staging, compression="zstd")
        validate(staging)
        os.replace(staging, output)
    finally:
        staging.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Parquet bersih Tugas 1. Default: unduh rilis publik.")
    parser.add_argument("--output", type=Path, default=DATASET)
    args = parser.parse_args()
    prepare(args.source, args.output)
    print(f"848.028 artikel tervalidasi: {args.output}")
