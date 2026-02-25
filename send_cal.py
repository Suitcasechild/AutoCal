import httpx
import time
import os

def get_current_factors(ip, auth=None):
    # English: Reads the current calibration factors from the Tasmota device.
    # Deutsch: Liest die aktuellen Kalibrierfaktoren vom Tasmota-Gerät.
    factors = {}
    commands = ["VoltageCal", "CurrentCal", "PowerCal"]
    try:
        for cmd in commands:
            r = httpx.get(f"http://{ip}/cm", params={"cmnd": cmd}, timeout=3, auth=auth)
            r.raise_for_status()
            val = list(r.json().values())[0]
            factors[cmd] = val
        return factors
    except Exception as e:
        print(f"Fehler beim Lesen der Faktoren: {e}")
        return None

def apply_calibration(ip, new_v, new_a, new_w, auth=None):
    """
    # English: Sends the final calibration data and returns an 'As Found'/'As Left' string.
    # Deutsch: Sendet die finalen Kalibrierdaten und gibt einen 'As Found'/'As Left' String zurück.
    """
    print("\n--- STATUS VOR DER ÜBERTRAGUNG ---")
    as_found = get_current_factors(ip, auth=auth)
    if not as_found:
        print("Fehler: Konnte bestehende Faktoren nicht lesen.")
        return None 

    # English: Build the command chain only for provided values.
    # Deutsch: Baue die Befehlskette nur für die angegebenen Werte auf.
    commands = []
    if new_v is not None: commands.append(f"VoltageCal {new_v}")
    if new_a is not None: commands.append(f"CurrentCal {new_a}")
    if new_w is not None: commands.append(f"PowerCal {new_w}")

    if not commands:
        print("Keine Werte zum Senden vorhanden.")
        return None

    # Senden der neuen Werte
    print(f"Sende neue Werte an {ip}...")
    try:
        cmd_chain = "; ".join(commands)
        r = httpx.get(f"http://{ip}/cm", params={"cmnd": f"Backlog {cmd_chain}"}, timeout=5, auth=auth)
        r.raise_for_status()
        time.sleep(2)

        print("\n--- VERIFIZIERUNG ---")
        as_left = get_current_factors(ip, auth=auth)
        
        if not as_left:
            print("Fehler: Konnte neue Faktoren nach dem Senden nicht verifizieren.")
            return None

        ts = time.strftime("%H:%M:%S")
        report_lines = []
        report_lines.append("\n" + "="*85 + "\n")
        report_lines.append(f"[{ts}] ÜBERTRAGUNG DER KALIBRIERWERTE ZUR DOSE\n")
        report_lines.append(f"[{ts}] Gesendete Werte:    " + " | ".join(commands) + "\n")
        report_lines.append(f"[{ts}] As Found (Vorher):  VCal {as_found['VoltageCal']} | ACal {as_found['CurrentCal']} | WCal {as_found['PowerCal']}\n")
        report_lines.append(f"[{ts}] As Left  (Nachher): VCal {as_left['VoltageCal']} | ACal {as_left['CurrentCal']} | WCal {as_left['PowerCal']}\n")
        
        # English: Check if all requested values were set correctly.
        # Deutsch: Prüfen, ob alle angeforderten Werte korrekt gesetzt wurden.
        success = True
        if new_v is not None and as_left['VoltageCal'] != new_v: success = False
        if new_a is not None and as_left['CurrentCal'] != new_a: success = False
        if new_w is not None and as_left['PowerCal'] != new_w: success = False

        status_text = "ERFOLGREICH" if success else "FEHLGESCHLAGEN"
        report_lines.append(f"[{ts}] Status der Übertragung: {status_text}\n")
        report_lines.append("="*85 + "\n")

        if new_v is not None: print(f"  VoltageCal: {as_left['VoltageCal']} {'[OK]' if as_left['VoltageCal'] == new_v else '[ERR]'}")
        if new_a is not None: print(f"  CurrentCal: {as_left['CurrentCal']} {'[OK]' if as_left['CurrentCal'] == new_a else '[ERR]'}")
        if new_w is not None: print(f"  PowerCal:   {as_left['PowerCal']}   {'[OK]' if as_left['PowerCal'] == new_w else '[ERR]'}")
        
        return "\n".join(report_lines)
        
    except Exception as e:
        print(f"Fehler bei der Übertragung: {e}")
        return None