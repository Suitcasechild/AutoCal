# Eventual Issues & Checklist

Diese Liste enthält potenzielle Schwachstellen, Design-Mängel und Verbesserungsvorschläge, die im Rahmen der Code-Analyse identifiziert wurden.

## 1. Robustheit & Fehlerbehandlung
- [ ] **Division durch Null / Leere Daten:** In `calibration_engine.py` (Methode `calculate_new_calibration`) könnten leere oder fehlerhafte CSV-Dateien zu Abstürzen führen (z. B. `iloc[1:-1]` auf leerem DataFrame).
- [ ] **Gefahr bei kleinen Datensätzen:** Wenn eine Messreihe weniger als 3 gültige Werte hat (z. B. durch viele Fehlmessungen), schlägt der Ausschluss von Min/Max via `iloc[1:-1]` fehl.
- [ ] **Broad Except Blocks:** Mehrere Stellen nutzen `except Exception:` oder sogar `except:`. Dies erschwert das Debugging, da spezifische Fehler (wie Netzwerk-Timeouts vs. JSON-Parsing-Fehler) verschluckt werden.
- [ ] **Ungültige CSV-Header:** Falls eine CSV-Datei manuell verändert wird oder beschädigt ist, gibt es keine Validierung der Header vor dem Einlesen in Pandas.

## 2. Netzwerk & API
- [ ] **Fehlende Authentifizierung im ConfigManager:** `ConfigManager.get_target_mac` führt HTTP-Requests ohne Zugangsdaten aus. Bei passwortgeschützten Geräten wird diese Funktion immer fehlschlagen.
- [ ] **URL-Encoding in `send_cal.py`:** Der `Backlog`-Befehl wird manuell mit `%20` (Leerzeichen) zusammengebaut. Sicherer wäre die Nutzung des `params`-Arguments von `httpx`, um Kodierungsfehler bei komplexeren Befehlen zu vermeiden.
- [ ] **Timeout-Management:** Die Timeouts sind fest auf 2-5 Sekunden eingestellt. In instabilen WLAN-Umgebungen (z. B. bei weit entfernten Steckdosen) könnte dies zu häufigen Abbrüchen führen. Eine Konfigurationsmöglichkeit in der `config.ini` wäre sinnvoll.

## 3. Code-Qualität & Wartbarkeit
- [ ] **Redundante Logik:** Die Ermittlung der MAC-Adresse und die Erstellung von Geräteverzeichnissen ist sowohl in `config_manager.py` als auch in `gui_main.py` implementiert. Änderungen müssen an beiden Stellen gepflegt werden.
- [ ] **Inkonsistente Key-Nutzung (Credentials):** Der `CredentialsManager` wird in der GUI mit der IP-Adresse als Schlüssel gefüttert, die internen Methodenbeschreibungen sprechen aber von `device_hostname`. Dies führt zu Verwirrung bei zukünftigen Erweiterungen.
- [ ] **Hartkodierte Pfade:** Die Datei `config.ini` wird an mehreren Stellen direkt im aktuellen Verzeichnis geöffnet (`with open('config.ini', ...)`), anstatt einen zentralen, absolut aufgelösten Pfad zu nutzen. Dies kann Probleme verursachen, wenn das Programm aus einem anderen Verzeichnis gestartet wird.

## 4. GUI & UX
- [ ] **Fehlende Fortschrittsanzeige:** Bei langen Messreihen (viele Stufen/Messungen) gibt es keine visuelle Fortschrittsanzeige (z. B. ProgressBar), sondern nur das fortlaufende Text-Log.
- [ ] **Blockierender Main-Thread:** Methoden wie `fetch_tasmota_info` werden teils direkt im Main-Thread aufgerufen (z. B. beim "Online-Check"). Bei einem Netzwerk-Timeout "friert" die GUI für einige Sekunden ein.
- [ ] **Fenster-Skalierung:** Das Hauptfenster lädt ein statisches UI-File. Bei unterschiedlichen Bildschirmauflösungen oder DPI-Einstellungen könnten Elemente abgeschnitten werden oder unschön aussehen.

## 5. Sicherheit
- [ ] **In-Memory Credentials:** Die Zugangsdaten liegen im Klartext im Arbeitsspeicher (`CredentialsManager`). Dies ist für dieses Tool akzeptabel, sollte aber bei einer Erweiterung (z. B. Fernwartung) überdacht werden.
- [ ] **Kein HTTPS:** Die Kommunikation mit Tasmota erfolgt über unverschlüsseltes HTTP. Passwörter werden im Klartext (Basic Auth) übertragen. Dies ist eine Einschränkung von Tasmota selbst, sollte aber im Hinterkopf behalten werden.
