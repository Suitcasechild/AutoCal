# Tasmota Precision Calibrator

*99% AI-Generated: A journey from zero Python knowledge to a fully functional PyQt application using solely prompt-driven development.*

A GUI-based tool for high-precision calibration and validation of Tasmota-based energy monitoring devices (like smart plugs). This application automates the process of measuring, calculating, and applying new calibration values to enhance the accuracy of power, voltage, and current readings.

It supports two main modes for reference measurements:
1.  **Professional Mode:** Uses a Fluke 45 multimeter via RS232 as the high-precision reference.
2.  **Home User Mode:** Uses a previously calibrated Tasmota device as a "master" reference via HTTP.

---

## Table of Contents
1. [The Vibecoding Experiment](#-the-vibecoding-experiment-95-ai-generated)
2. [Key Features](#key-features)
3. [User Guide](#user-guide)
4. [Technical Stack](#technical-stack)

---

## 🚀 The Vibecoding Experiment: 95% AI-Generated

*Welcome behind the scenes! This project is not just a piece of software, but the result of a fascinating experiment in modern application development.*

**The code in this repository was 95% created exclusively through prompts in the Gemini CLI.** And the most exciting part? The entire project was started from the perspective of an absolute beginner – **without any prior knowledge of Python or setting up development environments.** The goal was to find out if it's possible to build a functioning application simply by "feeling" the logic (vibecoding) and cleverly communicating with an AI.

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

## Key Features

* **Guided Calibration Process:** The UI walks you through every step, from device setup to applying the final calibration.
* **Dual Reference Support:** Choose between a professional multimeter (Fluke 45) or a consumer-grade, pre-calibrated Tasmota plug.
* **Advanced Mathematical Analysis:** Utilizes linear regression (`numpy`) to calculate the most accurate `PowerCal` value across the entire measurement range, enhancing linearity. `VoltageCal` and `CurrentCal` are calculated based on the mean deviation.
* **Interactive Decision Making:** Before applying any changes, the tool presents a detailed report. You can choose whether to apply the new values and even select between the regression-based `PowerCal` (recommended) or a simpler mean-based value.
* **Automated Reporting:** For every calibration run, detailed `.csv` files with raw measurement data and a comprehensive `.txt` protocol are generated and stored.
* **Non-Blocking UI:** Live data is displayed using `pyqtgraph`, and all communication (HTTP and Serial) runs in a background thread (`QThread`) to keep the UI responsive.
* **Pre-Measurement Checks:** Automatically verifies device settings (`SetOption21`, resolution) and allows re-applying calibration from previous reports without new measurements.

---