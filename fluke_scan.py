# -*- coding: utf-8 -*-
"""
# English: Logic for automatically searching for a Fluke 45 multimeter on all serial ports.
# Deutsch: Logik zur automatischen Suche nach einem Fluke 45 Multimeter an allen seriellen Schnittstellen.
"""
import serial
import serial.tools.list_ports
import time

def find_fluke(current_port=None, current_baud=None, progress_callback=None):
    """
    # English:
    # Scans all available serial ports and baud rates for a Fluke 45 multimeter.
    # Deutsch:
    # Scannt alle verfügbaren seriellen Ports und Baudraten nach einem Fluke 45 Multimeter.

    :param current_port: (str, optional) The port currently in config (tested first).
    :param current_baud: (int/str, optional) The baudrate currently in config (tested first).
    :param progress_callback: (callable, optional) Function called with progress percentage (0-100).
    :return: (dict or None) A dictionary with 'port' and 'baud' if found, else None.
    """
    baudrates = [9600, 4800, 2400, 1200, 600, 300]
    ports = [p.device for p in serial.tools.list_ports.comports()]
    
    # English: Total steps for progress calculation.
    # Deutsch: Gesamtzahl der Schritte für die Fortschrittsberechnung.
    total_steps = len(ports) * len(baudrates)
    if total_steps == 0:
        return None
    
    current_step = 0

    # --- Priority Check (Current Config) ---
    # --- Prioritäts-Check (Aktuelle Konfiguration) ---
    if current_port and current_port in ports:
        ports.remove(current_port)
        ports.insert(0, current_port)
        
    for port in ports:
        search_bauds = list(baudrates)
        if port == current_port and current_baud:
            try:
                cb = int(current_baud)
                if cb in search_bauds:
                    search_bauds.remove(cb)
                    search_bauds.insert(0, cb)
            except:
                pass

        for baud in search_bauds:
            current_step += 1
            if progress_callback:
                progress_callback(int((current_step / total_steps) * 100))
            
            ser = None
            try:
                # English: Attempt to open the serial port with a short timeout.
                # Deutsch: Versuche den seriellen Port mit einem kurzen Timeout zu öffnen.
                ser = serial.Serial(port, baud, timeout=1.0)
                
                # English: Clear buffers to ensure a clean start.
                # Deutsch: Puffer leeren, um einen sauberen Start zu gewährleisten.
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                
                # English: Send the identification query.
                # Deutsch: Sende die Identifikations-Abfrage.
                ser.write(b"*IDN?\r")
                
                # English: Wait long enough for slow baud rates (600/300).
                # Deutsch: Warte lange genug für langsame Baudraten (600/300).
                time.sleep(1.5)
                
                # English: Read response and check for "FLUKE".
                # Deutsch: Lese Antwort und prüfe auf "FLUKE".
                resp = ser.read_all().decode('utf-8', errors='replace').strip()
                
                if ser: ser.close()
                
                if "FLUKE" in resp.upper():
                    return {"port": port, "baud": str(baud), "info": resp}
            except:
                if ser: 
                    try: ser.close()
                    except: pass
                continue
                
    return None

if __name__ == "__main__":
    # English: Test run if script is executed directly.
    # Deutsch: Testlauf, wenn das Skript direkt ausgeführt wird.
    print("--- FLUKE 45 AUTO-SCAN DEBUG ---")
    available_ports = [p.device for p in serial.tools.list_ports.comports()]
    print(f"Verfügbare Ports: {available_ports}")
    
    def pc(p): 
        print(f"Fortschritt: {p}%", end="\r")
        
    result = find_fluke(progress_callback=pc)
    if result:
        print(f"\n[GEFUNDEN] Fluke 45 auf {result['port']} mit {result['baud']} Baud.")
        print(f"Identifikation: {result['info']}")
    else:
        print("\n[FEHLER] Kein Gerät gefunden. Bitte Kabel und Strom prüfen.")
