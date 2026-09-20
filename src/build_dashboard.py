"""Inline the dashboard data into a single self-contained HTML page.

The published page (dashboard/index.html) has no external dependencies: no CDN
scripts, web fonts or API calls, so it keeps working on GitHub Pages indefinitely.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> Path:
    template = (ROOT / "src" / "dashboard_template.html").read_text(encoding="utf-8")
    data = (ROOT / "dashboard" / "data.js").read_text(encoding="utf-8").replace("</", "<\\/")
    out = ROOT / "dashboard" / "index.html"
    out.write_text(template.replace("/*__DATA__*/", data), encoding="utf-8")
    print(f"Built {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.2f} MB)")
    return out


if __name__ == "__main__":
    main()
