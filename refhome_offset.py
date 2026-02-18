import time
import httpx

def ermittle_offset(ref_ip):
    """
    Ermittelt den Eigenverbrauch der DUT-Dose an der Referenz-Dose.
    Wird aufgerufen, während die DUT-Dose noch ausgeschaltet ist.
    """
    print(f"\n--- Schritt: Offset ermitteln (Eigenverbrauch DUT) ---")
    strom_werte = []
    leistung_werte = []
    
    for i in range(1, 6):
        try:
            r = httpx.get(f"http://{ref_ip}/cm?cmnd=Status%208", timeout=2)
            d = r.json()['StatusSNS']['ENERGY']
            a = float(d['Current'])
            w = float(d['Power'])
            strom_werte.append(a)
            leistung_werte.append(w)
            print(f"  Messung {i}/5: {w:.2f}W | {a:.3f}A")
        except Exception as e:
            print(f"  Fehler bei Offset-Messung {i}: {e}")
        time.sleep(1)
        
    avg_a = sum(strom_werte) / len(strom_werte) if strom_werte else 0.0
    avg_w = sum(leistung_werte) / len(leistung_werte) if leistung_werte else 0.0
    
    print(f"[OK] Offset bestimmt: {avg_w:.2f}W / {avg_a:.3f}A")
    print(f"     Diese Werte werden von allen Referenz-Messungen abgezogen.\n")
    return avg_a, avg_w