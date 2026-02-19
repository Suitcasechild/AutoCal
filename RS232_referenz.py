# -*- coding: utf-8 -*-
"""
# English:
# Standalone test script for communicating with a Fluke 45 multimeter via an RS232 (COM port) connection.
# This script initializes the device for AC voltage and current measurements and performs a series of readings.
# It is intended for testing and debugging purposes and is not directly used by the main GUI application.
#
# Deutsch:
# Eigenständiges Testskript für die Kommunikation mit einem Fluke 45 Multimeter über eine RS232 (COM-Port) Verbindung.
# Dieses Skript initialisiert das Gerät für Wechselspannungs- und Strommessungen und führt eine Reihe von Messungen durch.
# Es ist für Test- und Debugging-Zwecke gedacht und wird nicht direkt von der Haupt-GUI-Anwendung verwendet.
"""
import serial
import time

# --- CONFIGURATION ---
PORT = 'COM3' 
BAUD = 9600
# ---------------------

def format_val(s):
    """
    # English: Cleans the raw string from the multimeter and converts it to a float.
    # Deutsch: Säubert den Roh-String vom Multimeter und konvertiert ihn in einen Float.

    :param s: (str) The raw string part from the device, e.g., "=> 230.123".
              (str) Der rohe String-Teil vom Gerät, z.B. "=> 230.123".
    :return: (float) The cleaned float value, or 0.0 on error.
             (float) Der gesäuberte Float-Wert, oder 0.0 bei einem Fehler.
    """
    try:
        # English: Remove the prompt "=>" and any surrounding whitespace.
        # Deutsch: Entferne den Prompt "=>" und jeglichen umgebenden Leerraum.
        return float(s.replace("=>", "").strip())
    except:
        return 0.0

def run_10_measurements_fixed_range():
    """
    # English:
    # Initializes the Fluke 45, sets it to a fixed AC voltage range and dual-display AC current mode,
    # then performs 10 measurements and prints them to the console.
    # Deutsch:
    # Initialisiert das Fluke 45, versetzt es in einen festen Wechselspannungsbereich und den
    # Dual-Display-Modus für Wechselstrom, führt dann 10 Messungen durch und gibt sie in der Konsole aus.
    """
    try:
        # English: Open the serial port connection.
        # Deutsch: Öffne die serielle Port-Verbindung.
        ser = serial.Serial(PORT, BAUD, timeout=3)
        
        print("--- Initialisiere Gerät (VAC Fix-Range + AAC2) ---")
        # English: Reset the device to its default state.
        # Deutsch: Setze das Gerät auf seinen Standardzustand zurück.
        ser.write(b"*RST\r")
        time.sleep(1)
        
        # English: Set the primary display to AC Volts.
        # Deutsch: Setze die primäre Anzeige auf Wechselspannung (VAC).
        ser.write(b"VAC\r")
        time.sleep(0.5)
        
        # English: Set a fixed range of 300V (Range 4).
        # Deutsch: Setze einen festen Messbereich von 300V (Range 4).
        print("Setze Messbereich auf 300V (Fix)...")
        ser.write(b"RANGE 4\r")
        time.sleep(1)
        
        # English: Set the secondary display to AC Amps (this enables dual display).
        # Deutsch: Setze die sekundäre Anzeige auf Wechselstrom (AAC), was die Dual-Anzeige aktiviert.
        ser.write(b"AAC2\r")
        
        print("Warte 3s auf stabile Messung...")
        time.sleep(3)
        ser.reset_input_buffer() 

        print(f"{'Nr.':<5} | {'Spannung (V)':<12} | {'Strom (A)':<12}")
        print("-" * 40)

        # English: Loop to perform 10 measurements.
        # Deutsch: Schleife zur Durchführung von 10 Messungen.
        for i in range(1, 11):
            # English: Request the values from both displays.
            # Deutsch: Fordere die Werte beider Anzeigen an.
            ser.write(b"VAL?\r")
            
            time.sleep(1.5) 
            
            # English: Read all available data from the serial buffer.
            # Deutsch: Lese alle verfügbaren Daten aus dem seriellen Puffer.
            raw_data = ser.read_all().decode('utf-8', errors='replace').strip()
            
            if raw_data:
                # English: The device returns values separated by a comma.
                # Deutsch: Das Gerät gibt die Werte durch ein Komma getrennt zurück.
                parts = raw_data.split(",")
                
                if len(parts) >= 2:
                    v = format_val(parts[0])
                    a = format_val(parts[1])
                    print(f"{i:<5} | {v:<12.2f} | {a:<12.6f}")
                else:
                    # English: Print raw data if parsing fails.
                    # Deutsch: Gib die Rohdaten aus, wenn das Parsen fehlschlägt.
                    print(f"{i:<5} | Rohdaten: {repr(raw_data)}")
            
            # English: Clear the input buffer to prevent reading old data in the next loop.
            # Deutsch: Leere den Eingangspuffer, um das Lesen alter Daten in der nächsten Schleife zu verhindern.
            ser.reset_input_buffer()

        # English: Close the serial connection properly.
        # Deutsch: Schließe die serielle Verbindung ordnungsgemäß.
        ser.close()
        print("-" * 40)
        print("Messreihe beendet.")

    except Exception as e:
        print(f"Fehler: {e}")

# English: This block runs only when the script is executed directly.
# Deutsch: Dieser Block wird nur ausgeführt, wenn das Skript direkt gestartet wird.
if __name__ == "__main__":
    run_10_measurements_fixed_range()