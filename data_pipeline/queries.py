import sqlite3
import pandas as pd
import os
from DB_Schema import DB_PATH,SCHEMA_SQL,create_schema


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONVERTED_CSV_PATH = os.path.join(BASE_DIR, "books_clean.csv")
QUERY_LOG_PATH = "query_results.txt"

def load_to_sqlite(converted_df, db_path = DB_PATH):
    conn = create_schema(db_path)
    cur = conn.cursor()
    
    categories = sorted(converted_df["category"].unique())
    cat_id_map = {}
    for name in categories:
        cur.execute("INSERT INTO categories (category_name) VALUES(?)", (name,))
        cat_id_map[name] = cur.lastrowid
    
    for row in converted_df.itertuples(index = False):
        cur.execute(
            """INSERT INTO books(title, price_gbp, price_inr, rating, in_stock, category_id)
                VALUES (?, ?, ?, ?, ?, ?)""",
            (
                row.title,
                row.price_gbp,
                row.price_inr,
                int(row.rating),
                int(row.in_stock),
                cat_id_map[row.category]
            ),
        )
    conn.commit()
    return conn, cat_id_map


QUERIES = {
    "q1_top_rated_expensive":"""
        SELECT title, price_gbp, rating
        FROM books
        WHERE rating >=4
        ORDER BY price_gbp DESC
        LIMIT 10;
    """,
    "Q2_distinct_ratings": """
        SELECT DISTINCT rating
        FROM books
        ORDER BY rating;
    """,
    "Q3_midrange_price_between": """
        SELECT title, price_gbp, price_inr
        FROM books
        WHERE price_gbp BETWEEN 10 AND 20
        ORDER BY price_inr;
    """,
    "Q4_specific_categories_in": """
        SELECT title, category_id
        FROM books
        WHERE category_id IN (1, 2)
        ORDER BY category_id, title;
    """,
    "Q5_join_five_star_by_category": """
        SELECT b.title, b.price_inr, b.rating, c.category_name
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.rating = 5
        ORDER BY b.price_inr DESC
        LIMIT 10;
    """,
    "Q6_join_category_summary": """
        SELECT c.category_name,
               COUNT(*)                   AS num_books,
               ROUND(AVG(b.price_inr), 2) AS avg_price_inr
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        GROUP BY c.category_name
        ORDER BY num_books DESC;
    """,
}

def run_queries(conn, log_path=QUERY_LOG_PATH):
    results = {}
    with open(log_path, "w", encoding="utf-8") as log:
        for name, sql in QUERIES.items():
            df = pd.read_sql(sql, conn)
            results[name] = df
            log.write(f"--- {name} ---\n{sql.strip()}\n\n{df.to_string(index=False)}\n\n")
    return results
 
 
def main():
    converted_df = pd.read_csv(CONVERTED_CSV_PATH)
    print(f"Loaded {len(converted_df)} rows from {CONVERTED_CSV_PATH}\n")
 
    print("Loading into SQLite schema ...")
    conn, cat_id_map = load_to_sqlite(converted_df)
    print(f"  {len(cat_id_map)} categories, {len(converted_df)} books "
          f"loaded into {DB_PATH}\n")
 
    print("Running SQL queries ...")
    results = run_queries(conn)
    for name, df in results.items():
        print(f"  {name}: {len(df)} row(s)")
    print(f"\nFull query text + output saved -> {QUERY_LOG_PATH}")
 
    conn.close()
 
 
if __name__ == "__main__":
    main()