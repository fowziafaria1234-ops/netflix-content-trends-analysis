# Netflix Content Trends Analysis: project report

## Business questions
1. When did Netflix add most of its current catalogue, and is growth slowing?
2. Is the mix shifting between movies and TV?
3. Which genres and production countries dominate?
4. What does a typical title look like in rating and runtime?

## Data
7,787 titles (Kaggle “Netflix Movies and TV Shows”, snapshot to 16 Jan 2021). Real public data, 12 columns.

## Findings
- **Growth:** 96.6% of dated titles were added 2016–2020. Additions peaked in 2019 (2,153) and fell 6.7% in 2020.
- **Mix:** movies are 69.1% of the catalogue, but TV's share of new additions rose from 25.5% (2018) to 34.7% (2020).
- **Genres:** top movie labels are International Movies, Dramas, Comedies; top TV labels are International TV Shows, TV Dramas, TV Comedies.
- **Countries:** United States, India, United Kingdom, Canada, France lead. South Korea and Japan contribute more TV than film.
- **Ratings:** TV-MA is the most common rating; 45.3% of titles are adult-rated.
- **Runtime:** median movie 98 min (mean 99.3); 66.7% of TV shows have one season.

## Limitations
- Snapshot of available titles only: removed titles are absent, so early years are undercounted.
- 2021 covers 1–16 January only.
- Genre and country are multi-valued, so their counts exceed the title count.
- Director is missing for 30.7% of titles (mostly TV), so director rankings cover credited titles only.

## Recommendations (illustrative)
- Track the TV share of additions as a leading indicator of content strategy.
- Report genre and country as shares of titles, not raw sums, to avoid double counting.
- Refresh with a newer extract to test whether the 2020 slowdown continued.
