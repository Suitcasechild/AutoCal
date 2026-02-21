# 🚀 Tasmota Precision Calibrator v5.3.3

This update focuses on surgical precision during the calibration process and improved reliability for device preparation.

### 🌟 Top Features of this Version
1.  **Selective Calibration:** You can now choose exactly which factors (`VoltageCal`, `CurrentCal`, `PowerCal`) to send to the device via checkboxes.
2.  **Configurable Tolerance Limits:** Set your own absolute deviation limits (in %) in **Setup -> General**. The app will automatically recommend calibration if these limits are exceeded.
3.  **Visual Step Progress:** A real-time progress bar shows the status of the current measurement step, improving user feedback.
4.  **Robust Device Preparation:** The initialization of the DUT (Device Under Test) has been refactored to send commands individually with proper URL encoding, ensuring all settings reach the device correctly.

### 🛠️ Technical Improvements
*   **Deviation Analysis:** The results dialog now displays the calculated deviation for V, A, and W compared to the current device state.
*   **Color-Coded Feedback:** Green/Orange visual indicators for calibration recommendations.
*   **Dynamic UI Elements:** The progress bar is intelligently shown only during active calibration.
*   **Improved Backlog Stability:** Prevents truncated commands during the initial setup phase.

**Note for Users:** Existing reports remain compatible. Internal versioning is synchronized to v5.3.3.

---

# 🚀 Tasmota Precision Calibrator v5.3.3 (DE)

Dieses Update konzentriert sich auf chirurgische Präzision beim Kalibriervorgang und eine verbesserte Zuverlässigkeit bei der Gerätevorbereitung.

### 🌟 Top-Features dieser Version
1.  **Selektive Kalibrierung:** Sie können nun über Checkboxen exakt wählen, welche Faktoren (`VoltageCal`, `CurrentCal`, `PowerCal`) an die Dose gesendet werden sollen.
2.  **Konfigurierbare Toleranzgrenzen:** Legen Sie in **Setup -> Allgemein** eigene Limits für die Abweichung (in %) fest. Die App empfiehlt eine Kalibrierung automatisch bei Grenzwertüberschreitung.
3.  **Visueller Messfortschritt:** Ein Echtzeit-Fortschrittsbalken zeigt den Status der aktuellen Messstufe an und verbessert das Benutzerfeedback.
4.  **Robuste Gerätevorbereitung:** Die Initialisierung des Prüflings wurde überarbeitet. Befehle werden nun einzeln und mit korrekter URL-Kodierung gesendet, was Übertragungsfehler verhindert.

### 🛠️ Technische Verbesserungen
*   **Abweichungs-Analyse:** Der Ergebnis-Dialog zeigt nun die berechnete Abweichung für V, A und W im Vergleich zum Ist-Zustand der Dose an.
*   **Farb-Kodierung:** Visuelles Feedback (Grün/Orange) für Kalibrier-Empfehlungen.
*   **Dynamische UI:** Der Fortschrittsbalken wird intelligent nur während aktiver Messungen eingeblendet.
*   **Backlog-Stabilität:** Verhindert das Verschlucken von Befehlen während der Vorbereitungsphase.

**Hinweis für Anwender:** Bestehende Kalibrier-Reports bleiben kompatibel. Alle internen Versionsangaben wurden auf v5.3.3 synchronisiert.
