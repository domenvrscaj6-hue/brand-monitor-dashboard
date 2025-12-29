from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

def scrape_brute_force():
    print("🌐 Odpiram Edge...")
    driver = webdriver.Edge()
    
    try:
        driver.get("https://web-scraping.dev/reviews")
        time.sleep(3)
        
        last_count = 0
        print("🚀 Nalagam ocene...")
        
        while True:
            # Preštejemo okvirčke
            current_reviews = driver.find_elements(By.CLASS_NAME, "review")
            if len(current_reviews) > last_count:
                last_count = len(current_reviews)
                print(f"Najdeno {last_count} ocen...")
                try:
                    btn = driver.find_element(By.ID, "page-load-more")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(2)
                except:
                    break
            else:
                break

        print("📊 KONČNI ZAJEM: Prenašam vsebino vseh 96 elementov...")
        # Počakamo dodatnih 5 sekund, da se vsebina "usede"
        time.sleep(5) 
        
        final_elements = driver.find_elements(By.CLASS_NAME, "review")
        podatki = []
        
        for el in final_elements:
            # KLJUČ: Vzamemo CELOTNO besedilo okvirčka naenkrat
            surovo_besedilo = el.text.strip()
            if surovo_besedilo:
                vrstice = surovo_besedilo.split('\n')
                # Običajno je prva vrstica datum, ostalo je tekst
                if len(vrstice) >= 2:
                    podatki.append({
                        "Datum": vrstice[0].strip(),
                        "Vsebina": " ".join(vrstice[1:]).strip()
                    })
                else:
                    # Če je samo ena vrstica, jo vseeno shranimo
                    podatki.append({"Datum": "Neznano", "Vsebina": surovo_besedilo})

        if podatki:
            df = pd.DataFrame(podatki).drop_duplicates()
            os.makedirs("data", exist_ok=True)
            path = "data/reviews.csv"
            df.to_csv(path, index=False, encoding='utf-8-sig')
            print(f"🎉 USPEH! Shranjenih {len(df)} vrstic v {path}")
        else:
            print("❌ Še vedno ni vsebine. Poskušam zajeti celotno stran...")
            with open("data/raw_page.txt", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_brute_force()