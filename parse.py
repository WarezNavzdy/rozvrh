import json
import traceback
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URL pro získání anonymního přístupu
LOGIN_URL = "https://is.cuni.cz/studium/login.php?do=anonym"
# Čistá URL rozvrhu bez parametrů
SCHEDULE_URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_macro.php"

# Parametry pošleme bezpečně jako slovník, aby si Python pohlídal formátování
PARAMS = {
    "skr": "2026",
    "sem": "1",
    "fak": "11110",
    "druh": "MGR",
    "kruh": "1003",
    "b": "Zobraz MGR.MED.1.LEK.a.1003.P"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
    "Referer": "https://is.cuni.cz/studium/index.php"
}

def get_schedule():
    session = requests.Session()
    session.headers.update(headers)
    
    # Debugovací hlavička, která nám řekne, co přesně se děje a donutí Git udělat commit
    output = {
        "_debug": {
            "cas_spusteni": datetime.now().isoformat(),
            "kroky": []
        },
        "pocet_polozek": 0,
        "data": []
    }

    try:
        # KROK 1: Aktivace session
        r_login = session.get(LOGIN_URL, timeout=15, allow_redirects=True)
        output["_debug"]["kroky"].append({
            "akce": "prihlaseni",
            "status_code": r_login.status_code,
            "url_po_presmerovani": r_login.url,
            "cookies": session.cookies.get_dict()
        })

        # KROK 2: Stažení rozvrhu (parametry přidá requests automaticky a správně)
        r_sched = session.get(SCHEDULE_URL, params=PARAMS, timeout=15)
        r_sched.encoding = "utf-8"
        
        soup = BeautifulSoup(r_sched.text, "html.parser")
        page_title = soup.title.string.strip() if soup.title else "Bez titulku"
        
        output["_debug"]["kroky"].append({
            "akce": "stazeni_rozvrhu",
            "status_code": r_sched.status_code,
            "url_po_presmerovani": r_sched.url,
            "titulek_stranky": page_title
        })

        # KROK 3: Vytěžení úplně všech tabulek na stránce
        tables = soup.find_all("table")
        for table in tables:
            for row in table.find_all("tr"):
                # Vytáhneme text ze všech buněk na řádku
                cols = [c.get_text(separator=" ", strip=True) for c in row.find_all(["td", "th"])]
                # Vyfiltrujeme prázdné buňky
                cols_clean = [c for c in cols if c]
                
                # Pokud má řádek nějaký obsah, přidáme ho do výsledku
                if len(cols_clean) > 0:
                    output["data"].append(cols_clean)

        output["pocet_polozek"] = len(output["data"])

    except Exception as e:
        output["_debug"]["chyba"] = str(e)
        output["_debug"]["traceback"] = traceback.format_exc()

    return output

if __name__ == "__main__":
    vysledek = get_schedule()
    
    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(vysledek, f, ensure_ascii=False, indent=4)
