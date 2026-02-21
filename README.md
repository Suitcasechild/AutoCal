# Tasmota Precision Calibrator

*99% AI-Generated: A journey from zero Python knowledge to a fully functional PyQt application using solely prompt-driven development.*

([Deutsche Beschreibung unten](#tasmota-precision-calibrator-de))

---

## Table of Contents
1. [🚀 The Vibecoding Experiment](#-the-vibecoding-experiment-99-ai-generated)
2. [📖 About the Tool](#-about-the-tool)
3. [✨ Key Features](#-key-features)
4. [📘 User Guide](#-user-guide)
5. [💻 Technical Stack](#-technical-stack)

---

## 🚀 The Vibecoding Experiment: 99% AI-Generated

*Welcome behind the scenes! This project is not just a piece of software, but the result of a fascinating experiment in modern application development.*

**The code in this repository was 99% created exclusively through prompts in the Gemini CLI.** And the most exciting part? The entire project was started from the perspective of an absolute beginner – **without any prior knowledge of Python or setting up development environments.** The goal was to find out if it's possible to build a functioning application simply by "feeling" the logic (vibecoding) and cleverly communicating with an AI.

### 🏛️ The Pillars: Structure as a Foundation
Vibecoding does not mean firing off commands aimlessly. For an AI-driven project of this scale to succeed without prior knowledge, strong organization is required. The AI handled the programming, but the control was managed through a strict documentary framework:
* **The Requirements Document (Pflichtenheft):** A crystal-clear vision of what the software must be able to do.
* **Plans & To-Dos:** Detailed roadmaps to divide the development process into logical stages.
* **The Changelog:** Seamless documentation of all steps and changes as the project's "memory".
* **The Gemini Rules:** Specific rules dictating exactly how the AI should approach tasks, format code, and communicate.
* **Git & Version Control:** The ultimate safety net. Since much was built through trial and error, AI-guided Git support was essential for saving working milestones and rolling back failed experiments safely.

---

## 📖 About the Tool

A GUI-based tool for high-precision calibration and validation of Tasmota-based energy monitoring devices (like smart plugs). This application automates the process of measuring, calculating, and applying new calibration values to enhance the accuracy of power, voltage, and current readings.

It supports two main modes for reference measurements:
1.  **🔬 Professional Mode:** Uses a Fluke 45 multimeter via RS232 as the high-precision reference.
2.  **🏠 Home User Mode:** Uses a previously calibrated Tasmota device as a "master" reference via HTTP.

---

## ✨ Key Features

*   **🗺️ Guided Calibration Process:** The UI walks you through every step, from device setup to applying the final calibration.
*   **🔌 Dual Reference Support:** Choose between a professional multimeter (Fluke 45) or a consumer-grade, pre-calibrated Tasmota plug.
*   **🔍 Fluke Auto-Discovery (New):** No more manual COM port hunting. The tool automatically scans all ports and baud rates to find your Fluke 45.
*   **🎯 Selective Calibration (New):** Choose exactly which factors (Voltage, Current, Power) to apply. Includes an intelligent tolerance analysis with visual feedback (Green/Orange).
*   **⚖️ Configurable Tolerances (New):** Set your own absolute deviation limits in the setup. The app will recommend calibration only if these limits are exceeded.
*   **📊 Advanced Mathematical Analysis:** Utilizes linear regression (`numpy`) to calculate the most accurate `PowerCal` value across the entire measurement range.
*   **📘 Embedded Interactive Manual (New):** A professional HTML guide is now built directly into the app, featuring anchor navigation and step-by-step instructions.
*   **🔐 Session-Based Credentials (New):** Enter passwords once (e.g., during Online Check) and keep them for the entire session. Pre-filled "admin" user for faster workflow.
*   **💾 Automated Reporting:** Detailed `.csv` files with raw measurement data and a comprehensive `.txt` protocol are generated and stored automatically (MAC-address based folder structure).
*   **🛡️ Safety & Robustness:** Automatically turns off the device on manual abort, locks input fields during active runs, and handles noisy data by excluding min/max outliers.

---

## 📘 User Guide

### 1. ⚙️ Setup and Installation

#### Option A: Pre-compiled Version (Recommended for Users)
Download the latest `TasmotaCalibrator.exe` from the [Releases tab](https://github.com/Suitcasechild/AutoCal/releases). Simply run it on Windows.

#### Option B: From Source Code (For Developers)
1.  **Clone:** `git clone https://github.com/Suitcasechild/AutoCal.git`.
2.  **Install:** `pip install -r requirements.txt`.
3.  **Run:** `python gui_main.py`.

#### 📄 Configuration
Adjust `config.ini` or use the **Setup** menu within the app to set report directories, COM ports, or your reference Tasmota IP. The application now also allows configuring **[TOLERANCE abs%]** limits via the GUI.

---

### 2. 🚀 Performing a Calibration

#### 3.1 🔐 Online Check & Authentication
Enter the DUT IP. Click `🌐`. Credentials entered here are kept securely in memory for the whole session.

#### 3.2 🎯 Reference Selection
*   **🔬 PRO (Fluke 45):** Use the **"Find Fluke"** button in **Setup -> Fluke 45** to identify your device automatically.
*   **🏠 HOME (Tasmota):** The software automatically calculates and subtracts the DUT's self-consumption (Offset) before starting.

#### 3.3 🏁 Analysis and Application
After the measurement, a dialog displays the detailed protocol:
*   **☑️ Selective Mode:** Use the checkboxes to select only the factors you want to update.
*   **💡 Deviation Analysis:** Labels turn 🟢 (OK) or 🟠 (Calibration recommended) based on your configured limits.
*   **📤 Applying:** Click **"CALIBRATE"** to send values and perform an immediate "As Found/As Left" verification.

---

## 💻 Technical Stack

*   **Language:** Python 3.12+
*   **GUI:** PySide6 (Qt)
*   **Graphs:** pyqtgraph
*   **Data Analysis:** `pandas` & `numpy`

---
---

# Tasmota Precision Calibrator (DE)

*99% KI-generiert: Eine Reise von Null Python-Wissen zu einer voll funktionsfähigen PyQt-Anwendung, ausschließlich durch Prompt-gesteuerte Entwicklung.*

---

## ✨ Hauptmerkmale

*   **🗺️ Geführter Kalibrierprozess:** Intuitive Benutzeroberfläche von der Konfiguration bis zum finalen Flash.
*   **🔌 Duale Referenz-Unterstützung:** Wahlweise Fluke 45 (Profi) oder eine kalibrierte Tasmota-Dose (Heimanwender).
*   **🔍 Fluke Auto-Scan (Neu):** Das Programm findet das Fluke 45 vollautomatisch an allen COM-Ports und Baudraten.
*   **🎯 Selektive Kalibrierung (Neu):** Wählen Sie präzise, welche Faktoren (V, A, W) gesendet werden sollen.
*   **⚖️ Konfigurierbare Toleranzen (Neu):** Eigene Limits im Setup festlegbar. Die App bewertet die Abweichung automatisch (Grün/Orange).
*   **📊 Fortgeschrittene Analyse:** Lineare Regression (`numpy`) für höchste Präzision über den gesamten Messbereich.
*   **📘 Integrierte Anleitung (Neu):** Ein interaktives HTML-Handbuch ist nun direkt in die Software eingebettet.
*   **🔐 Sitzungsbasierte Passwörter (Neu):** Einmalige Passworteingabe genügt für die gesamte Programmsitzung.
*   **💾 Automatisierte Protokollierung:** Speicherung in MAC-basierten Ordnern als `.csv` und `.txt` (inkl. As-Found/As-Left Vergleich).

---

## 📘 Kurzanleitung (DE)

### 1. ⚙️ Vorbereitung
*   Nutzen Sie den **Setup-Dialog**, um Speicherpfade und Referenzgeräte zu konfigurieren.
*   Im Menü **Allgemein** können Sie die Toleranzgrenzen (Standard: 0,5%) für die Empfehlungslogik anpassen.

### 2. 🚀 Durchführung
1.  **Online-Check:** IP eingeben und `🌐` klicken. MAC und Version werden automatisch geladen.
2.  **Referenz finden:** Nutzen Sie bei Fluke-Betrieb den Button **"Fluke finden"**, um die Schnittstelle automatisch zu konfigurieren.
3.  **Kalibrieren:** Starten Sie den Prozess. Das Programm führt Sie durch die Schritte (Offset-Messung, Lastzuschaltung).
4.  **Anwenden:** Wählen Sie im Ergebnisdialog die gewünschten Faktoren über die Checkboxen aus und senden Sie diese an die Dose.

---

## 💻 Technischer Überblick

*   **Sprache:** Python 3.12+
*   **GUI:** PySide6 (Qt)
*   **Echtzeit-Diagramme:** pyqtgraph
*   **Datenverarbeitung:** `pandas` & `numpy`
