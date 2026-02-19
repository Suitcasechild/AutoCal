# -*- coding: utf-8 -*-
"""
# English:
# This script serves as the command-line entry point for the Tasmota Precision Calibrator.
# It allows running the calibration process interactively from the terminal without the GUI.
# Note: This script is maintained separately from the GUI and may have a simplified feature set.
#
# Deutsch:
# Dieses Skript dient als Kommandozeilen-Einstiegspunkt für den Tasmota Precision Calibrator.
# Es ermöglicht, den Kalibrierprozess interaktiv vom Terminal aus ohne die GUI zu starten.
# Hinweis: Dieses Skript wird getrennt von der GUI gewartet und hat möglicherweise einen vereinfachten Funktionsumfang.
"""
import time
import httpx
import os
import sys
import glob
import pandas as pd
from config_manager import ConfigManager
from reference_manager import ReferenceManager
from calibration_engine import CalibrationEngine

# --- Helper Functions / Hilfsfunktionen ---

def prepare_dut(target_ip, auth=None):
    """
    # English: Prepares the Device Under Test by setting necessary Tasmota options.
    # Deutsch: Bereitet den Prüfling (DUT) vor, indem notwendige Tasmota-Optionen gesetzt werden.
    """
    print(f"Bereite Ziel-Dose vor (Auflösung & Optionen)...")
    # English: Set resolution for voltage, power, current and enable SetOption21 for better measurements.
    # Deutsch: Setze die Auflösung für Spannung, Leistung, Strom und aktiviere SetOption21 für bessere Messungen.
    cmds = "VoltRes 2;WattRes 2;AmpRes 3;SetOption21 1"
    try:
        httpx.get(f"http://{target_ip}/cm?cmnd=Backlog%20{cmds}", timeout=5, auth=auth)
        return True
    except: 
        return False

def check_device_availability(ip, name, auth=None):
    """
    # English: Checks if a device is online by sending a status command.
    # Deutsch: Prüft, ob ein Gerät online ist, indem ein Status-Befehl gesendet wird.
    """
    print(f"Prüfe Erreichbarkeit: {name} ({ip})...")
    try:
        httpx.get(f"http://{ip}/cm?cmnd=Status", timeout=3.0, auth=auth)
        print(f"[OK] {name} ist online!")
        return True
    except:
        print(f"[FEHLER] {name} ({ip}) offline!")
        return False

def wait_for_power_on(target_ip, auth=None):
    """
    # English: Waits until the target device reports its power status as 'ON'.
    # Deutsch: Wartet, bis das Zielgerät seinen Stromstatus als 'ON' meldet.
    """
    print(f"Warte auf 'Power ON' an Ziel-Dose ({target_ip})...")
    while True:
        try:
            r = httpx.get(f"http://{target_ip}/cm?cmnd=Status%2011", timeout=2, auth=auth)
            if r.json()['StatusSTS']['POWER'] == "ON":
                print("Power ON erkannt! Inrush-Filter (7 Sek)...")
                time.sleep(7)
                return True
        except: 
            pass
        time.sleep(1)

def perform_measurement(target_ip, rm, device_path, step, duration, ts, auth=None):
    """
    # English: Performs the measurement for a single step, collecting data for a specific duration.
    # Deutsch: Führt die Messung für eine einzelne Stufe durch und sammelt Daten für eine bestimmte Dauer.
    """
    results = []
    start = time.time()
    print(f"Starte Messung Stufe {step} ({duration}s)...")
    while (time.time() - start) < duration:
        rv, ra, rw = rm.get_reference_data() # Assumes reference device does not need auth here
        try:
            rt_res = httpx.get(f"http://{target_ip}/cm?cmnd=Status%208", timeout=2, auth=auth).json()
            rt = rt_res['StatusSNS']['ENERGY']
            tv, ta, tw = float(rt['Voltage']), float(rt['Current']), float(rt['Power'])
            if rv is not None:
                results.append({
                    "Ref_Volt": rv, "Ref_Amp": ra, "Ref_Watt": rw, 
                    "Target_Volt": tv, "Target_Amp": ta, "Target_Watt": tw
                })
                print(f"[{int(time.time()-start):>3}s] Ref: {rw:.2f}W | DUT: {tw:.2f}W", end="\r")
        except: 
            pass
    if not results:
        print("\n[FEHLER] Keine Daten gesammelt!")
        return None
    
    # English: Save the collected data to a CSV file.
    # Deutsch: Speichere die gesammelten Daten in einer CSV-Datei.
    csv_path = os.path.join(device_path, f"{ts}_Stufe_{step}.csv")
    pd.DataFrame(results).to_csv(csv_path, index=False)
    return csv_path

if __name__ == "__main__":
    # English: Initialize managers for configuration and reference device.
    # Deutsch: Initialisiere Manager für Konfiguration und Referenzgerät.
    cm = ConfigManager()
    rm = ReferenceManager(cm.config)
    target_ip = cm.config['TARGET']['ip_address']
    
    print("=== TASMOTA PRECISION CALIBRATOR v4.0 (CLI) ===")
    print("1: Professionell (Fluke 45 via RS232)")
    print("2: Heimanwender (Referenz-Dose via HTTP)")
    choice = input("Auswahl: ")

    if choice == "1":
        cal_method_text = "Professionell (Fluke 45 via RS232)"
        if not rm.set_mode('PRO'): 
            sys.exit(1)
    else:
        cal_method_text = "Heimanwender (Referenz-Dose via HTTP)"
        rm.set_mode('HOME')
        # Note: This CLI version does not yet support authentication for the reference device.
        if not check_device_availability(cm.config['REFERENCE_HOME']['ip_address'], "Referenz"): 
            sys.exit(1)
    
    # --- Check for existing data ---
    # --- Prüfung auf bestehende Daten ---
    device_path = cm.setup_device_directory()
    engine = CalibrationEngine(device_path)
    existing_csvs = glob.glob(os.path.join(device_path, "*_Stufe_*.csv"))
    
    use_existing = False
    data_ts = time.strftime("%Y%m%d_%H%M%S") # Default for new measurement
    report_ts = data_ts

    if existing_csvs:
        latest_csv = max(existing_csvs, key=os.path.getctime)
        last_session_ts = os.path.basename(latest_csv).split('_Stufe_')[0]
        print(f"\n[INFO] Vorhandene Messdaten gefunden ({last_session_ts}).")
        print("Möchten Sie neue Daten aufzeichnen oder das letzte Protokoll neu generieren?")
        print("1: NEUE Messung starten")
        print("2: VORHANDENE Daten nutzen")
        choice_data = input("Auswahl [1/2]: ")
        
        if choice_data == "2":
            use_existing = True
            data_ts = last_session_ts
            report_ts = time.strftime("%Y%m%d_%H%M%S") # Timestamp of confirmation
            print(f"[OK] Nutze Daten von {data_ts} für neuen Report {report_ts}")
            
            # --- Read and reuse method from old protocol ---
            # --- Lese und übernehme alte Methode aus Protokoll ---
            old_report_path = os.path.join(device_path, f"{data_ts}_Protokoll.txt")
            if os.path.exists(old_report_path):
                try:
                    with open(old_report_path, "r") as f:
                        for line in f:
                            if line.startswith("Methode:"):
                                cal_method_text = line.split(":", 1)[1].strip()
                                break
                except:
                    pass

    # Note: This CLI version does not yet support authentication for the DUT.
    if not check_device_availability(target_ip, "Ziel-Dose"): 
        sys.exit(1)
    prepare_dut(target_ip)
    old_cal = rm.get_current_cal_factors(target_ip)
    all_results = []

    if not use_existing:
        # --- OFFSET MEASUREMENT ---
        if rm.mode == 'HOME':
            from refhome_offset import ermittle_offset
            print("\n--- SCHRITT: Eigenverbrauch (Offset) ermitteln ---")
            print("WICHTIG: Das Zielgerät (DUT) muss eingesteckt, aber AUSGESCHALTET sein.")
            input("Drücke ENTER, wenn das DUT ausgeschaltet ist, um den Offset zu messen...")
            
            # Note: This CLI version does not yet support authentication for the reference device.
            off_a, off_w = ermittle_offset(cm.config['REFERENCE_HOME']['ip_address'])
            rm.set_home_offset(off_a, off_w)
            
            print(f"\n[OK] Offset von {off_w:.2f}W / {off_a:.3f}A wird von der Referenz abgezogen.")

        # --- MEASUREMENT LOOP ---
        steps = int(cm.config['TARGET']['measurement_steps'])
        duration = int(cm.config['TARGET']['duration_per_step'])
        for s in range(1, steps + 1):
            print(f"\n--- LASTSTUFE {s} von {steps} ---")
            if wait_for_power_on(target_ip):
                csv = perform_measurement(target_ip, rm, device_path, s, duration, data_ts)
                if csv:
                    res = engine.calculate_new_calibration(csv, old_cal)
                    res['Stufe'] = s
                    all_results.append(res)
                print(f"\nStufe {s} fertig. Sicherheits-Abschaltung...")
                httpx.get(f"http://{target_ip}/cm?cmnd=Power%20OFF", timeout=2)
                if s < steps: 
                    print("Bereit für nächste Laststufe. Bitte DUT einschalten...")
    else:
        # --- Process existing data ---
        steps_files = sorted(glob.glob(os.path.join(device_path, f"{data_ts}_Stufe_*.csv")))
        for i, csv_file in enumerate(steps_files, 1):
            res = engine.calculate_new_calibration(csv_file, old_cal)
            res['Stufe'] = i
            all_results.append(res)

    # --- FINAL REPORT ---
    if all_results:
        report_file = engine.write_summary(all_results, data_ts, report_ts=report_ts, cal_mode=cal_method_text, old_cal=old_cal)
        print("\n" + "="*40)
        print("ERMITTLUNG DER KALIBRIERWERTE ABGESCHLOSSEN")
        print("="*40)

    # --- APPLY CALIBRATION ---
    confirm = input("\nSollen die neuen Kalibrierwerte jetzt an die Ziel-Dose übertragen werden? (j/n): ").lower()
    if confirm == 'j':
        print("\nStarte Übertragung...")
        from send_cal import apply_calibration
        # Note: This CLI version does not yet support authentication for applying calibration.
        # It relies on the now-outdated signature of apply_calibration.
        # This will fail if the device requires authentication.
        apply_calibration(target_ip, all_results, report_file)
    else:
        print("\nÜbertragung abgebrochen. Die Werte wurden nur im Protokoll gespeichert.")    
    
    rm.close()
    print("\n--- PROZESS ABGESCHLOSSEN ---")