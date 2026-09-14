import json
import requests
from bs4 import BeautifulSoup

URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_macro.php?skr=2026&sem=1&fak=11110&druh=MGR&kruh=1003&b=Zobraz+MGR.MED.1.LEK.a.1003.P"
BASE_URL = "https://is.cuni.cz/studium/rozvrhng/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
}

def get_schedule():
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # 1. Nejprve navštívíme základní rozhraní rozvrhu, abychom dostali relaci (cookies)
        session.get(BASE_URL, timeout=15)
        
        # 2. Stáhneme konkrétní rozvrh se všemi cookies
        response = session.get(URL, timeout=15)
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        events = []

        # Hledáme políčka s rozvrhem (podle CSS tříd nebo struktur tabulky)
        schedule_cells = soup.find_all(["td", "div"], class_=lambda c: c and "rozvrh" in c)

        for cell in schedule_cells:
            text = cell.get_text(separator=" | ", strip=True)
            if text:
                events.append({
                    "text": text,
                    "info": cell.get("title", "")
                })

        # Pokud CSS třídy nesedí, zkusíme vyextrahovat všechny tabulkové buňky
        if not events:
            rows = soup.find_all("tr")
            for row in rows:
                cols = [c.get_text(separator=" ", strip=True) for c in row.find_all(["td", "th"]) if c.get_text(strip=True)]
                if len(cols) > 1:
                    events.append({"riadok": cols})

        return events

    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    schedule_data = get_schedule()

    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=4)
