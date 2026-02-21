# 🚀 Tasmota Precision Calibrator v5.3.0

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
