import json
import requests
from bs4 import BeautifulSoup

URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_macro.php?skr=2026&sem=1&fak=11110&druh=MGR&kruh=1003&b=Zobraz+MGR.MED.1.LEK.a.1003.P"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "cs,en;q=0.9",
}


def get_schedule():
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.encoding = "utf-8"

        if response.status_code != 200:
            print(f"Chyba při stahování HTML: Status code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        events = []

        # Najdeme všechny tabulky na stránce
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all(["td", "th"])
                row_data = []

                for col in cols:
                    text = col.get_text(separator=" ", strip=True)
                    if text:
                        row_data.append(text)

                # Pokud řádek obsahuje smysluplná data, uložíme ho
                if len(row_data) > 1:
                    events.append({"riadok": row_data})

        return events

    except Exception as e:
        print(f"Chyba skriptu: {e}")
        return []


if __name__ == "__main__":
    schedule_data = get_schedule()

    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=4)

    print(f"Hotovo! Vyextrahováno {len(schedule_data)} položek do rozvrh.json.")
