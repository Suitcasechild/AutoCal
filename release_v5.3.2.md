# 🚀 Tasmota Precision Calibrator v5.3.2

This version marks a milestone in user guidance and process reliability for the Tasmota Precision Calibrator. It bundles groundbreaking automations and surgical calibration logic.

### 🌟 Top Features of this Version
1.  **Surgical Calibration (Selective Sending):** Target specific factors (`VoltageCal`, `CurrentCal`, `PowerCal`). You decide which values are sent to the device.
2.  **Intelligent Tolerance Analysis:** Evaluation of deviations against configurable limits (abs %). A color scheme (Green/Orange) provides immediate certainty whether calibration is technically necessary.
3.  **Automatic Fluke Scan (Auto-Discovery):** No more manual COM port hunting. The system scans all ports and baud rates (9600-300) to identify your Fluke 45 automatically.
4.  **Integrated Interactive Help:** A professional HTML guide is now built directly into the app, featuring anchor navigation and step-by-step instructions.
5.  **Optimized Credential Management:** Passwords are now kept securely in RAM for the whole session. The login popup is pre-filled with "admin" and auto-focuses the password field.

### 🛠️ Technical & Administrative Improvements
*   **Strict Device Identification:** Prevents connection errors by verifying the device ID ("FLUKE").
*   **Data Integrity:** Automatic exclusion of Min/Max values and filtering of zero-value artifacts.
*   **Central Documentation:** Consolidation of all requirements in the **Pflichtenheft v1.1**.

**Note for Users:** Existing calibration reports remains compatible. The new version synchronizes all internal versioning consistently to v5.3.2.

---

# 🚀 Tasmota Precision Calibrator v5.3.2 (DE)

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
*   **Datenintegrität:** Automatisches Ausschluss von Min/Max-Werten und Filterung von Nullwert-Artefakten.

**Hinweis für Anwender:** Bestehende Kalibrier-Reports bleiben kompatibel. Die neue Version synchronisiert alle internen Versionsangaben konsistent auf v5.3.2.
