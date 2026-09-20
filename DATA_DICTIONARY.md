# Data dictionary

## Raw: `data/raw/netflix_titles.csv`
| Column | Type | Description |
|---|---|---|
| show_id | text | Unique title ID (s1–s7787) |
| type | text | `Movie` or `TV Show` |
| title | text | Title name |
| director | text | Director(s), comma-separated; often blank for TV |
| cast | text | Cast, comma-separated |
| country | text | Production country/countries, comma-separated |
| date_added | text | Date the title was added to Netflix, e.g. `August 14, 2020` |
| release_year | int | Original release year |
| rating | text | Maturity rating (TV Parental Guidelines or MPAA) |
| duration | text | `93 min` for movies, `2 Seasons` for TV |
| listed_in | text | Genre labels, comma-separated (up to 3) |
| description | text | Short synopsis |

## Engineered: `data/processed/netflix_clean.csv`
| Column | Rule |
|---|---|
| date_added | Parsed to a date (10 blanks remain null) |
| year_added / month_added | From `date_added` |
| duration_min | Minutes, movies only |
| seasons | Season count, TV only |
| audience | Rating grouped: Kids (TV-Y, TV-Y7, TV-Y7-FV, TV-G, G), Older kids (TV-PG, PG), Teens (TV-14, PG-13), Adults (TV-MA, R, NC-17), Not rated (NR, UR, missing) |
| primary_country / primary_genre | First value listed |
| genre_count / country_count | Number of values listed |
| age_when_added | `year_added − release_year` |
| is_original_window | Added within one year of release |

## Other outputs
- `title_genres.csv`, `title_countries.csv`: one row per title × genre / country
- `data_quality.csv`: missing values per raw column
- `yearly_additions.csv`: movies, TV, total, YoY % and TV share per year added
- `kpi_summary.csv`: headline figures shown on the dashboard
