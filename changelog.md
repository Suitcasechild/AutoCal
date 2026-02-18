# Changelog

## v5.0.0 (2026-02-17)

### ✨ Features
*   **Präzisere Power-Kalibrierung:** Der `PowerCal`-Wert wird nun primär aus der Steigung der linearen Regression berechnet, was die Genauigkeit über den gesamten Messbereich verbessert.
*   **Interaktive Kalibrier-Methode:** Vor dem Senden der Daten an die Tasmota-Dose kann der Benutzer nun wählen, ob der `PowerCal`-Wert aus der Regression (empfohlen) oder aus dem Mittelwert der Stufen verwendet werden soll.
*   **Verbessertes Protokoll:** Das finale `.txt`-Protokoll wurde aktualisiert. Es zeigt nun den empfohlenen `PowerCal`-Wert aus der Regression sowie den alternativen Mittelwert an. Zudem wird protokolliert, welche Werte tatsächlich an die Dose gesendet wurden.

### 📚 Dokumentation
*   `Pflichtenheft.md` wurde aktualisiert, um die neue hybride Berechnungslogik und die interaktive Auswahl zu dokumentieren.
*   `Project_Status.md` wurde auf Version 5.0 aktualisiert und spiegelt die neuen Features als "validiert" wider.

### ♻️ Refactoring
*   Die Funktion `send_cal.apply_calibration` wurde refaktoriert. Sie akzeptiert nun direkt die finalen Kalibrierwerte, anstatt sie selbst zu berechnen. Dies entkoppelt die Sende-Logik von der Berechnungs-Logik.
