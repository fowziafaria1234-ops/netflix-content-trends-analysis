"""Static Matplotlib charts for the README and project report (assets/*.png)."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
RED, TV, BG, INK, MUTED = "#E50914", "#F5F5F1", "#141414", "#FFFFFF", "#9A9A9A"


def load() -> dict:
    raw = (ROOT / "dashboard" / "data.js").read_text(encoding="utf-8")
    return json.loads(raw[raw.index("=") + 1:].rstrip().rstrip(";"))


def style(ax, title):
    ax.set_facecolor(BG)
    ax.figure.set_facecolor(BG)
    ax.set_title(title, color=INK, loc="left", fontsize=14, fontweight="bold", pad=12)
    ax.tick_params(colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#333333")
    ax.grid(axis="y", color="#2a2a2a", linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(ASSETS / name, dpi=150, facecolor=BG)
    plt.close(fig)


def main():
    ASSETS.mkdir(exist_ok=True)
    d = load()
    y = d["yearly"]
    idx = [i for i, lab in enumerate(y["labels"]) if int(lab) >= 2012]
    labels = [y["labels"][i] for i in idx]
    mv, tv = [y["movie"][i] for i in idx], [y["tv"][i] for i in idx]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.bar(labels, mv, color=RED, label="Movies")
    ax.bar(labels, tv, bottom=mv, color=TV, label="TV Shows")
    style(ax, "Titles added to Netflix per year (2021 = 1-16 Jan only)")
    ax.legend(facecolor=BG, edgecolor="#333", labelcolor=INK)
    save(fig, "yearly-additions.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    g = d["genres_movie"][:10][::-1]
    ax.barh([k for k, _ in g], [v for _, v in g], color=RED)
    style(ax, "Top 10 movie genres (titles per genre label)")
    ax.grid(axis="x", color="#2a2a2a"); ax.grid(axis="y", visible=False)
    save(fig, "top-movie-genres.png")

    c = d["countries"]
    fig, ax = plt.subplots(figsize=(10, 5))
    labs = c["labels"][::-1]
    ax.barh(labs, c["movie"][::-1], color=RED, label="Movies")
    ax.barh(labs, c["tv"][::-1], left=c["movie"][::-1], color=TV, label="TV Shows")
    style(ax, "Top 12 production countries")
    ax.grid(axis="x", color="#2a2a2a"); ax.grid(axis="y", visible=False)
    ax.legend(facecolor=BG, edgecolor="#333", labelcolor=INK, loc="lower right")
    save(fig, "top-countries.png")

    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.bar(d["duration"]["labels"], d["duration"]["values"], color=RED)
    style(ax, f"Movie runtime distribution (median {d['kpis']['median_movie_min']:.0f} min)")
    ax.tick_params(axis="x", rotation=40)
    save(fig, "movie-runtime.png")
    print("Saved report charts to assets/")


if __name__ == "__main__":
    main()
