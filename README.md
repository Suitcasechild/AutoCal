# Tasmota Precision Calibrator

**(Deutsche Beschreibung unten)**

A GUI-based tool for high-precision calibration and validation of Tasmota-based energy monitoring devices (like smart plugs). This application automates the process of measuring, calculating, and applying new calibration values to enhance the accuracy of power, voltage, and current readings.

It supports two main modes for reference measurements:
1.  **Professional Mode:** Uses a Fluke 45 multimeter via RS232 as the high-precision reference.
2.  **Home User Mode:** Uses a previously calibrated Tasmota device as a "master" reference via HTTP.

---

## Key Features

*   **Guided Calibration Process:** The UI walks you through every step, from device setup to applying the final calibration.
*   **Dual Reference Support:** Choose between a professional multimeter (Fluke 45) or a consumer-grade, pre-calibrated Tasmota plug.
*   **Advanced Mathematical Analysis:** Utilizes linear regression (`numpy`) to calculate the most accurate `PowerCal` value across the entire measurement range, enhancing linearity. `VoltageCal` and `CurrentCal` are calculated based on the mean deviation.
*   **Interactive Decision Making:** Before applying any changes, the tool presents a detailed report. You can choose whether to apply the new values and even select between the regression-based `PowerCal` (recommended) or a simpler mean-based value.
*   **Automated Reporting:** For every calibration run, detailed `.csv` files with raw measurement data and a comprehensive `.txt` protocol are generated and stored.
*   **Non-Blocking UI:** Live data is displayed using `pyqtgraph`, and all communication (HTTP and Serial) runs in a background thread (`QThread`) to keep the UI responsive.
*   **Pre-Measurement Checks:** Automatically verifies device settings (`SetOption21`, resolution) and allows re-applying calibration from previous reports without new measurements.

## Technical Stack

*   **Language:** Python 3.12+
*   **GUI:** PySide6
*   **Real-time Graphs:** pyqtgraph
*   **Communication:** `pyserial` (for Fluke 45) & `httpx` (for Tasmota)
*   **Data Handling:** `pandas` & `numpy`

---
---

# Tasmota Precision Calibrator (DE)

Ein GUI-basiertes Werkzeug zur hochpräzisen Kalibrierung und Validierung von Tasmota-basierten Energiemessgeräten (z.B. Smart Plugs). Die Anwendung automatisiert den Prozess des Messens, Berechnens und Anwendens neuer Kalibrierwerte, um die Genauigkeit von Leistungs-, Spannungs- und Strommessungen zu verbessern.

Es unterstützt zwei Hauptmodi für die Referenzmessung:
1.  **Professioneller Modus:** Nutzt ein Fluke 45 Multimeter via RS232 als hochpräzise Referenz.
2.  **Heimanwender-Modus:** Nutzt ein bereits kalibriertes Tasmota-Gerät als "Master-Referenz" via HTTP.

---

## Hauptmerkmale

*   **Geführter Kalibrierprozess:** Die Benutzeroberfläche führt Sie durch jeden Schritt, von der Gerätekonfiguration bis zur Anwendung der finalen Kalibrierung.
*   **Duale Referenz-Unterstützung:** Wählen Sie zwischen einem professionellen Multimeter (Fluke 45) oder einem bereits kalibrierten Tasmota-Stecker.
*   **Fortgeschrittene mathematische Analyse:** Verwendet lineare Regression (`numpy`), um den genauesten `PowerCal`-Wert über den gesamten Messbereich zu berechnen und die Linearität zu verbessern. `VoltageCal` und `CurrentCal` werden auf Basis der mittleren Abweichung berechnet.
*   **Interaktive Entscheidungsfindung:** Vor dem Anwenden von Änderungen zeigt das Tool einen detaillierten Bericht an. Sie können entscheiden, ob Sie die neuen Werte anwenden und sogar zwischen dem regressionsbasierten `PowerCal`-Wert (empfohlen) oder einem einfacheren Mittelwert wählen.
*   **Automatisierte Protokollierung:** Für jeden Kalibrierdurchlauf werden detaillierte `.csv`-Dateien mit Rohmessdaten und ein umfassendes `.txt`-Protokoll erstellt und gespeichert.
*   **Nicht-blockierende GUI:** Live-Daten werden mit `pyqtgraph` angezeigt, und die gesamte Kommunikation (HTTP und Seriell) läuft in einem Hintergrund-Thread (`QThread`), um die Oberfläche reaktionsfähig zu halten.
*   **Prüfung vor der Messung:** Überprüft automatisch Geräteeinstellungen (`SetOption21`, Auflösung) und ermöglicht das erneute Anwenden einer Kalibrierung aus alten Protokollen, ohne eine neue Messung durchführen zu müssen.

## Technischer Überblick

*   **Sprache:** Python 3.12+
*   **GUI:** PySide6
*   **Echtzeit-Graphen:** pyqtgraph
*   **Kommunikation:** `pyserial` (für Fluke 45) & `httpx` (für Tasmota)
*   **Datenverarbeitung:** `pandas` & `numpy`
