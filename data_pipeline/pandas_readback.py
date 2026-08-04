import sqlite3
import pandas as pd
from DB_Schema import DB_PATH
from queries import QUERIES
import os

OUTPUT_PATH = "pandas_readback_results.txt"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "books_catalouge.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    
    q1_pandas = pd.read_sql(QUERIES["q1_top_rated_expensive"], conn)
    q6_pandas = pd.read_sql(QUERIES["Q6_join_category_summary"], conn)
 
    
    books_df = pd.read_sql("SELECT * FROM books;", conn)
    categories_df = pd.read_sql("SELECT * FROM categories;", conn)
 
    merged = books_df.merge(categories_df, on="category_id", how="inner")
    merged_q5 = (
        merged[merged["rating"] == 5][["title", "price_inr", "rating", "category_name"]]
        .sort_values("price_inr", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
 
    sql_q5 = pd.read_sql(QUERIES["Q5_join_five_star_by_category"], conn).reset_index(drop=True)
    equivalent = merged_q5.equals(sql_q5)
 
    conn.close()
 
    with open(OUTPUT_PATH, "w") as f:
        f.write("Q1 (pd.read_sql):\n")
        f.write(q1_pandas.to_string(index=False) + "\n\n")
 
        f.write("Q6 (pd.read_sql):\n")
        f.write(q6_pandas.to_string(index=False) + "\n\n")
 
        f.write("Q5 via SQL JOIN (pd.read_sql):\n")
        f.write(sql_q5.to_string(index=False) + "\n\n")
 
        f.write("Q5 reproduced via pd.merge on in-memory DataFrames:\n")
        f.write(merged_q5.to_string(index=False) + "\n\n")
 
        f.write(f"pd.merge result matches SQL JOIN result exactly: {equivalent}\n")
 
    print("Q1 via pd.read_sql, first 3 rows:")
    print(q1_pandas.head(3).to_string(index=False))
    print("\nQ6 via pd.read_sql:")
    print(q6_pandas.to_string(index=False))
    print(f"\npd.merge reproduction of Q5 matches SQL JOIN result exactly: {equivalent}")
    print(f"\nSaved full comparison -> {OUTPUT_PATH}")
 
    assert equivalent, "pd.merge reproduction did not match the SQL JOIN result!"
 
 
if __name__ == "__main__":
    main()