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

        schedule_cells = soup.find_all(["td", "div"], class_="rozvrh_akce")

        for cell in schedule_cells:
            title_el = cell.find("a") or cell.find("b")
            title = title_el.get_text(strip=True) if title_el else ""

            if not title:
                continue

            lines = cell.get_text(separator="\n").split("\n")
            text_lines = [line.strip() for line in lines if line.strip()]

            tooltip_info = cell.get("title", "")

            event_data = {
                "predmet": title,
                "raw_detaily": text_lines,
                "tooltip": tooltip_info,
            }

            events.append(event_data)

        return events

    except Exception as e:
        print(f"Nastala chyba při zpracování: {e}")
        return []


if __name__ == "__main__":
    schedule_data = get_schedule()

    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=4)

    print(
        f"Hotovo! Vyextrahováno {len(schedule_data)} událostí do rozvrh.json."
    )
