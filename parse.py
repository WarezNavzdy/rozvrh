import json
import requests
from bs4 import BeautifulSoup

# URL adresa veřejného rozvrhu 1. LF UK
URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_macro.php?skr=2026&sem=1&fak=11110&druh=MGR&kruh=1003&b=Zobraz+MGR.MED.1.LEK.a.1003.P"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_schedule():
    # 1. Stažení HTML obsahu
    response = requests.get(URL, headers=headers)
    response.encoding = "utf-8"  # Správné kódování pro češtinu

    if response.status_code != 200:
        print(f"Chyba při stahování: Status code {response.status_code}")
        return []

    # 2. Vytvoření parseru
    soup = BeautifulSoup(response.text, "html.parser")
    events = []

    # 3. Vyhledání buněk rozvrhu
    schedule_cells = soup.find_all(["td", "div"], class_="rozvrh_akce")

    for cell in schedule_cells:
        # Extrakce názvu předmětu
        title_el = cell.find("a") or cell.find("b")
        title = title_el.get_text(strip=True) if title_el else ""

        if not title:
            continue

        # Získání čistých řádků textu (ZDE BYLA CHYBA - OPRAVENO)
        lines = cell.get_text(separator="\n").split("\n")
        text_lines = [line.strip() for line in lines if line.strip()]

        # Extrakce atributu 'title' (tooltip)
        tooltip_info = cell.get("title", "")

        event_data = {
            "predmet": title,
            "raw_detaily": text_lines,
            "tooltip": tooltip_info,
        }

        events.append(event_data)

    return events


if __name__ == "__main__":
    schedule_data = get_schedule()

    # 4. Uložení výsledku do JSON souboru
    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=4)

    print(f"Hotovo! Vyextrahováno {len(schedule_data)} událostí do rozvrh.json.")