import json
import traceback
import requests
from bs4 import BeautifulSoup
from datetime import datetime

ANONYM_URL = "https://is.cuni.cz/studium/login.php?do=anonym"
ROZVRH_INDEX = "https://is.cuni.cz/studium/rozvrhng/index.php"
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
        # 1. KROK: Přihlášení jako anonym
        r_anonym = session.get(ANONYM_URL, timeout=15)
        output["_debug"]["kroky"].append({
            "akce": "anonymni_prihlaseni",
            "status_code": r_anonym.status_code,
            "url": r_anonym.url
        })

        # 2. KROK: Inicializace modulu Rozvrh (TOHLE BOTOVI CHYBĚLO)
        r_index = session.get(ROZVRH_INDEX, timeout=15)
        output["_debug"]["kroky"].append({
            "akce": "otevreni_modulu_rozvrh",
            "status_code": r_index.status_code,
            "url": r_index.url
        })

        # 3. KROK: Zobrazení samotného rozvrhu
        r_sched = session.get(SCHEDULE_URL, params=PARAMS, timeout=15)
        r_sched.encoding = "utf-8"
        soup_sched = BeautifulSoup(r_sched.text, "html.parser")
        
        output["_debug"]["kroky"].append({
            "akce": "stazeni_rozvrhu",
            "status_code": r_sched.status_code,
            "url": r_sched.url
        })

        # Vytěžení dat
        for table in soup_sched.find_all("table"):
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
