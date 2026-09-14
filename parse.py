import json
import traceback
import requests
from icalendar import Calendar
from datetime import datetime

# Tvůj unikátní ICS odkaz
URL = "https://is.cuni.cz/studium/rozvrhng/roz_student_micro.php?id=5f9a0f7350690e69e32bfbe856b89fc5&tid=&zobraz=1&b=1&kruh=1003&skr=2026&sem=1&fak=11110&ical=1"

def parse_ics():
    # Stáhneme ICS soubor
    response = requests.get(URL, timeout=15)
    response.raise_for_status() # Pokud by byl přeci jen problém, skript hodí přesnou chybu
    
    cal = Calendar.from_ical(response.content)
    events = []
    
    # Projdeme všechny události v kalendáři
    for component in cal.walk('vevent'):
        summary = str(component.get('summary', ''))
        description = str(component.get('description', ''))
        location = str(component.get('location', ''))
        
        # Získání a formátování času
        dtstart = component.get('dtstart')
        dtend = component.get('dtend')
        
        start_iso = dtstart.dt.isoformat() if dtstart else ""
        end_iso = dtend.dt.isoformat() if dtend else ""
        
        events.append({
            "predmet": summary,
            "mistnost": location,
            "zacatek": start_iso,
            "konec": end_iso,
            "detail": description
        })
        
    # Seřadíme hodiny podle času začátku
    events.sort(key=lambda x: x["zacatek"])
    
    return {
        "_meta": {
            "cas_aktualizace": datetime.now().isoformat(),
            "pocet_hodin": len(events),
            "zdroj": "ICS Export SIS"
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
