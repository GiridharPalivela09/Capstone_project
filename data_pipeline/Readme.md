# Books Catalogue Project

A small pipeline that scrapes book data from books.toscrape.com, cleans it up,
loads it into a SQLite database, and runs some queries on it. Built as a
practice project for scraping + pandas + SQL together.

## What's in this folder

| File | What it does |
|---|---|
| `Scrape.py` | Scrapes books from the site and saves `books_raw.csv` |
| `clean_convert_currency.py` | Cleans the raw csv, converts price to INR, saves `books_clean.csv` |
| `DB_Schema.py` | Creates the SQLite schema (`categories` and `books` tables) |
| `queries.py` | Loads the clean csv into the DB and runs the SQL queries, saves output to `query_results.txt` |
| `pandas_readback.py` | Reads the DB back with pandas and cross-checks a query result against an equivalent pandas merge |
| `books_raw.csv` | Raw scraped data (70 rows incl. header) |
| `books_clean.csv` | Cleaned data after processing |
| `books_catalouge.db` | Final SQLite database |
| `query_results.txt` | Output of all 6 SQL queries |
| `pandas_readback_results.txt` | Output of the pandas readback / cross-check script |

## How to run it (in order)

1. **Install requirements**

   ```bash
   pip install requests beautifulsoup4 pandas
   ```

2. **Scrape the data**

   ```bash
   python Scrape.py
   ```

   This pulls books from the categories listed in `CATEGORIES_TO_SCRAPE`
   (Travel, Mystery, Historical Fiction, etc.), stopping once it has at
   least 60 books, and writes `books_raw.csv`.

3. **Clean the data**

   ```bash
   python clean_convert_currency.py
   ```

   Reads `books_raw.csv`, cleans it, and writes `books_clean.csv`.

4. **Build the DB schema**

   ```bash
   python DB_Schema.py
   ```

   Creates `books_catalouge.db` with empty `categories` and `books` tables.
   (This step is optional on its own since `queries.py` calls
   `create_schema()` again anyway, but it's useful to run once just to
   check the schema looks right.)

5. **Load data + run queries**

   ```bash
   python queries.py
   ```

   Loads `books_clean.csv` into the DB and runs 6 queries, saving the
   results to `query_results.txt`.

6. **Cross-check with pandas**

   ```bash
   python pandas_readback.py
   ```

   Reads the DB back with `pd.read_sql`, and separately reproduces one of
   the join queries using `pd.merge` on in-memory DataFrames, then checks
   both give the exact same result. Saves output to
   `pandas_readback_results.txt`.

## Cleaning decisions (in `clean_convert_currency.py`)

- **Price**: pulled out with a regex (`[\d.]+`) since the raw price has a
  currency symbol in front of it (comes through as `Â£` due to encoding,
  the regex just ignores that and grabs the number).
- **Rating**: the scraper already converts the star-rating word
  (One/Two/Three/Four/Five) into a number using the `RATING` dict, so
  cleaning just re-parses that number safely and drops it if it isn't a
  valid int.
- **Availability**: converted to a plain `True`/`False` by checking if
  the text contains "in stock" or "out of stock" (case-insensitive).
  Anything that matches neither is treated as missing.
- **Dropped rows**: rows missing a title, missing a category, or with
  unreadable availability are dropped entirely, since there's no sensible
  way to fill those in.
- **Missing price / rating**: instead of dropping these rows, missing
  values are filled in with the **median** of that column. This was a
  judgment call — since it's usually just one or two rows here, using the
  median keeps the row instead of throwing away otherwise-good data, and
  it's less sensitive to outliers than the mean would be.
- **Currency conversion**: GBP to INR at a fixed rate of 105.50
  (`price_inr = price_gbp * 105.50`, rounded to 2 decimals). This is a
  fixed rate for the exercise, not a live exchange rate.
- In this run, all 69 scraped books passed the cleaning step with no rows
  dropped and no missing values to impute — `books_raw.csv` and
  `books_clean.csv` both have 69 data rows.

## Database design (`DB_Schema.py`)

Two tables, normalized so category names aren't repeated on every book row:

- `categories(category_id, category_name)`
- `books(book_id, title, price_gbp, price_inr, rating, in_stock, category_id)`
  with `category_id` as a foreign key into `categories`.

`in_stock` is stored as `0`/`1` (SQLite has no real boolean type).

## Queries (`queries.py`)

1. **q1_top_rated_expensive** — top 10 books rated 4+ stars, sorted by
   price (highest first)
2. **Q2_distinct_ratings** — list of distinct rating values in the data
3. **Q3_midrange_price_between** — books priced between £10 and £20
4. **Q4_specific_categories_in** — books belonging to category_id 1 or 2
5. **Q5_join_five_star_by_category** — top 10 five-star books with their
   category name (join on `categories`)
6. **Q6_join_category_summary** — per-category book count and average
   price in INR

## Notes

- The scraped `title` text has some encoding artifacts (e.g. `â` showing
  up instead of an apostrophe or dash) because of how the source site
  encodes special characters. This wasn't fixed in cleaning since it
  doesn't affect the numeric analysis — could be fixed later with a
  proper UTF-8 re-decode if needed.
- `pandas_readback.py` exists mainly to prove that a SQL join query and
  an equivalent `pandas.merge` give identical results — a good sanity
  check that the SQL is doing what you'd expect.