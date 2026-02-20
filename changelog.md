# Changelog

## v5.3.0 (2026-02-20)

### ✨ Features
*   **Automatisches Ausschalten bei Abbruch:** Wenn die Messung manuell über den "Messung abbrechen"-Button beendet wird, versucht das Programm nun automatisch, die Zieldose (Prüfling) auszuschalten, um einen sicheren Zustand zu gewährleisten.
    *   **English:** Automatic Power-Off on Abort: When the measurement is manually ended via the "Cancel Measurement" button, the program now automatically attempts to power off the DUT (device under test) to ensure a safe state.
*   **Verbesserte Robustheit der CalibrationEngine:**
    *   **CSV-Validierung:** Vor der Verarbeitung von Messdaten wird nun geprüft, ob alle erforderlichen Spalten vorhanden sind.
    *   **Handling kleiner Datensätze:** Bei weniger als 3 Messpunkten erfolgt nun ein automatischer Fallback auf den einfachen Mittelwert, um Abstürze beim Ausschluss von Extremwerten zu verhindern.
*   **Zentralisierung & Wartbarkeit:**
    *   **Zentrale Pfadverwaltung:** Die `config.ini` wird nun über einen absoluten Pfad verwaltet, was den Start der App aus beliebigen Verzeichnissen ermöglicht.
    *   **Redundanz-Eliminierung:** Die Logik zur MAC-Ermittlung und Verzeichnisverwaltung wurde im `ConfigManager` zentralisiert.
    *   **Authentifizierungs-Support:** Der automatische Abruf der MAC-Adresse unterstützt nun Zugangsdaten.
*   **Behebung von Stabilitäts- und Performance-Problemen:**
    *   **Speicherleck behoben:** Die Live-Graphen nutzen nun `collections.deque` mit einer Begrenzung auf 1000 Datenpunkte. Dies verhindert, dass der Arbeitsspeicher bei langen Laufzeiten unbegrenzt anwächst.
    *   **Typsicherheit verbessert:** Ein potenzieller Absturz (`TypeError`) bei der Verarbeitung von Messwerten wurde behoben. Werte werden nun erst in Zahlen (`float`) umgewandelt, bevor Vergleiche durchgeführt werden.
    *   **English:** Stability and Performance Bugfixes: Fixed a memory leak in live graphs by using `collections.deque` with a 1000-point limit. Improved type safety by ensuring values are converted to `float` before comparison, preventing potential `TypeError` crashes.
*   **Entkoppelung der Messwertanzeige:** Die Anzeige der Messwerte des Prüflings (DUT) in der GUI ist nun unabhängig vom gewählten Referenzmodus. Zuvor wurden die DUT-Werte nur angezeigt, wenn das Fluke als Referenz gewählt war. Zusätzlich wurde veralteter, auskommentierter Code in der Anzeige-Logik entfernt.
    *   **English:** Decoupling of Measurement Display: The display of DUT measurement values in the GUI is now independent of the selected reference mode. Previously, DUT values were only shown when the Fluke was selected as the reference. Additionally, obsolete commented-out code in the display logic was removed.
*   **Verbesserte Mittelwertberechnung:** Die Berechnung der Mittelwerte für Spannung, Strom und Leistung schließt nun den höchsten und niedrigsten Messwert jeder Reihe aus. Dies erhöht die Robustheit der Kalibrierergebnisse gegenüber Ausreißern.
    *   **English:** Improved Mean Calculation: The calculation of mean values for voltage, current, and power now excludes the highest and lowest measurement from each series. This enhances the robustness of calibration results against outliers.
*   **Verbesserte Messwerterfassung (Nullwert-Behandlung):** Messungen, bei denen Referenz- oder Prüflingswerte `0` ergeben, werden nun als ungültig erkannt und automatisch wiederholt. Dies stellt sicher, dass nur valide Messdaten für die Kalibrierung verwendet werden. Für die Hauptkalibrierung wird die intern benötigte Anzahl an Messungen um 2 erhöht, um den Ausschluss von Minimal- und Maximalwerten bei der Mittelwertbildung zu kompensieren. Auch die Offset-Prüfung berücksichtigt nun ungültige Messwerte.
    *   **English:** Improved Measurement Data Acquisition (Zero-Value Handling): Measurements where reference or DUT values result in `0` are now recognized as invalid and automatically repeated. This ensures that only valid measurement data is used for calibration. For the main calibration, the internally required number of measurements is increased by 2 to compensate for the exclusion of minimum and maximum values during mean calculation. The offset check also now accounts for invalid measurements.
*   **Anpassung der Plot-Achsen:** Die X-Achse der Live-Diagramme beginnt nun bei 1 anstatt bei 0, um die Zählung der Messwerte besser widerzuspiegeln.
    *   **English:** Plot Axis Adjustment: The X-axis of the live charts now starts at 1 instead of 0 to better reflect the count of measurements.
*   **Rundung von CSV-Exportdaten:** Alle Messwerte, die in CSV-Dateien gespeichert werden, werden nun auf maximal 3 Nachkommastellen gerundet, um eine einheitliche und präzise Darstellung zu gewährleisten.
    *   **English:** Rounding of CSV Export Data: All measurement values saved to CSV files are now rounded to a maximum of 3 decimal places to ensure consistent and precise representation.
*   **Fehlerbehebung Messwerterfassung (GUI Worker):** Korrigiert einen Fehler im GUI-Worker, bei dem 0-Werte, die durch Timeouts oder andere Lesefehler von der Tasmota-Dose entstanden sind, fälschlicherweise in die Messdaten aufgenommen wurden. Nun werden solche Messungen korrekt als ungültig erkannt, verworfen und die Erfassung wird wiederholt, bis die erforderliche Anzahl gültiger Messwerte erreicht ist.
    *   **English:** Measurement Data Acquisition Bugfix (GUI Worker): Fixed an issue in the GUI worker where 0-values, caused by timeouts or other read errors from the Tasmota device, were incorrectly included in the measurement data. Now, such measurements are correctly identified as invalid, discarded, and the acquisition is repeated until the required number of valid measurements is obtained.
*   **Anpassung Logging:** Die detaillierte Protokollierung jedes einzelnen Messwertpaares während der Messwerterfassung wurde auf Wunsch des Benutzers entfernt, um die Ausgabe zu reduzieren. Fehlermeldungen und Warnungen bei ungültigen Messungen bleiben erhalten.
    *   **English:** Logging Adjustment: The detailed logging of each individual measurement pair during data acquisition has been removed at the user's request to reduce output. Error messages and warnings for invalid measurements remain.
*   **Fehlerbehebung Plot-Darstellung (Strom):** Ein Fehler wurde behoben, bei dem im Live-Plot der Strom-Messwerte (`Ampere`) die "Ist (DUT)"-Kurve fälschlicherweise die Referenzwerte (`Ref_Amp`) anzeigte. Dies führte dazu, dass die Soll- und Ist-Kurven identisch waren und die tatsächliche DUT-Messung fehlte. Nun werden die korrekten DUT-Werte geplottet.
    *   **English:** Plot Display Bugfix (Current): Fixed an issue in the live plot of current measurements (`Ampere`) where the "Actual (DUT)" curve was incorrectly displaying the reference values (`Ref_Amp`). This resulted in identical target and actual curves and the actual DUT measurement being missing. Now, the correct DUT values are plotted.
*   **Wartezeit Offset-Messung:** Eine 5-sekündige Pause wurde in der GUI-Version eingefügt, um sicherzustellen, dass die Zieldose nach dem Ausschalten vollständig stabil ist, bevor die Offset-Messung beginnt.
    *   **English:** Offset Measurement Wait Time: A 5-second pause has been added to the GUI version to ensure the target device is fully stable after powering off before the offset measurement begins.
*   **Verbesserte Abbruch-Reaktion (GUI):** Die Reaktionsfähigkeit des "Messung abbrechen"-Buttons im GUI wurde verbessert, um ein sofortigeres Anhalten des Messvorgangs zu gewährleisten. Dies wurde durch häufigere Prüfungen des Abbruchsignals (`self.is_running`) vor kritischen I/O-Operationen erreicht. Die `time.sleep`-Dauer nach jeder gültigen Messung wurde auf den ursprünglichen Wert von 1 Sekunde zurückgesetzt. Die Timeouts für HTTP-Anfragen bleiben unverändert.
    *   **English:** Improved Abort Responsiveness (GUI): The responsiveness of the "Cancel Measurement" button in the GUI has been improved to ensure a more immediate halt of the measurement process. This was achieved by more frequent checks of the abort signal (`self.is_running`) before critical I/O operations. The `time.sleep` duration after each valid measurement has been reverted to its original value of 1 second. HTTP request timeouts remain unchanged.
*   **Fehlerbehebung Einrückung (GUI):** Ein `IndentationError` in `gui_main.py` in der `update_live_data`-Methode wurde behoben, der durch eine fehlerhafte Einrückung des `if/else`-Blocks zur Aktualisierung der LCD-Anzeigen und DUT-Labels verursacht wurde.
    *   **English:** Indentation Error Fix (GUI): An `IndentationError` in `gui_main.py` within the `update_live_data` method was resolved, caused by incorrect indentation of the `if/else` block responsible for updating LCD displays and DUT labels.
*   **Behoben: IndentationError in update_live_data (Benutzerkorrektur):** Der in `gui_main.py` aufgetretene `IndentationError` in der `update_live_data`-Methode wurde vom Benutzer behoben.
    *   **English:** Fixed: IndentationError in update_live_data (User Correction): The `IndentationError` encountered in `gui_main.py` within the `update_live_data` method was resolved by the user.

## v5.2.0 (2026-02-19)

### 📝 Planung & Spezifikation
*   **Neues Feature 'Manuelle Kalibrierung':** Ein neues, umfangreiches Feature für eine manuelle Kalibrierungsmethode wurde spezifiziert. Die Anforderungen und der Implementierungsplan wurden in der Datei `TODO.md` festgehalten.
*   **Neues Feature 'Dynamisches Credential-Management':** Die Anforderungen für die dynamische Abfrage von Zugangsdaten für passwortgeschützte Tasmota-Geräte wurden definiert und in `TODO.md` ergänzt.

## v5.1.0 (2026-02-18)

### 📚 Dokumentation
*   **Projektdokumentation:** Eine detaillierte `README.md` wurde erstellt, die das Projekt, dessen Features und den technischen Stack in Deutsch und Englisch beschreibt.

### ⚙️ Konfiguration
*   **Git-Konfiguration:** `.gitignore` Datei hinzugefügt, um Python-Caches, virtuelle Umgebungen, Build-Artefakte und Windows-Systemdateien aus dem Repository auszuschließen.

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
