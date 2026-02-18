# Projektstatus: Tasmota Precision Calibrator v5.2
**Datum:** 18. Februar 2026
**Status:** Funktional / Validiert
**Entwicklungsstufe:** Refactoring abgeschlossen.

---

## 1. Übersicht & Architektur
Das System ist modular aufgebaut, um Hardware-Referenzen (Fluke) und mathematische Auswertungen (Regression) getrennt voneinander zu behandeln.

### Komponenten:
* **`main.py`**: Steuerung des Ablaufs, User-Interface und Sicherheits-Logik.
* **`reference_manager.py`**: Abstraktion der Referenzquellen (RS232 für Fluke 45 / HTTP für Tasmota-Referenz).
* **`data_analyzer.py`**: Statistische Auswertung mittels linearer Regression ($Soll = m \cdot Ist + b$).
* **`calibration_engine.py`**: Mittelwertbildung und Protokollgenerierung.
* **`config.ini`**: Zentrale Verwaltung von IP-Adressen, COM-Ports und Messparametern.

---

## 2. Lastenheft - Erledigte Punkte (Checkliste)

- [x] **Refactoring der Messlogik:** Umstellung von Zeit- auf anzahlbasierte Messung für höhere Reproduzierbarkeit.
- [x] **Multi-Referenz-Support:** Wahlweise Fluke 45 oder Tasmota-Referenzdose.
- [x] **Hardware-Validierung:** Fluke-Verfügbarkeitsprüfung via `*IDN?` (Hardware-Ping).
- [x] **Lineare Regression:** Ermittlung der Steigung ($m$) zur globalen Fehlerkorrektur für die Leistung.
- [x] **Hybride Kalibriermethoden:**
    * VCal/ACal: Mittelwertbildung der Stufen-Vorschläge.
    * PCal: Berechnung aus der Regressions-Steigung.
- [x] **Interaktive Kalibrierung:** Dialog zur Auswahl der `PowerCal`-Methode (Regression vs. Mittelwert) vor dem Senden.
- [x] **Dynamische Visualisierung:** Interaktiver Graph der Regressionsgeraden im Report-Fenster.
- [x] **"Re-Apply" Funktion:** Erneutes Anwenden einer Kalibrierung nur durch Auslesen eines bestehenden Reports, ohne neue Messung.
- [x] **Detailliertes Reporting:** Umfassendes `.txt`-Protokoll mit detailliertem Geräte-Header, allen Werten, Abweichungen und Faktoren.
- [x] **Post-Kalibrierungs-UI:** Report-Fenster bleibt nach dem Kalibrieren zur Verifizierung geöffnet und wird aktualisiert.
- [x] **Sicherheitsabschaltung:** Automatisches `Power OFF` nach jeder Messstufe.

---

## 3. Mathematisches Modell
Das System nutzt einen hybriden Ansatz zur Berechnung der Kalibrierfaktoren:

1.  **`VoltageCal` & `CurrentCal` (Mittelwert-basiert):**
    *   Für jede Messstufe wird ein Korrekturfaktor basierend auf der Abweichung der Mittelwerte berechnet.
    *   Der finale Faktor ist der Durchschnitt aller dieser Stufen-Faktoren.
    
2.  **`PowerCal` (Regressions-basiert):**
    *   Über alle Messpunkte der Leistung wird eine lineare Regression gelegt, um die globale, lineare Abweichung zu ermitteln.
    *   **Formel:** $PowerCal_{neu} = PowerCal_{alt} \cdot m$ (wobei $m$ die Steigung der Regressionsgeraden ist).
    *   **Güteprüfung:** Das Bestimmtheitsmaß ($R^2$) wird überwacht. Ein Wert nahe 1.000 signalisiert eine exzellente Linearität und eine verlässliche Messreihe.

---

## 4. Fahrplan (Roadmap) & Offene Punkte

### Nächste Schritte (geplant):
1.  **Validierungs-Lauf:** Optionaler Check nach der Kalibrierung, um die Genauigkeit zu verifizieren.

### Hardware-Pendenzen:
* Strompfad am Fluke 45 physisch anschließen (derzeit $0.00A$ im Testaufbau).
* Prüfung der Linearität bei extremen Kleinstlasten ($< 2W$).

---

## 5. Anleitung für den Wiedereinstieg
Um an diesem Punkt weiterzumachen:
1.  Stelle sicher, dass `data_analyzer.py` im Projektverzeichnis liegt.
2.  Starte `main.py`.
3.  Die Ergebnisse liegen nach jedem Durchlauf revisionssicher im Ordner `./Reports/[MAC-ADRESSE]/`.