# Eventual Issues & Checklist

Diese Liste enthält potenzielle Schwachstellen, Design-Mängel und Verbesserungsvorschläge, die im Rahmen der Code-Analyse identifiziert wurden.

## 1. Robustheit & Fehlerbehandlung
- [x] **Division durch Null / Leere Daten:** In `calibration_engine.py` (Methode `calculate_new_calibration`) werden nun leere oder fehlerhafte CSV-Dateien sicher abgefangen.
- [x] **Gefahr bei kleinen Datensätzen:** Wenn eine Messreihe weniger als 3 gültige Werte hat, erfolgt nun ein Fallback auf den einfachen Mittelwert statt eines Absturzes.
- [ ] **Broad Except Blocks:** Mehrere Stellen nutzen `except Exception:` oder sogar `except:`. Dies erschwert das Debugging, da spezifische Fehler verschluckt werden könnten.
- [x] **Invalid CSV Headers:** In `calibration_engine.py` wird nun vor der Verarbeitung geprüft, ob alle benötigten Spalten in der CSV vorhanden sind.

## 2. Netzwerk & API
- [x] **Fehlende Authentifizierung im ConfigManager:** `ConfigManager.get_target_mac` unterstützt nun Authentifizierungsdaten beim Abrufen der MAC-Adresse.
- [ ] **URL-Encoding in `send_cal.py`:** Der `Backlog`-Befehl wird manuell mit `%20` (Leerzeichen) zusammengebaut. Sicherer wäre die Nutzung des `params`-Arguments von `httpx`.
- [ ] **Timeout-Management:** Die Timeouts sind fest auf 2-5 Sekunden eingestellt. Eine Konfigurationsmöglichkeit in der `config.ini` wäre sinnvoll.

## 3. Code-Qualität & Wartbarkeit
- [x] **Redundante Logik:** Die Ermittlung der MAC-Adresse und Verzeichniserstellung ist nun zentral im `ConfigManager` gebündelt.
- [x] **Inkonsistente Key-Nutzung (Credentials):** Der `CredentialsManager` nutzt nun die einheitliche Bezeichnung `identifier` für IPs und Hostnamen.
- [x] **Hartkodierte Pfade:** Die Datei `config.ini` wird nun über einen zentralen, absolut aufgelösten Pfad (`self.config_path`) im `ConfigManager` verwaltet.

## 4. GUI & UX
- [ ] **Fehlende Fortschrittsanzeige:** Bei langen Messreihen (viele Stufen/Messungen) gibt es keine visuelle Fortschrittsanzeige (z. B. ProgressBar).
- [ ] **Blockierender Main-Thread:** Methoden wie `fetch_tasmota_info` werden teils direkt im Main-Thread aufgerufen, was die GUI kurzzeitig einfrieren lassen kann.
- [ ] **Fenster-Skalierung:** Das Hauptfenster lädt ein statisches UI-File. Bei unterschiedlichen Auflösungen könnten Elemente unschön dargestellt werden.

## 5. Sicherheit
- [ ] **In-Memory Credentials:** Die Zugangsdaten liegen im Klartext im Arbeitsspeicher (`CredentialsManager`).
- [ ] **Kein HTTPS:** Die Kommunikation mit Tasmota erfolgt über unverschlüsseltes HTTP. Passwörter werden im Klartext (Basic Auth) übertragen.
