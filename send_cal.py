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
    
    # HINWEIS: Diese Funktion ist redundant zu `get_current_cal_factors` in `reference_manager.py`.
    # Sollte in Zukunft refaktorisiert werden.

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
            # English: Access the value by key, which is more robust.
            # Deutsch: Greife über den Schlüssel auf den Wert zu, das ist robuster.
            val = r.json().get(cmd)
            if val is not None:
                factors[cmd] = val
        return factors
    except Exception as e:
        # English: Print an error if reading the factors fails.
        # Deutsch: Gib einen Fehler aus, wenn das Lesen der Faktoren fehlschlägt.
        print(_("Fehler beim Lesen der Faktoren: {e}").format(e=e))
        return None

def apply_calibration(ip, new_v=None, new_a=None, new_w=None, auth=None):
    """
    # English:
    # Sends the final calibration data to the device. Supports selective calibration:
    # If a parameter is None, it is not changed.
    # Deutsch:
    # Sendet die finalen Kalibrierdaten an das Gerät. Unterstützt selektive Kalibrierung:
    # Wenn ein Parameter None ist, wird dieser nicht geändert.

    :param ip: (str) The IP address of the target device.
    :param new_v: (int, optional) New VoltageCal value.
    :param new_a: (int, optional) New CurrentCal value.
    :param new_w: (int, optional) New PowerCal value.
    :param auth: (tuple, optional) HTTP Auth tuple.
    :return: (str or None) Formatted report string or None on error.
    """
    print(_("\n--- STATUS VOR DER ÜBERTRAGUNG ---"))
    as_found = get_current_factors(ip, auth=auth)
    if not as_found:
        print(_("Fehler: Konnte bestehende Faktoren nicht lesen."))
        return None 

    # English: Build the command chain only for provided values.
    # Deutsch: Baue die Befehlskette nur für die bereitgestellten Werte auf.
    cmds = []
    if new_v is not None: cmds.append(f"VoltageCal {new_v}")
    if new_a is not None: cmds.append(f"CurrentCal {new_a}")
    if new_w is not None: cmds.append(f"PowerCal {new_w}")

    if not cmds:
        print(_("Info: Keine Kalibrierwerte zum Senden ausgewählt."))
        return _("Keine Änderungen vorgenommen.\n")

    print(_("Sende neue Werte an {ip}...").format(ip=ip))
    try:
        cmd_chain = "; ".join(cmds)
        httpx.get(f"http://{ip}/cm?cmnd=Backlog%20{cmd_chain}", timeout=5, auth=auth)
        time.sleep(2)

        print(_("\n--- VERIFIZIERUNG ---"))
        as_left = get_current_factors(ip, auth=auth)
        if not as_left:
            print(_("Fehler: Konnte neue Faktoren nach dem Senden nicht verifizieren."))
            return None

        ts = time.strftime("%H:%M:%S")
        report_lines = ["\n" + "="*85 + "\n"]
        report_lines.append(_("[{ts}] SELEKTIVE ÜBERTRAGUNG DER KALIBRIERWERTE\n").format(ts=ts))
        
        success = True
        if new_v is not None:
            ok = (as_left['VoltageCal'] == new_v)
            report_lines.append(_("[{ts}] VoltageCal: {as_found_vcal} -> {new_v} | {status}\n").format(ts=ts, as_found_vcal=as_found['VoltageCal'], new_v=new_v, status='[OK]' if ok else '[FEHLER]'))
            if not ok: success = False
        
        if new_a is not None:
            ok = (as_left['CurrentCal'] == new_a)
            report_lines.append(_("[{ts}] CurrentCal: {as_found_acal} -> {new_a} | {status}\n").format(ts=ts, as_found_acal=as_found['CurrentCal'], new_a=new_a, status='[OK]' if ok else '[FEHLER]'))
            if not ok: success = False

        if new_w is not None:
            ok = (as_left['PowerCal'] == new_w)
            report_lines.append(_("[{ts}] PowerCal:   {as_found_wcal} -> {new_w} | {status}\n").format(ts=ts, as_found_wcal=as_found['PowerCal'], new_w=new_w, status='[OK]' if ok else '[FEHLER]'))
            if not ok: success = False

        status_text = _("ERFOLGREICH") if success else _("TEILWEISE FEHLGESCHLAGEN")
        report_lines.append(_("[{ts}] Gesamtstatus: {status_text}\n").format(ts=ts, status_text=status_text))
        report_lines.append("="*85 + "\n")
        
        return "".join(report_lines)
        
    except Exception as e:
        print(_("Fehler bei der Übertragung: {e}").format(e=e))
        return None