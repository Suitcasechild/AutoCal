# 🚀 Tasmota Precision Calibrator - Release Notes

This document provides an overview of the most important changes and innovations per version. / In diesem Dokument finden Sie eine Übersicht der wichtigsten Änderungen und Neuerungen pro Version.

---

## [v5.4.1] - 2026-02-22

This major release significantly expands the capabilities of the Tasmota Precision Calibrator, introducing a full manual workflow alongside major UI and architectural improvements.

### 🌟 Top Features
1.  **Manual Calibration Mode:** Calibrate devices using any external reference meter without serial connection via a new 3-point entry UI.
2.  **Photo-Method Support:** Optimized workflow for high-precision synchronization using smartphone photos.
3.  **Strict Field Validation:** Enforced data integrity with 2/3 decimal formatting and visual red-border feedback.
4.  **Cancellable Entry Mode:** Safe mode for manual input with auto power-off and UI locking.
5.  **Modeless Guidance:** New interactive help window that doesn't block the main GUI.
6.  **Internationalization (i18n):** Full support for English/German languages.
7.  **UI Mode Switching:** Switch between "Home Only" and "Pro/Home" interface layouts.
8.  **Selective Calibration:** Choose exactly which CAL factors to update via checkboxes.
9.  **Configurable Tolerance Limits:** Define custom deviation limits in Setup with color-coded recommendations.
10. **Visual Step Progress:** Real-time feedback via a dynamic progress bar.

### 🛠️ Technical Improvements
*   **Intelligent Calculation Engine:** Automatically skips incomplete data series.
*   **Secure Asset System:** Help content stored internally to prevent external manipulation.
*   **Unified Workflow:** Integrated "Old Report" detection for all calibration starts.
*   **Robust Communication:** Enhanced RS232 logic and refactored DUT initialization.

---

## [v5.4.1] - 2026-02-22 (DE)

Dieses große Release erweitert den Funktionsumfang des Tasmota Precision Calibrators massiv und führt einen vollständigen manuellen Workflow sowie bedeutende UI- und Architektur-Verbesserungen ein.

### 🌟 Top-Features
1.  **Manueller Kalibriermodus:** Kalibrierung mit beliebigen externen Messgeräten ohne serielle Verbindung über eine neue 3-Punkt-Eingabe.
2.  **Unterstützung der Foto-Methode:** Optimierter Workflow für höchste Präzision mittels Smartphone-Fotos.
3.  **Strikte Feld-Validierung:** Sicherstellung der Datenqualität durch Formatvorgaben und visuelles Feedback (roter Rahmen).
4.  **Abbrechbarer Eingabemodus:** Sicherer Modus für manuelle Eingaben inklusive Auto-Power-Off und UI-Sperren.
5.  **Nicht-modale Anleitung:** Neues interaktives Hilfefenster, das die Bedienung der GUI nicht blockiert.
6.  **Internationalisierung (i18n):** Vollständige Unterstützung für Deutsch/Englisch.
7.  **UI-Modus-Umschaltung:** Wechsel zwischen "Home Only" und "Pro/Home" Layout.
8.  **Selektive Kalibrierung:** Auswahl der zu aktualisierenden Faktoren über Checkboxen.
9.  **Konfigurierbare Toleranzgrenzen:** Benutzerdefinierte Limits im Setup mit farblichen Empfehlungen.
10. **Visueller Messfortschritt:** Echtzeit-Feedback durch einen dynamischen Fortschrittsbalken.

### 🛠️ Technische Verbesserungen
*   **Intelligente Berechnungs-Engine:** Automatisches Überspringen unvollständiger Messreihen.
*   **Sicheres Asset-System:** Interne Speicherung von Hilfeinhalten zur Manipulationsvermeidung.
*   **Einheitlicher Workflow:** "Alte Messdaten"-Erkennung für alle Kalibrierungs-Starts.
*   **Robuste Kommunikation:** Verbesserte RS232-Logik und überarbeitete Dose-Initialisierung.

---

## [v5.3.2] - 2026-02-21

Focus on reliability, user guidance, and credential management.

### 🌟 Top Features
*   **Integrated Interactive Manual:** Embedded dark-theme manual with anchor navigation.
*   **Fluke 45 Auto-Scan:** Automatically identify the multimeter across all ports and baud rates.
*   **Optimized Credential Management:** Session-based RAM storage for enhanced security.

---

## [v5.3.0] - 2026-02-20

Initial release of the v5 series with core PyQt interface and automated calibration logic.
