# 🚀 Tasmota Precision Calibrator v5.4.2

This release introduces an integrated help system for dynamic calibration and comprehensive documentation updates regarding flash memory protection.

## 🌟 Top Features & Improvements (v5.4.2)
1.  **Integrated Dynamic Help:** A new help button directly in the Dynamic Power-Calibration dialog provides instant access to technical documentation.
2.  **Embedded HTML Assets:** The full technical documentation is now securely embedded as an HTML asset, ensuring integrity and providing a modern Dark-Theme look.
3.  **Non-Modal Help Window:** The help dialog is non-modal, allowing users to read instructions while interacting with the calibration interface.
4.  **Advanced Search Function:** Includes a built-in search bar with "wrap-around" logic to quickly find specific terms within the documentation.
5.  **Flash Protection Documentation:** Added detailed sections to `anleitung.md` and `userguide.md` explaining the `SaveData 0` mechanism and its impact on manual configuration changes.
6.  **i18n Readiness:** Further prepared internal strings for full translation support.
7.  **Bugfixes:** Resolved a Python namespace issue (`AttributeError`) related to text cursor handling in the search function.

## 🛠️ Technical Details
*   **Asset Management:** New `assets_dynamic_info.py` for secure, hard-coded documentation storage.
*   **UI Logic:** Enhanced `DynamicCalDialog` with persistent help window reference and robust event handling.

---

# 🚀 Tasmota Precision Calibrator v5.4.2 (DE)

Dieses Release führt ein integriertes Hilfesystem für die dynamische Kalibrierung ein und bietet umfassende Dokumentations-Updates zum Thema Flash-Speicherschutz.

## 🌟 Top-Features & Verbesserungen (v5.4.2)
1.  **Integrierte dynamische Hilfe:** Ein neuer Hilfe-Button direkt im Dialog für die dynamische Power-Kalibrierung bietet sofortigen Zugriff auf die technische Dokumentation.
2.  **Eingebettete HTML-Assets:** Die vollständige technische Dokumentation ist nun sicher als HTML-Asset eingebettet, was die Integrität gewährleistet und ein modernes Dark-Theme bietet.
3.  **Nicht-modales Hilfefenster:** Der Hilfe-Dialog ist nicht-modal, sodass Benutzer die Anleitung lesen können, während sie mit der Kalibrierungsoberfläche interagieren.
4.  **Erweiterte Suchfunktion:** Enthält eine integrierte Suchleiste mit "Wrap-around"-Logik zum schnellen Finden spezifischer Begriffe in der Dokumentation.
5.  **Dokumentation zum Flash-Schutz:** Detaillierte Abschnitte in `anleitung.md` und `userguide.md` hinzugefügt, die den `SaveData 0`-Mechanismus und seine Auswirkungen auf manuelle Konfigurationsänderungen erklären.
6.  **i18n-Vorbereitung:** Interne Texte wurden weiter für die vollständige Übersetzungsunterstützung vorbereitet.
7.  **Fehlerbehebungen:** Ein Python-Namespace-Problem (`AttributeError`) im Zusammenhang mit der Text-Cursor-Verarbeitung in der Suchfunktion wurde behoben.

## 🛠️ Technische Details
*   **Asset-Management:** Neue `assets_dynamic_info.py` für die sichere, fest im Code verankerte Speicherung der Dokumentation.
*   **UI-Logik:** Erweiterter `DynamicCalDialog` mit persistenter Hilfe-Fenster-Referenz und robuster Ereignisbehandlung.

---
**Note for Users:** Existing reports and configurations remain fully compatible. Internal versioning is synchronized to v5.4.2.
**Hinweis für Anwender:** Bestehende Kalibrier-Reports und Konfigurationen bleiben voll kompatibel. Alle internen Versionsangaben wurden auf v5.4.2 synchronisiert.
