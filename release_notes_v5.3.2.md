# 🚀 Tasmota Precision Calibrator v5.3.2

Diese Version markiert einen Meilenstein in der Benutzerführung und Prozesssicherheit des Tasmota Precision Calibrators. Sie bündelt bahnbrechende Automatisierungen und eine chirurgisch präzise Kalibrierungs-Logik.

### 🌟 Top-Features dieser Version

1.  **Chirurgische Kalibrierung (Selektives Senden):**
    Der neue Ergebnis-Dialog erlaubt die gezielte Auswahl einzelner Faktoren (`VoltageCal`, `CurrentCal`, `PowerCal`). Sie entscheiden, welche Werte an die Dose gesendet werden.
2.  **Intelligente Toleranz-Analyse:**
    Das System bewertet Abweichungen automatisch gegen konfigurierbare Limits (abs %). Ein Farbschema (Grün/Orange) gibt sofortige Sicherheit, ob eine Kalibrierung technisch notwendig ist.
3.  **Automatischer Fluke-Scan (Auto-Discovery):**
    Kein Suchen nach COM-Ports mehr. Das System scannt alle Schnittstellen und Baudraten (9600-300) und identifiziert Ihr Fluke 45 vollautomatisch.
4.  **Integrierte Interaktive Hilfe:**
    Eine professionelle HTML-Bedienungsanleitung im Dark-Theme ist nun direkt in die Software eingebettet – inklusive Navigation per Inhaltsverzeichnis.
5.  **Optimiertes Credential-Management:**
    Zugangsdaten werden nun pro Sitzung sicher im RAM behalten. Der Login-Dialog wurde für maximale Geschwindigkeit optimiert (Standard-User "admin" und Auto-Fokus).

### 🛠️ Technische & Administrative Verbesserungen
*   **Zentrale Dokumentation:** Alle Anforderungen und Roadmaps wurden im konsolidierten **Pflichtenheft v1.1** zusammengeführt.
*   **Config-Erweiterung:** Einführung der Sektion `[TOLERANCE abs%]` für benutzerdefinierte Grenzwerte.
*   **Robuste Kommunikation:** Strenge Identitätsprüfung ("FLUKE"-Check) und optimierte Timeouts für langsame Baudraten.
*   **Datenintegrität:** Automatischer Ausschluss von Min/Max-Werten und Filterung von Nullwert-Artefakten.

**Hinweis für Anwender:** Bestehende Kalibrier-Reports bleiben kompatibel. Die neue Version synchronisiert alle internen Versionsangaben konsistent auf v5.3.2.
