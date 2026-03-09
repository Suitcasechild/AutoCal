# 🧠 Tasmota Knowledge for Dummies: Why "SaveData" Saves Your Device

> 💡 **IMPORTANT PRELIMINARY NOTE:** The following explanations regarding `SaveData 0` and "Auto-Save" are **ONLY** important if you are using **Dynamic Calibration** (via Rule). If you are performing a regular standard calibration (PRO or HOME mode), this topic is irrelevant for you and you don't need to worry about it!

This guide explains in simple terms what happens behind the scenes of your Tasmota device when you calibrate it, and why we need to use "tricks" like `SaveData 0` and "Auto-Save."

---

## 1. 💾 Your Device's Memory (RAM vs. Flash)

Imagine your Tasmota socket like a person with a notepad:

*   **Short-term Memory (RAM):** This is where the device remembers things happening right now (how much current is flowing?). It's lightning fast, but if you pull the plug, everything is forgotten.
*   **The Notepad (Flash Memory):** This is where important things are "written down" (WiFi password, device name, calibration values). If the power goes out, the device can simply read them again later.

### The Problem: The Notepad Wears Out!
The Flash memory (the notepad) is made of a kind of electronic paper. You can write on it, but after about 100,000 erasures and re-writes, the paper gets worn through and the device is **broken**.

---

## 2. ⚡ SaveData 1: The "Cautious" Mode (Standard)

Normally, Tasmota is set to `SaveData 1`.
*   **What Happens?** Every time you change a setting (e.g., rename the device), the device writes it immediately onto the notepad (Flash).
*   **Why is this good?** If the power fails, the device still knows everything after a restart.
*   **When is this bad?** When we change things very often – for example, every second.

---

## 3. 🛡️ SaveData 0: The "Protective Shield" (For Professionals)

When we use **Dynamic Calibration**, our program constantly calculates new values so that the measurement is always super accurate. This happens with every load change (e.g., when the refrigerator kicks in).

*   **The Risk:** If we left it at `SaveData 1`, the device would "wear through" the notepad within a few weeks and become electronic waste.
*   **The Solution:** We switch to `SaveData 0`. Now, the device keeps all changes **only in its head (RAM)** and does NOT write them on the notepad.
*   **The Benefit:** The notepad is protected. The device lives forever.

---

## 4. 📉 The Downside of SaveData 0

When the protective shield (`SaveData 0`) is on, there's a problem:
1.  **Counter Loss:** The device diligently counts your consumed watt-hours (Wh). But it only keeps this number in its head. If someone trips over the cable or a fuse blows, the number is gone. After a restart, your counter will be back to what it was before the power failure.
2.  **Settings are Lost:** If you rename the device or set a timer while `SaveData 0` is active, it won't be saved. After a restart, the device will have its old name again.

---

## 5. 🚀 The Rescue: "Auto-Save" (Rule2)

This is where our new trick comes in. We want the protection of `SaveData 0`, but not the danger of losing all counter readings.

**The solution is a small robot (a "Rule") that does the following:**
1.  It waits for 5 minutes.
2.  It briefly lowers the protective shield (`SaveData 1`).
3.  Tasmota notices this and immediately writes all current counter readings onto the notepad.
4.  The robot waits for 1 second (`Delay 10`).
5.  It immediately raises the protective shield again (`SaveData 0`).

**Why is this brilliant?**
*   In the worst case, you only lose the data from the last 5 minutes, not from weeks.
*   The device is only stressed once every 5 minutes instead of every second. The notepad (Flash) can easily handle this for 50 years.

---

## 📋 Summary: What You Need to Remember

| Mode | What Happens? | Benefits | Drawbacks |
| :--- | :--- | :--- | :--- |
| **SaveData 1** | Writes everything immediately to the chip. | Safe against power failure. | Chip breaks with constant changes. |
| **SaveData 0** | Keeps everything only in RAM. | Chip is protected (Longevity!). | Data loss during power failure. |
| **Auto-Save** | Briefly switches every 5 min. | Best safety + long life. | Requires a small Rule on the device. |

### How do I make manual changes now?
If you are in `SaveData 0` mode (due to dynamic calibration) and want to permanently change the device's name:
1.  Go to the Tasmota console.
2.  Type `SaveData 1` and press Enter.
3.  Change your name/WiFi/timer.
4.  Type `SaveData 0` and press Enter (to reactivate the protection).

---
*Created on March 09, 2026 – Keeping technology understandable for everyone.*
