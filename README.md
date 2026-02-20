# Tasmota Precision Calibrator

*99% AI-Generated: A journey from zero Python knowledge to a fully functional PyQt application using solely prompt-driven development.*

([Deutsche Beschreibung unten](#tasmota-precision-calibrator-de))

---

## Table of Contents
1. [The Vibecoding Experiment](#-the-vibecoding-experiment-99-ai-generated)
2. [Key Features](#key-features)
3. [User Guide](#user-guide)
4. [Technical Stack](#technical-stack)

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

A GUI-based tool for high-precision calibration and validation of Tasmota-based energy monitoring devices (like smart plugs). This application automates the process of measuring, calculating, and applying new calibration values to enhance the accuracy of power, voltage, and current readings.

It supports two main modes for reference measurements:
1.  **Professional Mode:** Uses a Fluke 45 multimeter via RS232 as the high-precision reference.
2.  **Home User Mode:** Uses a previously calibrated Tasmota device as a "master" reference via HTTP.

---

## Key Features

*   **Guided Calibration Process:** The UI walks you through every step, from device setup to applying the final calibration.
*   **Dual Reference Support:** Choose between a professional multimeter (Fluke 45) or a consumer-grade, pre-calibrated Tasmota plug.
*   **Advanced Mathematical Analysis:** Utilizes linear regression (`numpy`) to calculate the most accurate `PowerCal` value across the entire measurement range, enhancing linearity. `VoltageCal` and `CurrentCal` are calculated based on the mean deviation.
*   **Interactive Decision Making:** Before applying any changes, the tool presents a detailed report. You can choose whether to apply the new values and even select between the regression-based `PowerCal` (recommended) or a simpler mean-based value.
*   **Automated Reporting:** For every calibration run, detailed `.csv` files with raw measurement data and a comprehensive `.txt` protocol are generated and stored.
*   **Non-Blocking UI:** Live data is displayed using `pyqtgraph`, and all communication (HTTP and Serial) runs in a background thread (`QThread`) to keep the UI responsive.
*   **Pre-Measurement Checks:** Automatically verifies device settings (`SetOption21`, resolution) and allows re-applying calibration from previous reports without new measurements.

---

## User Guide

### 1. Preparation & Installation
**Option A: Pre-compiled Version (Recommended for Users)**

For users who do not want to install Python, a pre-compiled version (`.exe` for Windows) is available in the [Releases tab](https://github.com/Suitcasechild/AutoCal/releases). Simply download the latest `TasmotaCalibrator.exe` and run it.

**Option B: From Source Code (For Developers)**

1.  **Clone Repository:** Download the project to your computer, e.g., with `git clone https://github.com/Suitcasechild/AutoCal.git`.
2.  **Install Dependencies:** The project includes a `requirements.txt` file. Install all required libraries using the command:  
    `pip install -r requirements.txt`
3.  **Configuration (`config.ini`):** If necessary, adjust the `config.ini` file. Here you can set default IP addresses and the storage location for reports (`root_report_dir`).

### 2. The Main Window
*   **IP Address of DUT:** Enter the IP address of the Tasmota device you want to calibrate.
*   **Calibration Parameters:**
    *   **Steps:** The number of different load points you want to measure (e.g., 3 for 60W, 100W, 200W).
    *   **Measurements per Step:** The number of individual measurements per load step. More measurements (e.g., 15-30) lead to more stable average values.
*   **Reference Selection:** Choose your reference source.
    *   **PRO (Fluke 45):** For measurement with the multimeter.
    *   **HOME (Tasmota):** For measurement using another Tasmota device as a reference.
*   **Graphs & Log:** The graphs display live measurement data. The log window below documents the entire process flow and shows errors.

### 3. Performing a Calibration
1.  **Preparation:** Enter the DUT's IP and select your reference.
2.  **Online Check (Optional):** Click the `🌐` button to check if the device is reachable and to display its device data (Name, Version, MAC).
3.  **Start Measurement:** Click **"Start Calibration"**.
4.  **Handling Password Protection:** If one of your Tasmota devices (DUT or reference) is password-protected, a dialog will automatically appear. Enter the username and password. This data is only held in memory for the current session and is **never** saved. You have up to three attempts in case of a typo.
5.  **Follow Instructions:** The software will now prompt you to turn on the load for the first step. Do this and wait for the measurement for the step to complete.
6.  **Further Steps:** The software automatically turns off the load and prompts you to prepare and turn on the next load step. Repeat this for all configured steps.
7.  **Completion & Analysis:** After the last step, the **Report Dialog** will appear. Here you will see the complete analysis.
8.  **Apply Calibration:** In the report dialog, you have the choice:
    *   **CALIBRATE:** Click here to send the new values. You will be asked whether to use the `PowerCal` value from the regression (recommended) or the average value.
    *   **DO NOT CALIBRATE:** Closes the dialog without sending the new values. The reports are still saved.

### 4. Using Existing Data (Re-Apply)
*   If you start a calibration for a device for which data already exists, the software will ask if you want to perform a **"New Measurement"** or **"Use Old Report"**.
*   If you choose "Use Old Report," the measurement is skipped, and the report dialog is displayed directly with the values from the last calibration. This is useful if you just want to re-apply the values.

---

## Technical Stack

*   **Language:** Python 3.12+
*   **GUI:** PySide6
*   **Real-time Graphs:** pyqtgraph
*   **Communication:** `pyserial` (for Fluke 45) & `httpx` (for Tasmota)
*   **Data Handling:** `pandas` & `numpy`

---
---

# Tasmota Precision Calibrator (DE)

*99% KI-generiert: Eine Reise von Null Python-Wissen zu einer voll funktionsfähigen PyQt-Anwendung, ausschließlich durch Prompt-gesteuerte Entwicklung.*

---

## Inhaltsverzeichnis
1. [Das Vibecoding-Experiment](#-das-vibecoding-experiment-99-ki-generiert)
2. [Hauptmerkmale](#hauptmerkmale)
3. [Bedienungsanleitung](#bedienungsanleitung)
4. [Technischer Überblick](#technischer-überblick)

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

Ein GUI-basiertes Werkzeug zur hochpräzisen Kalibrierung und Validierung von Tasmota-basierten Energiemessgeräten (z.B. Smart Plugs). Die Anwendung automatisiert den Prozess des Messens, Berechnens und Anwendens neuer Kalibrierwerte, um die Genauigkeit von Leistungs-, Spannungs- und Strommessungen zu verbessern.

Es unterstützt zwei Hauptmodi für die Referenzmessung:
1.  **Professioneller Modus:** Nutzt ein Fluke 45 Multimeter via RS232 als hochpräzise Referenz.
2.  **Heimanwender-Modus:** Nutzt ein bereits kalibriertes Tasmota-Gerät als "Master-Referenz" via HTTP.

---

## Hauptmerkmale

*   **Geführter Kalibrierprozess:** Die Benutzeroberfläche führt Sie durch jeden Schritt, von der Gerätekonfiguration bis zur Anwendung der finalen Kalibrierung.
*   **Duale Referenz-Unterstützung:** Wählen Sie zwischen einem professionellen Multimeter (Fluke 45) oder einem bereits kalibrierten Tasmota-Stecker.
*   **Fortgeschrittene mathematische Analyse:** Verwendet lineare Regression (`numpy`), um den genauesten `PowerCal`-Wert über den gesamten Messbereich zu berechnen und die Linearität zu verbessern. `VoltageCal` und `CurrentCal` werden auf Basis der mittleren Abweichung berechnet.
*   **Interaktive Entscheidungsfindung:** Vor dem Anwenden von Änderungen zeigt das Tool einen detaillierten Bericht an. Sie können entscheiden, ob Sie die neuen Werte anwenden und sogar zwischen dem regressionsbasierten `PowerCal`-Wert (empfohlen) oder einem einfacheren Mittelwert wählen.
*   **Automatisierte Protokollierung:** Für jeden Kalibrierdurchlauf werden detaillierte `.csv`-Dateien mit Rohmessdaten und ein umfassendes `.txt`-Protokoll erstellt und gespeichert.
*   **Nicht-blockierende GUI:** Live-Daten werden mit `pyqtgraph` angezeigt, und die gesamte Kommunikation (HTTP und Seriell) läuft in einem Hintergrund-Thread (`QThread`), um die Oberfläche reaktionsfähig zu halten.
*   **Prüfung vor der Messung:** Überprüft automatisch Geräteeinstellungen (`SetOption21`, Auflösung) und ermöglicht das erneute Anwenden einer Kalibrierung aus alten Protokollen, ohne eine neue Messung durchführen zu müssen.

---

## Bedienungsanleitung

### 1. Vorbereitung & Installation
**Option A: Vorkompilierte Version (Empfohlen für Anwender)**

Für Benutzer, die Python nicht installieren möchten, steht im [Releases-Tab](https://github.com/Suitcasechild/AutoCal/releases) eine vorkompilierte Version (`.exe` für Windows) zur Verfügung. Laden Sie einfach die neueste `TasmotaCalibrator.exe` herunter und führen Sie sie aus.

**Option B: Aus dem Quellcode (Für Entwickler)**

1.  **Repository klonen:** Laden Sie das Projekt auf Ihren Computer herunter, z.B. mit `git clone https://github.com/Suitcasechild/AutoCal.git`.
2.  **Abhängigkeiten installieren:** Das Projekt enthält eine `requirements.txt`-Datei. Installieren Sie alle benötigten Bibliotheken mit dem Befehl:  
    `pip install -r requirements.txt`
3.  **Konfiguration (`config.ini`):** Passen Sie bei Bedarf die `config.ini`-Datei an. Hier können Sie Standard-IP-Adressen und den Speicherort für die Reports (`root_report_dir`) festlegen.

### 2. Das Hauptfenster
*   **IP-Adresse des Prüflings (DUT):** Geben Sie hier die IP-Adresse der Tasmota-Dose ein, die Sie kalibrieren möchten.
*   **Kalibrier-Parameter:**
    *   **Stufen:** Anzahl der verschiedenen Lastpunkte, die Sie messen möchten (z.B. 3 für 60W, 100W, 200W).
    *   **Messungen pro Stufe:** Anzahl der Einzelmessungen pro Laststufe. Mehr Messungen (z.B. 15-30) führen zu stabileren Mittelwerten.
*   **Referenz-Auswahl:** Wählen Sie Ihre Referenzquelle aus.
    *   **PRO (Fluke 45):** Für die Messung mit dem Multimeter.
    *   **HOME (Tasmota):** Für die Messung mit einer anderen Tasmota-Dose als Referenz.
*   **Graphen & Log:** Die Graphen zeigen Live-Messdaten an. Das Log-Fenster darunter dokumentiert den gesamten Prozessablauf und zeigt Fehler an.

### 3. Durchführung einer Kalibrierung
1.  **Vorbereitung:** Geben Sie die IP des Prüflings ein und wählen Sie Ihre Referenz.
2.  **Online Check (Optional):** Klicken Sie auf den `🌐`-Button, um zu prüfen, ob das Gerät erreichbar ist und um dessen Gerätedaten (Name, Version, MAC) anzuzeigen.
3.  **Messung starten:** Klicken Sie auf **"Kalibrierung Starten"**.
4.  **Umgang mit Passwortschutz:** Falls eines Ihrer Tasmota-Geräte (Prüfling oder Referenz) passwortgeschützt ist, erscheint automatisch ein Dialog. Geben Sie Benutzername und Passwort ein. Diese Daten werden nur für die aktuelle Sitzung im Speicher gehalten und **niemals** gespeichert. Bei Fehleingabe haben Sie bis zu drei Versuche.
5.  **Anweisungen folgen:** Die Software wird Sie nun auffordern, die Last für die erste Stufe einzuschalten. Tun Sie dies und warten Sie, bis die Messung für die Stufe abgeschlossen ist.
6.  **Weitere Stufen:** Die Software schaltet die Last automatisch ab und fordert Sie auf, die nächste Laststufe vorzubereiten und einzuschalten. Wiederholen Sie dies für alle konfigurierten Stufen.
7.  **Abschluss & Auswertung:** Nach der letzten Stufe erscheint der **Report-Dialog**. Hier sehen Sie die vollständige Auswertung.
8.  **Kalibrierung anwenden:** Im Report-Dialog haben Sie die Wahl:
    *   **KALIBRIEREN:** Klicken Sie hier, um die neuen Werte zu senden. Sie werden gefragt, ob der `PowerCal`-Wert aus der Regression (empfohlen) oder dem Mittelwert verwendet werden soll.
    *   **NICHT KALIBRIEREN:** Schließt den Dialog, ohne die neuen Werte zu senden. Die Protokolle werden trotzdem gespeichert.

### 4. Verwendung bestehender Daten (Re-Apply)
*   Wenn Sie eine Kalibrierung für ein Gerät starten, für das bereits Daten existieren, fragt die Software, ob Sie eine **"Neue Messung"** oder den **"Alten Report nutzen"** möchten.
*   Wenn Sie "Alten Report nutzen" wählen, wird die Messung übersprungen und direkt der Report-Dialog mit den Werten der letzten Kalibrierung angezeigt. Dies ist nützlich, wenn Sie die Werte lediglich erneut anwenden möchten.

---

## Technischer Überblick

*   **Sprache:** Python 3.12+
*   **GUI:** PySide6
*   **Echtzeit-Graphen:** pyqtgraph
*   **Kommunikation:** `pyserial` (für Fluke 45) & `httpx` (für Tasmota)
*   **Datenverarbeitung:** `pandas` & `numpy`
