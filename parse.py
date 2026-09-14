import json
import traceback
import requests
import urllib.parse
from icalendar import Calendar
from datetime import datetime

# Tvůj funkční ScraperAPI klíč
API_KEY = "5def1e9cd2bbc227e56f10ec4fd067a4"

# Tvůj správný odkaz na ICS
TARGET_URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_micro.php?id=5f9a0f7350690e69e32bfbe856b89fc5&tid=&zobraz=1&b=1&kruh=1003&skr=2026&sem=1&fak=11110&ical=1"

# Zabalíme tvůj odkaz do maskovací služby
PROXY_URL = f"http://api.scraperapi.com/?api_key={API_KEY}&url={urllib.parse.quote(TARGET_URL)}"

def parse_ics():
    # Stáhneme to přes prostředníka (timeout dáme delší, proxy může chvilku trvat)
    response = requests.get(PROXY_URL, timeout=45)
    response.raise_for_status() 
    
    cal = Calendar.from_ical(response.content)
    events = []
    
    for component in cal.walk('vevent'):
        summary = str(component.get('summary', ''))
        location = str(component.get('location', ''))
        
        dtstart = component.get('dtstart')
        dtend = component.get('dtend')
        
        start_iso = dtstart.dt.isoformat() if dtstart else ""
        end_iso = dtend.dt.isoformat() if dtend else ""
        
        events.append({
            "predmet": summary,
            "mistnost": location,
            "zacatek": start_iso,
            "konec": end_iso
        })
        
    events.sort(key=lambda x: x["zacatek"] if x["zacatek"] else "")
    
    return {
        "_meta": {
            "cas_aktualizace": datetime.now().isoformat(),
            "pocet_hodin": len(events),
            "zdroj": "ICS přes ScraperAPI"
        },
        "data": events
    }

if __name__ == "__main__":
    try:
        vysledek = parse_ics()
    except Exception as e:
        vysledek = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        
    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(vysledek, f, ensure_ascii=False, indent=4)
        
    print("Skript dokončen.")
