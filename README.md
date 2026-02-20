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

### 🛠️ The Journey: From "Zero Knowledge" to a Running App
The process took place in three major phases:
1.  **Setting up the Toolchain:** The AI served as a patient mentor for absolute basics (installing Python, understanding `pip`, setting up an IDE, and basic Git commands).
2.  **Integrating the Gemini CLI:** Learning how to use the terminal to communicate with the AI model directly from the development environment.
3.  **The "Vibecoding" Process:** Instead of typing syntax, requirements and workflows were formulated in natural language based on the *Plans* and *To-Dos*. The AI translated these "vibes" into executable Python code. Crashes and stack traces were simply fed back to the AI for immediate fixes. Complex elements (like live graphs) were built iteratively through constant inquiry, guided by the *Gemini Rules* and secured by *Git commits*.

*When reading the code, look at it through this lens: It is the product of an intensive, highly structured conversation between human and machine.*

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
*   **📊 Advanced Mathematical Analysis:** Utilizes linear regression (`numpy`) to calculate the most accurate `PowerCal` value across the entire measurement range, enhancing linearity. `VoltageCal` and `CurrentCal` are calculated based on the mean deviation.
*   **🤝 Interactive Decision Making:** Before applying any changes, the tool presents a detailed report. You can choose whether to apply the new values and even select between the regression-based `PowerCal` (recommended) or a simpler mean-based value.
*   **💾 Automated Reporting:** For every calibration run, detailed `.csv` files with raw measurement data and a comprehensive `.txt` protocol are generated and stored.
*   **📈 Non-Blocking UI:** Live data is displayed using `pyqtgraph`, and all communication (HTTP and Serial) runs in a background thread (`QThread`) to keep the UI responsive.
*   **🛡️ Safety & Robustness:** Automatically turns off the device on manual abort, locks input fields during active runs to prevent errors, and handles noisy data by excluding min/max outliers.
*   **🌐 Coming Soon:** Automatic language switching between English and German based on system settings or manual selection.

---

## 📘 User Guide

### Detailed Table of Contents
1. [⚙️ Setup and Installation](#1-setup-and-installation)
    * [Option A: Pre-compiled EXE](#option-a-pre-compiled-version-recommended-for-users)
    * [Option B: From Source Code](#option-b-from-source-code-for-developers)
    * [📄 Configuring config.ini](#config-file-details)
2. [🖼️ Interface Overview](#2-the-main-window-interface)
    * [⌨️ Input and Configuration](#input-and-configuration)
    * [📺 Real-time Displays](#real-time-displays)
    * [📉 Live Charts](#live-charts)
3. [🚀 Executing a Calibration](#3-performing-a-calibration-step-by-step)
    * [🔐 Online Check & Authentication](#31-online-check--authentication)
    * [🎯 Reference Selection](#32-reference-selection)
    * [⏱️ The Measurement Run](#33-the-measurement-run)
    * [🔒 Safety Features](#34-safety-features)
4. [🏁 Results and Verification](#4-analysis-and-application)
    * [📋 Understanding the Report](#41-understanding-the-report)
    * [📤 Applying Values](#42-applying-values)
    * [🔄 Re-Applying Old Data](#43-using-existing-data-re-apply)

---

### 1. ⚙️ Setup and Installation

#### Option A: Pre-compiled Version (Recommended for Users)
For users who do not want to install Python, a pre-compiled version (`.exe` for Windows) is available in the [Releases tab](https://github.com/Suitcasechild/AutoCal/releases). Simply download the latest `TasmotaCalibrator.exe` and run it.

#### Option B: From Source Code (For Developers)
1.  **Clone Repository:** `git clone https://github.com/Suitcasechild/AutoCal.git`.
2.  **Install Dependencies:** `pip install -r requirements.txt`.
3.  **Run Application:** `python gui_main.py`.

#### 📄 Config File Details
Adjust the `config.ini` file if needed. You can set the default report directory and pre-configure COM ports for the Fluke 45 or the IP of your reference Tasmota plug. The application now automatically creates a default config file if it's missing.

---

### 2. 🖼️ The Main Window Interface

#### ⌨️ Input and Configuration
The top section of the UI allows you to select your reference source (PRO, HOME, or Manual) and enter the target device (DUT) IP address. Here, you also define the measurement parameters: **Steps** (number of load levels) and **Measurements per Step** (number of samples per level).

#### 📺 Real-time Displays
The middle section provides live status information for both the DUT and the chosen reference. 
*   **📱 DUT Info:** Displays the device's hostname, MAC address, and firmware version, alongside live sensor readings for voltage, current, and power.
*   **📑 Reference Info:** 
    *   In **PRO mode**, the large LCD numbers mimic the Fluke 45's dual display.
    *   In **HOME mode**, a dedicated panel shows the reference Tasmota device's identity and live sensor data for side-by-side comparison.

#### 📉 Live Charts
The right-hand panel features high-performance `pyqtgraph` charts. These plots show the **Soll (Reference)** and **Ist (DUT)** values simultaneously, allowing you to visually assess the deviation and stabilization of the measurement in real-time.

---

### 3. 🚀 Performing a Calibration (Step-by-Step)

#### 3.1 🔐 Online Check & Authentication
Enter the IP of your DUT. Click the `🌐` button. If the device is password-protected, a dialog will appear. Your credentials are kept in temporary memory and never stored on disk.

#### 3.2 🎯 Reference Selection
*   **🔬 PRO (Fluke 45):** Connect your multimeter via RS232. Use the **Setup -> Fluke 45** menu to configure the COM port.
*   **🏠 HOME (Tasmota):** Ensure your reference plug is calibrated. Use the **Setup -> Tasmota** menu to set its IP. The software will automatically calculate and subtract the DUT's self-consumption (Offset) before starting.

#### 3.3 ⏱️ The Measurement Run
Click **"Start Calibration"**. The software will guide you:
1.  **Stabilization:** After turning on the load, a 7-second filter ensures the inrush current has settled.
2.  **Data Collection:** Multiple measurements are taken. Min/Max values are automatically discarded to eliminate noise.
3.  **Step Transition:** The DUT is automatically turned off between steps to allow you to change the load safely.

#### 3.4 🔒 Safety Features
*   **🚫 UI Locking:** Once a run starts, all configuration frames and setup menus are disabled to prevent accidental changes.
*   **🔌 Automatic Power-Off:** If you click "Cancel Measurement", the software immediately sends a `Power OFF` command to the DUT to ensure the load is not left active.

---

### 4. 🏁 Analysis and Application

#### 4.1 📋 Understanding the Report
After the final step, a dialog displays the detailed protocol. It shows the deviation for every single step and provides two suggestions for `PowerCal`:
*   **📈 Regression (Recommended):** Uses mathematical slope analysis for best accuracy across the whole range.
*   **🧮 Mean Value:** A simple average of the deviation.

#### 4.2 📤 Applying Values
Click **"CALIBRATE"**. The software sends the commands, waits for the device to acknowledge, and then performs a **Verification Read**. It appends an "As Found / As Left" block to your report to prove the calibration was successful.

#### 4.3 🔄 Using Existing Data (Re-Apply)
If you start a calibration for a device with existing reports, you can skip the measurement and directly jump to the application dialog to re-send the last known good values.

---

## 💻 Technical Stack

*   **Language:** Python 3.12+
*   **GUI:** PySide6 (Qt)
*   **Real-time Graphs:** pyqtgraph
*   **Communication:** `pyserial` (Fluke 45) & `httpx` (Tasmota HTTP API)
*   **Data Analysis:** `pandas` & `numpy`

---
---

# Tasmota Precision Calibrator (DE)

*99% KI-generiert: Eine Reise von Null Python-Wissen zu einer voll funktionsfähigen PyQt-Anwendung, ausschließlich durch Prompt-gesteuerte Entwicklung.*

([English description above](#tasmota-precision-calibrator))

---

## Inhaltsverzeichnis
1. [🚀 Das Vibecoding-Experiment](#-das-vibecoding-experiment-99-ki-generiert)
2. [📖 Über das Programm](#-über-das-programm)
3. [✨ Hauptmerkmale](#-hauptmerkmale)
4. [📘 Bedienungsanleitung](#-bedienungsanleitung-de)
5. [💻 Technischer Überblick](#-technischer-überblick)

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

### 🛠️ Die Reise: Vom „Nullwissen“ zur laufenden App
Der Prozess fand in drei großen Phasen statt:
1.  **Einrichtung der Toolchain:** Die KI diente als geduldiger Mentor für absolute Grundlagen (Installation von Python, Verständnis von `pip`, Einrichtung einer IDE und grundlegende Git-Befehle).
2.  **Integration des Gemini-CLI:** Erlernen der Nutzung des Terminals, um direkt aus der Entwicklungsumgebung mit dem KI-Modell zu kommunizieren.
3.  **Der „Vibecoding“-Prozess:** Anstatt Syntax zu tippen, wurden Anforderungen und Arbeitsabläufe in natürlicher Sprache auf Basis der *Pläne* und *To-Dos* formuliert. Die KI übersetzte diese „Vibes“ in ausführbaren Python-Code. Abstürze und Stack-Traces wurden einfach an die KI zurückgegeben, um sofortige Korrekturen zu erhalten. Komplexe Elemente (wie Live-Graphen) wurden iterativ durch ständiges Nachfragen aufgebaut, geleitet von den *Gemini-Regeln* und abgesichert durch *Git-Commits*.

*Wenn Sie den Code lesen, betrachten Sie ihn durch diese Brille: Er ist das Produkt eines intensiven, hochstrukturierten Gesprächs zwischen Mensch und Maschine.*

---

## 📖 Über das Programm

Ein GUI-basiertes Werkzeug zur hochpräzisen Kalibrierung und Validierung von Tasmota-basierten Energiemessgeräten (z.B. Smart Plugs). Die Anwendung automatisiert den Prozess des Messens, Berechnens und Anwendens neuer Kalibrierwerte, um die Genauigkeit von Leistungs-, Spannungs- und Strommessungen zu verbessern.

Es unterstützt zwei Hauptmodi für die Referenzmessung:
1.  **🔬 Professioneller Modus:** Nutzt ein Fluke 45 Multimeter via RS232 als hochpräzise Referenz.
2.  **🏠 Heimanwender-Modus:** Nutzt ein bereits kalibriertes Tasmota-Gerät als "Master-Referenz" via HTTP.

---

## ✨ Hauptmerkmale

*   **🗺️ Geführter Kalibrierprozess:** Die Benutzeroberfläche führt Sie durch jeden Schritt, von der Gerätekonfiguration bis zur Anwendung der finalen Kalibrierung.
*   **🔌 Duale Referenz-Unterstützung:** Wählen Sie zwischen einem professionellen Multimeter (Fluke 45) oder einem bereits kalibrierten Tasmota-Stecker.
*   **📊 Fortgeschrittene mathematische Analyse:** Verwendet lineare Regression (`numpy`), um den genauesten `PowerCal`-Wert über den gesamten Messbereich zu berechnen. Extremwerte (Min/Max) werden automatisch gefiltert.
*   **🤝 Interaktive Entscheidungsfindung:** Vor dem Anwenden sehen Sie einen detaillierten Bericht und können zwischen regressionsbasiertem `PowerCal` (empfohlen) oder Mittelwert wählen.
*   **💾 Automatisierte Protokollierung:** Detaillierte `.csv`-Rohdaten und ein umfassendes `.txt`-Protokoll werden für jeden Lauf gespeichert.
*   **📈 Sicherheit & Stabilität:** Automatisches Ausschalten des Prüflings bei Abbruch, Sperrung der Eingabefelder während der Messung und robuster Umgang mit instabilen Netzwerkdaten.
*   **🌐 In Kürze:** Automatische Sprachumschaltung zwischen Deutsch und Englisch basierend auf den Systemeinstellungen oder manueller Wahl.

---

## 📘 Bedienungsanleitung (DE)

### Detailliertes Inhaltsverzeichnis
1. [⚙️ Vorbereitung & Installation](#1-vorbereitung--installation)
    * [Option A: Vorkompilierte EXE](#option-a-vorkompilierte-version-empfohlen-für-anwender)
    * [Option B: Aus dem Quellcode](#option-b-aus-dem-quellcode-für-entwickler)
    * [📄 Konfiguration (config.ini)](#konfiguration-der-configini)
2. [🖼️ Die Benutzeroberfläche im Detail](#2-die-benutzeroberfläche-im-detail)
    * [⌨️ Eingabe und Konfiguration](#eingabe-und-konfiguration-1)
    * [📺 Echtzeit-Anzeigen](#echtzeit-anzeigen-1)
    * [📉 Live-Diagramme](#live-diagramme-1)
3. [🚀 Durchführung einer Kalibrierung](#3-durchführung-einer-kalibrierung-schritt-für-schritt)
    * [🔐 Online-Check & Authentifizierung](#31-online-check--authentifizierung)
    * [🎯 Wahl der Referenz](#32-referenz-auswahl)
    * [⏱️ Der Messvorgang](#33-der-messvorgang)
    * [🔒 Sicherheitsfunktionen](#34-sicherheitsfunktionen)
4. [🏁 Auswertung & Anwendung](#4-auswertung--anwendung)
    * [📋 Den Report verstehen](#41-den-bericht-verstehen)
    * [📤 Kalibrierung anwenden](#42-kalibrierung-anwenden)
    * [🔄 Verwendung bestehender Daten](#43-verwendung-bestehender-daten-re-apply)

---

### 1. ⚙️ Vorbereitung & Installation

#### Option A: Vorkompilierte Version (Empfohlen für Anwender)
Laden Sie einfach die neueste `TasmotaCalibrator.exe` aus den [Releases](https://github.com/Suitcasechild/AutoCal/releases) herunter. Keine Python-Installation nötig.

#### Option B: Aus dem Quellcode (Für Entwickler)
1.  **Repository klonen:** `git clone https://github.com/Suitcasechild/AutoCal.git`.
2.  **Abhängigkeiten installieren:** `pip install -r requirements.txt`.
3.  **Starten:** `python gui_main.py`.

#### 📄 Konfiguration der config.ini
In der `config.ini` können Sie Standard-Pfade für Reports sowie COM-Ports für das Fluke 45 fest hinterlegen. Die Anwendung erstellt nun automatisch eine Standarddatei, falls diese fehlt.

---

### 2. 🖼️ Die Benutzeroberfläche im Detail

#### ⌨️ Eingabe und Konfiguration
Im oberen Bereich wählen Sie Ihre Referenzquelle (PRO, HOME oder Manuell) und geben die IP des Prüflings (DUT) ein. Hier legen Sie auch die Messparameter fest: **Stufen** (Anzahl der Lastpunkte) und **Messwerte pro Stufe** (Anzahl der Stichproben pro Punkt).

#### 📺 Echtzeit-Anzeigen
Der mittlere Bereich informiert Sie live über den Status beider Geräte.
*   **📱 Prüfling-Info:** Zeigt Hostnamen, MAC-Adresse und Firmware-Version sowie die aktuellen Sensorwerte für Spannung, Strom und Leistung an.
*   **📑 Referenz-Info:** 
    *   Im **PRO-Modus** spiegeln große LCD-Anzeigen das Display des Fluke 45 wider.
    *   Im **HOME-Modus** sehen Sie einen dedizierten Bereich mit der Identität und den Live-Werten der Referenz-Dose zum direkten Vergleich.

#### 📉 Live-Diagramme
Auf der rechten Seite befinden sich drei hochperformante Diagramme (`pyqtgraph`). Diese zeichnen simultan die **Soll- (Referenz)** und **Ist-Werte (Prüfling)** auf, sodass Sie Abweichungen und die Stabilisierung der Werte sofort visuell beurteilen können.

---

### 3. 🚀 Durchführung einer Kalibrierung (Schritt-für-Schritt)

#### 3.1 🔐 Online-Check & Authentifizierung
Geben Sie die IP ein und klicken Sie auf `🌐`. Falls das Gerät ein Passwort hat, öffnet sich ein Dialog. Diese Daten werden nur temporär im Speicher gehalten.

#### 3.2 🎯 Referenz-Auswahl
*   **🔬 PRO:** Verbinden Sie das Fluke 45 via RS232. Über das Menü **Setup -> Fluke 45** stellen Sie den COM-Port ein.
*   **🏠 HOME:** Nutzen Sie eine bereits kalibrierte Steckdose. Über das Menü **Setup -> Tasmota** konfigurieren Sie die IP der Referenz. Das Programm ermittelt vorab automatisch den Eigenverbrauch des Prüflings und zieht diesen als Offset ab.

#### 3.3 ⏱️ Der Messvorgang
Klicken Sie auf **"Kalibrierung Starten"**:
1.  **Stabilisierung:** Ein 7-sekündiger Filter sorgt nach dem Einschalten dafür, dass der Einschaltstrom abgeklungen ist.
2.  **Datenerfassung:** Es werden mehrere Messungen durchgeführt. Min/Max-Ausreißer werden automatisch entfernt, um Rauschen zu eliminieren.
3.  **Stufenwechsel:** Zwischen den Stufen wird der Prüfling ausgeschaltet, damit Sie die Last sicher wechseln können.

#### 3.4 🔒 Sicherheitsfunktionen
*   **🚫 Eingabesperre (UI-Locking):** Während der Messung werden alle Steuerelemente (Frames und Setup-Menüs) deaktiviert, um Fehlbedienungen zu vermeiden.
*   **🔌 Abbruch-Sicherheit:** Beim Klick auf "Messung abbrechen" wird sofort ein `Power OFF` an den Prüfling gesendet.

---

### 4. 🏁 Auswertung & Anwendung

#### 4.1 📋 Den Bericht verstehen
Nach der Messung zeigt ein Dialog das Protokoll mit allen Abweichungen. Für `PowerCal` gibt es zwei Optionen:
*   **📈 Regression (Empfohlen):** Nutzt mathematische Steigungsanalyse für höchste Präzision über den gesamten Bereich.
*   **🧮 Mittelwert:** Einfacher Durchschnitt der Abweichungen.

#### 4.2 📤 Kalibrierung anwenden
Klicken Sie auf **"KALIBRIEREN"**. Das Programm sendet die Werte, verifiziert den Schreibvorgang und ergänzt das Protokoll um einen "As Found / As Left"-Block als Nachweis für den Erfolg.

#### 4.3 🔄 Verwendung bestehender Daten (Re-Apply)
Findet das Programm alte Reports, können Sie die Messung überspringen und direkt die letzten guten Kalibrierwerte erneut an die Dose senden.

---

## 💻 Technischer Überblick

*   **Sprache:** Python 3.12+
*   **GUI:** PySide6 (Qt)
*   **Echtzeit-Diagramme:** pyqtgraph
*   **Kommunikation:** `pyserial` (Fluke 45) & `httpx` (Tasmota API)
*   **Datenverarbeitung:** `pandas` & `numpy`
