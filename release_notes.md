# 🚀 Tasmota Precision Calibrator - Release Notes

In diesem Dokument finden Sie eine Übersicht der wichtigsten Änderungen und Neuerungen pro Version.

---

## [v5.3.2] - 2026-02-21

Diese Version markiert einen Meilenstein in der Benutzerführung und Prozesssicherheit des Tasmota Precision Calibrators. Sie bündelt bahnbrechende Automatisierungen und eine chirurgisch präzise Kalibrierungs-Logik.

### 🌟 Top-Features dieser Version
1.  **Chirurgische Kalibrierung (Selektives Senden):** Gezielte Auswahl einzelner Faktoren (`VoltageCal`, `CurrentCal`, `PowerCal`). Sie entscheiden, welche Werte an die Dose gesendet werden.
2.  **Intelligente Toleranz-Analyse:** Bewertung der Abweichungen gegen konfigurierbare Limits (abs %). Farbschema (Grün/Orange) zur Empfehlung der Kalibrierung.
3.  **Automatischer Fluke-Scan (Auto-Discovery):** Systematischer Scan aller COM-Ports und Baudraten (9600-300) zur automatischen Identifizierung des Fluke 45.
4.  **Integrierte Interaktive Hilfe:** Professionelles HTML-Handbuch direkt in der Software eingebettet – inklusive Dark Mode und Navigation.
5.  **Optimiertes Credential-Management:** Sitzungsbasierte Speicherung im RAM und UI-Optimierung (admin vorbefüllt, Auto-Fokus).

### 🛠️ Technische Verbesserungen
*   **Strenge Geräte-Identifikation:** Verhindert Verbindungsfehler durch Prüfung der Geräte-ID ("FLUKE").
*   **Datenintegrität:** Automatischer Ausschluss von Min/Max-Werten und Filterung von Nullwert-Artefakten.
*   **Zentrale Dokumentation:** Zusammenführung aller Anforderungen im Pflichtenheft v1.1.

---

## [v5.3.0] - 2026-02-20

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
