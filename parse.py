import json
import traceback
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Přesná URL bez jakýchkoliv úprav. 
# Použijeme ji jako jeden surový string přesně tak, jak ji kopíruješ do prohlížeče.
URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_macro.php?skr=2026&sem=1&fak=11110&druh=MGR&kruh=1003&b=Zobraz+MGR.MED.1.LEK.a.1003.P"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8"
}

def get_schedule():
    output = {
        "_debug": {
            "cas_spusteni": datetime.now().isoformat(),
        },
        "data": []
    }

    try:
        # Voláme to úplně napřímo, bez Session, bez přihlašování, prostě jako ty v anonymním okně.
        response = requests.get(URL, headers=headers, timeout=15)
        response.encoding = "utf-8"
        
        output["_debug"]["status_code"] = response.status_code
        output["_debug"]["vysledna_url"] = response.url
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Vytěžení dat - bereme úplně všechno z tabulek
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
