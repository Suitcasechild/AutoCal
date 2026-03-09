# 📘 User Manual: Tasmota Precision Calibrator

Welcome to the **Tasmota Precision Calibrator**. This tool has been developed to elevate the calibration of Tasmota energy measurement devices to a professional level.

---

<a name="index"></a>
## 📌 Table of Contents
*   [🔬 1. Technical Background: Why "Cal" Commands?](#ch1)
    *   [1.1 The Advantage Over Set Commands](#ch1_1)
    *   [1.2 Measurement Uncertainty and Timing](#ch1_2)
*   [🔌 2. Hardware Preparation & Measurement Setup](#ch2)
    *   [2.1 Physical Measurement Setup (IMPORTANT!)](#ch2_1)
    *   [2.2 Fluke 45 Settings](#ch2_2)
*   [🖥️ 3. Menu Reference & Functions](#ch3)
    *   [3.1 Menu: File](#ch3_1)
    *   [3.2 Menu: Setup](#ch3_2)
    *   [3.3 Menu: Help](#ch3_3)
*   [📂 4. The Report Directory & Measurement Data](#ch4)
    *   [4.1 Folder Structure (MAC-based)](#ch4_1)
    *   [4.2 File Types and Contents](#ch4_2)
    *   [4.3 Using Existing Measurement Data](#ch4_3)
*   [🚀 5. The Calibration Process (Step by Step)](#ch5)
    *   [5.1 🛠️ Preparation & Initialization](#ch5_1)
    *   [5.2 ▶️ Start of the Measurement Sequence](#ch5_2)
    *   [5.3 🔄 Determination of Self-Consumption](#ch5_3)
    *   [5.4 📉 Measurement Under Load](#ch5_4)
    *   [5.5 ✅ Analysis and Finalization](#ch5_5)
*   [🛠️ 6. Troubleshooting & Expert Tips](#ch6)

---

<a name="ch1"></a>
## 🔬 1. Technical Background: Why "Cal" Commands?

In Tasmota, there are two ways to calibrate: `Set` commands (e.g., `VoltSet`) and `Cal` commands (e.g., `VoltageCal`). This program exclusively uses the `Cal` commands.

<a name="ch1_1"></a>
### 1.1 The Advantage Over Set Commands
With the traditional method using `Set` commands, the user must read a value and enter it manually. During this time span, the mains voltage or the load may have already changed slightly, leading to an inaccurate calibration.

<a name="ch1_2"></a>
### 1.2 Measurement Uncertainty and Timing
*   **⚖️ Statistical Certainty:** The software captures many data points (e.g., 30 measurements) simultaneously from the reference and the device under test (DUT).
*   **📈 Regression:** Instead of a simple point calibration, a linear regression is performed. This mathematically compensates for fluctuations in the power grid and drastically minimizes measurement uncertainty.
*   **⏱️ Time Advantage:** Since the software queries the values automatically, the risk of error due to human reading or typing errors is eliminated.

---

<a name="ch2"></a>
## 🔌 2. Hardware Preparation & Measurement Setup

<a name="ch2_1"></a>
### 2.1 Physical Measurement Setup (IMPORTANT!)
The correct setup differs depending on which reference device you are using.

#### **A) Setup with Tasmota Reference Socket (HOME Mode)**
In this mode, the reference socket also measures the self-consumption of the DUT, which is later automatically subtracted.
1.  **🏠 Wall Socket:** Power source.
2.  **📏 Reference Socket:** Your already calibrated Tasmota socket.
3.  **🔌 Device Under Test (DUT):** The Tasmota socket to be newly calibrated.
4.  **💡 Load:** A stable consumer (e.g., incandescent bulb).

#### **B) Setup with Fluke 45 (PRO Mode)**
Here, the Fluke is connected directly behind the DUT with a measurement adapter to precisely capture its output values.
1.  **🏠 Wall Socket:** Power source.
2.  **🔌 Device Under Test (DUT):** The Tasmota socket to be calibrated.
3.  **📏 Fluke 45:** Connection via measurement adapter (between DUT and load).
4.  **💡 Load:** A stable consumer (e.g., incandescent bulb).

⚠️ **Important Note:** In both cases, ensure that **connecting cables are as short as possible** between the DUT and the measuring device/adapter to minimize measurement errors due to cable losses.

💡 **Tip:** Do not use switching power supplies or motors as a load, as these provide unstable values. A resistive load (filament) is ideal.

<a name="ch2_2"></a>
### 2.2 Fluke 45 Settings
*   Connect the device to the PC via RS232.
*   **Menu Operation on the Device:** 
    *   Press the **"2nd"** and **"RATE"** (BAUD) buttons sequentially to enter the setup menu.
    *   Use the **arrow keys** (next to the display) to change the values.
    *   Confirm each setting with the **"AUTO"** button.
*   **Important: Turn off PRINT mode:**
    *   Press **"2nd"** and **"MIN MAX"** (ADDR) sequentially.
    *   Set the value under "PRINT" to **"0"** (Off) using the **arrow keys**.
    *   Confirm with **"AUTO"**.
*   **Optimal Parameters:**
    *   **Baud Rate:** 9600 (recommended)
    *   **Parity:** None
    *   **Echo:** Off
*   **Automation:** The program automatically sets the device to dual-display mode (Primary Display: **VAC**, Secondary Display: **AAC**).

---

<a name="ch3"></a>
## 🖥️ 3. Menu Reference & Functions

<a name="ch3_1"></a>
### 3.1 📁 Menu: File
*   **💾 Save Log:** Saves the entire text history of the log window in a `.txt` file for later error analysis.
*   **📂 Open Report Folder:** Opens Windows Explorer directly in the root directory of your measurement reports.
*   **❌ Exit:** Closes the program. Ongoing measurements will be canceled.

<a name="ch3_2"></a>
### 3.2 ⚙️ Menu: Setup
*   **🌐 General:** 
    *   **Report Path:** Define where the logs are stored.
    *   **Language:** The language setting (`language = auto`) is created in `config.ini` on the first start. It can be manually changed to `de` or `en` there.
    *   **Tolerance Limits (abs%):** Here you can define from which deviation (in percent) the software should recommend a calibration for voltage, current, and power.
*   **📟 Fluke 45:** Configure the RS232 interface (including "Find Fluke").
*   **🔌 Tasmota Reference:** Enter the IP address of the reference socket.

<a name="ch3_3"></a>
### 3.3 ❓ Menu: Help
*   **📘 Manual:** Opens this document. The window is non-modal, so you can work in the GUI in parallel.
*   **ℹ️ License & Info:** Shows the current software version (e.g., v5.4.2) and information about the developer.

---

<a name="ch4"></a>
## 📂 4. The Report Directory & Measurement Data

<a name="ch4_1"></a>
### 4.1 Folder Structure (MAC-based)
To avoid confusion, the software creates a separate subfolder for each Tasmota socket named after its unique **MAC address** (e.g., `Reports/2C-BC-BB.../`).

<a name="ch4_2"></a>
### 4.2 File Types and Contents
In each device folder, you will find:
*   **📊 CSV Files (`..._Stufe_1.csv`):** Tabular measurement values for every single second. Ideal for your own evaluation in Excel.
*   **📄 Protocols (`..._Protokoll.txt`):** The summary report. It contains the calculated factors and documents the "As-Found" (Before) and "As-Left" (After) state.

<a name="ch4_3"></a>
### 4.3 Using Existing Measurement Data
If you start a calibration for a device for which data already exists, the software asks if you want to use it. This saves time if you only want to generate a new report or re-apply the values without setting up the hardware again.

---

<a name="ch5"></a>
## 🚀 5. The Calibration Process (Step by Step)

This section serves as exact instructions for the operator. Please follow the steps in the order given.

<a name="ch5_1"></a>
### 5.1 🛠️ Preparation & Initialization
1.  **⌨️ Action:** Enter the **IP address of the device under test (DUT)** in the main window.
2.  **🌐 Action:** Click on **"Online Check"**.
    *   *Background:* The software checks accessibility, reads the MAC address, and automatically creates the appropriate subfolder in the Reports folder. Device info (version, name, MAC) is displayed in the right panel.
    *   *Note on Credentials:* If the device is password-protected, the query appears here. The data is saved for the entire session and does not need to be re-entered at the start of calibration.
3.  **🖱️ Action:** Select the **Reference Source** (Fluke 45 or Tasmota Reference).
    *   *Background:* This determines the communication path (RS232 or HTTP) through which the comparison values are obtained.
4.  **⚙️ Action:** Set the **Measurement Parameters** (Steps & Measurements per Step).
    *   **🏠 HOME Mode:** The number of measurement steps is fixed at **1** and disabled. A single step with approx. 30 measurements is the standard here for maximum precision.
    *   **🔬 PRO Mode:** Here you can select multiple steps (e.g., for recording a characteristic curve). 
    *   *Recommendation (PRO):* 3 steps with 25 measurements usually provide an excellent ratio between time expenditure and precision.

<a name="ch5_2"></a>
### 5.2 ▶️ Start of the Measurement Sequence
1.  **🖱️ Action:** Click the **"Start Calibration"** button.
    *   *Background:* The software now locks all input fields in the main menu to prevent misconfigurations during the measurement. If the device is password-protected, the password query now appears automatically.

<a name="ch5_3"></a>
### 5.3 🔄 Determination of Self-Consumption (Offset Measurement) — [Tasmota Reference Only]
*Note: This step is automatically skipped for Fluke 45.*
1.  **🔌 Action:** Wait for the DUT to switch off automatically.
    *   *Background:* If you use a **Tasmota reference socket**, the program **automatically switches OFF** the relay of the device under test (DUT). Since the reference socket is plugged in before the DUT, it also measures its self-consumption (electronics/WLAN). This "offset" is mathematically subtracted from the later reference values to evaluate only the pure load at the output.
2.  **⏳ Action:** Do not touch the setup during the 5-second stabilization phase.

<a name="ch5_4"></a>
### 5.4 📉 Measurement Under Load
1.  **📢 Action:** A popup window appears: **"Please switch on the target socket now!"**. Now switch on the DUT via the web interface or the button on the device.
2.  **📊 Action:** Observe the **live graphs** and the **progress bar**.
    *   *Background:* The software waits 7 seconds (inrush filter) after switching on until the current flow has stabilized. Only then does the recording of data points begin.
    *   *Progress:* A new bar below the measurement parameters shows you in real-time how many of the required measurements for the current step have already been completed.
    *   *Background:* Every second, a data pair (Reference & DUT) is queried. Invalid values (0-values due to network errors) are automatically detected, discarded, and the measurement is repeated until the required number is reached.

<a name="ch5_5"></a>
### 5.5 ✅ Analysis and Finalization
1.  **📋 Action:** After completion of the last step, the **"Calibration Protocol & Selection"** window opens automatically.
2.  **🔍 Action:** Check the colored info labels in the lower area.
    *   *Background:* The software compares the new values with the factors currently stored in the device.
    *   🟢 **Green:** The deviation is within tolerance (Standard: V/A < 0.5%, W < 5.0%). Calibration is optional. The checkbox is automatically deactivated.
    *   🟠 **Orange:** The deviation is too high. Calibration is strongly recommended. The checkbox is automatically activated.
3.  **☑️ Action:** Manually adjust the selection via the checkboxes if necessary.
    *   *Note:* You can select `VoltageCal`, `CurrentCal`, and `PowerCal` individually.
    *   **🏠 HOME Mode:** To simplify operation, only the relevant power option (**PowerCal**) is displayed. The regression analysis and the graph are hidden here.
    *   **🔬 PRO Mode:** You have the choice between **Mean** and **Regression**. You can visually check the measurement curve via the **"📊 REGRESSION GRAPH"** button. Both at the same time is not possible.
4.  **📤 Action:** Click the **"Calibrate Selection"** button.
    *   *Background:* Only the marked factors are sent to the DUT. The software verifies the transmission immediately ("As-Left" check) and documents the result in the log.

---

<a name="ch6"></a>
## 🛠️ 6. Troubleshooting & Expert Tips

*   **❌ Problem:** "No serial response from Fluke"
    *   **Solution:** Check cables or run "Find Fluke" in setup again. Often it's due to a wrong COM port.
*   **⚠️ Problem:** "HTTP 401 Unauthorized"
    *   **Solution:** The device is password-protected. Enter the data in the popup that appears. "admin" is already preset as the default user.
*   **🔐 Tip on Credentials:** The app saves entered passwords securely in memory until the program is closed. Use the **"Online Check"** before the measurement to store the credentials once. This allows the actual calibration process to run through without interruption by popups.
*   **🌡️ Tip for Experts:** Let the measurement setup "warm up" for approx. 5 minutes. Electronic components drift slightly until they reach their operating temperature. Calibration in a warm state is more precise.
*   **🛡️ IMPORTANT: Flash Protection (SaveData 0):** 
    *   **Background:** To protect the flash memory of the Tasmota device from excessive write cycles, this program sets the device to `SaveData 0` permanently **only when performing dynamic calibration (expert feature)**. During standard calibration (PRO/HOME), the storage behavior remains unaffected.
    *   **Impact:** When dynamic calibration is active, all calibration values are held only in volatile memory (RAM). While these are not lost upon reboot (as they were sent at the start of measurement), **manual changes** to the device (WiFi data, name, timers) are not permanently saved in this mode.
    *   **Making Manual Changes:** If you wish to save settings permanently, enter `SaveData 1` in the Tasmota console, make your changes, and then set it back to `SaveData 0` for protection.

---
[🏠 Back to Index](#index)
