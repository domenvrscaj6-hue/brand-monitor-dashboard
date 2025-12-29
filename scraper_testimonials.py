from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

def scrape_testimonials_scroll():
    print("🌐 Odpiram Edge za testimoniale...")
    driver = webdriver.Edge()
    
    try:
        driver.get("https://web-scraping.dev/testimonials")
        time.sleep(3)
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        print("🚀 Začenjam drsenje (scroll) do konca strani...")

        while True:
            # Podrsamo do dna strani
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Počakamo 2 sekundi (uporabnik je rekel 1s, dodava malo rezerve za stabilnost)
            time.sleep(2)
            
            # Preverimo novo višino strani
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Če se višina ni spremenila, smo na koncu
            if new_height == last_height:
                print("✅ Doseženo dno strani. Nič več novih testimonialov.")
                break
            
            last_height = new_height
            print("Nalagam nove vsebine...")

        print("📊 Prenašam besedila testimonialov...")
        # Ponovimo zmagovalno "brute force" metodo
        testimonial_elements = driver.find_elements(By.CLASS_NAME, "testimonial")
        results = []
        
        for el in testimonial_elements:
            try:
                # Iščemo specifičen razred 'text' znotraj testimonial kartice
                txt = el.find_element(By.CLASS_NAME, "text").get_attribute("innerText")
                if txt:
                    results.append({"Testimonial": txt.strip()})
            except:
                continue
        
        if results:
            df = pd.DataFrame(results).drop_duplicates()
            os.makedirs("data", exist_ok=True)
            path = "data/testimonials.csv"
            df.to_csv(path, index=False, encoding='utf-8-sig')
            print(f"🎉 USPEH! Shranjenih {len(df)} testimonialov.")
        else:
            print("❌ Napaka: Seznam testimonialov je prazen.")

    finally:
        print("🛑 Zapiram brskalnik.")
        driver.quit()

if __name__ == "__main__":
    scrape_testimonials_scroll()