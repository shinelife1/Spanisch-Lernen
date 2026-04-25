import customtkinter as ctk
import json
import os
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo

# =============================================================================
# 1. KONFIGURATION & DESIGN
# =============================================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DATA_FILE = "vokabel_ultimate_data.json"

class VokabelApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenster-Konfiguration
        self.title("🇪🇸 Vocabulary Master Ultimate GUI - Spain 2026")
        self.geometry("900x750")
        
        # Daten-Initialisierung
        self.daten = self.laden()
        
        # Quiz-Variablen
        self.quiz_pool = []
        self.quiz_index = 0
        self.runde_korrekt = 0
        self.limit = 0

        # Haupt-Frame (Die Bühne der App)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=30, pady=30)

        # Start mit dem Hauptmenü
        self.zeige_hauptmenue()

    # =============================================================================
    # 2. DATEN-LOGIK (LADEN / SPEICHERN)
    # =============================================================================

    def laden(self):
        """ Lädt die JSON-Datenbank mit Migrationslogik. """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    # Struktur-Check (wie im Terminal-Code)
                    if "abteile" not in d:
                        alte_v = d.get("vokabeln", {})
                        alte_s = d.get("saetze", {})
                        d["abteile"] = {"Allgemein": {"vokabeln": alte_v, "saetze": alte_s}}
                    if "settings" not in d:
                        d["settings"] = {"modus": "SP_DE", "typ": "vokabeln", "aktiv_abteil": "Allgemein"}
                    if "stats" not in d:
                        d["stats"] = {"punkte": 0, "korrekt": 0, "falsch": 0}
                    return d
            except Exception as e:
                print(f"Ladefehler: {e}")
        
        # Standard-Daten falls Datei fehlt
        return {
            "abteile": {"Allgemein": {"vokabeln": {"Hola": "Hallo"}, "saetze": {"Como estas?": "Wie geht es dir?"}}},
            "stats": {"punkte": 0, "korrekt": 0, "falsch": 0},
            "settings": {"modus": "SP_DE", "typ": "vokabeln", "aktiv_abteil": "Allgemein"}
        }

    def speichern(self):
        """ Sichert den aktuellen Zustand. """
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.daten, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Speicherfehler: {e}")

    def clear_screen(self):
        """ Löscht alle Widgets im Container für den Ansichts-Wechsel. """
        for widget in self.container.winfo_children():
            widget.destroy()

    # =============================================================================
    # 3. ANSICHTEN (UI-LOGIK)
    # =============================================================================

    def zeige_hauptmenue(self):
        self.clear_screen()
        self.unbind("<Return>") # Enter-Taste vom Quiz lösen
        
        # Daten-Referenzen
        s = self.daten["stats"]
        sett = self.daten["settings"]
        punkte = s["punkte"]
        rang = self.get_rang_name(punkte)
        zeit = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%H:%M:%S")

        # --- Dashboard Frame ---
        dash = ctk.CTkFrame(self.container, corner_radius=15, border_width=2, border_color="#3a7ebf")
        dash.pack(fill="x", pady=(0, 20), padx=10)

        title = ctk.CTkLabel(dash, text="VOCABULARY MASTER ULTIMATE", font=("Arial", 28, "bold"), text_color="#3a7ebf")
        title.pack(pady=(15, 5))

        info_bar = ctk.CTkLabel(dash, text=f"🕒 Berlin: {zeit}  |  📂 Abteil: {sett['aktiv_abteil'].upper()}", font=("Arial", 13, "italic"))
        info_bar.pack(pady=5)

        # --- Stats Sektion ---
        stats_frame = ctk.CTkFrame(dash, fg_color="transparent")
        stats_frame.pack(pady=10)
        
        ctk.CTkLabel(stats_frame, text=f"👤 Rang: {rang}", font=("Arial", 16, "bold"), text_color="#e6b800").grid(row=0, column=0, padx=20)
        ctk.CTkLabel(stats_frame, text=f"🏆 Punkte: {punkte}", font=("Arial", 16, "bold"), text_color="#2fa572").grid(row=0, column=1, padx=20)
        ctk.CTkLabel(stats_frame, text=f"✅ {s['korrekt']} | ❌ {s['falsch']}", font=("Arial", 16)).grid(row=0, column=2, padx=20)

        # --- Menü Buttons ---
        btn_container = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_container.pack(expand=True)

        options = [
            ("🚀 Marathon-Quiz starten", self.setup_quiz, "#3a7ebf"),
            ("📖 Freies Üben (Lernen)", self.start_ueben, "#3a7ebf"),
            ("➕ Wort/Satz hinzufügen", self.zeige_hinzufuegen, "#3a7ebf"),
            ("📁 Liste verwalten / Löschen", self.zeige_verwaltung, "#3a7ebf"),
            ("🔍 Suchen (Wörterbuch)", self.zeige_suche, "#2fa572"),
            ("⚙️ Einstellungen (Modus/Typ)", self.zeige_einstellungen, "#e6b800"),
            ("❌ Beenden & Speichern", self.safe_exit, "#721c24")
        ]

        for text, cmd, color in options:
            btn = ctk.CTkButton(btn_container, text=text, command=cmd, font=("Arial", 15, "bold"), 
                                height=45, width=400, fg_color=color, hover_color="#2b2b2b")
            btn.pack(pady=8)

    def get_rang_name(self, p):
        if p < 100: return "Principiante"
        elif p < 300: return "Turista"
        elif p < 600: return "Residente"
        elif p < 1000: return "Local"
        else: return "Hidalgo"

    # =============================================================================
    # 4. QUIZ-SEKTION
    # =============================================================================

    def setup_quiz(self):
        self.clear_screen()
        pool = self.daten["abteile"][self.daten["settings"]["aktiv_abteil"]][self.daten["settings"]["typ"]]
        
        if not pool:
            ctk.CTkLabel(self.container, text="Fehler: Das Abteil ist leer!", font=("Arial", 20), text_color="red").pack(pady=50)
            ctk.CTkButton(self.container, text="Zurück", command=self.zeige_hauptmenue).pack()
            return

        lbl = ctk.CTkLabel(self.container, text="Wie viele Fragen möchtest du beantworten?", font=("Arial", 18))
        lbl.pack(pady=30)

        slider = ctk.CTkSlider(self.container, from_=1, to=len(pool), number_of_steps=len(pool), width=400)
        slider.set(min(10, len(pool)))
        slider.pack(pady=10)

        slider_val = ctk.CTkLabel(self.container, text=f"Auswahl: {int(slider.get())}")
        slider_val.pack()
        slider.configure(command=lambda v: slider_val.configure(text=f"Auswahl: {int(v)}"))

        def start():
            self.limit = int(slider.get())
            self.quiz_pool = list(pool.items())
            random.shuffle(self.quiz_pool)
            self.quiz_pool = self.quiz_pool[:self.limit]
            self.quiz_index = 0
            self.runde_korrekt = 0
            self.naechste_frage()

        ctk.CTkButton(self.container, text="QUIZ STARTEN", fg_color="green", command=start, height=50, width=200).pack(pady=40)

    def naechste_frage(self):
        self.clear_screen()
        if self.quiz_index >= len(self.quiz_pool):
            self.quiz_finish()
            return

        # Fortschrittsbalken
        prozent = (self.quiz_index + 1) / self.limit
        bar = ctk.CTkProgressBar(self.container, width=500)
        bar.pack(pady=20)
        bar.set(prozent)
        
        # Daten
        sp, de = self.quiz_pool[self.quiz_index]
        modus = self.daten["settings"]["modus"]
        frage, loesung = (sp, de) if modus == "SP_DE" else (de, sp)

        # UI
        ctk.CTkLabel(self.container, text=f"Frage {self.quiz_index + 1} von {self.limit}", font=("Arial", 14, "italic")).pack()
        ctk.CTkLabel(self.container, text="Was heißt:", font=("Arial", 18)).pack(pady=(20, 5))
        ctk.CTkLabel(self.container, text=frage, font=("Arial", 32, "bold"), text_color="#3a7ebf").pack(pady=20)

        entry = ctk.CTkEntry(self.container, width=350, height=45, font=("Arial", 18), placeholder_text="Deine Antwort...")
        entry.pack(pady=10)
        entry.focus()

        feedback_lbl = ctk.CTkLabel(self.container, text="")
        feedback_lbl.pack(pady=10)

        def validieren(event=None):
            ans = entry.get().strip().lower()
            if ans == loesung.lower():
                feedback_lbl.configure(text="✨ RICHTIG! +10 Punkte", text_color="green")
                self.daten["stats"]["punkte"] += 10
                self.daten["stats"]["korrekt"] += 1
                self.runde_korrekt += 1
            else:
                feedback_lbl.configure(text=f"❌ FALSCH! Lösung: {loesung}", text_color="red")
                self.daten["stats"]["punkte"] = max(0, self.daten["stats"]["punkte"] - 5)
                self.daten["stats"]["falsch"] += 1
            
            self.quiz_index += 1
            self.after(1200, self.naechste_frage)

        self.bind("<Return>", validieren)
        ctk.CTkButton(self.container, text="PRÜFEN", command=validieren, width=150).pack(pady=10)

    def quiz_finish(self):
        self.clear_screen()
        self.unbind("<Return>")
        self.speichern()
        
        ctk.CTkLabel(self.container, text="🏁 QUIZ BEENDET", font=("Arial", 30, "bold"), text_color="#e6b800").pack(pady=30)
        ctk.CTkLabel(self.container, text=f"Ergebnis: {self.runde_korrekt} von {self.limit} richtig!", font=("Arial", 20)).pack(pady=10)
        
        success_rate = (self.runde_korrekt / self.limit) * 100
        ctk.CTkLabel(self.container, text=f"Erfolgsquote: {int(success_rate)}%", font=("Arial", 16, "italic")).pack(pady=10)

        ctk.CTkButton(self.container, text="ZURÜCK ZUM MENÜ", command=self.zeige_hauptmenue, width=250, height=45).pack(pady=40)

    # =============================================================================
    # 5. ÜBUNGS-SEKTION (LERNMODUS)
    # =============================================================================

    def start_ueben(self):
        self.clear_screen()
        pool_dict = self.daten["abteile"][self.daten["settings"]["aktiv_abteil"]][self.daten["settings"]["typ"]]
        if not pool_dict: return

        def lade_uebung():
            self.clear_screen()
            q, l = random.choice(list(pool_dict.items()))
            modus = self.daten["settings"]["modus"]
            f_w, l_w = (q, l) if modus == "SP_DE" else (l, q)

            ctk.CTkLabel(self.container, text="📖 ÜBUNGSMODUS", font=("Arial", 22, "bold"), text_color="#e6b800").pack(pady=20)
            ctk.CTkLabel(self.container, text="Tippe '?' für die Lösung", font=("Arial", 12, "italic")).pack()
            
            q_lbl = ctk.CTkLabel(self.container, text=f_w, font=("Arial", 30, "bold"), text_color="#3a7ebf")
            q_lbl.pack(pady=40)

            ans_ent = ctk.CTkEntry(self.container, width=300, height=40)
            ans_ent.pack(pady=10)
            ans_ent.focus()

            def check_ans(event=None):
                user_val = ans_ent.get().strip().lower()
                if user_val == "?":
                    q_lbl.configure(text=f"Lösung: {l_w}", text_color="orange")
                    ans_ent.delete(0, "end")
                elif user_val == l_w.lower():
                    q_lbl.configure(text="✔ RICHTIG!", text_color="green")
                    self.after(800, lade_uebung)
                else:
                    ans_ent.configure(border_color="red")
            
            self.bind("<Return>", check_ans)
            
            btn_box = ctk.CTkFrame(self.container, fg_color="transparent")
            btn_box.pack(pady=30)
            ctk.CTkButton(btn_box, text="Nächste", command=lade_uebung).grid(row=0, column=0, padx=10)
            ctk.CTkButton(btn_box, text="Menü", command=self.zeige_hauptmenue, fg_color="#721c24").grid(row=0, column=1, padx=10)

        lade_uebung()

    # =============================================================================
    # 6. VERWALTUNG & EINSTELLUNGEN
    # =============================================================================

    def zeige_hinzufuegen(self):
        self.clear_screen()
        abt = self.daten["settings"]["aktiv_abteil"]
        typ = self.daten["settings"]["typ"]

        ctk.CTkLabel(self.container, text=f"➕ NEUER EINTRAG IN: {abt.upper()}", font=("Arial", 20, "bold")).pack(pady=20)
        
        sp_in = ctk.CTkEntry(self.container, placeholder_text="Spanisch...", width=400, height=40)
        sp_in.pack(pady=10)
        de_in = ctk.CTkEntry(self.container, placeholder_text="Deutsch...", width=400, height=40)
        de_in.pack(pady=10)

        def save():
            s, d = sp_in.get().strip(), de_in.get().strip()
            if s and d:
                self.daten["abteile"][abt][typ][s] = d
                self.speichern()
                self.zeige_hauptmenue()

        ctk.CTkButton(self.container, text="SPEICHERN", command=save, fg_color="green").pack(pady=20)
        ctk.CTkButton(self.container, text="ABBRECHEN", command=self.zeige_hauptmenue, fg_color="gray").pack()

    def zeige_verwaltung(self):
        self.clear_screen()
        abt = self.daten["settings"]["aktiv_abteil"]
        typ = self.daten["settings"]["typ"]
        pool = self.daten["abteile"][abt][typ]

        ctk.CTkLabel(self.container, text=f"📁 VERWALTUNG: {abt}", font=("Arial", 20, "bold")).pack(pady=10)
        
        # Scrollbare Liste
        scroll = ctk.CTkScrollableFrame(self.container, width=600, height=400)
        scroll.pack(pady=10)

        for s, d in pool.items():
            row = ctk.CTkFrame(scroll, fg_color="#2b2b2b")
            row.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(row, text=f"{s} = {d}", font=("Arial", 13)).pack(side="left", padx=10, pady=5)
            
            def delete(k=s):
                del self.daten["abteile"][abt][typ][k]
                self.speichern()
                self.zeige_verwaltung()
            
            ctk.CTkButton(row, text="X", width=30, fg_color="#721c24", command=delete).pack(side="right", padx=5)

        ctk.CTkButton(self.container, text="ZURÜCK", command=self.zeige_hauptmenue).pack(pady=20)

    def zeige_einstellungen(self):
        self.clear_screen()
        sett = self.daten["settings"]

        ctk.CTkLabel(self.container, text="⚙️ EINSTELLUNGEN & ABTEILE", font=("Arial", 22, "bold")).pack(pady=20)

        # Richtungs-Toggle
        m_text = f"Modus: {sett['modus']}"
        def toggle_m():
            sett["modus"] = "DE_SP" if sett["modus"] == "SP_DE" else "SP_DE"
            self.zeige_einstellungen()
        ctk.CTkButton(self.container, text=m_text, command=toggle_m, width=300).pack(pady=10)

        # Typ-Toggle
        t_text = f"Lern-Typ: {sett['typ'].capitalize()}"
        def toggle_t():
            sett["typ"] = "saetze" if sett["typ"] == "vokabeln" else "vokabeln"
            self.zeige_einstellungen()
        ctk.CTkButton(self.container, text=t_text, command=toggle_t, width=300).pack(pady=10)

        # Abteil Auswahl
        ctk.CTkLabel(self.container, text="Abteil auswählen:", font=("Arial", 14, "bold")).pack(pady=(20, 5))
        for a_name in self.daten["abteile"].keys():
            color = "#2fa572" if a_name == sett["aktiv_abteil"] else "gray"
            ctk.CTkButton(self.container, text=a_name, fg_color=color, width=300, 
                          command=lambda n=a_name: self.set_active_abt(n)).pack(pady=2)

        ctk.CTkButton(self.container, text="NEUES ABTEIL +", command=self.neues_abteil_dialog).pack(pady=20)
        ctk.CTkButton(self.container, text="HAUPTMENÜ", command=self.zeige_hauptmenue, fg_color="#3a7ebf").pack(pady=10)

    def set_active_abt(self, n):
        self.daten["settings"]["aktiv_abteil"] = n
        self.speichern()
        self.zeige_einstellungen()

    def neues_abteil_dialog(self):
        dialog = ctk.CTkInputDialog(text="Name des neuen Abteils:", title="Abteil erstellen")
        name = dialog.get_input()
        if name:
            self.daten["abteile"][name] = {"vokabeln": {}, "saetze": {}}
            self.daten["settings"]["aktiv_abteil"] = name
            self.speichern()
            self.zeige_einstellungen()

    # =============================================================================
    # 7. SUCHE & EXIT
    # =============================================================================

    def zeige_suche(self):
        self.clear_screen()
        ctk.CTkLabel(self.container, text="🔍 GLOBALE SUCHE", font=("Arial", 22, "bold")).pack(pady=10)
        
        entry = ctk.CTkEntry(self.container, width=400, placeholder_text="Wort oder Satz suchen...")
        entry.pack(pady=10)
        entry.focus()

        res_scroll = ctk.CTkScrollableFrame(self.container, width=600, height=350)
        res_scroll.pack(pady=10)

        def search(event=None):
            for w in res_scroll.winfo_children(): w.destroy()
            q = entry.get().lower()
            if not q: return
            
            for abt_n, abt_c in self.daten["abteile"].items():
                for t in ["vokabeln", "saetze"]:
                    for s, d in abt_c[t].items():
                        if q in s.lower() or q in d.lower():
                            l = ctk.CTkLabel(res_scroll, text=f"[{abt_n}/{t}]  {s} = {d}", font=("Arial", 13))
                            l.pack(anchor="w", padx=10, pady=2)

        self.bind("<Return>", search)
        ctk.CTkButton(self.container, text="SUCHEN", command=search).pack(pady=10)
        ctk.CTkButton(self.container, text="ZURÜCK", command=self.zeige_hauptmenue).pack(pady=10)

    def safe_exit(self):
        self.speichern()
        self.quit()

if __name__ == "__main__":
    app = VokabelApp()
    app.mainloop()
