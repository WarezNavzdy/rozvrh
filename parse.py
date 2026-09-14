import json
import requests
from bs4 import BeautifulSoup

URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_macro.php?skr=2026&sem=1&fak=11110&druh=MGR&kruh=1003&b=Zobraz+MGR.MED.1.LEK.a.1003.P"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
}


def get_schedule():
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        output = []

        # 1. Vyhledání všech odkazu a textu v rozvrhu
        cells = soup.find_all(["td", "th", "div"])
        for cell in cells:
            text = cell.get_text(strip=True)
            if text and len(text) > 3:
                output.append(text)

        # Pokud skript nic nenašel, uloží alespoň titulek stránky a část HTML pro diagnózu
        if not output:
            title = soup.title.string if soup.title else "Bez titulku"
            return [{"status": "Nenalezena data", "page_title": title, "body_sample": soup.get_text()[:300]}]

        return output[:100]  # Vráti prvních 100 zachycených prvků

    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    schedule_data = get_schedule()

    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=4)
