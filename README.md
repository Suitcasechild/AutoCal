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

## Inhaltsverzeichnis
1. [🚀 Das Vibecoding-Experiment](#-das-vibecoding-experiment-99-ki-generiert)
2. [📖 Über das Programm](#-über-das-programm-de)
3. [✨ Hauptmerkmale](#-hauptmerkmale-de)
4. [📘 Bedienungsanleitung](#-bedienungsanleitung-de)
5. [💻 Technischer Überblick](#-technischer-überblick-de)

---

## 🚀 Das Vibecoding-Experiment: 99% KI-generiert

*Willkommen hinter den Kulissen! Dieses Projekt ist nicht nur eine Software, sondern das Ergebnis eines faszinierenden Experiments in der modernen Anwendungsentwicklung.*

**Der Code in diesem Repository wurde zu 99% ausschließlich durch Prompts im Gemini-CLI erstellt.** Und das Spannendste daran? Das gesamte Projekt wurde aus der Perspektive eines absoluten Anfängers gestartet – **ohne jegliche Vorkenntnisse in Python oder der Einrichtung von Entwicklungsumgebungen.** Das Ziel war herauszufinden, ob es möglich ist, eine funktionierende Anwendung zu bauen, indem man sich einfach in die Logik "hineinfühlt" (Vibecoding) und geschickt mit einer KI kommuniziert.

### 🏛️ Die Säulen: Struktur als Fundament
Vibecoding bedeutet nicht, ziellos Befehle abzufeuern. Damit ein KI-gesteuertes Projekt dieser Größenordnung ohne Vorkenntnisse gelingt, ist eine starke Organisation erforderlich. Die KI übernahm die Programmierung, aber die Steuerung erfolgte über einen strengen dokumentarischen Rahmen:
* **Das Pflichtenheft:** Eine glasklare Vision dessen, was die Software können muss.
* **Pläne & To-Dos:** Detaillierte Roadmaps, um den Entwicklungsprozess in logische Phasen zu unterteilen.
* **Das Changelog:** Lückenlose Dokumentation aller Schritte und Änderungen als "Gedächtnis" des Projekts.
* **Die Gemini-Regeln:** Spezifische Regeln, die genau vorschreiben, wie die KI an Aufgaben herangehen, Code formatieren und kommunizieren soll.
* **Git & Versionskontrolle:** Das ultimative Sicherheitsnetz. Da vieles durch Ausprobieren (Trial and Error) entstand, war KI-geführte Git-Unterstützung unerlässlich, um funktionierende Meilensteine zu speichern und gescheiterte Experimente sicher rückgängig zu machen.

---

<a name="über-das-programm-de"></a>
## 📖 Über das Programm

Ein GUI-basiertes Werkzeug zur hochpräzisen Kalibrierung und Validierung von Tasmota-basierten Energiemessgeräten (z.B. Smart Plugs). Die Anwendung automatisiert den Prozess des Messens, Berechnens und Anwendens neuer Kalibrierwerte, um die Genauigkeit von Leistungs-, Spannungs- und Strommessungen zu verbessern.

Es unterstützt zwei Hauptmodi für die Referenzmessung:
1.  **🔬 Professioneller Modus:** Nutzt ein Fluke 45 Multimeter via RS232 als hochpräzise Referenz.
2.  **🏠 Heimanwender-Modus:** Nutzt ein bereits kalibriertes Tasmota-Gerät als "Master-Referenz" via HTTP.

---

<a name="hauptmerkmale-de"></a>
## ✨ Hauptmerkmale

*   **🗺️ Geführter Kalibrierprozess:** Die Benutzeroberfläche führt Sie durch jeden Schritt, von der Gerätekonfiguration bis zur Anwendung der finalen Kalibrierung.
*   **🔌 Duale Referenz-Unterstützung:** Wählen Sie zwischen einem professionellen Multimeter (Fluke 45) oder einem bereits kalibrierten Tasmota-Stecker.
*   **🔍 Fluke Auto-Scan (Neu):** Kein Suchen nach COM-Ports mehr. Das Programm findet das Fluke 45 vollautomatisch an allen COM-Ports und Baudraten.
*   **🎯 Selektive Kalibrierung (Neu):** Wählen Sie präzise, welche Faktoren (Spannung, Strom, Leistung) gesendet werden sollen. Inklusive intelligenter Toleranz-Analyse und visuellem Feedback (Grün/Orange).
*   **⚖️ Konfigurierbare Toleranzen (Neu):** Eigene absolute Limits im Setup festlegbar. Die App empfiehlt eine Kalibrierung nur bei Grenzwertüberschreitung.
*   **📊 Fortgeschrittene mathematische Analyse:** Verwendet lineare Regression (`numpy`), um den genauesten `PowerCal`-Wert über den gesamten Messbereich zu berechnen.
*   **📘 Integrierte interaktive Anleitung (Neu):** Ein professionelles HTML-Handbuch ist nun direkt in die Software eingebettet – inklusive Navigation und detaillierten Anweisungen.
*   **🔐 Sitzungsbasierte Passwörter (Neu):** Zugangsdaten einmalig eingeben (z.B. beim Online-Check) und für die gesamte Sitzung behalten. Vorbefüllter "admin"-User für schnelles Arbeiten.
*   **💾 Automatisierte Protokollierung:** Detaillierte `.csv`-Dateien mit Rohdaten und ein umfassendes `.txt`-Protokoll werden automatisch erstellt (MAC-basierte Ordnerstruktur).
*   **📈 Sicherheit & Stabilität:** Automatisches Ausschalten des Prüflings bei Abbruch, Sperrung der Eingabefelder während der Messung und robuster Umgang mit instabilen Netzwerkdaten durch Min/Max-Filterung.

---

<a name="bedienungsanleitung-de"></a>
## 📘 Bedienungsanleitung

### 1. ⚙️ Vorbereitung & Installation

#### Option A: Vorkompilierte Version (Empfohlen für Anwender)
Laden Sie einfach die neueste `TasmotaCalibrator.exe` aus den [Releases](https://github.com/Suitcasechild/AutoCal/releases) herunter. Einfach unter Windows starten.

#### Option B: Aus dem Quellcode (Für Entwickler)
1.  **Klonen:** `git clone https://github.com/Suitcasechild/AutoCal.git`.
2.  **Installieren:** `pip install -r requirements.txt`.
3.  **Starten:** `python gui_main.py`.

#### 📄 Konfiguration
Passen Sie die `config.ini` an oder nutzen Sie das **Setup-Menü** in der App, um Pfade, COM-Ports oder Ihre Referenz-IP festzulegen. Die Anwendung erlaubt nun auch die Konfiguration der **[TOLERANCE abs%]** Limits über die GUI.

---

### 2. 🚀 Durchführung einer Kalibrierung

#### 3.1 🔐 Online-Check & Authentifizierung
Geben Sie die IP des Prüflings ein. Klicken Sie auf `🌐`. Hier eingegebene Zugangsdaten werden sicher im Arbeitsspeicher für die gesamte Sitzung behalten.

#### 3.2 🎯 Wahl der Referenz
*   **🔬 PRO (Fluke 45):** Nutzen Sie den **"Fluke finden"** Button in **Setup -> Fluke 45**, um Ihr Gerät automatisch zu identifizieren.
*   **🏠 HOME (Tasmota):** Das Programm ermittelt vorab automatisch den Eigenverbrauch des Prüflings (Offset) und zieht diesen ab.

#### 3.3 🏁 Auswertung & Anwendung
Nach der Messung zeigt ein Dialog das detaillierte Protokoll:
*   **☑️ Selektiver Modus:** Nutzen Sie die Checkboxen, um nur gewünschte Faktoren zu aktualisieren.
*   **💡 Abweichungs-Analyse:** Labels werden 🟢 (OK) oder 🟠 (Kalibrierung empfohlen), basierend auf Ihren konfigurierten Limits.
*   **📤 Anwenden:** Klicken Sie auf **"KALIBRIEREN"**, um die Werte zu senden und eine sofortige "As-Found/As-Left" Verifizierung durchzuführen.

---

<a name="technischer-überblick-de"></a>
## 💻 Technischer Überblick

*   **Sprache:** Python 3.12+
*   **GUI:** PySide6 (Qt)
*   **Diagramme:** pyqtgraph
*   **Datenanalyse:** `pandas` & `numpy`
