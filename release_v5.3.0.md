# 🚀 Tasmota Precision Calibrator v5.3.0

This release marks a significant milestone in the development of the AutoCal tool. In addition to expanded visualizations, this update focuses on massive stability, data security, and a significantly improved user experience.

### ✨ New Features
*   **📑 Detailed Reference Display:** A new dedicated area (`frame_tasref`) now shows all device information (Name, MAC, Version) and live measurement values of the Tasmota reference device – analogous to the DUT.
*   **🚫 UI Input Locking:** To prevent misconfigurations during an active measurement, all input fields, checkboxes, and setup menus are automatically locked during the calibration run.
*   **🔌 Automatic Power-Off on Abort:** Safety first! If a measurement is manually cancelled via the button, the program immediately sends a power-off command to the DUT.
*   **📄 Auto-Config Creation:** The program now detects a missing `config.ini` and automatically creates a default file with sensible base values.

### 🛠️ Robustness & Code Quality
*   **🧮 Intelligent Mean Calculation:** The `CalibrationEngine` now validates CSV headers and features an automatic fallback mode for small datasets (less than 3 data points) to prevent crashes.
*   **📂 Centralized Path Management:** Management of configuration and directories has been bundled in the `ConfigManager`. Thanks to absolute paths, the app now starts reliably from any working directory.
*   **🔗 Decoupled Measurement Display:** The display of DUT values in the GUI is now completely independent of the selected reference mode (Fluke or Tasmota).
*   **🆔 MAC Compatibility:** The format of the device folders has been reverted to the proven hyphen notation (e.g., `2C-BC-...`) to maintain compatibility with old reports.

### 🐞 Stability & Performance
*   **📈 Memory Leak Fixed:** Live charts now use `collections.deque` with a fixed upper limit of 1000 data points. This prevents uncontrolled memory growth during long runs.
*   **🛡️ Type Safety:** A potential crash (`TypeError`) when processing measurement values has been eliminated by pre-converting to floating-point numbers.
*   **🌐 Robust MAC Retrieval:** Errors when retrieving the device MAC have been fixed, especially when IP addresses were entered without a protocol prefix (`http://`).

### 🔒 Privacy & Security
*   **保護 Protection of DUT-IP:** For privacy reasons, the IP address of the DUT is no longer permanently stored in the `config.ini`.

### 📚 Documentation
*   **📖 New Manual:** The `README.md` has been completely redesigned and now contains a detailed, illustrated user manual with a table of contents and jump marks in German and English.
*   **🤖 99% AI-Generated:** The documentation has been supplemented with the fascinating background story of the "Vibecoding" experiment.

**Note for Users:** Existing calibration reports remains compatible. The new version synchronizes all internal versioning consistently to v5.3.0.

---

# 🚀 Tasmota Precision Calibrator v5.3.0 (DE)

Dieses Release markiert einen bedeutenden Meilenstein in der Entwicklung des AutoCal-Tools. Neben erweiterten Visualisierungen liegt der Fokus dieses Updates auf massiver Stabilität, Datensicherheit und einer deutlich verbesserten Benutzerführung.

### ✨ Neue Features
*   **📑 Detaillierte Referenz-Anzeige:** Ein neuer dedizierter Bereich (`frame_tasref`) zeigt nun alle Geräte-Informationen (Name, MAC, Version) und Live-Messwerte der Tasmota-Referenzdose an – analog zum Prüfling.
*   **🚫 UI-Eingabesperre (Locking):** Um Fehlkonfigurationen während einer laufenden Messung zu verhindern, werden alle Eingabefelder, Checkboxen und Setup-Menüs während des Kalibrierlaufs automatisch gesperrt.
*   **🔌 Automatisches Ausschalten bei Abbruch:** Sicherheit geht vor! Wenn eine Messung manuell über den Button abgebrochen wird, sendet das Programm sofort einen Ausschaltbefehl an den Prüfling.
*   **📄 Auto-Konfigurations-Erstellung:** Das Programm erkennt nun eine fehlende `config.ini` und erstellt automatisch eine Standarddatei mit sinnvollen Basiswerten.

### 🛠️ Robustheit & Code-Qualität
*   **🧮 Intelligente Mittelwertbildung:** Die `CalibrationEngine` validiert nun CSV-Header und beherrscht einen automatischen Fallback-Modus für kleine Datensätze (weniger als 3 Messpunkte), um Abstürze zu vermeiden.
*   **📂 Zentralisiertes Pfad-Management:** Die Verwaltung der Konfiguration und Verzeichnisse wurde im `ConfigManager` gebündelt. Dank absoluter Pfade startet die App nun zuverlässig aus jedem Arbeitsverzeichnis.
*   **🔗 Entkoppelte Messwertanzeige:** Die Anzeige der DUT-Werte in der GUI ist nun vollständig unabhängig vom gewählten Referenzmodus (Fluke oder Tasmota).
*   **🆔 MAC-Kompatibilität:** Das Format der Geräteordner wurde auf die bewährte Bindestrich-Notation (z.B. `2C-BC-...`) zurückgesetzt, um die Kompatibilität mit alten Reports zu wahren.

### 🐞 Stabilität & Performance
*   **📈 Speicherleck behoben:** Die Live-Diagramme nutzen nun `collections.deque` mit einer festen Obergrenze von 1000 Datenpunkten. Dies verhindert unkontrolliertes Speicherwachstum bei langen Laufzeiten.
*   **🛡️ Typsicherheit:** Ein potenzieller Absturz (`TypeError`) bei der Verarbeitung von Messwerten wurde durch eine Vorab-Konvertierung in Fließkommazahlen eliminiert.
*   **🌐 Robuster MAC-Abruf:** Fehler beim Abrufen der Geräte-MAC wurden behoben, insbesondere wenn IP-Adressen ohne Protokoll-Präfix (`http://`) eingegeben wurden.

### 🔒 Datenschutz & Sicherheit
*   **🙈 Schutz der DUT-IP:** Aus Sicherheitsgründen wird die IP-Adresse des Prüflings nicht mehr dauerhaft in der `config.ini` gespeichert.

### 📚 Dokumentation
*   **📖 Neues Handbuch:** Die `README.md` wurde komplett überarbeitet und enthält nun eine detaillierte, bebilderte Bedienungsanleitung mit Inhaltsverzeichnis und Sprungmarken in Deutsch und Englisch.
*   **🤖 99% AI-Generated:** Die Dokumentation wurde um die faszinierende Hintergrundgeschichte des "Vibecoding"-Experiments ergänzt.

---
**Hinweis für Anwender:** Bestehende Kalibrier-Reports bleiben kompatibel. Die neue Version synchronisiert alle internen Versionsangaben konsistent auf v5.3.0.

---
*Generated with 99% AI support via Gemini CLI.* 🚀
