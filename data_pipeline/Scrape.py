#=========================================================
# Importing Libraries 
#=========================================================
import re
import sqlite3
import time 
from urllib.parse import urljoin
import requests
import pandas as pd
from bs4 import BeautifulSoup

#====================================================
#Configuration
#====================================================

BASE_URL = "https://books.toscrape.com/"
HEADERS  = {"User-Agent": "Mozilla/5.0 (educational scraping exercises)"}
CATEGORIES_TO_SCRAPE = [
    "Travel",
    "Mystery",
    "Historical Fiction",
    "Sequential Art",
    "Classics",
    "Philosophy",
    "Romance",
    "Womens Fiction",
    "Fiction",
    "History",
    "Childrens",
    "Religion",
]

GBP_INR_RATE = 105.50

MIN_BOOKS = 60

RATING = {"One":1, "Two":2, "Three":3, "Four":4, "Five" : 5}

RAW_CSV_PATH = "books_raw.csv"


#========================================================================================================
# Scrape
#=========================================================================================================


def get_category_urls(session):
    res = session.get(BASE_URL, headers = HEADERS, timeout=15)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    
    
    links = {}
    for a in soup.select("div.side_categories ul li ul li a"):
        name = a.text.strip()
        href = urljoin(BASE_URL, a["href"])
        links[name] = href
    return links


def scrape_category(session, start_url, category_name):
    books = []
    url = start_url
    while url:
        res = session.get(url, headers = HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        for article in soup.select("article.product_pod"):
            title = article.h3.a["title"].strip()
            price_text = article.select_one(".price_color").text.strip()
            rating_classes = article.select_one("p.star-rating")["class"]
            rating_word = rating_classes[1] if len(rating_classes) > 1 else ""
            availability_text = article.select_one(".availability").text.strip()
            rating = RATING.get(rating_word, 0)
            
            books.append(
                {
                    "title": title,
                    "price": price_text,
                    "star_rating": rating,
                    "availability": availability_text,
                    "category": category_name,
                }
            )
        next_link = soup.select_one("li.next a")
        url = urljoin(url, next_link["href"]) if next_link else None
        time.sleep(0.2)
        
    return books

def scrape_all(min_books = MIN_BOOKS, categories = CATEGORIES_TO_SCRAPE):
    session = requests.session()
    category_urls = get_category_urls(session)
    
    
    all_books = []
    for cat_name in categories:
        if cat_name not in category_urls:
            print(f" [skip] category not found on site: {cat_name}")
            continue
        cat_books = scrape_category(session, category_urls[cat_name], cat_name)
        all_books.extend(cat_books)
        print(f" scraped{len(cat_books):>3} books from '{cat_name}'"
              f"(running total : {len(all_books)})")
        if len(all_books) >= min_books:
            break
    if len(all_books)  < min_books:
        raise RuntimeError(
            f"Only collected {len(all_books)} books, need at least {min_books}. "
            "Add more categories to CATEGORIES_TO_SCRAPE."
        )
    return all_books

def main():
    print("Scraping books.toscrape.com ...")
    raw_books = scrape_all()
    raw_df = pd.DataFrame(raw_books)
    raw_df.to_csv(RAW_CSV_PATH, index=False)
    print(f"\nSaved {len(raw_df)} rows -> {RAW_CSV_PATH}")
    print(raw_df.head(3).to_string(index=False))
 
 
if __name__ == "__main__":
    main()
    