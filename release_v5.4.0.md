# 🚀 Tasmota Precision Calibrator v5.4.0

This major release significantly expands the capabilities of the Tasmota Precision Calibrator, introducing a full manual workflow alongside major UI and architectural improvements.

### 🌟 Top Features
1.  **Manual Calibration Mode:** Calibrate devices using any external reference meter without serial connection. Includes a dedicated UI for 3-point data entry.
2.  **Photo-Method Support:** Optimized workflow for high-precision synchronization using smartphone photos to capture reference and DUT values simultaneously.
3.  **Strict Field Validation:** Enforced data integrity with 2-decimal (V, W) and 3-decimal (A) formatting, including visual red-border feedback and intelligent "Apply" button locking.
4.  **Cancellable Entry Mode:** Dedicated mode for manual input that keeps the DUT state managed (auto power-off) and locks relevant UI frames to prevent misconfiguration.
5.  **Modeless Guidance:** A new interactive help window that provides step-by-step instructions without blocking the main application interface.
6.  **Internationalization (i18n):** Full infrastructure for multi-language support (English/German), including an auto-detection setting in `config.ini`.
7.  **UI Mode Switching:** Switch between simplified "Home Only" (Tasmota reference) and "Pro/Home" (Fluke/Tasmota) interface layouts.
8.  **Selective Calibration:** Surgical precision by choosing exactly which factors (`VoltageCal`, `CurrentCal`, `PowerCal`) to update via checkboxes.
9.  **Configurable Tolerance Limits:** Define custom absolute deviation limits in Setup. The app now provides visual color-coded recommendations based on these limits.
10. **Visual Step Progress:** Real-time feedback for measurement steps via a dynamic progress bar.

### 🛠️ Technical Improvements
*   **Intelligent Calculation Engine:** Automatically detects incomplete data series and skips only affected CAL factors.
*   **Secure Asset System:** Help content is now stored internally to prevent external file manipulation.
*   **Unified Workflow:** Integrated "Old Report" detection for both automated and manual calibration starts.
*   **Robust Communication:** Enhanced Fluke 45 RS232 logic and refactored DUT initialization with proper URL encoding.
*   **Code Hardening:** Comprehensive audit of all modules for improved error handling and stability against edge cases.

**Note for Users:** Existing reports remain compatible. Internal versioning is synchronized to v5.4.0.

---

# 🚀 Tasmota Precision Calibrator v5.4.0 (DE)

Dieses große Release erweitert den Funktionsumfang des Tasmota Precision Calibrators massiv und führt einen vollständigen manuellen Workflow sowie bedeutende UI- und Architektur-Verbesserungen ein.

### 🌟 Top-Features
1.  **Manueller Kalibriermodus:** Kalibrierung mit beliebigen externen Messgeräten ohne serielle Verbindung über einen neuen Eingabebereich für 3-Punkt-Messungen.
2.  **Unterstützung der Foto-Methode:** Optimierter Workflow für höchste Präzision durch gleichzeitiges Erfassen von Referenz- und Prüflingswerten mittels Smartphone-Fotos.
3.  **Strikte Feld-Validierung:** Sicherstellung der Datenqualität durch Formatvorgaben (2 Stellen für V/W, 3 Stellen für A) mit visuellem Feedback (roter Rahmen).
4.  **Abbrechbarer Eingabemodus:** Sicherer Modus für manuelle Eingaben, der den Zustand der Dose verwaltet (Auto-Power-Off) und Fehlkonfigurationen durch UI-Sperren verhindert.
5.  **Nicht-modale Anleitung:** Ein neues interaktives Hilfefenster mit Schritt-für-Schritt-Anleitungen, das die Bedienung der GUI nicht blockiert.
6.  **Internationalisierung (i18n):** Vollständige Infrastruktur für Mehrsprachigkeit (Deutsch/Englisch) inklusive automatischer Spracherkennung.
7.  **UI-Modus-Umschaltung:** Wechsel zwischen vereinfachtem "Home Only" (Tasmota-Referenz) und "Pro/Home" (Fluke/Tasmota) Layout.
8.  **Selektive Kalibrierung:** Punktgenaue Auswahl der zu aktualisierenden Faktoren (`VoltageCal`, `CurrentCal`, `PowerCal`) über Checkboxen.
9.  **Konfigurierbare Toleranzgrenzen:** Benutzerdefinierte Limits für Abweichungen im Setup, inklusive farblicher Empfehlungen (Grün/Orange).
10. **Visueller Messfortschritt:** Echtzeit-Feedback während der Messungen durch einen dynamischen Fortschrittsbalken.

### 🛠️ Technische Verbesserungen
*   **Intelligente Berechnungs-Engine:** Erkennt unvollständige Messreihen und überspringt gezielt nur die betroffenen CAL-Faktoren.
*   **Sicheres Asset-System:** Hilfeinhalte werden intern gespeichert, um Manipulationen von außen zu verhindern.
*   **Einheitlicher Workflow:** "Alte Messdaten"-Erkennung nun sowohl für automatisierte als auch für manuelle Starts integriert.
*   **Robuste Kommunikation:** Verbesserte Fluke 45 RS232-Logik und überarbeitete Initialisierung der Dose mit korrekter URL-Kodierung.
*   **Code-Härtung:** Umfassende Überprüfung aller Module für bessere Fehlerbehandlung und Stabilität in Randfällen.

**Hinweis für Anwender:** Bestehende Kalibrier-Reports bleiben kompatibel. Alle internen Versionsangaben wurden auf v5.4.0 synchronisiert.
