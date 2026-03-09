# 🚀 Documentation: Dynamic Power Calibration (Tasmota Rules)

This document describes the functionality, mathematical logic, and safety mechanisms of the dynamic **Power Calibration** for Tasmota devices.

---

## 📋 Table of Contents
1. [Introduction & Objectives](#1-introduction--objectives)
2. [The Problem with Static Power Calibration](#2-the-problem-with-static-power-calibration)
3. [Functionality of Dynamic Regulation](#3-functionality-of-dynamic-regulation)
    - 3.1 [Calculation of Switching Points (Current Thresholds)](#31-calculation-of-switching-points-current-thresholds)
    - 3.2 [Why Current (A) as Trigger Source?](#32-why-current-a-as-trigger-source)
    - 3.3 [Hysteresis Logic (Anti-Flicker)](#33-hysteresis-logic-anti-flicker)
4. [Anatomy of the Tasmota Rule (Practical Example)](#4-anatomy-of-the-tasmota-rule-practical-example)
    - 4.1 [Example Table (Program View)](#41-example-table-program-view)
    - 4.2 [The Generated Rule String](#42-the-generated-rule-string)
    - 4.3 [Rule Mode 5 (Once Mode)](#43-rule-mode-5-once-mode)
5. [Continuous Operation with SaveData 0](#5-continuous-operation-with-savedata-0)
    - 5.1 [Why SaveData 0? (Flash Protection)](#51-why-savedata-0-flash-protection)
    - 5.2 [Manual Changes on the Device](#52-manual-changes-on-the-device)
6. [Impact on Energy Measurement (Counter Readings)](#6-impact-on-energy-measurement-counter-readings)
7. [IMPORTANT: Summary & Safety](#7-important-summary--safety)
8. [Workflow and Traceability](#8-workflow-and-traceability)

---

## 1. 💡 Introduction & Objectives
Dynamic **Power Calibration** is an expert feature that drastically increases the measurement accuracy of active power (`Power`) across the entire load range. Instead of using a single, fixed calibration value (`PowerCal`), this system utilizes Tasmota's internal rules to adjust the **PowerCal value** in real-time based on the flowing current.

## 2. ⚠️ The Problem with Static Power Calibration
Power measurement sensors often do not operate linearly. A device that is perfectly **Power-calibrated** at high load (e.g., 2000W) often shows significant deviations at low loads. A static value is therefore always just a compromise.

## 3. ⚙️ Functionality of Dynamic Regulation

### 3.1 Calculation of Switching Points (Current Thresholds)
To create smooth transitions between measurement stages, the system calculates the midpoint between two adjacent measurement points.
*   **Example:** 
    - Stage 1 measured at **1.0A**
    - Stage 2 measured at **4.0A**
    - **Switching Point:** (1.0 + 4.0) / 2 = **2.5A**

### 3.2 Why Current (A) as Trigger Source?
Switching of the **Power Calibration** occurs exclusively based on the **current measurement values (Energy#Current)**.
*   **Stability:** The current value is linear for most sensors across the entire range and independent of the power correction being performed.
*   **No Circular Reference:** Since we are currently correcting the power (`Power`), using it as a trigger would lead to unstable states.

### 3.3 Hysteresis Logic (Anti-Flicker)
To prevent the system from constantly jumping between values at a switching point, a **hysteresis** (default: 0.15A) is applied.
*   **Switching Up:** Occurs exactly at the current switching point (e.g., 2.50A).
*   **Switching Down:** Occurs only when the current falls below the switching point minus the hysteresis (e.g., 2.50A - 0.15A = 2.35A).

## 4. 🔍 Anatomy of the Tasmota Rule (Practical Example)

### 4.1 Example Table (Program View)
Assuming three measurement stages were performed (hysteresis 0.15A):

| Current (A) [Reference] | PowerCal [Proposal] | Range (A) [Validity] |
| :--- | :--- | :--- |
| 0.894 A | **9576** | 0.000 - 2.587 A |
| 4.280 A | **9413** | 2.437 - 6.623 A |
| 8.966 A | **9361** | 6.473 - 10.000 A |

*   **Threshold 1 (2.587A):** Midpoint between 0.894A and 4.280A.
*   **Threshold 2 (6.623A):** Midpoint between 4.280A and 8.966A.

### 4.2 The Generated Rule String
The resulting command for Tasmota is:

`Rule1 ON Energy#Current>0 DO PowerCal 9576 ENDON ON Energy#Current>2.587 DO PowerCal 9413 ENDON ON Energy#Current>6.623 DO PowerCal 9361 ENDON ON Energy#Current<6.473 DO PowerCal 9413 ENDON ON Energy#Current<2.437 DO PowerCal 9576 ENDON`

*   `Energy#Current>X.XXX`: Switches up when load increases.
*   `Energy#Current<X.XXX`: Switches back down (hysteresis) when load decreases.

### 4.3 Rule Mode 5 (Once Mode)
By using the command `Rule1 5`, the "Once Mode" is activated. A trigger is only executed when the state changes from "False" to "True". This prevents redundant commands during every second's measurement.

## 5. 🛡️ Continuous Operation with SaveData 0

### 5.1 Why SaveData 0? (Flash Protection)
Hardware memory (Flash) has limited write cycles. Since the rule changes the **PowerCal value** with every load change, the memory would be quickly destroyed without protection.
*   **AutoCal sets the device to `SaveData 0` permanently**.
*   Changes occur only in **RAM (Working Memory)**. The Flash remains protected.

### 5.2 Manual Changes on the Device
**ATTENTION:** In `SaveData 0` mode, manual changes (WiFi, timers, name) are lost after a reboot!
1.  Command: Enter `SaveData 1` in the console.
2.  Perform changes.
3.  **IMPORTANT:** Enter `SaveData 0` again afterwards.

## 6. <span style="color:red">⚡ Impact on Energy Measurement (Counter Readings)</span>
A consequence of `SaveData 0` mode affects the energy counters of the socket (`Total`, `Today`, `Yesterday`).

1.  **Storage Location:** Tasmota manages counter readings in the same area as system settings.
2.  **Behavior during Operation:** Wh continue to be counted and displayed correctly in RAM.
3.  **Behavior upon Reboot:** Without "burning" them into the Flash, the data accumulated since the last save process will be lost.
4.  **Necessity:** Without `SaveData 0`, every rule action would physically destroy the Flash memory.

## 7. <span style="color:red">🛑 IMPORTANT: Summary & Safety</span>

*   **The Compromise:** Highest precision of **Power Calibration** requires waiving automatic continuous storage of counter readings in the device.
*   **Data Backup:** Use external systems (Home Assistant, MQTT) for seamless statistics.
*   **Manual Changes:** Mandatory manual switching to `SaveData 1` and back to `0`.
*   **Flash Protection:** **Never** set the device to `SaveData 1` as long as a dynamic rule is active that changes values frequently!

## 8. 📝 Workflow and Traceability
The entire process is recorded for audit purposes and appended to the end of the original `Protokoll.txt`.

---
*Documentation created on March 03, 2026, for the AutoCal project.*
