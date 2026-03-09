# 🚀 Tasmota Precision Calibrator v5.4.2

This release introduces an integrated help system for dynamic calibration and comprehensive documentation updates regarding flash memory protection.

## 🌟 Top Features & Improvements (v5.4.2)
1.  **Dynamic Calibration via Support Points:** Advanced power calibration using multiple measurement steps (support points). The system automatically calculates optimal switching thresholds (including hysteresis) based on the flflowing current (A).
2.  **Integrated Dynamic Help:** A new help button directly in the Dynamic Power-Calibration dialog provides instant access to technical documentation.
3.  **Embedded HTML Assets:** The full technical documentation is now securely embedded as an HTML asset, ensuring integrity and providing a modern Dark-Theme look.
4.  **Non-Modal Help Window:** The help dialog is non-modal, allowing users to read instructions while interacting with the calibration interface.
5.  **Advanced Search Function:** Includes a built-in search bar with "wrap-around" logic to quickly find specific terms within the documentation.
6.  **Flash Protection Documentation:** Added detailed sections to `anleitung.md` and `userguide.md` explaining the `SaveData 0` mechanism and its impact on manual configuration changes.
7.  **i18n Readiness:** Further prepared internal strings for full translation support.
8.  **Bugfixes:** Resolved a Python namespace issue (`AttributeError`) related to text cursor handling in the search function.

## 🛠️ Technical Details
*   **Asset Management:** New `assets_dynamic_info.py` for secure, hard-coded documentation storage.
*   **UI Logic:** Enhanced `DynamicCalDialog` with persistent help window reference and robust event handling.

---

# 🚀 Tasmota Precision Calibrator v5.4.2 (DE)

Dieses Release führt ein integriertes Hilfesystem für die dynamische Kalibrierung ein und bietet umfassende Dokumentations-Updates zum Thema Flash-Speicherschutz.

## 🌟 Top-Features & Verbesserungen (v5.4.2)
1.  **Dynamische Kalibrierung über Stützpunkte:** Fortgeschrittene Leistungskalibrierung unter Nutzung mehrerer Messstufen (Stützpunkte). Das System berechnet basierend auf dem fließenden Strom (A) automatisch optimale Umschaltschwellen inklusive Hysterese, um die Genauigkeit über den gesamten Lastbereich zu maximieren.
2.  **Integrierte dynamische Hilfe:** Ein neuer Hilfe-Button direkt im Dialog für die dynamische Power-Kalibrierung bietet sofortigen Zugriff auf die technische Dokumentation.
3.  **Eingebettete HTML-Assets:** Die vollständige technische Dokumentation ist nun sicher als HTML-Asset eingebettet, was die Integrität gewährleistet und ein modernes Dark-Theme bietet.
4.  **Nicht-modales Hilfefenster:** Der Hilfe-Dialog ist nicht-modal, sodass Benutzer die Anleitung lesen können, während sie mit der Kalibrierungsoberfläche interagieren.
5.  **Erweiterte Suchfunktion:** Enthält eine integrierte Suchleiste mit "Wrap-around"-Logik zum schnellen Finden spezifischer Begriffe in der Dokumentation.
6.  **Dokumentation zum Flash-Schutz:** Detaillierte Abschnitte in `anleitung.md` und `userguide.md` hinzugefügt, die den `SaveData 0`-Mechanismus und seine Auswirkungen auf manuelle Konfigurationsänderungen erklären.
7.  **i18n-Vorbereitung:** Interne Texte wurden weiter für die vollständige Übersetzungsunterstützung vorbereitet.
8.  **Fehlerbehebungen:** Ein Python-Namespace-Problem (`AttributeError`) im Zusammenhang mit der Text-Cursor-Verarbeitung in der Suchfunktion wurde behoben.

## 🛠️ Technische Details
*   **Asset-Management:** Neue `assets_dynamic_info.py` für die sichere, fest im Code verankerte Speicherung der Dokumentation.
*   **UI-Logik:** Erweiterter `DynamicCalDialog` mit persistenter Hilfe-Fenster-Referenz und robuster Ereignisbehandlung.

---
**Note for Users:** Existing reports and configurations remain fully compatible. Internal versioning is synchronized to v5.4.2.
**Hinweis für Anwender:** Bestehende Kalibrier-Reports und Konfigurationen bleiben voll kompatibel. Alle internen Versionsangaben wurden auf v5.4.2 synchronisiert.
