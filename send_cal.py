import httpx
import time
import os

def get_current_factors(ip):
    factors = {}
    commands = ["VoltageCal", "CurrentCal", "PowerCal"]
    try:
        for cmd in commands:
            r = httpx.get(f"http://{ip}/cm?cmnd={cmd}", timeout=3)
            val = list(r.json().values())[0]
            factors[cmd] = val
        return factors
    except Exception as e:
        print(f"Fehler beim Lesen der Faktoren: {e}")
        return None

def apply_calibration(ip, new_v, new_a, new_w):
    """Sendet die finalen Kalibrierdaten und gibt einen 'As Found'/'As Left' String zurück."""
    print("\n--- STATUS VOR DER ÜBERTRAGUNG ---")
    as_found = get_current_factors(ip)
    if not as_found:
        print("Fehler: Konnte bestehende Faktoren nicht lesen.")
        return None 

    # Senden der neuen Werte
    print(f"Sende neue Werte an {ip}...")
    try:
        cmd_chain = f"VoltageCal {new_v}; CurrentCal {new_a}; PowerCal {new_w}"
        httpx.get(f"http://{ip}/cm?cmnd=Backlog%20{cmd_chain}", timeout=5)
        time.sleep(2)

        print("\n--- VERIFIZIERUNG ---")
        as_left = get_current_factors(ip)
        
        if not as_left:
            print("Fehler: Konnte neue Faktoren nach dem Senden nicht verifizieren.")
            return None

        ts = time.strftime("%H:%M:%S")
        report_lines = []
        report_lines.append("\n" + "="*85 + "\n")
        report_lines.append(f"[{ts}] ÜBERTRAGUNG DER KALIBRIERWERTE ZUR DOSE\n")
        report_lines.append(f"[{ts}] Gesendete Werte:    VCal {new_v} | ACal {new_a} | WCal {new_w}\n")
        report_lines.append(f"[{ts}] As Found (Vorher):  VCal {as_found['VoltageCal']} | ACal {as_found['CurrentCal']} | WCal {as_found['PowerCal']}\n")
        report_lines.append(f"[{ts}] As Left  (Nachher): VCal {as_left['VoltageCal']} | ACal {as_left['CurrentCal']} | WCal {as_left['PowerCal']}\n")
        
        success = (as_left['VoltageCal'] == new_v and as_left['CurrentCal'] == new_a and as_left['PowerCal'] == new_w)
        status_text = "ERFOLGREICH" if success else "FEHLGESCHLAGEN"
        report_lines.append(f"[{ts}] Status der Übertragung: {status_text}\n")
        report_lines.append("="*85 + "\n")

        print(f"  VoltageCal: {as_left['VoltageCal']} {'[OK]' if as_left['VoltageCal'] == new_v else '[ERR]'}")
        print(f"  CurrentCal: {as_left['CurrentCal']} {'[OK]' if as_left['CurrentCal'] == new_a else '[ERR]'}")
        print(f"  PowerCal:   {as_left['PowerCal']}   {'[OK]' if as_left['PowerCal'] == new_w else '[ERR]'}")
        
        return "\n".join(report_lines)
        
    except Exception as e:
        print(f"Fehler bei der Übertragung: {e}")
        return None