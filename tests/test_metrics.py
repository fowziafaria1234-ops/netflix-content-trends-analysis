"""Reconciliation tests: every dashboard figure must trace back to the raw file."""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(scope="module")
def raw():
    return pd.read_csv(ROOT / "data" / "raw" / "netflix_titles.csv")


@pytest.fixture(scope="module")
def data():
    txt = (ROOT / "dashboard" / "data.js").read_text(encoding="utf-8")
    return json.loads(txt[txt.index("=") + 1:].rstrip().rstrip(";"))


def test_row_counts(raw, data):
    k = data["kpis"]
    assert k["titles"] == len(raw) == 7787
    assert k["movies"] == (raw.type == "Movie").sum() == 5377
    assert k["tv"] == (raw.type == "TV Show").sum() == 2410
    assert len(data["titles"]) == len(raw)
    assert raw.show_id.is_unique


def test_yearly_additions_reconcile(raw, data):
    dated = raw.date_added.notna().sum()
    assert sum(data["yearly"]["total"]) == dated == len(raw) - 10
    assert data["kpis"]["peak_year"] == 2019


def test_type_splits_sum(data):
    for key in ("ratings", "audience"):
        block = data[key]
        assert sum(block["movie"]) + sum(block["tv"]) == data["kpis"]["titles"]
    assert sum(v for _, v in data["seasons"]) == data["kpis"]["tv"]
    assert sum(data["duration"]["values"]) == data["kpis"]["movies"]
    assert sum(data["monthly"]["values"]) == sum(data["yearly"]["total"])


def test_genre_counts_match_raw(raw, data):
    movies = raw[raw.type == "Movie"].listed_in.str.split(", ").explode().value_counts()
    for genre, n in data["genres_movie"]:
        assert movies[genre] == n


def test_country_counts_match_raw(raw, data):
    c = raw.country.dropna().str.split(",").explode().str.strip()
    c = c[c != ""].value_counts()
    for i, name in enumerate(data["countries"]["labels"]):
        assert data["countries"]["movie"][i] + data["countries"]["tv"][i] == c[name]


def test_median_runtime(raw, data):
    mins = raw[raw.type == "Movie"].duration.str.extract(r"(\d+)")[0].astype(int)
    assert data["kpis"]["median_movie_min"] == mins.median()


def test_dashboard_is_self_contained():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "window.NETFLIX_DATA=" in html
    assert "<script src" not in html and "<link rel=\"stylesheet\"" not in html
    assert "fonts.googleapis" not in html
