import os
import json
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo

# =============================================================================
# 1. STYLE-KLASSE: FARBEN UND UI-ELEMENTE
# =============================================================================
class Style:
    """
    Diese Klasse speichert alle ANSI-Farbcodes, um das Terminal schöner
    zu gestalten. Das sorgt für eine bessere User Experience (UX).
    """
    GRUEN = '\033[92m'
    GELB = '\033[93m'
    ROT = '\033[91m'
    BLAU = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    FETT = '\033[1m'
    UNTERSTRICH = '\033[4m'
    ENDE = '\033[0m'
    
    # Trennlinien für die Strukturierung der Anzeige
    LINIE_DICK = f"{CYAN}" + "━" * 60 + f"{ENDE}"
    LINIE_DUNN = f"{CYAN}" + "─" * 60 + f"{ENDE}"

# Name der Datei, in der alle Fortschritte gespeichert werden
DATA_FILE = "vokabel_ultimate_data.json"

# =============================================================================
# 2. DATA-MANAGEMENT (LADEN, SPEICHERN, UPDATEN)
# =============================================================================

def laden():
    """
    Lädt die Datenbank aus der JSON-Datei.
    Beinhaltet eine Migrationslogik, um alte Dateiformate automatisch
    auf das neue Abteil-System (Kategorien) zu aktualisieren.
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                
                # PRÜFUNG: Existiert das Abteil-System?
                if "abteile" not in d:
                    # Migration von alter Struktur
                    alte_v = d.get("vokabeln", {})
                    alte_s = d.get("saetze", {})
                    d["abteile"] = {
                        "Allgemein": {
                            "vokabeln": alte_v,
                            "saetze": alte_s
                        }
                    }
                
                # PRÜFUNG: Einstellungen vorhanden?
                if "settings" not in d:
                    d["settings"] = {
                        "modus": "SP_DE",
                        "typ": "vokabeln",
                        "aktiv_abteil": "Allgemein"
                    }
                
                # PRÜFUNG: Statistiken vorhanden?
                if "stats" not in d:
                    d["stats"] = {"punkte": 0, "korrekt": 0, "falsch": 0}
                
                return d
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            time.sleep(2)
            
    # Standard-Struktur bei Erststart
    return {
        "abteile": {
            "Allgemein": {
                "vokabeln": {"Hola": "Hallo", "Gracias": "Danke"},
                "saetze": {"Como estas?": "Wie geht es dir?"}
            },
            "Restaurant": {
                "vokabeln": {"La cuenta": "Die Rechnung", "Agua": "Wasser"},
                "saetze": {"Una mesa para dos": "Ein Tisch für zwei"}
            }
        },
        "stats": {"punkte": 0, "korrekt": 0, "falsch": 0},
        "settings": {
            "modus": "SP_DE",
            "typ": "vokabeln",
            "aktiv_abteil": "Allgemein"
        }
    }

def speichern(daten):
    """
    Speichert den aktuellen Zustand in der JSON-Datei.
    Verwendet indent=4 für bessere Lesbarkeit durch den Menschen.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

# =============================================================================
# 3. LOGIK-FUNKTIONEN (RÄNGE, BALKEN, HILFE)
# =============================================================================

def get_rang_info(punkte):
    """
    Gibt den aktuellen Rang und die Punkte bis zum nächsten Level zurück.
    """
    if punkte < 100:
        return "Principiante (Anfänger)", 100 - punkte
    elif punkte < 300:
        return "Turista (Tourist)", 300 - punkte
    elif punkte < 600:
        return "Residente (Einwohner)", 600 - punkte
    elif punkte < 1000:
        return "Local (Einheimischer)", 1000 - punkte
    else:
        return "Hidalgo (Spanischer Edelmann)", 0

def zeichne_fortschritt(aktuell, gesamt):
    """
    Erstellt eine visuelle Ladeleiste für das Quiz.
    """
    laenge = 25
    prozent = aktuell / gesamt
    gefuellt = int(laenge * prozent)
    bar = "█" * gefuellt + "░" * (laenge - gefuellt)
    return f"{Style.BLAU}|{bar}| {aktuell}/{gesamt}{Style.ENDE}"

def zeige_hilfe():
    """
    Ein ausführliches Handbuch innerhalb des Programms.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Style.LINIE_DICK)
    print(f"{Style.FETT}{Style.GELB}   HILFE & ANLEITUNG{Style.ENDE}")
    print(Style.LINIE_DICK)
    print("1. MARATHON-QUIZ: Teste dein Wissen mit Punktesystem.")
    print("   Richtig = +10 Punkte | Falsch = -5 Punkte.")
    print("2. FREIES ÜBEN: Lerne ohne Stress. Benutze '?' für Tipps.")
    print("3. ABTEILE: Organisiere Wörter in Gruppen (z.B. Urlaub, Arbeit).")
    print("4. EINSTELLUNGEN: Wechsel zwischen Vokabeln und Sätzen.")
    print("5. SUCHEN: Schnelles Nachschlagen wie in einem Wörterbuch.")
    print("\nTipp: Benutze im Quiz keine Sonderzeichen (á, ñ), wenn du")
    print("das entsprechende Tastaturlayout nicht hast.")
    print(Style.LINIE_DUNN)
    input("Drücke Enter, um zum Menü zurückzukehren...")

def print_logo():
    """
    Gibt ein dekoratives Logo im Terminal aus.
    """
    print(f"{Style.GRUEN}{Style.FETT}")
    print("  ███████╗██████╗  █████╗ ██╗███╗   ██╗")
    print("  ██╔════╝██╔══██╗██╔══██╗██║████╗  ██║")
    print("  ███████╗██████╔╝███████║██║██╔██╗ ██║")
    print("  ╚════██║██╔═══╝ ██╔══██║██║██║╚██╗██║")
    print("  ███████║██║     ██║  ██║██║██║ ╚████║")
    print("  ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝")
    print(f"      VOCABULARY MASTER ULTIMATE{Style.ENDE}")

# =============================================================================
# 4. HAUPTSCHLEIFE (MENÜSTEUERUNG)
# =============================================================================

daten = laden()

while True:
    # GUI-Vorbereitung
    os.system('cls' if os.name == 'nt' else 'clear')
    berlin_zeit = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%H:%M:%S")
    
    # Kurzvariablen für besseren Zugriff
    s = daten["stats"]
    sett = daten["settings"]
    punkte = s["punkte"]
    rang, bis_next = get_rang_info(punkte)
    
    # Aktives Abteil laden
    abt_name = sett["aktiv_abteil"]
    # Validierung: Existiert das Abteil noch?
    if abt_name not in daten["abteile"]:
        abt_name = list(daten["abteile"].keys())[0]
        sett["aktiv_abteil"] = abt_name
        
    typ = sett["typ"] # 'vokabeln' oder 'saetze'
    pool = daten["abteile"][abt_name][typ]
    
    # Dashboard-Anzeige
    print_logo()
    print(Style.LINIE_DICK)
    print(f"🕒 {berlin_zeit} | 📂 {Style.FETT}ABTEIL: {abt_name.upper()}{Style.ENDE}")
    print(f"💡 Modus: {typ.capitalize()} | {sett['modus']}")
    print(Style.LINIE_DUNN)
    print(f"👤 RANG  : {Style.GELB}{rang}{Style.ENDE}")
    print(f"🏆 PUNKTE: {Style.GRUEN}{punkte}{Style.ENDE} (Noch {bis_next} bis zum nächsten Level)")
    print(f"📊 STATS : ✅ {s['korrekt']} Korrekt | ❌ {s['falsch']} Falsch")
    print(Style.LINIE_DICK)
    
    # Menü-Optionen
    print(f"{Style.BLAU}[1]{Style.ENDE} Marathon-Quiz starten")
    print(f"{Style.BLAU}[2]{Style.ENDE} Freies Üben (Lern-Modus)")
    print(f"{Style.BLAU}[3]{Style.ENDE} Eintrag zu '{abt_name}' hinzufügen")
    print(f"{Style.BLAU}[4]{Style.ENDE} Abteil verwalten (Löschen/Ansehen)")
    print(f"{Style.GELB}[5]{Style.ENDE} EINSTELLUNGEN (Abteil/Modus/Typ)")
    print(f"{Style.GRUEN}[6]{Style.ENDE} Suchen (Wörterbuch-Suche)")
    print(f"{Style.MAGENTA}[7]{Style.ENDE} Hilfe / Anleitung")
    print(f"{Style.ROT}[8]{Style.ENDE} Beenden & Speichern")
    print(Style.LINIE_DUNN)
    
    wahl = input(f"{Style.FETT}Deine Wahl (1-8): {Style.ENDE}")

    # --- AKTIONEN ---
    
    if wahl == "1": # QUIZ
        if not pool:
            print(f"{Style.ROT}Dieses Abteil ist leer!{Style.ENDE}")
            time.sleep(1.5)
            continue
            
        try:
            limit_in = input(f"Wie viele Fragen? (1-{len(pool)}): ")
            limit = int(limit_in)
            limit = min(max(1, limit), len(pool))
        except:
            limit = 5
            
        fragen = list(pool.keys())
        random.shuffle(fragen)
        fragen = fragen[:limit]
        runde_korrekt = 0
        
        for idx, q_key in enumerate(fragen, 1):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(Style.LINIE_DICK)
            print(f"QUIZ-MODUS | {zeichne_fortschritt(idx, limit)}")
            print(Style.LINIE_DUNN)
            
            original_de = pool[q_key]
            
            # Richtung bestimmen
            if sett["modus"] == "SP_DE":
                frage, antwort_ziel = q_key, original_de
            else:
                frage, antwort_ziel = original_de, q_key
                
            print(f"\nÜbersetze: {Style.FETT}{Style.CYAN}{frage}{Style.ENDE}")
            user_ans = input("Antwort: ").strip().lower()
            
            if user_ans == antwort_ziel.lower():
                print(f"\n{Style.GRUEN}✨ EXZELLENT! +10 Punkte.{Style.ENDE}")
                s["punkte"] += 10
                s["korrekt"] += 1
                runde_korrekt += 1
            else:
                print(f"\n{Style.ROT}❌ LEIDER FALSCH.{Style.ENDE}")
                print(f"Lösung: {Style.FETT}{antwort_ziel}{Style.ENDE}")
                s["falsch"] += 1
                s["punkte"] = max(0, s["punkte"] - 5)
                
            time.sleep(1)
            input("\nWeiter mit Enter...")
            
        speichern(daten)
        print(f"\n{Style.GELB}RUNDE BEENDET! Du hast {runde_korrekt}/{limit} geschafft.{Style.ENDE}")
        time.sleep(2)

    elif wahl == "2": # ÜBEN
        if not pool:
            print("Abteil leer!"); time.sleep(1); continue
            
        training = True
        while training:
            os.system('cls' if os.name == 'nt' else 'clear')
            q = random.choice(list(pool.keys()))
            de = pool[q]
            f, loes = (q, de) if sett["modus"] == "SP_DE" else (de, q)
            
            print(f"{Style.GELB}--- LERNMODUS ---{Style.ENDE}")
            print("('exit' zum Verlassen, '?' für Lösung)")
            print(f"Frage: {Style.CYAN}{f}{Style.ENDE}")
            
            ans = input("Antwort: ").strip().lower()
            if ans == "exit":
                training = False
            elif ans == "?":
                print(f"Lösung: {Style.FETT}{loes}{Style.ENDE}")
                input("Enter...")
            elif ans == loes.lower():
                print(f"{Style.GRUEN}Richtig!{Style.ENDE}")
                time.sleep(0.5)
            else:
                print(f"{Style.ROT}Nicht ganz...{Style.ENDE}")
                time.sleep(0.8)

    elif wahl == "3": # HINZUFÜGEN
        print(f"\n{Style.FETT}Hinzufügen zu {abt_name} ({typ}){Style.ENDE}")
        sp = input("Spanisch: ").strip()
        de = input("Deutsch : ").strip()
        if sp and de:
            pool[sp] = de
            speichern(daten)
            print(f"{Style.GRUEN}Erfolgreich gespeichert!{Style.ENDE}")
        else:
            print(f"{Style.ROT}Abgebrochen: Leere Eingabe.{Style.ENDE}")
        time.sleep(1.5)

    elif wahl == "4": # VERWALTEN
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Style.FETT}LISTE: {abt_name} ({typ}){Style.ENDE}")
        items = list(pool.items())
        for i, (k, v) in enumerate(items, 1):
            print(f"{i:2}. {k:18} ➔  {v}")
        
        nr = input(f"\nNummer zum Löschen (oder Enter): ")
        if nr.isdigit():
            idx = int(nr) - 1
            if 0 <= idx < len(items):
                key_del = items[idx][0]
                del pool[key_del]
                speichern(daten)
                print("Gelöscht!")
            else:
                print("Ungültig!")
        input("Enter...")

    elif wahl == "5": # EINSTELLUNGEN
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Style.GELB}{Style.FETT}⚙️ EINSTELLUNGEN{Style.ENDE}")
            print(f"1: Abteil wechseln (Aktuell: {abt_name})")
            print(f"2: Neues Abteil erstellen")
            print(f"3: Abteil löschen")
            print(f"4: Typ wechseln (Vokabeln / Sätze)")
            print(f"5: Richtung wechseln ({sett['modus']})")
            print(f"6: Zurück")
            
            sub = input("\nWahl: ")
            if sub == "1":
                abts = list(daten["abteile"].keys())
                for i, n in enumerate(abts, 1): print(f"[{i}] {n}")
                a_wahl = input("Nr wählen: ")
                if a_wahl.isdigit() and 1 <= int(a_wahl) <= len(abts):
                    sett["aktiv_abteil"] = abts[int(a_wahl)-1]
            elif sub == "2":
                neu_abt = input("Name des neuen Abteils: ").strip()
                if neu_abt:
                    daten["abteile"][neu_abt] = {"vokabeln": {}, "saetze": {}}
                    sett["aktiv_abteil"] = neu_abt
            elif sub == "3":
                if len(daten["abteile"]) > 1:
                    del daten["abteile"][abt_name]
                    sett["aktiv_abteil"] = list(daten["abteile"].keys())[0]
                    print("Abteil gelöscht.")
                else:
                    print("Letztes Abteil kann nicht gelöscht werden.")
            elif sub == "4":
                sett["typ"] = "saetze" if sett["typ"] == "vokabeln" else "vokabeln"
            elif sub == "5":
                sett["modus"] = "DE_SP" if sett["modus"] == "SP_DE" else "SP_DE"
            elif sub == "6":
                break
            speichern(daten)

    elif wahl == "6": # SUCHEN
        q = input("\n🔍 Suche (in allen Abteilen): ").lower()
        found = False
        print(Style.LINIE_DUNN)
        for a_n, a_c in daten["abteile"].items():
            # Suche in Vokabeln UND Sätzen
            for t_n in ["vokabeln", "saetze"]:
                for sp, de in a_c[t_n].items():
                    if q in sp.lower() or q in de.lower():
                        print(f"[{a_n}/{t_n}] {Style.GRUEN}{sp}{Style.ENDE} = {de}")
                        found = True
        if not found: print(f"{Style.ROT}Kein Treffer für '{q}'{Style.ENDE}")
        input(f"\n{Style.LINIE_DUNN}\nEnter...")

    elif wahl == "7": # HILFE
        zeige_hilfe()

    elif wahl == "8": # EXIT
        speichern(daten)
        print(f"\n{Style.GRUEN}¡Adiós! Viel Erfolg in Spanien.{Style.ENDE}")
        break

# --- ENDE DER DATEI (VOCABULARY MASTER ULTIMATE) ---
