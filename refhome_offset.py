# -*- coding: utf-8 -*-
"""
# English: This module calculates the power consumption offset of the device under test (DUT).
# Deutsch: Dieses Modul berechnet den Eigenverbrauchs-Offset des Prüflings (DUT).
"""
import time
import httpx

def ermittle_offset(ref_ip, auth=None):
    """
    # English:
    # Determines the idle power consumption (offset) of the DUT by measuring it at the reference device.
    # This is called while the DUT is plugged in but turned off.
    # It takes multiple readings and returns the average current and power.
    # Deutsch:
    # Ermittelt den Eigenverbrauch (Offset) der DUT-Dose durch Messung an der Referenz-Dose.
    # Wird aufgerufen, während die DUT-Dose eingesteckt, aber ausgeschaltet ist.
    # Nimmt mehrere Messwerte auf und gibt den durchschnittlichen Strom und die Leistung zurück.

    :param ref_ip: (str) The IP address of the reference Tasmota device.
                   (str) Die IP-Adresse des Referenz-Tasmota-Geräts.
    :param auth: (tuple, optional) A tuple for HTTP Basic Auth (user, password).
                 (tuple, optional) Ein Tupel für HTTP Basic Auth (Benutzer, Passwort).
    :return: (tuple) A tuple containing the average current (A) and average power (W) offset.
             (tuple) Ein Tupel mit dem durchschnittlichen Strom- (A) und Leistungs-Offset (W).
    """
    print(f"\n--- Schritt: Offset ermitteln (Eigenverbrauch DUT) ---")
    strom_werte = []
    leistung_werte = []
    
    # English: Aim for 5 valid readings to get a stable average.
    # Deutsch: Ziel sind 5 gültige Messungen für einen stabilen Mittelwert.
    desired_valid_readings = 5
    current_attempt = 0

    while len(strom_werte) < desired_valid_readings:
        current_attempt += 1
        try:
            # English: Request sensor/energy data from the reference device.
            # Deutsch: Fordere Sensor-/Energiedaten vom Referenzgerät an.
            r = httpx.get(f"http://{ref_ip}/cm?cmnd=Status%208", timeout=2, auth=auth)
            d = r.json()['StatusSNS']['ENERGY']
            a = float(d['Current'])
            w = float(d['Power'])

            # English: Check for zero values, which are considered invalid for offset.
            # Deutsch: Prüfe auf Nullwerte, die als ungültig für den Offset gelten.
            if a == 0.0 or w == 0.0:
                print(f"  [WARN] Messversuch {current_attempt}: Ungültige Offset-Messung (0-Wert). Wiederhole... ({len(strom_werte)}/{desired_valid_readings})")
            else:
                strom_werte.append(a)
                leistung_werte.append(w)
                print(f"  Messung {len(strom_werte)}/{desired_valid_readings}: {w:.2f}W | {a:.3f}A")
        except Exception as e:
            print(f"  [FEHLER] Messversuch {current_attempt}: {e}. Wiederhole...")
        time.sleep(1) # Wait for 1 second between attempts
        
    # English: Calculate the average of the collected values.
    # Deutsch: Berechne den Mittelwert der gesammelten Werte.
    avg_a = sum(strom_werte) / len(strom_werte) if strom_werte else 0.0
    avg_w = sum(leistung_werte) / len(leistung_werte) if leistung_werte else 0.0
    

    print(f"[OK] Offset bestimmt: {avg_w:.2f}W / {avg_a:.3f}A")
    print(f"     Diese Werte werden von allen Referenz-Messungen abgezogen.\n")
    return avg_a, avg_w