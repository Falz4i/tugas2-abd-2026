"""Regresi penyebut dan celah arsip. Jalankan setelah python -m src.prepare_data."""
import unittest
from datetime import date

from src.queries import monthly_summary, sample_titles


class NewsQueriesTest(unittest.TestCase):
    def test_full_archive(self):
        summary = monthly_summary(date(2014, 8, 1), date(2020, 5, 1))
        self.assertEqual(summary["total"].sum(), 848028)
        self.assertEqual(summary["pct"].null_count(), summary.height)

    def test_keyword_changes_only_numerator(self):
        month = date(2014, 8, 1)
        for keyword, expected in [("banjir", 0), (" PEMILU ", 3)]:
            with self.subTest(keyword=keyword):
                result = monthly_summary(month, month, keyword=keyword)
                cnn, tempo = result.to_dicts()
                self.assertEqual((cnn["source"], cnn["total"], cnn["hits"]),
                                 ("CNN Indonesia", 694, expected))
                self.assertAlmostEqual(cnn["pct"], 100 * expected / 694)
                self.assertEqual((tempo["source"], tempo["total"], tempo["pct"]),
                                 ("Tempo", 0, None))
                titles = sample_titles(month, month, keyword=keyword)
                self.assertEqual(titles.height, expected)
                self.assertTrue(all(keyword.strip().lower() in t.lower()
                                    for t in titles["title"]))
