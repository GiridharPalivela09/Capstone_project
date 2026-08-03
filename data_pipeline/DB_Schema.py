import sqlite3

#====================================================
# Database and Schema
#======================================================
DB_PATH = "books_catalouge.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS categories(
    category_id INTEGER PRIMARY KEY,
    category_name  TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS books(
    book_id     INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    price_gbp   REAL NOT NULL,
    price_inr   REAL NOT NULL,
    rating      INTEGER NOT NULL,
    in_stock    INTEGER NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(category_id) 
);

"""

def create_schema(db_path = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("DROP TABLE IF EXISTS books; DROP TABLE IF EXISTS categories;")
    cur.executescript(SCHEMA_SQL)
    conn.commit()
    return conn

def main():
    conn = create_schema()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
    tables =[row[0] for row in cur.fetchall()]
    print(f"Created schema in {DB_PATH}")
    print(f"Tables: {tables}")
 
    cur.execute("PRAGMA table_info(categories);")
    print("\ncategories columns:", cur.fetchall())
    cur.execute("PRAGMA table_info(books);")
    print("books columns:", cur.fetchall())
 
    conn.close()
 
 
if __name__ == "__main__":
    main()