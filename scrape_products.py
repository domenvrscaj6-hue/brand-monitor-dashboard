import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# KONSTANTE
BASE_URL = "https://web-scraping.dev/products"
PAGES = range(1, 6)
OUTPUT_FILE = "data/products.csv"

def scrape_all_products():
    all_products = []
    
    for page in PAGES:
        print(f"Scrapam stran {page}...")
        params = {"page": page}
        
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            product_elements = soup.select('div.row.product')
            
            for el in product_elements:
                name_el = el.select_one('h3 > a')
                desc_el = el.select_one('div.short-description')
                price_el = el.select_one('div.price')
                
                all_products.append({
                    "ime": name_el.get_text(strip=True) if name_el else "N/A",
                    "opis": desc_el.get_text(strip=True) if desc_el else "N/A",
                    "cena": price_el.get_text(strip=True) if price_el else "N/A",
                    "stran": page
                })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Napaka na strani {page}: {e}")

    if all_products:
        os.makedirs("data", exist_ok=True)
        df = pd.DataFrame(all_products)
        
        # --- ODSTRANJEVANJE DUPLIKATOV ---
        zacetno_st = len(df)
        # Odstranimo vrstice, kjer sta IME in OPIS identična
        df = df.drop_duplicates(subset=['ime', 'opis'], keep='first')
        koncno_st = len(df)
        
        if zacetno_st > koncno_st:
            print(f"Očiščeno: Odstranjenih {zacetno_st - koncno_st} duplikatov.")
        # --------------------------------
        
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        return df
    return None

if __name__ == "__main__":
    df = scrape_all_products()
    if df is not None:
        print(f"\n✅ Uspeh! Ustvarjena očiščena datoteka s {len(df)} unikati.")
        print(df.head())