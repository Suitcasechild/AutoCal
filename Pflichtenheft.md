# Pflichtenheft: Tasmota Precision Calibrator (v1.2)

## 1. Zielsetzung und Systemüberblick
Entwicklung einer automatisierten Software zur hochpräzisen Kalibrierung und Genauigkeitsvalidierung von Tasmota-basierten Energiemessgeräten (z.B. Nous A8T). Das System eliminiert Messfehler durch statistische Langzeitmessung und lineare Regression. Es unterstützt zwei Betriebsmodi:
1.  **Professioneller Modus:** Referenzmessung via Fluke 45 (RS232).
2.  **Heimanwender-Modus:** Referenzmessung via einer bereits kalibrierten "Master-Dose" (HTTP).

## 2. Benutzeroberfläche & Menüstruktur
Die Anwendung bietet eine klare Menüführung zur administrativen Steuerung und Information.

### 2.1 Menü: Datei
*   **Log Speichern:** Exportiert den aktuellen Sitzungsverlauf des Log-Fensters in eine `.txt`-Datei.
*   **Report-Ordner öffnen:** Öffnet das Windows-Verzeichnis der Messberichte (MAC-basiert).
*   **Beenden:** Sicheres Schließen der Anwendung.

### 2.2 Menü: Setup
*   **Allgemein:** 
    *   Konfiguration des Report-Speicherpfads.
    *   Definition von **Toleranzgrenzen (abs %)** für Spannung, Strom und Leistung zur automatischen Bewertung der Messgenauigkeit.
*   **Fluke 45:** 
    *   **Auto-Scan ("Fluke finden"):** Automatisierte Suche an allen COM-Ports und Baudraten (9600-300) mit Identitätsprüfung ("FLUKE"-Check).
*   **Tasmota-Referenz:** Konfiguration der IP-Adresse für den Referenzbetrieb via Master-Dose.

### 2.3 Menü: Hilfe
*   **Anleitung:** Öffnet die **integrierte, interaktive HTML-Bedienungsanleitung** mit Inhaltsverzeichnis und detaillierten Anweisungen.
*   **Lizenz & Info:** Anzeige von Version (v5.4.0), Autor und rechtlichen Hinweisen.

## 3. Funktionale Anforderungen (Implementierung)

### 3.1 Referenz-Anbindung & Konfiguration
*   **Fluke 45:** Robuste Anbindung via `pyserial`. Automatisches Setzen in den Dual-Display-Modus (`VAC`/`AAC`) und Fixierung des Messbereichs (`RANGE 4`).
*   **Tasmota-Referenz:** Datenerfassung via HTTP-API (Status 8).
*   **Toleranz-Management:** Speicherung der Limits in der `config.ini` (`[TOLERANCE abs%]`) und Anwendung in der Ergebnis-Analyse.

### 3.2 Datenerfassung & Synchronisation
*   **Fehlertoleranz:** Automatisches Verwerfen von Nullwerten und Wiederholung der Messung bis zur Zielanzahl.
*   **Bereinigung:** Ausschluss von Extremwerten (Min/Max) bei der Mittelwertbildung zur Eliminierung von Ausreißern.
*   **Inrush-Filter:** 7 Sekunden Wartezeit nach Lastzuschaltung zur Stabilisierung.

### 3.3 Messablauf & Workflow
*   **Geführter Prozess:** Automatisches Ausschalten des Prüflings für die Offset-Messung (nur HOME-Modus).
*   **Daten-Reuse:** Möglichkeit, bereits vorhandene CSV-Daten für neue Analysen und Kalibrierungen heranzuziehen.
*   **UI-Stabilität:** Sperrung kritischer Bedienelemente während aktiver Messzyklen.

### 3.4 Mathematische Auswertung & Kalibrierung
*   **Selektive Kalibrierung:** Checkbox-basierte Auswahl der zu übertragenden Faktoren (VoltageCal, CurrentCal, PowerCal).
*   **PowerCal-Methoden:** Wahlmöglichkeit zwischen statistischem Mittelwert (Mean) und linearer Regression (empfohlen).
*   **Visualisierung:** Optionale Anzeige der Regressionsgeraden im Vergleich zum Idealzustand.

### 3.5 Authentifizierung (Passwortschutz)
*   **Sitzungs-Persistence:** Speicherung der Zugangsdaten im Arbeitsspeicher für die Dauer der Programmausführung.
*   **UI-Komfort:** Voreinstellung des Benutzers "admin" und Fokus-Steuerung im Login-Dialog.

## 4. Output & Berichte
*   **Automatisierter Report (.txt):** Umfassendes Protokoll inkl. "As-Found/As-Left" Vergleich.
*   **Detailliertes Log (.csv):** Speicherung aller Rohdatenpaare (auf 3 Stellen gerundet).

## 5. Technische Toolchain
*   **Sprache:** Python 3.12+
*   **Bibliotheken:** PySide6, pyqtgraph, httpx, pandas, numpy, pyserial.
*   **Sicherheit:** Einbettung von Assets (Anleitung) in den Binärcode.

## 6. Entwicklungsstatus & Roadmap

### 6.1 Abgeschlossene Erweiterungen (Historie)
*   [x] **Umstellung Messsteuerung:** Wechsel von zeitbasierter Dauer auf anzahlbasierte Messungen pro Stufe.
*   [x] **Graph-Optimierung:** Umstellung auf absolute Messwerte und Start der X-Achse bei 1.
*   [x] **Statistische Filter:** Implementierung des Min/Max-Ausschlusses bei der Mittelwertbildung.
*   [x] **Dynamisches Credential-Management:** Automatisierte Passwortabfrage bei 401-Fehlern mit Sitzungsspeicherung.
*   [x] **Zusätzliche UI-Labels:** Live-Anzeige der DUT-Werte in dedizierten Labels unabhängig vom Graphen.
*   [x] **Auto-Scan Fluke:** Implementierung der automatischen Port-Suche mit robuster Baudraten-Erkennung.
*   [x] **Selektive Kalibrierung:** Einführung von Checkboxen und Toleranz-Analyse (Grün/Orange) im Report-Fenster.
*   [x] **Konfigurierbare Toleranzen:** Limits für V, A und P über das Setup einstellbar (`[TOLERANCE abs%]`).
*   [x] **Visueller Messfortschritt:** Implementierung eines Fortschrittsbalkens (`progress_status`) in der Haupt-GUI, der den Status der aktuellen Messstufe in Echtzeit anzeigt. Der Balken wird nur während einer aktiven Messung eingeblendet und bleibt ansonsten unsichtbar.
*   [x] **Hochgeschwindigkeits-Kommunikation Fluke:** Umstellung auf eine ereignisgesteuerte Abfrage (`readline`) in Kombination mit einem automatischen Puffer-Reset vor jeder Messung. Dies eliminiert unnötige Wartezeiten, verhindert Fehlmessungen durch Puffer-Überreste und maximiert die zeitliche Synchronität zwischen Referenz und Prüfling.

### 6.2 Offene Punkte & Geplante Features (Roadmap)
*   [ ] **Manuelle Kalibrierung:**
    *   Implementierung eines Workflows zur manuellen Eingabe von Referenzwerten (für Anwender ohne direkte Schnittstelle).
    *   Workflow: Last-Steuerung, manuelle Eingabemaske für bis zu 4 Messungen pro Stufe, Generierung spezieller "manuell"-CSVs.
*   [ ] **Internationalisierung (i18n):**
    *   Vorbereitung der Software für eine automatische oder manuelle Sprachumschaltung (Deutsch/Englisch).
