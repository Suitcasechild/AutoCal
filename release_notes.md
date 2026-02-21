# 🚀 Tasmota Precision Calibrator - Release Notes

This document provides an overview of the most important changes and innovations per version. / In diesem Dokument finden Sie eine Übersicht der wichtigsten Änderungen und Neuerungen pro Version.

---

## [v5.3.3] - 2026-02-21

This update focuses on surgical precision during the calibration process and improved reliability for device preparation.

### 🌟 Top Features of this Version
1.  **Selective Calibration:** Targeted updates for V, A, or W via checkboxes.
2.  **Configurable Tolerance Limits:** Set absolute limits (abs %) in **Setup -> General**.
3.  **Visual Step Progress:** Real-time feedback for the current measurement step.
4.  **Robust Device Preparation:** Commands sent individually with URL encoding.

### 🛠️ Technical Improvements
*   **Deviation Analysis:** Visual indicators (Green/Orange) for recommendations.
*   **Dynamic UI:** Intelligent visibility control for progress indicators.
*   **Backlog Stability:** Enhanced reliability during the initialization phase.

---

## [v5.3.3] - 2026-02-21 (DE)

Dieses Update konzentriert sich auf chirurgische Präzision beim Kalibriervorgang und eine verbesserte Zuverlässigkeit bei der Gerätevorbereitung.

### 🌟 Top-Features dieser Version
1.  **Selektive Kalibrierung:** Gezielte Auswahl von V, A oder W über Checkboxen.
2.  **Konfigurierbare Toleranzgrenzen:** Eigene Limits (abs %) in **Setup -> Allgemein** festlegbar.
3.  **Visueller Messfortschritt:** Echtzeit-Rückmeldung über den Status der aktuellen Stufe.
4.  **Robuste Gerätevorbereitung:** Befehle werden einzeln mit URL-Kodierung gesendet.

### 🛠️ Technische Verbesserungen
*   **Abweichungs-Analyse:** Visuelle Empfehlungen (Grün/Orange) im Ergebnis-Dialog.
*   **Dynamische UI:** Fortschrittsanzeigen werden nur bei Bedarf eingeblendet.
*   **Backlog-Stabilität:** Erhöhte Zuverlässigkeit bei der Initialisierung.

---

## [v5.3.2] - 2026-02-21

This version marks a milestone in user guidance and process reliability for the Tasmota Precision Calibrator. It bundles groundbreaking automations and surgical calibration logic.

### 🌟 Top Features of this Version
1.  **Surgical Calibration (Selective Sending):** Target specific factors (`VoltageCal`, `CurrentCal`, `PowerCal`). You decide which values are sent to the device.
2.  **Intelligent Tolerance Analysis:** Evaluation of deviations against configurable limits (abs %). A color scheme (Green/Orange) provides immediate certainty whether calibration is technically necessary.
3.  **Automatic Fluke Scan (Auto-Discovery):** System scans all ports and baud rates (9600-300) to identify your Fluke 45 automatically.
4.  **Integrated Interactive Help:** Professional HTML guide built directly into the app – including Dark Mode and navigation.
5.  **Optimized Credential Management:** Session-based RAM storage and UI optimization (admin pre-filled, auto-focus).

### 🛠️ Technical Improvements
*   **Strict Device ID:** Prevents connection errors via "FLUKE" ID check.
*   **Data Integrity:** Automatic exclusion of Min/Max values and filtering of zero-value artifacts.
*   **Central Documentation:** Consolidation of all requirements in the **Pflichtenheft v1.1**.

---

## [v5.3.2] - 2026-02-21 (DE)

Diese Version markiert einen Meilenstein in der Benutzerführung und Prozesssicherheit des Tasmota Precision Calibrators. Sie bündelt bahnbrechende Automatisierungen und eine chirurgisch präzise Kalibrierungs-Logik.

### 🌟 Top-Features dieser Version
1.  **Chirurgische Kalibrierung (Selektives Senden):** Gezielte Auswahl einzelner Faktoren (`VoltageCal`, `CurrentCal`, `PowerCal`). Sie entscheiden, welche Werte an die Dose gesendet werden.
2.  **Intelligente Toleranz-Analyse:** Bewertung der Abweichungen gegen konfigurierbare Limits (abs %). Farbschema (Grün/Orange) zur Empfehlung der Kalibrierung.
3.  **Automatischer Fluke-Scan (Auto-Discovery):** Systematischer Scan aller COM-Ports und Baudraten (9600-300) zur automatischen Identifizierung des Fluke 45.
4.  **Integrierte Interaktive Hilfe:** Professionelles HTML-Handbuch direkt in der Software eingebettet – inklusive Dark Mode und Navigation.
5.  **Optimiertes Credential-Management:** Sitzungsbasierte Speicherung im RAM und UI-Optimierung (admin vorbefüllt, Auto-Fokus).

### 🛠️ Technische Verbesserungen
*   **Strenge Geräte-Identifikation:** Verhindert Verbindungsfehler durch Prüfung der Geräte-ID ("FLUKE").
*   **Datenintegrität:** Automatisches Ausschluss von Min/Max-Werten und Filterung von Nullwert-Artefakten.
*   **Zentrale Dokumentation:** Zusammenführung aller Anforderungen im Pflichtenheft v1.1.

---

## [v5.3.0] - 2026-02-20

This release marks a significant milestone in the development of the AutoCal tool. In addition to expanded visualizations, this update focuses on massive stability, data security, and a significantly improved user experience.

### ✨ New Features
*   **📑 Detailed Reference Display:** New dedicated area (`frame_tasref`) showing device information and live values of the Tasmota reference plug – analogous to the DUT.
*   **🚫 UI Input Locking:** Automatic locking of input fields during active measurements to prevent errors.
*   **🔌 Automatic Power-Off on Abort:** Immediate power-off command upon manual measurement cancellation.
*   **📄 Auto-Config Creation:** Automatic creation of a default `config.ini` upon program start.

### 🛠️ Robustness & Code Quality
*   **🧮 Intelligent Mean Calculation:** Validation of CSV headers and fallback mode for small datasets.
*   **📂 Centralized Path Management:** Configuration management via absolute paths.
*   **🐞 Stability:** Fixed memory leaks in graphs and improved type safety.

---

## [v5.3.0] - 2026-02-20 (DE)

Dieses Release markiert einen bedeutenden Meilenstein in der Entwicklung des AutoCal-Tools. Neben erweiterten Visualisierungen liegt der Fokus dieses Updates auf massiver Stabilität, Datensicherheit und einer deutlich verbesserten Benutzerführung.

### ✨ Neue Features
*   **📑 Detaillierte Referenz-Anzeige:** Neuer Bereich (`frame_tasref`) mit Geräte-Informationen und Live-Messwerten der Tasmota-Referenzdose.
*   **🚫 UI-Eingabesperre (Locking):** Automatisches Sperren der Eingabefelder während aktiver Messungen zur Fehlervermeidung.
*   **🔌 Automatisches Ausschalten bei Abbruch:** Sofortiger Ausschaltbefehl bei manuellem Messabbruch.
*   **📄 Auto-Konfigurations-Erstellung:** Automatische Erstellung einer Standard-`config.ini` bei Programmstart.

### 🛠️ Robustheit & Code-Qualität
*   **🧮 Intelligente Mittelwertbildung:** Validierung von CSV-Headern und Fallback-Modus für kleine Datensätze.
*   **📂 Zentralisiertes Pfad-Management:** Verwaltung der Konfiguration via absoluter Pfade.
*   **🐞 Stabilität:** Behebung von Speicherlecks in Graphen und Verbesserung der Typsicherheit.

---
*Generated with 99% AI support via Gemini CLI.* 🚀
