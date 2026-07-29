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

Base_URL = "https://books.toscrape.com/"
Headers = {"User-Agent": "Mozilla/5.0 (educational scraping exercises)"}
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

DB_PATH = "books_catalog.db"




