"""Clean the raw Netflix catalogue extract and engineer analysis features.

Input : data/raw/netflix_titles.csv   (7,787 titles, catalogue snapshot to 16 Jan 2021)
Output: data/processed/netflix_clean.csv
        data/processed/title_genres.csv     (one row per title x genre)
        data/processed/title_countries.csv  (one row per title x country)
        data/processed/data_quality.csv     (missing-value audit)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "netflix_titles.csv"
OUT = ROOT / "data" / "processed"

# Ratings are grouped into audience bands so movie (MPAA) and TV (TV Parental
# Guidelines) ratings can be compared on one scale.
AUDIENCE = {
    "TV-Y": "Kids", "TV-Y7": "Kids", "TV-Y7-FV": "Kids", "TV-G": "Kids", "G": "Kids",
    "TV-PG": "Older kids", "PG": "Older kids",
    "TV-14": "Teens", "PG-13": "Teens",
    "TV-MA": "Adults", "R": "Adults", "NC-17": "Adults",
    "NR": "Not rated", "UR": "Not rated",
}


def split_list(value: str) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def load_raw() -> pd.DataFrame:
    return pd.read_csv(RAW, dtype={"release_year": "Int64"})


def audit(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isna().sum()
    return pd.DataFrame({
        "column": missing.index,
        "missing": missing.values,
        "missing_pct": (missing.values / len(df) * 100).round(2),
    })


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["type", "title", "director", "cast", "country", "date_added", "rating", "duration", "listed_in", "description"]:
        df[col] = df[col].astype("string").str.strip().astype(object).where(df[col].notna())

    df["date_added"] = pd.to_datetime(df["date_added"], format="%B %d, %Y", errors="coerce")
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    df["month_added"] = df["date_added"].dt.month.astype("Int64")

    # Duration is "93 min" for films and "2 Seasons" for series: split into numeric features.
    num = df["duration"].str.extract(r"(\d+)")[0].astype(float)
    df["duration_min"] = np.where(df["type"].eq("Movie"), num, np.nan)
    df["seasons"] = np.where(df["type"].eq("TV Show"), num, np.nan)

    df["rating"] = df["rating"].fillna("Not recorded")
    df["audience"] = df["rating"].map(AUDIENCE).fillna("Not rated")
    df["country"] = df["country"].fillna("Unknown")
    df["director"] = df["director"].fillna("Unknown")
    df["cast"] = df["cast"].fillna("")

    df["primary_country"] = df["country"].map(lambda v: split_list(v)[0])
    df["primary_genre"] = df["listed_in"].map(lambda v: split_list(v)[0])
    df["genre_count"] = df["listed_in"].map(lambda v: len(split_list(v)))
    df["country_count"] = df["country"].map(lambda v: 0 if v == "Unknown" else len(split_list(v)))
    df["age_when_added"] = (df["year_added"] - df["release_year"]).astype("Int64")
    df["is_original_window"] = df["age_when_added"].le(1)  # released within a year of being added
    return df


def explode(df: pd.DataFrame, column: str, name: str) -> pd.DataFrame:
    out = df[["show_id", "type", column]].copy()
    out[name] = out[column].map(split_list)
    out = out.explode(name).drop(columns=column)
    return out[out[name].notna() & out[name].ne("Unknown")]


def main() -> pd.DataFrame:
    OUT.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    audit(raw).to_csv(OUT / "data_quality.csv", index=False)
    df = clean(raw)
    df.to_csv(OUT / "netflix_clean.csv", index=False)
    explode(df, "listed_in", "genre").to_csv(OUT / "title_genres.csv", index=False)
    explode(df, "country", "country_name").to_csv(OUT / "title_countries.csv", index=False)
    print(f"Cleaned {len(df):,} titles -> {OUT}")
    return df


if __name__ == "__main__":
    main()
