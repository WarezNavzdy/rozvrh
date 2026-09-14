import json
import traceback
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_macro.php?skr=2026&sem=1&fak=11110&druh=MGR&kruh=1003&b=Zobraz+MGR.MED.1.LEK.a.1003.P"

def get_schedule():
    output = {
        "_debug": {
            "cas_spusteni": datetime.now().isoformat(),
        },
        "data": []
    }

    try:
        # Vytvoření scraperu, který maskuje Python jako Chrome
        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })
        
        # Otevření odkazu přes maskovaný prohlížeč
        response = scraper.get(URL, timeout=20)
        response.encoding = "utf-8"
        
        output["_debug"]["status_code"] = response.status_code
        output["_debug"]["vysledna_url"] = response.url
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Vytěžení dat
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cols = [c.get_text(separator=" ", strip=True) for c in row.find_all(["td", "th"])]
                cols_clean = [c for c in cols if c]
                if len(cols_clean) > 0:
                    output["data"].append(cols_clean)

    except Exception as e:
        output["_debug"]["chyba"] = str(e)
        output["_debug"]["traceback"] = traceback.format_exc()

    return output

if __name__ == "__main__":
    vysledek = get_schedule()
    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(vysledek, f, ensure_ascii=False, indent=4)
