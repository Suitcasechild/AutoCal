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
    
    # English: Take 5 readings to get a stable average.
    # Deutsch: Nimm 5 Messungen auf, um einen stabilen Mittelwert zu erhalten.
    for i in range(1, 6):
        try:
            # English: Request sensor/energy data from the reference device.
            # Deutsch: Fordere Sensor-/Energiedaten vom Referenzgerät an.
            r = httpx.get(f"http://{ref_ip}/cm?cmnd=Status%208", timeout=2, auth=auth)
            d = r.json()['StatusSNS']['ENERGY']
            a = float(d['Current'])
            w = float(d['Power'])
            strom_werte.append(a)
            leistung_werte.append(w)
            print(f"  Messung {i}/5: {w:.2f}W | {a:.3f}A")
        except Exception as e:
            print(f"  Fehler bei Offset-Messung {i}: {e}")
        time.sleep(1)
        
    # English: Calculate the average of the collected values.
    # Deutsch: Berechne den Mittelwert der gesammelten Werte.
    avg_a = sum(strom_werte) / len(strom_werte) if strom_werte else 0.0
    avg_w = sum(leistung_werte) / len(leistung_werte) if leistung_werte else 0.0
    
    print(f"[OK] Offset bestimmt: {avg_w:.2f}W / {avg_a:.3f}A")
    print(f"     Diese Werte werden von allen Referenz-Messungen abgezogen.\n")
    return avg_a, avg_w