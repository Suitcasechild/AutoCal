# Pflichtenheft: Tasmota Precision Calibrator (v1.0)

## 1. Zielsetzung und Systemüberblick
Entwicklung einer automatisierten Software zur hochpräzisen Kalibrierung und Genauigkeitsvalidierung von Tasmota-basierten Energiemessgeräten (z.B. Nous A8T). Das System eliminiert Messfehler durch statistische Langzeitmessung und lineare Regression. Es unterstützt zwei Betriebsmodi:
1.  **Professioneller Modus:** Referenzmessung via Fluke 45 (RS232).
2.  **Heimanwender-Modus:** Referenzmessung via einer bereits kalibrierten "Master-Dose" (HTTP).

## 2. Funktionale Anforderungen (Implementierung)

### 2.1 Nutzerprofile & Referenz-Schnittstellen
*   **Modus-Auswahl:** Die GUI ermöglicht dem Nutzer die Auswahl zwischen "Professioneller Anwender" (Fluke 45) und "Heimanwender" (Tasmota-Referenzdose) über Checkboxen.
*   **Referenz-Anbindung (Professioneller Modus - Fluke 45):**
    *   Die Anbindung erfolgt über die `pyserial`-Bibliothek mit konfigurierbaren Parametern (Port, 9600 Baud, 8N1).
    *   Bei Initialisierung wird das Gerät in den Remote-Modus (`*REM`) versetzt und konfiguriert: `FUNC1 VAC`, `FUNC2 AAC`, `RATE MEDIUM`. Ein fester Messbereich (`RANGE 4` für 300V) wird gesetzt, um "Autorange" zu vermeiden.
    *   Die Verbindung wird durch eine `*IDN?`-Abfrage verifiziert, um sicherzustellen, dass das Gerät antwortet.
*   **Referenz-Anbindung (Heimanwender-Modus - Tasmota-Referenzdose):**
    *   Die IP-Adresse der Referenzdose wird in der GUI konfiguriert.
    *   Messwerte (U,I,P) werden über die `httpx`-Bibliothek von der Tasmota HTTP-API (Status 8) abgefragt.
*   **Prüfling (Ziel-Dose - Tasmota-Konfiguration):**
    *   Vor jeder Messung sendet die Software einen `Backlog`-Befehl, um sicherzustellen, dass die Tasmota-Einstellungen des Prüflings korrekt sind: `VoltRes 2`, `WattRes 2`, `AmpRes 3`, `SetOption21 1`.
    *   Messwerte und bestehende Kalibrierfaktoren werden ebenfalls über die HTTP-API abgefragt.

### 2.2 Datenerfassung & Synchronisation
*   **Polling-Zyklus:** Ein `QThread` (`MeasurementWorker`) sorgt für eine asynchrone, die GUI nicht blockierende Abfrage beider Geräte in einem konfigurierbaren Intervall (Standard 2s).
*   **Dual-Value Query (Fluke):** Die gleichzeitige Abfrage von Spannung und Strom vom Fluke 45 wird durch den `VAL?`-Befehl realisiert, der beide Werte in einer Antwort liefert.
*   **Referenz-Leistungsberechnung:** Bei Verwendung des Fluke 45 wird die Referenzleistung (Wirkleistung) unter der Annahme einer rein ohmschen Last (cosφ=1) aus `Pref = Ufluke × Ifluke` berechnet.
*   **Zeitstempel-Abgleich:** Um Zeitversatz zwischen der schnellen seriellen Abfrage und der langsameren HTTP-Abfrage zu minimieren, werden die Messwerte gepuffert und als Paare verarbeitet.

### 2.3 Messablauf (Geführter Prozess)
*   **Messdaten-Verwaltung:** Vor dem Start prüft die Software, ob im gerätespezifischen Verzeichnis (benannt nach der MAC-Adresse des Prüflings) bereits Messdaten (`.csv`) und ein Report (`.txt`) existieren. Der Nutzer kann wählen:
    1.  **Neue Messung:** Alte Daten werden ignoriert.
    2.  **Alte Daten nutzen (Re-Apply):** Es findet keine neue Messung und keine Neuauswertung der `.csv`-Dateien statt. Stattdessen wird der bestehende Report (`..._Protokoll.txt`) nach den finalen Kalibriervorschlägen durchsucht.
        *   Dem Nutzer wird der Inhalt des alten Reports angezeigt.
        *   Bei Auswahl von "KALIBRIEREN" werden die aus dem alten Report extrahierten Werte (inkl. der Auswahlmöglichkeit für `PowerCal`) verwendet.
        *   Nach der Übertragung wird ein neuer, verkürzter "Re-Apply"-Report erstellt, der auf den ursprünglichen Report verweist und die "As Found"/"As Left"-Werte enthält.
*   **Null-Messung (Offset-Korrektur):** Im Heimanwender-Modus wird der Nutzer angeleitet, den Prüfling eingeschaltet, aber die Last ausgeschaltet zu lassen. Das Programm misst den von der Referenzdose erfassten Ruhestrom/-leistung des Prüflings und zieht diesen Wert bei allen nachfolgenden Messungen als Offset ab.
*   **Manueller Last-Trigger:** Der `MeasurementWorker` wartet in einer Schleife, bis er via HTTP-Abfrage (`Status 11`) erkennt, dass der Prüfling eingeschaltet wurde (`"POWER":"ON"`).
*   **Sicherheits-Abschaltung:** Nach jeder Messstufe sendet die Software automatisch einen `Power OFF`-Befehl an den Prüfling.
*   **Multi-Punkt-Messung:** Die Messung erfolgt über eine in der GUI definierte Anzahl von Stufen und eine Anzahl an Messungen pro Stufe. Die Software zeichnet für jede Stufe eine Serie von Messwert-Paaren (Referenz vs. Prüfling) auf und speichert sie in einer separaten `.csv`-Datei.
*   **Stabilitätswächter & Statistische Aufbereitung (Geplant/Optional):** Zukünftige Implementierungen können Mechanismen zur Erkennung von Netzschwankungen (Standardabweichung) und zur Filterung von Ausreißern (Median-Filter) beinhalten.

### 2.4 Mathematische Auswertung & Kalibrierung
*   **Lineare Regression:** Zur Optimierung der Linearität über den gesamten Messbereich wird eine lineare Regression (Kleinstquadratmethode) auf die gesammelten Leistungsmesspunkte angewendet. Die `data_analyzer.py` führt diese Berechnung durch.
*   **Korrekturvorschlag:** Die neuen Kalibrierfaktoren werden unterschiedlich berechnet:
    *   `VCal_neu` und `CCal_neu` werden aus dem **Mittelwert** der prozentualen Abweichungen über alle Stufen ermittelt.
    *   `PCal_neu` wird primär aus der **Steigung (m)** der linearen Regressionsanalyse berechnet (`PCal_neu = PCal_alt * m`).
*   **Validierung & Entscheidung:** Ein `QDialog` (`CalibrationReportDialog`) zeigt den vollständigen Bericht an. 
    *   Der Nutzer kann zwischen "KALIBRIEREN" und "NICHT KALIBRIEREN" wählen.
    *   Bei Auswahl von "KALIBRIEREN" wird der Nutzer in einem zweiten Dialog gefragt, ob für `PowerCal` der **Mittelwert der Stufen** oder der präzisere **Wert aus der Regression** (empfohlen) verwendet werden soll.
    *   Nach erfolgreicher Übertragung bleibt der Dialog geöffnet, aktualisiert seine Textansicht mit den "As Found"/"As Left"-Werten und blendet einen "Schließen"-Button ein.
*   **Automatisierter Flash:** Bei Bestätigung werden die neuen Kalibrierwerte via `Backlog`-Befehl an den Prüfling gesendet (`send_cal.py`).
*   **Re-Check (Optional):** Ein erneuter Genauigkeitscheck kann durch das Starten einer weiteren Messung mit den neuen Kalibrierwerten manuell durchgeführt werden.

## 3. Nicht-funktionale Anforderungen
*   **Präzision:** Berechnungen werden intern mit Fließkommazahlen durchgeführt und erst für die Übertragung an Tasmota auf die erforderlichen Ganzzahlwerte gerundet.
*   **Fehlertoleranz:** `httpx`- und `pyserial`-Aufrufe sind mit Timeouts versehen, um ein Einfrieren der Anwendung bei Verbindungsabbrüchen zu verhindern. Fehler werden im Log-Fenster der GUI ausgegeben.
*   **Temperatur-Drift-Log (Geplant/Optional):** Eine Warnung bei thermischem Drift ist derzeit nicht implementiert, kann aber durch Analyse der Messwert-Stabilität über Zeit hinzugefügt werden.

## 4. Output & Dokumentation
*   **Live-GUI:** Die Benutzeroberfläche, erstellt mit `PySide6`, zeigt Live-Daten in `pyqtgraph`-Diagrammen an, deren X-Achse die Messungsnummer darstellt. Ein Log-Fenster informiert über den Programmablauf.
*   **Automatisierter Report (.txt):** Für jede Kalibrierung wird eine `.txt`-Datei erstellt, die den Prozess dokumentiert. Sie enthält:
    *   Detaillierte Geräteinformationen im Header:
        *   **Prüfling:** Name, Hostname, MAC-Adresse.
        *   **Referenz (Tasmota):** Name, Hostname, MAC-Adresse.
        *   **Referenz (Fluke):** Statischer Text `FLUKE 45 DUAL Mode Calculated Power (P)`.
    *   Messergebnisse und Abweichungen pro Stufe.
    *   Ergebnisse der Regressionsanalyse.
    *   Vergleich der alten und neuen Kalibrierfaktoren.
    *   "As Found" (vorher) und "As Left" (nachher) Werte, die nach der Übertragung an die Dose angehängt werden.
*   **Detailliertes Log (.csv):** Alle Rohdaten-Paare (Zeitstempel, U, I, P beider Geräte) werden für jede Messstufe in einer separaten `.csv`-Datei gespeichert.

## 5. Technische Toolchain (Implementiert)
*   **Sprache:** Python 3.12+
*   **Bibliotheken:**
    *   `pyserial`: Für die serielle Kommunikation mit dem Fluke 45.
    *   `httpx`: Für HTTP-Anfragen an Tasmota-Geräte.
    *   `pandas`: Für die Verarbeitung der Messdaten und den Export in `.csv`-Dateien.
    *   `numpy`: Für numerische Berechnungen (z.B. lineare Regression).
    *   `PySide6`: Für die Erstellung der grafischen Benutzeroberfläche.
    *   `pyqtgraph`: Für die Darstellung von Echtzeit-Graphen in der GUI.
