import json
import traceback
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

LOGIN_URL = "https://is.cuni.cz/studium/login.php"
SCHEDULE_URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_macro.php"

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
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8"
}

def get_schedule():
    session = requests.Session()
    session.headers.update(headers)
    
    output = {
        "_debug": {
            "cas_spusteni": datetime.now().isoformat(),
            "kroky": []
        },
        "data": []
    }

    try:
        # 1. Načtení hlavní přihlašovací stránky (abychom dostali cookies a tokeny)
        r_init = session.get(LOGIN_URL, timeout=15)
        soup_init = BeautifulSoup(r_init.text, "html.parser")
        
        output["_debug"]["kroky"].append({
            "akce": "nacteni_login_stranky",
            "status_code": r_init.status_code
        })

        # 2. Nalezení odkazu pro anonymní přihlášení (ten obsahuje dynamický token)
        anonym_href = None
        for a in soup_init.find_all("a", href=True):
            if "do=anonym" in a["href"]:
                anonym_href = a["href"]
                break
        
        # 3. Kliknutí na anonymní odkaz s platným tokenem
        if anonym_href:
            anonym_url = urljoin(r_init.url, anonym_href)
            r_anonym = session.get(anonym_url, timeout=15)
            
            output["_debug"]["kroky"].append({
                "akce": "kliknuti_na_anonym",
                "status_code": r_anonym.status_code,
                "vysledna_url": r_anonym.url
            })
        else:
            output["_debug"]["kroky"].append({"akce": "chyba", "detail": "Nenalezen odkaz pro anonymni prihlaseni."})

        # 4. Stažení samotného rozvrhu (teď už jako legálně ověřený anonym)
        r_sched = session.get(SCHEDULE_URL, params=PARAMS, timeout=15)
        r_sched.encoding = "utf-8"
        soup_sched = BeautifulSoup(r_sched.text, "html.parser")
        
        output["_debug"]["kroky"].append({
            "akce": "stazeni_rozvrhu",
            "status_code": r_sched.status_code,
            "vysledna_url": r_sched.url
        })

        # 5. Parsování dat z tabulek rozvrhu
        tables = soup_sched.find_all("table")
        for table in tables:
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
