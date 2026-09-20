"""Aggregate the cleaned catalogue into the metrics used by the dashboard.

Output: data/processed/kpi_summary.csv
        data/processed/yearly_additions.csv
        dashboard/data.js  (all dashboard data, embedded so the page needs no server)
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
DASH = ROOT / "dashboard"


def counts(series: pd.Series, top: int | None = None) -> list[list]:
    vc = series.value_counts()
    if top:
        vc = vc.head(top)
    return [[str(k), int(v)] for k, v in vc.items()]


def split_by_type(frame: pd.DataFrame, key: str, keys: list) -> dict:
    table = pd.crosstab(frame[key], frame["type"]).reindex(keys, fill_value=0)
    return {
        "labels": [str(k) for k in keys],
        "movie": [int(v) for v in table.get("Movie", pd.Series(0, index=keys))],
        "tv": [int(v) for v in table.get("TV Show", pd.Series(0, index=keys))],
    }


def main() -> dict:
    df = pd.read_csv(PROC / "netflix_clean.csv", parse_dates=["date_added"], keep_default_na=False,
                     na_values={"date_added": [""], "duration_min": [""], "seasons": [""],
                                "year_added": [""], "month_added": [""], "age_when_added": [""]})
    genres = pd.read_csv(PROC / "title_genres.csv")
    countries = pd.read_csv(PROC / "title_countries.csv")
    quality = pd.read_csv(PROC / "data_quality.csv")

    movies, tv = df[df.type == "Movie"], df[df.type == "TV Show"]
    added = df.dropna(subset=["year_added"]).copy()
    added["year_added"] = added["year_added"].astype(int)

    years = list(range(int(added.year_added.min()), int(added.year_added.max()) + 1))
    yearly = split_by_type(added, "year_added", years)
    totals = [m + t for m, t in zip(yearly["movie"], yearly["tv"])]
    yoy = [None] + [round((totals[i] / totals[i - 1] - 1) * 100, 1) if totals[i - 1] else None
                    for i in range(1, len(totals))]
    yearly["total"], yearly["yoy_pct"] = totals, yoy
    tv_share = [round(t / s * 100, 1) if s else None for t, s in zip(yearly["tv"], totals)]
    yearly["tv_share_pct"] = tv_share
    pd.DataFrame(yearly).to_csv(PROC / "yearly_additions.csv", index=False)

    peak_i = totals.index(max(totals))
    last_full = max(y for y in years if y < 2021)
    recent = df[df.release_year >= 2000]
    rel_years = list(range(2000, int(df.release_year.max()) + 1))

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = added.groupby("month_added").size().reindex(range(1, 13), fill_value=0)

    bins = list(range(0, 211, 15))
    dur = pd.cut(movies.duration_min, bins=bins + [400], right=False)
    dur_labels = [f"{b}-{b + 14}" for b in bins[:-1]] + ["210+"]

    rating_order = ["TV-MA", "TV-14", "TV-PG", "R", "PG-13", "TV-Y", "TV-Y7", "PG", "TV-G", "NR",
                    "G", "TV-Y7-FV", "UR", "NC-17", "Not recorded"]
    rating_order = [r for r in rating_order if r in set(df.rating)]

    top_genres_m = genres[genres.type == "Movie"].genre.value_counts().head(10)
    top_genres_t = genres[genres.type == "TV Show"].genre.value_counts().head(10)
    top_countries = countries.country_name.value_counts().head(12).index.tolist()
    country_split = pd.crosstab(countries.country_name, countries.type).reindex(top_countries)

    directors = df[df.director != "Unknown"].director.str.split(",").explode().str.strip()
    cast = df[df.cast != ""].cast.str.split(",").explode().str.strip()

    kpis = {
        "titles": len(df), "movies": len(movies), "tv": len(tv),
        "movie_share_pct": round(len(movies) / len(df) * 100, 1),
        "countries": int(countries.country_name.nunique()),
        "genres": int(genres.genre.nunique()),
        "directors": int(directors.nunique()),
        "median_movie_min": float(movies.duration_min.median()),
        "mean_movie_min": round(float(movies.duration_min.mean()), 1),
        "single_season_pct": round(float((tv.seasons == 1).mean() * 100), 1),
        "median_release_year": int(df.release_year.median()),
        "oldest_release": int(df.release_year.min()),
        "newest_release": int(df.release_year.max()),
        "first_added": df.date_added.min().strftime("%d %b %Y"),
        "last_added": df.date_added.max().strftime("%d %b %Y"),
        "peak_year": years[peak_i], "peak_year_titles": totals[peak_i],
        "last_full_year": last_full,
        "last_full_year_titles": totals[years.index(last_full)],
        "added_2016_2020": int(added.year_added.between(2016, 2020).sum()),
        "added_2016_2020_pct": round(float(added.year_added.between(2016, 2020).mean() * 100), 1),
        "adult_pct": round(float((df.audience == "Adults").mean() * 100), 1),
        "released_2015_plus_pct": round(float((df.release_year >= 2015).mean() * 100), 1),
        "fresh_on_arrival_pct": round(float(added.is_original_window.astype(str).eq("True").mean() * 100), 1),
        "missing_director": int(quality.set_index("column").loc["director", "missing"]),
        "missing_date": int(quality.set_index("column").loc["date_added", "missing"]),
    }
    pd.DataFrame([kpis]).T.rename(columns={0: "value"}).to_csv(PROC / "kpi_summary.csv")

    titles = []
    for r in df.itertuples():
        titles.append([
            r.show_id, r.title, 0 if r.type == "Movie" else 1, int(r.release_year), r.rating,
            r.duration, r.listed_in, r.country, r.director if r.director != "Unknown" else "",
            ", ".join(r.cast.split(", ")[:4]) if r.cast else "",
            r.date_added.strftime("%d %b %Y") if pd.notna(r.date_added) else "", r.description,
        ])

    data = {
        "source": {
            "name": "Netflix Movies and TV Shows (Kaggle, Shivam Bansal)",
            "rows": len(df), "snapshot": kpis["last_added"],
            "note": "Catalogue snapshot scraped from Netflix via Flixable; 2021 covers 1-16 January only.",
        },
        "kpis": kpis,
        "yearly": yearly,
        "release": split_by_type(recent, "release_year", rel_years),
        "monthly": {"labels": month_names, "values": [int(v) for v in monthly]},
        "duration": {"labels": dur_labels, "values": [int(v) for v in dur.value_counts(sort=False)]},
        "seasons": [[k, int(v)] for k, v in tv.seasons.astype(int).astype(str).where(tv.seasons < 6, "6+")
                    .value_counts().reindex(["1", "2", "3", "4", "5", "6+"], fill_value=0).items()],
        "ratings": split_by_type(df, "rating", rating_order),
        "audience": split_by_type(df, "audience", ["Kids", "Older kids", "Teens", "Adults", "Not rated"]),
        "genres_movie": [[k, int(v)] for k, v in top_genres_m.items()],
        "genres_tv": [[k, int(v)] for k, v in top_genres_t.items()],
        "countries": {
            "labels": top_countries,
            "movie": [int(v) for v in country_split.get("Movie", 0)],
            "tv": [int(v) for v in country_split.get("TV Show", 0)],
        },
        "directors": counts(directors, 10),
        "cast": counts(cast, 10),
        "quality": quality.to_dict(orient="records"),
        "titles": titles,
    }
    DASH.mkdir(exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    (DASH / "data.js").write_text("window.NETFLIX_DATA=" + payload + ";\n", encoding="utf-8")
    print(f"Wrote dashboard data ({len(payload) / 1e6:.2f} MB) for {len(titles):,} titles")
    return data


if __name__ == "__main__":
    main()
