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

### Feature: Manuelle Kalibrierung

#### 1. Vorbereitung & Workflow-Integration
*   **Neue Datei:** Der gesamte Ablauf für die manuelle Kalibrierung wird in einer neuen Datei `man_calib_engine.py` implementiert.
*   **Checkbox:** Die Logik für die neue, manuell vom Benutzer erstellte Checkbox `check_ref_manual` wird implementiert, um den manuellen Kalibrier-Workflow aus `man_calib_engine.py` zu starten.
*   **Last-Steuerung:**
    1.  Die bestehende Aufforderung zum Einschalten der Zieldose wird **zu Beginn und vor jeder neuen Laststufe** beibehalten.
    2.  Nach dem Klick auf `Übernehmen` für eine Stufe schaltet die Anwendung die Last automatisch ab.
*   **Prozess-Steuerung:**
    *   Die Anzahl der Stufen wird aus den Haupteinstellungen übernommen.
    *   Die Anzahl der Messungen pro Stufe wird ebenfalls übernommen, aber auf **maximal 4 begrenzt**.
    *   Ein Klick auf `Abbrechen` im Eingabefenster beendet den gesamten Kalibrierungsprozess.

#### 2. Das manuelle Eingabefenster
*   **Erstellung:** Ein neues Dialogfenster wird per Code erstellt, das für jede Laststufe einmal angezeigt wird.
*   **Anzeige:** Das Fenster zeigt klar die aktuelle Stufe an (z.B. "Manuelle Eingabe: Stufe 1 von 3").
*   **Eingabefelder:** Das Fenster enthält Zeilen für bis zu 4 Messungen. Jede Zeile hat folgende Felder:
    *   `Leistung Tasmota (W)` *(Pflichtfeld)*
    *   `Leistung Referenz (W)` *(Pflichtfeld)*
    *   `Spannung Tasmota (V)` *(Optional)*
    *   `Spannung Referenz (V)` *(Optional)*
    *   `Strom Tasmota (A)` *(Optional)*
    *   `Strom Referenz (A)` *(Optional)*
*   **Buttons:** Der `Übernehmen`-Button ist erst aktiv, wenn alle Pflichtfelder für die geforderte Anzahl an Messungen ausgefüllt sind.

#### 3. Datenverarbeitung und Speicherung
*   **CSV-Erstellung:** Nach Bestätigung einer Stufe werden die eingegebenen Werte in eine CSV-Datei geschrieben.
    *   Die "Referenz"-Werte werden zu `Ref_Volt`, `Ref_Amp`, `Ref_Watt`.
    *   Die "Tasmota"-Werte werden zu `Target_Volt`, `Target_Amp`, `Target_Watt`.
*   **Dateiname & Ort:** Die CSV-Dateien werden im `Reports`-Verzeichnis gespeichert und enthalten einen Vermerk im Namen, z.B. `2026..._manuell_Stufe_1.csv`.
*   **Optionale Werte:** Wenn Spannungs- oder Stromwerte fehlen, werden diese in der CSV als 0 (oder leer) gespeichert und bei der Kalibrierungsberechnung für `VoltageCal` und `CurrentCal` ignoriert.

#### 4. Analyse und Protokoll
*   Die bestehenden Analysefunktionen werden zur Berechnung der Kalibrierwerte aus den neuen, manuell erstellten CSVs wiederverwendet.
*   Im finalen `Protokoll.txt` wird ein deutlicher Hinweis ergänzt:
    `HINWEIS: Diese Kalibrierung wurde auf Basis manuell eingegebener Referenzwerte durchgeführt.`
*   Das Protokoll schlägt nur Kalibrierwerte für die Metriken vor, für die vollständige Daten (Tasmota und Referenz) eingegeben wurden.

---

### Feature: Dynamisches Credential-Management (Pro Gerät)

*   **1. Zentrale Fehlerbehandlung (Trigger)**
    *   Die Verbindungslogik wird so angepasst, dass sie bei einem **HTTP `401`-Fehler** (Unauthorized) nicht abbricht, sondern eine neue Funktion zur Anforderung von Zugangsdaten aufruft.
    *   Dies betrifft sowohl den Haupt-Kalibrierprozess als auch den **"Online Check"**-Button.

*   **2. Implementierung: `CredentialsManager`**
    *   Eine neue Klasse (z.B. `CredentialsManager`) wird erstellt, um die Zugangsdaten **temporär im Arbeitsspeicher** zu verwalten.
    *   **Methoden:**
        *   `set_credentials(device_hostname, user, password)`: Speichert Daten für ein spezifisches Gerät.
        *   `get_credentials(device_hostname)`: Holt die Daten für das Gerät.
        *   `clear_all_credentials()`: Löscht alle zwischengespeicherten Daten (muss am Ende jedes Prozesses aufgerufen werden).

*   **3. Implementierung: Wiederverwendbarer Eingabedialog**
    *   Ein wiederverwendbares Dialogfenster wird per Code erstellt.
    *   Das Fenster zeigt an, für welches Gerät die Eingabe benötigt wird und welcher Versuch es ist (z.B. "Zugangsdaten für [Gerätename] - Versuch 1 von 3").
    *   **Fenster-Inhalt:**
        *   Felder für `Benutzername` und `Passwort`.
        *   Das Passwort-Feld **muss** die Eingabe maskieren (z.B. `******`).
        *   Der Hinweis **`Die Zugangsdaten werden nicht dauerhaft gespeichert und nur für diesen Kalibrierprozess verwendet.`** sollte gut sichtbar platziert sein.
        *   Buttons: `OK` und `Abbrechen`.

*   **4. Angepasster Verbindungsablauf (mit 3 Versuchen)**
    1.  Ein Verbindungsversuch zu einem Gerät wird gestartet.
    2.  Bei einem `401`-Fehler wird eine Schleife für die Eingabe gestartet:
        a. Der Eingabedialog wird für das betroffene Gerät angezeigt.
        b. Der Benutzer gibt die Daten ein. Bei `Abbrechen` wird der ganze Prozess beendet.
        c. Die neuen Daten werden im `CredentialsManager` gespeichert.
        d. Der Verbindungsversuch wird mit den neuen Daten wiederholt.
    3.  **Wenn die Verbindung nach insgesamt drei Versuchen weiterhin fehlschlägt**, wird der Vorgang mit einer klaren Fehlermeldung ("Verbindung zu [Gerätename] fehlgeschlagen. Bitte Zugangsdaten prüfen.") abgebrochen.
    4.  Nach einer erfolgreichen Verbindung werden für alle weiteren Anfragen an dieses Gerät die funktionierenden Zugangsdaten aus dem `CredentialsManager` verwendet.

### Verbesserungen der Messwertverarbeitung und GUI

*   **1. Messlogik anpassen (Nullwerte und Wiederholung)**
    *   **Ziel:** Ungültige Messwerte (0) sollen nicht protokolliert, sondern durch zusätzliche gültige Messungen ersetzt werden.
    *   **Betroffene Dateien:** `main.py`, `refhome_offset.py`
    *   **Aufgabe:**
        *   Implementiere eine Prüfung innerhalb der Messschleife: Wenn ein Referenz- oder Prüflingswert `0` ist, wird das Messpaar verworfen.
        *   Protokolliere eine Meldung im Log über die ungültige Messung und die erneute Messung.
        *   Stelle sicher, dass die gewünschte Anzahl an *gültigen* Messungen pro Stufe erreicht wird.
        *   Intern erhöhe die Anzahl der zu nehmenden Messungen um 2, um den Ausschluss von Min/Max-Werten zu kompensieren (siehe Punkt 3).
        *   Wende diese Logik auf normale Kalibrierung und Offset-Prüfung an.

*   **2. Plot-Darstellung anpassen (X-Achse und Absolutwerte)**
    *   **Ziel:** Plots sollen absolute Messwerte anzeigen und die X-Achse soll bei 1 beginnen.
    *   **Betroffene Datei:** `gui_main.py`
    *   **Aufgabe:**
        *   Passe die X-Achsen-Generierung in der Live-Plot-Aktualisierung an, sodass sie bei `1` beginnt (`range(1, len(plot_data) + 1)`).
        *   Bestätige, dass die Plots stets die absoluten, validen Messwerte anzeigen und "0"-Werte, falls vorhanden, nicht sichtbar sind (dies sollte durch Punkt 1 gelöst sein).

*   **3. Mittelwertberechnung anpassen (Min/Max-Ausschluss)**
    *   **Ziel:** Mittelwerte sollen robuster gegen Ausreißer sein.
    *   **Betroffene Datei:** `calibration_engine.py`
    *   **Aufgabe:**
        *   Ändere die Mittelwertberechnung so, dass der niedrigste und der höchste Wert einer Messreihe vor der Berechnung ausgeschlossen werden.
        *   Dies gilt für alle Mittelwerte (Volt, Ampere, Watt) in allen Berechnungen der Anwendung.

*   **4. CSV-Export auf 3 Nachkommastellen runden**
    *   **Ziel:** Einheitliche und präzise Darstellung der Messwerte in den CSV-Dateien.
    *   **Betroffene Dateien:** `main.py`, `gui_main.py` (und ggf. `data_analyzer.py` bei direkten Schreiboperationen)
    *   **Aufgabe:**
        *   Stelle sicher, dass alle Messwerte (Ref_Volt, Target_Volt, Ref_Amp, Target_Amp, Ref_Watt, Target_Watt) vor dem Speichern in eine CSV-Datei auf maximal 3 Nachkommastellen gerundet werden.
-   [x] **GUI anpassen: Achsenbeschriftung:** In `gui_main.py` die Beschriftung der X-Achse von `plot_widget.setLabel('bottom', 'Zeit', units='s')` zu `plot_widget.setLabel('bottom', 'Messung', units='#')` ändern. (Bereits implementiert)

### Feature: Anzeige der DUT-Messwerte in Labels

*   **Ziel:** Live-Anzeige von Spannung, Strom, Leistung des Prüflings in dedizierten Labels in der GUI.
*   **Betroffene Datei:** `gui_main.py`
*   **Aufgabe:**
    *   Erweitere die `update_live_data`-Methode, um die Labels `lbl_v_dut`, `lbl_a_dut` und `lbl_w_dut` mit den entsprechenden Werten des Prüflings zu aktualisieren.
    *   Wende die vorgegebenen Nachkommastellen an: Spannung 2, Strom 3, Leistung 2.
    *   Sorge dafür, dass die Labels "----" anzeigen, wenn keine Messung aktiv ist oder die DUT ausgeschaltet ist (durch Integration in die bestehende Logik für die LCD-Anzeigen).
    *   Erweitere die `reset_lcd_displays`-Methode, um auch diese neuen Labels zurückzusetzen.
