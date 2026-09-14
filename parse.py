import json
import traceback
import os
from icalendar import Calendar
from datetime import datetime

# Název tvého souboru, který jsi nahrál na GitHub
ICS_FILE = "muj_rozvrh.ics"

def parse_local_ics():
    # Kontrola, jestli jsi soubor nahrál správně
    if not os.path.exists(ICS_FILE):
        return {"error": f"Soubor '{ICS_FILE}' nebyl v repozitáři nalezen."}

    # Načtení a parsování lokálního souboru
    with open(ICS_FILE, "rb") as f:
        cal = Calendar.from_ical(f.read())
        
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
        
    # Seřadíme podle času
    events.sort(key=lambda x: x["zacatek"] if x["zacatek"] else "")
    
    return {
        "_meta": {
            "cas_aktualizace": datetime.now().isoformat(),
            "pocet_hodin": len(events),
            "zdroj": "Lokální ICS soubor"
        },
        "data": events
    }

if __name__ == "__main__":
    try:
        vysledek = parse_local_ics()
    except Exception as e:
        vysledek = {"error": str(e), "traceback": traceback.format_exc()}
        
    with open("rozvrh.json", "w", encoding="utf-8") as f:
        json.dump(vysledek, f, ensure_ascii=False, indent=4)
        
    print("Hotovo! Lokální ICS převeden na JSON.")
