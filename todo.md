# To-Do: Umbau der Messlogik

**Status:** Geplant
**Priorität:** Hoch

Dieses Dokument beschreibt die notwendigen Schritte, um die Messsteuerung von einer zeitbasierten Dauer auf eine anzahlbasierte Messung umzustellen.

---

### 1. GUI anpassen (`gui_main.py` & `main_gui.ui`)

-   [ ] **Label ändern:** In `main_gui.ui` das `QLabel` von "Dauer pro Stufe (s)" zu "Messungen pro Stufe" ändern.
-   [ ] **Widget umbenennen:** Den `objectName` des `QSpinBox` von `spin_duration` zu `spin_measurements` ändern, um die Konsistenz im Code zu wahren.
-   [ ] **Achsenbeschriftung anpassen:** In `gui_main.py` (ca. Zeile 529) die Beschriftung der X-Achse von `plot_widget.setLabel('bottom', 'Zeit', units='s')` zu `plot_widget.setLabel('bottom', 'Messung', units='#')` ändern.

### 2. Konfiguration anpassen (`gui_main.py` & `config.ini`)

-   [ ] **INI-Wert aktualisieren:** In `gui_main.py` (ca. Zeile 707 und 614) die Logik anpassen, sodass `measurements_per_step` statt `duration_per_step` aus der `config.ini` gelesen und geschrieben wird.
-   [ ] **config.ini anpassen:** Den bestehenden Eintrag `duration_per_step` manuell oder per Skript in `measurements_per_step` umbenennen und einen sinnvollen Standardwert (z.B. `15`) setzen.

### 3. Mess-Logik im `MeasurementWorker` umbauen (`gui_main.py`)

-   [ ] **Schleifentyp ändern:** Die `while`-Schleife (ca. Zeile 181) durch eine `for`-Schleife ersetzen, die auf der Anzahl der Messungen basiert: `for i in range(self.params['measurements']):`.
-   [ ] **Parameter umbenennen:** Den an den Worker übergebenen Parameter `duration` in `measurements` umbenennen (ca. Zeile 774), um Klarheit zu schaffen.

### 4. Grafen-Daten anpassen (`gui_main.py`)

-   [ ] **X-Werte übergeben:** In der Funktion `update_live_data` (ca. Zeile 560) muss die `setData`-Methode explizit mit X- und Y-Werten aufgerufen werden, um die Achse korrekt zu füllen.
    -   `x_values = list(range(len(plot_data)))`
    -   `self.curves[curve_key].setData(x=x_values, y=plot_data)`

---
**Hinweis:** Die Implementierung des Messintervalls (`time.sleep(1)`) bleibt nach Rücksprache unverändert.
