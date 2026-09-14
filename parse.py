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
    response.encoding = "utf-8"  # Nastavení kódování pro správnou češtinu

    if response.status_code != 200:
        print(f"Chyba při stahování: Status code {response.status_code}")
        return []

    # 2. Vytvoření parseru
    soup = BeautifulSoup(response.text, "html.parser")
    events = []

    # 3. Vyhledání buněk rozvrhu (IS UK používá pro políčka akcí třídu 'rozvrh_akce')
    schedule_cells = soup.find_all(["td", "div"], class_="rozvrh_akce")

    for cell in schedule_cells:
        # Extrakce názvu předmětu (bývá v odkazu nebo divu s názvem)
        title_el = cell.find("a") or cell.find("b")
        title = title_el.get_text(strip=True) if title_el else ""

        # Pokud jsme nenašli název, přeskočíme prázdnou buňku
        if not title:
            continue

        # Získání celého textu z buňky pro další detaily
        text_lines = [
            line.strip()
            for line.strip() in cell.get_text(separator="\n").split("\n")
            if line.strip()
        ]

        # Extrakce z tooltipu/atributu 'title', kde IS UK často schovává kompletní detaily
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