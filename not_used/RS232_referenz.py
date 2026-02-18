import serial
import time

PORT = 'COM3' 
BAUD = 9600

def format_val(s):
    try:
        # Säubert den String von Prompts und konvertiert in Float
        return float(s.replace("=>", "").strip())
    except:
        return 0.0

def run_10_measurements_fixed_range():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=3)
        
        print("--- Initialisiere Gerät (VAC Fix-Range + AAC2) ---")
        ser.write(b"*RST\r")
        time.sleep(1)
        
        # Primäranzeige auf VAC
        ser.write(b"VAC\r")
        time.sleep(0.5)
        
        # Bereich auf 300V fixieren (Range 4)
        print("Setze Messbereich auf 300V (Fix)...")
        ser.write(b"RANGE 4\r")
        time.sleep(1)
        
        # Sekundäranzeige auf AAC (aktiviert Dual)
        ser.write(b"AAC2\r")
        
        print("Warte 3s auf stabile Messung...")
        time.sleep(3)
        ser.reset_input_buffer() 

        print(f"{'Nr.':<5} | {'Spannung (V)':<12} | {'Strom (A)':<12}")
        print("-" * 40)

        for i in range(1, 11):
            ser.write(b"VAL?\r")
            
            time.sleep(1.5) 
            
            raw_data = ser.read_all().decode('utf-8', errors='replace').strip()
            
            if raw_data:
                parts = raw_data.split(",")
                
                if len(parts) >= 2:
                    v = format_val(parts[0])
                    a = format_val(parts[1])
                    print(f"{i:<5} | {v:<12.2f} | {a:<12.6f}")
                else:
                    print(f"{i:<5} | Rohdaten: {repr(raw_data)}")
            
            ser.reset_input_buffer()

        ser.close()
        print("-" * 40)
        print("Messreihe beendet.")

    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    run_10_measurements_fixed_range()