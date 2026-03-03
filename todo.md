# To-Do: Umbau der Messlogik

**Status:** Erledigt
**Priorität:** Hoch

Dieses Dokument beschreibt die notwendigen Schritte, um die Messsteuerung von einer zeitbasierten Dauer auf eine anzahlbasierte Messung umzustellen.  

----

### 1. GUI anpassen (`gui_main.py` & `main_gui.ui`)

-   [x] **Label ändern:** In `main_gui.ui` das `QLabel` von "Dauer pro Stufe (s)" zu "Messungen pro Stufe" ändern. *(Manuelle Anpassung durch Nutzer erforderlich)*
-   [x] **Widget umbenennen:** Den `objectName` des `QSpinBox` von `spin_duration` zu `spin_measurements` ändern, um die Konsistenz im Code zu wahren. *(Manuelle Anpassung durch Nutzer erforderlich)*   
-   [x] **Achsenbeschriftung anpassen:** In `gui_main.py` (ca. Zeile 529) die Beschriftung der X-Achse von `plot_widget.setLabel('bottom', 'Zeit', units='s')` zu `plot_widget.setLabel('bottom', 'Messung', units='#')` ändern.

### 2. Konfiguration anpassen (`gui_main.py` & `config.ini`)

-   [x] **INI-Wert aktualisieren:** In `gui_main.py` (ca. Zeile 707 und 614) die Logik anpassen, sodass `measurements_per_step` statt `duration_per_step` aus der `config.ini` gelesen und geschrieben wird.
-   [x] **config.ini anpassen:** Den bestehenden Eintrag `duration_per_step` manuell oder per Skript in `measurements_per_step` umbenennen und einen sinnvollen Standardwert (z.B. `15`) setzen.

### 3. Mess-Logik im `MeasurementWorker` umbauen (`gui_main.py`)

-   [x] **Schleifentyp ändern:** Die `while`-Schleife (ca. Zeile 181) durch eine `for`-Schleife ersetzen, die auf der Anzahl der Messungen basiert: `for i in range(self.params['measurements']):`.       
-   [x] **Parameter umbenennen:** Den an den Worker übergebenen Parameter `duration` in `measurements` umbenennen (ca. Zeile 774), um Klarheit zu schaffen.

### 4. Grafen-Daten anpassen (`gui_main.py`)

-   [x] **X-Werte übergeben:** In der Funktion `update_live_data` (ca. Zeile 560) muss die `setData`-Methode explizit mit X- und Y-Werten aufgerufen werden, um die Achse korrekt zu füllen.
    -   `x_values = list(range(len(plot_data)))`
    -   `self.curves[curve_key].setData(x=x_values, y=plot_data)`

----
**Hinweis:** Die Implementierung des Messintervalls (`time.sleep(1)`) bleibt nach Rücksprache unverändert.

---

### Feature: Internationalisierung (i18n) & UI-Sprachsteuerung

**Ziel:** Die Anwendung zweisprachig (DE/EN) machen und dem Benutzer die Kontrolle über die Sprache geben.

---
#### **Vorbereitende Schritte (für beide Varianten identisch):**

*   [x] **1. Konfiguration für Sprachauswahl (`config_manager.py`)**
    *   [x] Sicherstellen, dass beim Erstellen einer neuen `config.ini` in der Sektion `[GENERAL]` der Eintrag `language = auto` hinzugefügt wird.
    *   [x] Die Benutzer-Dokumentation (z.B. `anleitung.md`) um einen Hinweis ergänzen, dass die Sprache manuell auf `de`, `en` oder `auto` gesetzt werden kann.

*   [x] **2. Implementierung des Übersetzungs-Backends (`i18n_manager.py`)**
    *   [x] Eine neue Datei `i18n_manager.py` erstellen, die die `gettext`-Logik kapselt.
    *   [x] Diese Datei soll eine `setup_translation()`-Funktion enthalten, die den `language`-Eintrag auswertet, die korrekte `.mo`-Datei lädt und die Übersetzungsfunktion `_` global verfügbar macht.

*   [x] **3. Vorbereitung der Code-Basis (Texte markieren)**
    *   [x] Die `setup_translation()`-Funktion ganz am Anfang von `gui_main.py` aufrufen.
    *   [x] Alle für den Benutzer sichtbaren Zeichenketten in den `.py`-Dateien mit `_()` markieren.

---
#### **Variante A: Workflow mit Babel (Kommandozeile)**

*   [ ] **4. Erstellen und Verwalten der Übersetzungsdateien**
    *   [ ] Das Paket `Babel` zur `requirements.txt` hinzufügen.
    *   [ ] Eine `babel.cfg`-Datei erstellen, die `pybabel` anweist, alle `.py`-Dateien zu durchsuchen.
    *   [ ] Den `pybabel`-Workflow durchführen, um die Sprachdateien zu generieren:
        1.  `extract`: Erstellt die `messages.pot`-Vorlage.
        2.  `init`: Erstellt die `de/messages.po` und `en/messages.po` Dateien.
        3.  **Manuelle Arbeit:** Die `msgstr`-Einträge in den `.po`-Dateien mit den Übersetzungen füllen.
        4.  `compile`: Erstellt die finalen `.mo`-Dateien.

---
#### **Variante B: Workflow mit Poedit (Grafische Oberfläche)**

*   [ ] **4. Erstellen und Verwalten der Übersetzungsdateien mit Poedit**
    *   [ ] **Neues Projekt in Poedit:** Ein neues Übersetzungsprojekt erstellen.
    *   [ ] **Quellpfade konfigurieren:** Poedit so einrichten, dass es den Projektordner nach `.py`-Dateien durchsucht.
    *   [ ] **Schlüsselwörter festlegen:** Poedit mitteilen, dass es nach dem Schlüsselwort `_` suchen soll.
    *   [ ] **Kataloge erstellen & Übersetzen:** Poedit scannt den Code, erstellt die Kataloge für `de` und `en` und bietet eine grafische Oberfläche zum Übersetzen.
    *   [ ] **Speichern:** Beim Speichern in Poedit werden die `.po`- und die für das Programm notwendigen `.mo`-Dateien automatisch generiert und aktualisiert.

---

### Feature: Dynamisches Credential-Management (Pro Gerät)

*   [x] **1. Zentrale Fehlerbehandlung (Trigger)**
    *   [x] Die Verbindungslogik wurde so angepasst, dass sie bei einem **HTTP `401`-Fehler** (Unauthorized) nicht abbricht, sondern eine neue Funktion zur Anforderung von Zugangsdaten aufruft.
    *   [x] Dies betrifft sowohl den Haupt-Kalibrierprozess als auch den **"Online Check"**-Button.  

*   [x] **2. Implementierung: `CredentialsManager`**
    *   [x] Eine neue Klasse `CredentialsManager` wurde erstellt, um die Zugangsdaten **temporär im Arbeitsspeicher** zu verwalten.
    *   [x] **Methoden:**
        *   `set_credentials(identifier, user, password)`: Speichert Daten für ein spezifisches Gerät.
        *   `get_credentials(identifier)`: Holt die Daten für das Gerät.
        *   `clear_all_credentials()`: Löscht alle zwischengespeicherten Daten (am Ende jedes Prozesses).

*   [x] **3. Implementierung: Wiederverwendbarer Eingabedialog**
    *   [x] Ein wiederverwendbares Dialogfenster `CredentialDialog` wurde implementiert.
    *   [x] Das Fenster zeigt an, für welches Gerät die Eingabe benötigt wird und welcher Versuch es ist.
    *   [x] **Fenster-Inhalt:**
        *   Felder für `Benutzername` und `Passwort`.
        *   Das Passwort-Feld maskiert die Eingabe.
        *   Hinweis auf temporäre Speicherung vorhanden.
        *   Buttons: `OK` und `Abbrechen`.

*   [x] **4. Angepasster Verbindungsablauf (mit 3 Versuchen)**
    1.  [x] Ein Verbindungsversuch zu einem Gerät wird gestartet.
    2.  [x] Bei einem `401`-Fehler wird eine Schleife für die Eingabe gestartet:
        a. [x] Der Eingabedialog wird für das betroffene Gerät angezeigt.
        b. [x] Der Benutzer gibt die Daten ein. Bei `Abbrechen` wird der ganze Prozess beendet.      
        c. [x] Die neuen Daten werden im `CredentialsManager` gespeichert.
        d. [x] Der Verbindungsversuch wird mit den neuen Daten wiederholt.
    3.  [x] Wenn die Verbindung nach insgesamt drei Versuchen weiterhin fehlschlägt, wird der Vorgang mit einer klaren Fehlermeldung abgebrochen.
    4.  [x] Nach einer erfolgreichen Verbindung werden für alle weiteren Anfragen an dieses Gerät die funktionierenden Zugangsdaten aus dem `CredentialsManager` verwendet.

### Verbesserungen der Messwertverarbeitung und GUI

*   [x] **1. Messlogik anpassen (Nullwerte und Wiederholung)**
    *   [x] **Ziel:** Ungültige Messwerte (0) sollen nicht protokolliert, sondern durch zusätzliche gültige Messungen ersetzt werden.
    *   [x] **Betroffene Dateien:** `main.py`, `gui_main.py`, `refhome_offset.py`
    *   [x] **Aufgabe:**
        *   [x] Implementiere eine Prüfung innerhalb der Messschleife: Wenn ein Referenz- oder Prüflingswert `0` ist, wird das Messpaar verworfen.
        *   [x] Protokolliere eine Meldung im Log über die ungültige Messung und die erneute Messung.
        *   [x] Stelle sicher, dass die gewünschte Anzahl an *gültigen* Messungen pro Stufe erreicht wird.
        *   [x] Intern erhöhe die Anzahl der zu nehmenden Messungen um 2, um den Ausschluss von Min/Max-Werten zu kompensieren.
        *   [x] Wende diese Logik auf normale Kalibrierung und Offset-Prüfung an.

*   [x] **2. Plot-Darstellung anpassen (X-Achse und Absolutwerte)**
    *   [x] **Ziel:** Plots sollen absolute Messwerte anzeigen und die X-Achse soll bei 1 beginnen.  
    *   [x] **Betroffene Datei:** `gui_main.py`
    *   [x] **Aufgabe:**
        *   [x] Passe die X-Achsen-Generierung in der Live-Plot-Aktualisierung an, sodass sie bei `1` beginnt (`range(1, len(plot_data) + 1)`).
        *   [x] Bestätige, dass die Plots stets die absoluten, validen Messwerte anzeigen.

*   [x] **3. Mittelwertberechnung anpassen (Min/Max-Ausschluss)**
    *   [x] **Ziel:** Mittelwerte sollen robuster gegen Ausreißer sein.
    *   [x] **Betroffene Datei:** `calibration_engine.py`
    *   [x] **Aufgabe:**
        *   [x] Ändere die Mittelwertberechnung so, dass der niedrigste und der höchste Wert einer Messreihe vor der Berechnung ausgeschlossen werden.
        *   [x] Dies gilt für alle Mittelwerte (Volt, Ampere, Watt) in allen Berechnungen der Anwendung.

*   [x] **4. CSV-Export auf 3 Nachkommastellen runden**
    *   [x] **Ziel:** Einheitliche und präzise Darstellung der Messwerte in den CSV-Dateien.
    *   [x] **Betroffene Dateien:** `main.py`, `gui_main.py`
    *   [x] **Aufgabe:**
        *   [x] Stelle sicher, dass alle Messwerte (Ref_Volt, Target_Volt, Ref_Amp, Target_Amp, Ref_Watt, Target_Watt) vor dem Speichern in eine CSV-Datei auf maximal 3 Nachkommastellen gerundet werden.

### Feature: Anzeige der DUT-Messwerte in Labels

*   [x] **Ziel:** Live-Anzeige von Spannung, Strom, Leistung des Prüflings in dedizierten Labels in der GUI.
*   [x] **Betroffene Datei:** `gui_main.py`
*   [x] **Aufgabe:**
    *   [x] Erweitere die `update_live_data`-Methode, um die Labels `lbl_v_dut`, `lbl_a_dut` und `lbl_w_dut` with den entsprechenden Werten des Prüflings zu aktualisieren.
    *   [x] Wende die vorgegebenen Nachkommastellen an: Spannung 2, Strom 3, Leistung 2.
    *   [x] Sorge dafür, dass die Labels "----" anzeigen, wenn keine Messung aktiv ist oder die DUT ausgeschaltet ist.
    *   [x] Erweitere die `reset_lcd_displays`-Methode, um auch diese neuen Labels zurückzusetzen.   

---

### UI-Stabilität (Locking)

- [x] **Eingabesperre während der Messung:** Implementierung einer Funktion zum Sperren von `frame_2` (Referenzwahl), `frame_3` (IP-Eingabe) und `frame_4` (Messparameter) während eines aktiven Kalibrierlaufs.
    - [x] Erstellen einer Methode `set_ui_locked(self, locked: bool)` in `MainWindow`.
    - [x] Aufruf von `set_ui_locked(True)` beim Start der Messung.
    - [x] Aufruf von `set_ui_locked(False)` am Ende oder beim Abbruch der Messung.

---

### Feature: Anzeige der Tasmota-Referenz-Informationen (frame_tas_ref)

- [x] **Sichtbarkeitssteuerung (Visibility):**
    - [x] Verbindung von `check_ref_home.toggled` mit `frame_tas_ref.setVisible` in `setup_ui_logic`.
    - [x] Initialer Aufruf von `frame_tas_ref.setVisible(check_ref_home.isChecked())` in `MainWindow.__init__`.
- [x] **Erweiterung Geräte-Info (`fetch_tasmota_info`):**
    - [x] Implementierung der Logik für `is_dut=False`, um `lbl_name_ref`, `lbl_host_ref`, `lbl_mac_ref` und `lbl_version_ref` zu befüllen.
- [x] **Erweiterung Live-Anzeige (`update_live_data`):**
    - [x] Abbildung der Referenz-Messwerte auf `lbl_v_ref`, `lbl_a_ref` und `lbl_w_ref`.
    - [x] Anwendung der Formatierung (Spannung 2, Strom 3, Leistung 2 Nachkommastellen).
    - [x] Integration der "----" Anzeige bei Inaktivität oder `dut_off`.
- [x] **Erweiterung Reset-Logik (`reset_lcd_displays`):**
    - [x] Hinzufügen der neuen Referenz-Labels (`lbl_v_ref`, `lbl_a_ref`, `lbl_w_ref` sowie Info-Labels) zum Reset-Vorgang.

---

### System-Robustheit

- [x] **Automatische Konfigurations-Erstellung:** Falls die `config.ini` fehlt, wird sie automatisch mit Standardwerten (COM1, 1 Stufe, 15 Messungen) erstellt.
- [x] **Datenschutz (DUT IP):** Die IP-Adresse des Prüflings wird aus Sicherheitsgründen **nicht** mehr dauerhaft in der `config.ini` gespeichert.

---

### Feature: Fluke 45 Auto-Scan (Auto-Discovery)

- [x] **Scan-Logik ausgelagert (`fluke_scan.py`):**
    - [x] Implementierung der systematischen Suche über alle verfügbaren COM-Ports.
    - [x] Abfrage der Baudraten in der Reihenfolge: 9600, 4800, 2400, 1200, 600, 300.
    - [x] **Priorisierung:** Aktuelle Konfiguration wird zuerst geprüft.
    - [x] **Robustheit:** Wartezeit auf 1,5s erhöht (für langsame Baudraten) und Puffer-Reset vor jeder Abfrage.
- [x] **UI-Integration (`setup_fluke.ui` & `gui_main.py`):**
    - [x] Button `btn_search_fluke` mit Hintergrund-Worker (`FlukeScanWorker`) verbunden.
    - [x] Fortschrittsbalken (`progress_scan`) implementiert und mit dem Scan-Status verknüpft.      
    - [x] Automatische Übernahme der gefundenen Werte in die Eingabefelder bei Erfolg.
    - [x] Benutzer-Feedback via `QMessageBox` (Erfolg/Fehlgeschlagen).

    ---

    ### Feature: Optimierung des Credential-Managements (Session-Persistence)

    - [x] **Sitzungsbasierte Speicherung:**
        - [x] Entfernen der automatischen Löschbefehle (`clear_all_credentials`) am Ende von Messvorgängen oder beim Start neuer Kalibrierungen.
        - [x] Ziel: Einmal eingegebene Zugangsdaten (z.B. beim "Online Check") bleiben für die gesamte Dauer der Programmausführung erhalten.
    - [x] **Verbesserung des Eingabedialogs (`CredentialDialog`):**
        - [x] Vorbefüllung des Benutzernamens mit dem Standardwert `"admin"`.
        - [x] Automatischer Fokus auf das Passwort-Feld beim Öffnen des Dialogs für schnelleren Arbeitsfluss.
        - [x] Hinweistext auf Deutsch angepasst (Sitzungsspeicherung im RAM).
    - [x] **Prozess-Integration:**
        - [x] Sicherstellen, dass der Haupt-Kalibrierprozess die bereits im Arbeitsspeicher vorhandenen Daten des Prüflings und der Referenzdose nahtlos übernimmt, ohne erneut nachzufragen.

---

### Feature: Vereinfachte HOME-Kalibrierung (Tasmota-Referenz)

- [x] **Einschränkung der Messstufen:**
    - [x] Implementierung einer Logik in `gui_main.py`, die bei Auswahl von "Tasmota" (HOME-Modus) die Anzahl der Messstufen fest auf **1** setzt.
    - [x] Das Eingabefeld `spin_steps` muss im HOME-Modus deaktiviert (ausgegraut) werden.
    - [x] Bei Abwahl des HOME-Modus wird das Feld wieder freigegeben und der vorherige Wert (aus der Konfiguration) wiederhergestellt.
- [x] **Anpassung des Ergebnis-Dialogs (`CalibrationReportDialog`):**
    - [x] Übergabe des aktuellen Kalibrierungsmodus ("PRO" oder "HOME") an den Dialog.
    - [x] Im HOME-Modus wird der Button `📊 REGRESSIONS-GRAPH` ausgeblendet, da er bei nur einer Messstufe nicht relevant ist.
    - [x] Ausblenden der Checkbox `PowerCal (Regression)` im HOME-Modus, um Verwirrung zu vermeiden.

---

### Feature: UI-Modus Umschaltung (Home/Pro)

**Ziel:** Dem Benutzer ermöglichen, die Sichtbarkeit von UI-Elementen basierend auf dem Kalibrierungs-Modus (Home-only vs. Pro/Home) umzuschalten.

#### 1. Qt Designer (`main_gui.ui`) Anpassungen (MANUELL DURCH DEN BENUTZER)
*   [x] **Öffne `main_gui.ui` im Qt Designer.**
*   [x] **Menü "Hilfe" (`menuHelp`) anpassen:**
    *   Füge ein neues **Untermenü** hinzu (z.B. "UI-Modus").
    *   Innerhalb dieses Untermenüs füge **zwei Aktionen** (`QAction`) hinzu:
        *   **Aktion 1:** `objectName: action_ui_mode_home_only`, `text: Home-Modus erzwingen`, `checkable: true`
        *   **Aktion 2:** `objectName: action_ui_mode_pro_home`, `text: Pro/Home Modus (Standard)`, `checkable: true`
        *   **Wichtig:** Gruppiere diese beiden Aktionen als `Exclusive` (`actionGroup`), sodass immer nur eine davon ausgewählt sein kann.
*   [x] **Speichere die `main_gui.ui` Datei.**

#### 2. `config_manager.py` Anpassungen (DURCH DEN ASSISTENTEN)
*   [x] Füge dem `[GENERAL]`-Abschnitt in der Default-Konfiguration den Eintrag `ui_mode = home_only` hinzu.

#### 3. `gui_main.py` Logik-Anpassungen (DURCH DEN ASSISTENTEN)
*   [x] **Initialisierung:** Lade den `ui_mode` aus der Konfiguration.
*   [x] **Neue Methode `_apply_ui_mode_settings(self)`:**
    *   Lese den aktuellen `ui_mode` aus `self.cm.config`.
    *   Basierend auf dem `ui_mode`:
        *   Setze die Sichtbarkeit von `self.ui.check_ref_pro` (Checkbox für Fluke).
        *   Setze die Sichtbarkeit von `self.ui.spin_steps` (Spinner für Anzahl der Stufen).
        *   Setze den `checked`-Status von `self.ui.check_ref_manual` (Checkbox für Manuelle Kalibrierung).
*   [x] **Aufruf der Methode:** Rufe `_apply_ui_mode_settings()` nach dem Laden der Konfiguration und Initialisierung der UI auf.
*   [x] **Menü-Verbindungen:** Verbinde `action_ui_mode_home_only` und `action_ui_mode_pro_home` mit entsprechenden Slots, die:
    *   Den `ui_mode` in `config.ini` aktualisieren.
    *   Die Konfiguration dauerhaft speichern.
    *   Anschließend `_apply_ui_mode_settings()` aufrufen, um die UI-Änderungen sofort anzuwenden.
*   [x] **Texte markieren:** Markiere alle neuen sichtbaren Texte mit `_()` für die Übersetzung.

---

### Feature: Dynamische Power-Kalibrierung (Tasmota Rules) - ERLEDIGT

- [x] **1. Menü-Integration & Sichtbarkeit (`gui_main.py`)**
    - [x] Neuen Menüpunkt hinzufügen: `Tools` -> `Dynamische Power-Kalibrierung`.
    - [x] Sichtbarkeits-Logik: Menüpunkt nur im Pro-Modus (`pro_home`) sichtbar.

- [x] **2. Neues Fenster: `DynamicCalDialog` (`dynamic_cal.ui`)**
    - [x] Eingabefeld für IP-Adresse und Online-Check.
    - [x] Anzeige-Bereich für Geräte-Info (Name, MAC, Version).
    - [x] **Sicherheit:** Status-Anzeige von `SaveData` und `Rule1`.
    - [x] **Robustheit:** Warn-Popup bei belegter `Rule1` mit Kopier-Funktion.
    - [x] Tabelle: Anzeige der Bereiche (Hysterese eingerechnet) und PowerCal-Werte.
    - [x] Eingabefeld: Hysterese (Standardwert: `0.15A`).
    - [x] Textbereich: Live-Vorschau des generierten `Rule1`-Befehls inkl. Längen-Check.
    - [x] Log-Ausgabe für Echtzeit-Feedback.

- [x] **3. Backend-Logik & Zustands-Management**
    - [x] Abruf von MAC, `SaveData` und Inhalt von `Rule1` (robuster Parser für `Rules`/`Text`).
    - [x] Suche nach passenden Reports im MAC-Ordner.
    - [x] Berechnung der Umschaltpunkte und Hysterese-Schwellen.
    - [x] **Cleanup-Logik:** `SaveData` wird bei Abbruch wiederhergestellt, bleibt bei Erfolg aber auf `0`.

- [x] **4. Übertragung, Dokumentation & Flash-Schutz**
    - [x] Rule via HTTP-Backlog übertragen.
    - [x] **Aktivierung:** Befehl `Rule1 5` (Once Mode) zur Vermeidung von Flattern.
    - [x] **Traceability:** Dokumentation der Rule-Aktivierung in der `Protokoll.txt` des Reports.
    - [x] **Flash-Schutz:** Automatisches Setzen von `SaveData 0` nach Abschluss.

- [ ] **5. i18n & Dokumentation**
    - [ ] Übersetzungs-Keys für alle neuen Texte, Warnungen und Log-Meldungen (DE/EN).
    - [ ] Feature und Flash-Schutz-Thematik in `anleitung.md` / `userguide.md` dokumentieren.
