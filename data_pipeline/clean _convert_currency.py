import re
import pandas as pd
import os

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_CSV_PATH = os.path.join(BASE_DIR, "books_raw.csv")
CLEAN_CSV_PATH = "books_clean.csv"

rate = GBP_INR_RATE = 105.50

RATING = {"One":1, "Two":2, "Three":3, "Four":4, "Five" : 5}

def parse_price(price_text):
    match = re.search(r"[\d.]+", str(price_text).replace(",",""))
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None
    
def parse_rating(rating_word):
    return RATING.get(str(rating_word).strip(), None)

def parse_availability(availability_text):
    text = str(availability_text).lower()
    if "in stock" in text:
        return True
    if "out of stock" in text:
        return False
    return None

def clean_dataframe(raw_df):
    df = raw_df.copy()
    
    df["price_gbp"] = df["price"].apply(parse_price)
    df["rating"] = df["star_rating"].apply(parse_rating)
    df["in_stock_raw"] = df["availability"].apply(parse_availability)
    
    before = len(df)
    df = df[df["title"].astype(str).str.strip().ne("")& df["title"].notna()]
    df = df[df["category"].astype(str).str.strip().ne("")& df["category"].notna()]
    df = df[df["in_stock_raw"].notna()]
    dropped = before - len(df)
    if dropped:
        print(f" dropped {dropped} row(s) with unparseable/missing "
              f"title, category, or availability")
        
    for col in ["price_gbp", "rating"]:
        n_missing = df[col].isna().sum()
        if n_missing :
            median_value = df[col].median()
            df[col] = df[col].fillna(median_value)
            print(f" median-imputed {n_missing} value(s) in '{col}"
                  f" with median = {median_value}")
    
    df["rating"] = df["rating"].fillna(0)
    df["rating"] = df["rating"].round().astype(int)
    df["in_stock"] = df["in_stock_raw"].astype(bool)
    df["price_inr"] = (df["price_gbp"] * rate).round(2)
    
    df = df[["title", "price_gbp","price_inr", "rating", "in_stock", "category"]]
    df = df.reset_index(drop=True)
    return df

def main():
    raw_df = pd.read_csv(RAW_CSV_PATH)
    print(f"Loaded {len(raw_df)} raw rows from {RAW_CSV_PATH}\n")
 
    print("Cleaning ...")
    clean_df = clean_dataframe(raw_df)
 
    clean_df.to_csv(CLEAN_CSV_PATH, index=False)
    print(f"\nSaved {len(clean_df)} cleaned rows -> {CLEAN_CSV_PATH}")
    print(clean_df.dtypes)
    print(clean_df.head(3).to_string(index=False))
 
 
if __name__ == "__main__":
    main()