"""Kueri Phase 2 untuk arsip judul CNN Indonesia dan Tempo."""
from datetime import date
from pathlib import Path

import duckdb
import polars as pl
import streamlit as st

DATASET = Path(__file__).resolve().parents[1] / "data/processed/jejak_liputan.parquet"
MEDIA = ("CNN Indonesia", "Tempo")


def _parameters(start, end, sources, keyword, path):
    start, end = start.replace(day=1), end.replace(day=1)
    if start > end:
        raise ValueError("Bulan awal harus mendahului atau sama dengan bulan akhir.")
    sources = sorted(set(sources))
    if not set(sources).issubset(MEDIA):
        raise ValueError("Media tidak dikenal.")
    return {
        "file": str(Path(path).resolve()),
        "start": start,
        "end": end,
        "sources": sources,
        "term": keyword.strip().lower(),
    }


def _read(sql, params):
    dataset = Path(params["file"]).stat()
    return _cached_read(sql, params, (dataset.st_size, dataset.st_mtime_ns))


@st.cache_data(max_entries=64, show_spinner=False)
def _cached_read(sql, params, file_version):
    """Versi berkas menjadi bagian dari kunci cache saat Parquet diganti."""
    with duckdb.connect() as con:
        result = con.sql(sql, params=params)
        if hasattr(result, "to_arrow_table"):
            return pl.from_arrow(result.to_arrow_table())
        return pl.from_arrow(result.fetch_arrow_table())


def monthly_summary(start: date, end: date, sources=MEDIA, keyword="", path=DATASET):
    """Satu baris per bulan dan media. Bulan akhir termasuk dalam hasil."""
    params = _parameters(start, end, sources, keyword, path)
    return _read("""
        WITH months AS (
            SELECT period::DATE AS month
            FROM generate_series(CAST($start AS DATE), CAST($end AS DATE),
                                 INTERVAL '1 month') AS calendar(period)
        ), media AS (
            SELECT unnest(CAST($sources AS VARCHAR[])) AS source
        ), counts AS (
            SELECT month, source, count(*) AS total,
                   count(*) FILTER (WHERE contains(lower(title), $term)) AS hits
            FROM read_parquet($file)
            WHERE month BETWEEN $start AND $end AND source IN (SELECT source FROM media)
            GROUP BY month, source
        )
        SELECT months.month, media.source, coalesce(total, 0) AS total,
               CASE WHEN $term <> '' THEN coalesce(hits, 0) END AS hits,
               CASE WHEN $term <> '' THEN 100.0 * hits / nullif(total, 0) END AS pct
        FROM months CROSS JOIN media
        LEFT JOIN counts USING (month, source)
        ORDER BY months.month, media.source
    """, params)


def sample_titles(start: date, end: date, sources=MEDIA, keyword="", path=DATASET):
    """Hingga 100 judul terbaru dalam cakupan filter yang sama."""
    params = _parameters(start, end, sources, keyword, path)
    return _read("""
        SELECT source, published_at, title
        FROM read_parquet($file)
        WHERE month BETWEEN $start AND $end
          AND source IN (SELECT unnest(CAST($sources AS VARCHAR[])))
          AND contains(lower(title), $term)
        ORDER BY published_at DESC, source, title
        LIMIT 100
    """, params)
