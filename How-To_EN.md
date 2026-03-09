# 📖 How-To: Tasmota Calibration for Beginners
## *From zero to your own Master Reference Socket*

This document describes the way to high-precision calibration of your Tasmota devices, even if you **don't** have a professional multimeter (Fluke 45) and **no** pre-calibrated reference socket.

---

## 📋 Table of Contents
1. [The Concept: The "Bootstrapping" Strategy](#1-the-concept)
2. [Prerequisites & Hardware](#2-prerequisites)
3. [Step 1: Preparing the First Device (DUT)](#3-step-1)
4. [Step 2: Manual Calibration (The Foundation)](#4-step-2)
    - 4.1 [The Photo Method for Synchronization](#41-photo-method)
    - 4.2 [Entering Measurement Values](#42-entering)
5. [Step 3: Verification & Elevation to Master Socket](#5-step-3)
6. [Step 4: Scaling (Calibrating Further Devices)](#6-step-4)
7. [Important Tips for Maximum Precision](#7-tips)

---

<a name="1-the-concept"></a>
## 1. 💡 The Concept: The "Bootstrapping" Strategy
Since you have no reference, we will create one.
*   **Phase 1:** You take a Tasmota socket and calibrate it extremely carefully with a simple plug-in energy meter (manual method).
*   **Phase 2:** This socket is now your "Gold Standard" (Master Socket).
*   **Phase 3:** You simply plug all further sockets behind this Master Socket. The software compares both sockets automatically and calibrates the new socket in seconds (HOME mode).

---

<a name="2-prerequisites"></a>
## 2. 🔌 Prerequisites & Hardware
You will need:
1.  **The Device Under Test (DUT):** The Tasmota socket that needs to be calibrated.
2.  **A simple measuring device:** A commercially available plug-in energy meter.
3.  **Loads for Calibration & Testing:** Since the manual calibration in the app is optimized for a single load stage, you should have the following consumers ready:
    *   **Calibration Load (Ideal):** A fan heater or kettle with approx. **1200W**. This is the optimal operating point for the base calibration.
    *   **Test Loads (Verification):** An incandescent bulb (approx. **200W**) and a strong load (approx. **2500W**) to check how large the deviations are in the peripheral areas after calibration.
    *   **AVOID** LED lamps, PCs, or TVs (unstable switching power supplies).
4.  **Smartphone:** For the photo method.

---

<a name="3-step-1"></a>
## 3. 🛠️ Step 1: Preparing the First Device (DUT)
1.  Plug the simple measuring device into the wall socket.
2.  Plug the Tasmota socket (DUT) into the measuring device.
3.  Connect the load to the Tasmota socket.
4.  **IMPORTANT:** Switch on the load and let everything **warm up for 5 minutes** (stabilize component drift).
5.  Open the Tasmota Calibrator, enter the IP of the socket, and click **"Online Check"**.

---

<a name="4-step-2"></a>
## 4. 📉 Step 2: Manual Calibration (The Foundation)
Select **"Manual (Input)"** under Reference in the main menu.

💡 **Tip:** Use the integrated **Help Button** directly in the manual measurement capture window for a quick guide. You can also find detailed background info in the file `manual_info.md`.

<a name="41-photo-method"></a>
### 4.1 The Photo Method for Synchronization
Tasmota and your measuring device do not show values at exactly the same millisecond. To compensate for this offset:
1.  Click **"Start Calibration"** in the app. The app starts logging the internal values of the socket.
2.  Take your smartphone and take a **photo** showing both the display of your external measuring device and the monitor of your PC (with the running app).
3.  Repeat this for three different load states (if possible, e.g., Stage 1, Stage 2, and Stage 3).

<a name="42-entering"></a>
### 4.2 Entering Measurement Values
1.  After the app has finished the measurement, the input mask opens.
2.  Look at your photos. Find the timestamp in the app's list that was shown in the photo.
3.  Enter the values from the display of your measuring device (V, A, W) into the corresponding fields in the app.
4.  The app now calculates the optimal calibration factors using **linear regression**.
5.  Click **"Calibrate Selection"** to send the values to the socket.

---

<a name="5-step-3"></a>
## 5. ✅ Step 3: Verification & Elevation to Master Socket
After the socket has been calibrated:
1.  Check the values in the Tasmota web interface against your measuring device. Do they match?
2.  **Congratulations!** This socket is now your **Reference Socket**. Mark it (e.g., with a sticker "MASTER").

---

<a name="6-schritt-4"></a>
## 6. 🚀 Step 4: Scaling (Calibrating Further Devices)
From now on, it gets easy:
1.  Plug your **Master Socket** into the wall.
2.  Plug the **new socket (DUT)** into the Master Socket.
3.  Connect the load to the new socket.
4.  In the app, select **"Tasmota (HOME Mode)"** as Reference and enter the IP of the Master Socket.
5.  Click Start. The app handles the rest (self-consumption deduction, comparison, sending) automatically in about 60 seconds.

---

<a name="7-tipps"></a>
## 7. 💡 Important Tips for Maximum Precision
*   **Short Chain:** Do not use unnecessary extension cables between Master and DUT. Any contact resistance distorts the result.
*   **SaveData 0:** If you later use the **Dynamic Calibration** (expert feature), click the **Help Button** there in the dialog for deeper insights. Detailed technical information can be found in the file `manual_dynamic_cal.md`. Remember that manual changes to the socket (name, WiFi) are only saved if you briefly enter `SaveData 1` in the console beforehand.
*   **Stable Voltage:** Do not necessarily calibrate when the washing machine or oven is running in the house, as this can make the mains voltage unstable.

---
*Documentation created on March 09, 2026, for the AutoCal project.*
