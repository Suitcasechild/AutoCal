# -*- coding: utf-8 -*-
"""
# English: This module is responsible for sending the final calibration data to the Tasmota device.
# Deutsch: Dieses Modul ist dafür verantwortlich, die finalen Kalibrierdaten an das Tasmota-Gerät zu senden.
"""
import httpx
import time
import os

def get_current_factors(ip, auth=None):
    """
    # English: Reads the current calibration factors from a Tasmota device.
    # Deutsch: Liest die aktuellen Kalibrierfaktoren von einem Tasmota-Gerät aus.

    :param ip: (str) The IP address of the Tasmota device.
               (str) Die IP-Adresse des Tasmota-Geräts.
    :param auth: (tuple, optional) A tuple for HTTP Basic Auth (user, password).
                 (tuple, optional) Ein Tupel für HTTP Basic Auth (Benutzer, Passwort).
    :return: (dict or None) A dictionary with the current factors or None on error.
             (dict oder None) Ein Dictionary mit den aktuellen Faktoren oder None bei einem Fehler.
    """
    # English: Initialize an empty dictionary to store the factors.
    # Deutsch: Initialisiert ein leeres Dictionary zum Speichern der Faktoren.
    factors = {}
    commands = ["VoltageCal", "CurrentCal", "PowerCal"]
    try:
        # English: Iterate through the commands to query each factor.
        # Deutsch: Iteriere durch die Befehle, um jeden Faktor abzufragen.
        for cmd in commands:
            r = httpx.get(f"http://{ip}/cm?cmnd={cmd}", timeout=3, auth=auth)
            r.raise_for_status()
            val = list(r.json().values())[0]
            factors[cmd] = val
        return factors
    except Exception as e:
        # English: Print an error if reading the factors fails.
        # Deutsch: Gib einen Fehler aus, wenn das Lesen der Faktoren fehlschlägt.
        print(f"Fehler beim Lesen der Faktoren: {e}")
        return None

def apply_calibration(ip, new_v, new_a, new_w, auth=None):
    """
    # English:
    # Sends the final calibration data to the device and returns an 'As Found'/'As Left' report string.
    # It first reads the current values, then sends the new ones, and finally verifies the write operation.
    # Deutsch:
    # Sendet die finalen Kalibrierdaten an das Gerät und gibt einen 'As Found'/'As Left'-Protokollstring zurück.
    # Liest zuerst die aktuellen Werte, sendet dann die neuen und verifiziert abschließend den Schreibvorgang.

    :param ip: (str) The IP address of the target device.
               (str) Die IP-Adresse des Zielgeräts.
    :param new_v: (int) The new VoltageCal value.
                  (int) Der neue Wert für VoltageCal.
    :param new_a: (int) The new CurrentCal value.
                  (int) Der neue Wert für CurrentCal.
    :param new_w: (int) The new PowerCal value.
                  (int) Der neue Wert für PowerCal.
    :param auth: (tuple, optional) A tuple for HTTP Basic Auth (user, password).
                 (tuple, optional) Ein Tupel für HTTP Basic Auth (Benutzer, Passwort).
    :return: (str or None) A formatted string for the report or None on error.
             (str oder None) Ein formatierter String für das Protokoll oder None bei einem Fehler.
    """
    print("\n--- STATUS VOR DER ÜBERTRAGUNG ---")
    # English: Get the 'As Found' values before making changes.
    # Deutsch: Hole die 'As Found'-Werte (Zustand vorher), bevor Änderungen vorgenommen werden.
    as_found = get_current_factors(ip, auth=auth)
    if not as_found:
        print("Fehler: Konnte bestehende Faktoren nicht lesen.")
        return None 

    # English: Send the new values to the device using a Tasmota 'Backlog' command.
    # Deutsch: Sende die neuen Werte über einen Tasmota 'Backlog'-Befehl an das Gerät.
    print(f"Sende neue Werte an {ip}...")
    try:
        cmd_chain = f"VoltageCal {new_v}; CurrentCal {new_a}; PowerCal {new_w}"
        httpx.get(f"http://{ip}/cm?cmnd=Backlog%20{cmd_chain}", timeout=5, auth=auth)
        time.sleep(2)

        print("\n--- VERIFIZIERUNG ---")
        # English: Get the 'As Left' values after sending the new ones to verify.
        # Deutsch: Hole die 'As Left'-Werte (Zustand nachher) zur Verifizierung.
        as_left = get_current_factors(ip, auth=auth)
        
        if not as_left:
            print("Fehler: Konnte neue Faktoren nach dem Senden nicht verifizieren.")
            return None

        # English: Build the report string.
        # Deutsch: Baue den Protokoll-String zusammen.
        ts = time.strftime("%H:%M:%S")
        report_lines = []
        report_lines.append("\n" + "="*85 + "\n")
        report_lines.append(f"[{ts}] ÜBERTRAGUNG DER KALIBRIERWERTE ZUR DOSE\n")
        report_lines.append(f"[{ts}] Gesendete Werte:    VCal {new_v} | ACal {new_a} | WCal {new_w}\n")
        report_lines.append(f"[{ts}] As Found (Vorher):  VCal {as_found['VoltageCal']} | ACal {as_found['CurrentCal']} | WCal {as_found['PowerCal']}\n")
        report_lines.append(f"[{ts}] As Left  (Nachher): VCal {as_left['VoltageCal']} | ACal {as_left['CurrentCal']} | WCal {as_left['PowerCal']}\n")
        
        # English: Check if the values were applied successfully.
        # Deutsch: Prüfe, ob die Werte erfolgreich angewendet wurden.
        success = (as_left['VoltageCal'] == new_v and as_left['CurrentCal'] == new_a and as_left['PowerCal'] == new_w)
        status_text = "ERFOLGREICH" if success else "FEHLGESCHLAGEN"
        report_lines.append(f"[{ts}] Status der Übertragung: {status_text}\n")
        report_lines.append("="*85 + "\n")

        # English: Also print the verification status to the console.
        # Deutsch: Gib den Verifizierungs-Status auch in der Konsole aus.
        print(f"  VoltageCal: {as_left['VoltageCal']} {'[OK]' if as_left['VoltageCal'] == new_v else '[ERR]'}")
        print(f"  CurrentCal: {as_left['CurrentCal']} {'[OK]' if as_left['CurrentCal'] == new_a else '[ERR]'}")
        print(f"  PowerCal:   {as_left['PowerCal']}   {'[OK]' if as_left['PowerCal'] == new_w else '[ERR]'}")
        
        return "\n".join(report_lines)
        
    except Exception as e:
        print(f"Fehler bei der Übertragung: {e}")
        return None