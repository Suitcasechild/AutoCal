import serial
import httpx
import time

class ReferenceManager:
    def __init__(self, config):
        self.config = config
        self.ser = None
        self.mode = None
        self.offset_a = 0.0  # NEU
        self.offset_w = 0.0  # NEU

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == 'PRO':
            return self._setup_fluke()
        return True
    
    def set_home_offset(self, a, w):
        """Speichert die ermittelten Offset-Werte"""
        self.offset_a = a
        self.offset_w = w

    def _setup_fluke(self):
        """Initialisierung exakt wie in RS232_referenz.py, mit Hardware-Ping"""
        port = self.config['REFERENCE_PRO']['com_port']
        baud = int(self.config['REFERENCE_PRO']['baudrate'])
        try:
            # Verbindung öffnen (klappt immer, solange USB-Adapter steckt)
            self.ser = serial.Serial(port, baud, timeout=3)
            
            print(f"--- Initialisiere Fluke 45 auf {port} ---")
            
            # --- NEU: Hardware-Ping ---
            # Wir prüfen, ob auf der Leitung wirklich jemand antwortet,
            # bevor wir 5 Sekunden lang Initialisierungsbefehle ins Leere senden.
            self.ser.write(b"*IDN?\r")
            time.sleep(0.5)
            test_resp = self.ser.read_all().decode('utf-8', errors='replace').strip()
            
            if not test_resp:
                raise Exception("Keine serielle Antwort (Gerät stromlos oder Kabel nicht verbunden?)")
            
            print("Verbindung bestätigt. Setze Modus (VAC Fix-Range + AAC2)...")
            # --------------------------
            
            self.ser.write(b"*RST\r")
            time.sleep(1)
            
            # Primäranzeige auf VAC
            self.ser.write(b"VAC\r")
            time.sleep(0.5)
            
            # Bereich auf 300V fixieren (Range 4)
            self.ser.write(b"RANGE 4\r")
            time.sleep(1)
            
            # Sekundäranzeige auf AAC (aktiviert Dual Anzeige)
            self.ser.write(b"AAC2\r")
            
            print("Warte 3s auf stabile Messung...")
            time.sleep(3)
            self.ser.reset_input_buffer()
            
            print(f"[OK] Fluke 45 ({port}) ist online und bereit.")
            return True
        except Exception as e:
            print(f"[FEHLER] Fluke 45 Initialisierung fehlgeschlagen: {e}")
            return False

    def get_reference_data(self, auth=None):
        if self.mode == 'PRO':
            return self._get_fluke_data()
        return self._get_tasmota_ref_data(auth)

    def _get_fluke_data(self):
        """Abfrage mit VAL? wie im Testskript"""
        try:
            self.ser.write(b"VAL?\r")
            time.sleep(1.5) 
            
            raw = self.ser.read_all().decode('utf-8', errors='replace').strip()
            if raw:
                parts = raw.replace("=>", "").strip().split(",")
                if len(parts) >= 2:
                    v = float(parts[0].strip())
                    a = float(parts[1].strip())
                    return v, a, v * a
            return None, None, None
        except:
            return None, None, None

    def _get_tasmota_ref_data(self, auth=None):
        ip = self.config['REFERENCE_HOME']['ip_address']
        try:
            r = httpx.get(f"http://{ip}/cm?cmnd=Status%208", timeout=2, auth=auth)
            d = r.json()['StatusSNS']['ENERGY']
            
            # 1. Rohwerte von der Referenzdose lesen
            v_raw = float(d['Voltage'])
            a_raw = float(d['Current'])
            w_raw = float(d['Power'])
            
            # 2. Offset abziehen (Eigenverbrauch der Ziel-Dose)
            # Wir stellen mit max(0.0, ...) sicher, dass keine negativen Werte entstehen
            v = v_raw
            a = max(0.0, a_raw - self.offset_a)
            w = max(0.0, w_raw - self.offset_w)
            
            return v, a, w
        except Exception as e:
            # Falls ein Fehler auftritt (z.B. Timeout), geben wir None zurück
            return None, None, None

    def get_current_cal_factors(self, target_ip, auth=None):
        factors = {"VCal": 20230, "ACal": 2500, "WCal": 12500}
        cmds = {"VoltageCal": "VCal", "CurrentCal": "ACal", "PowerCal": "WCal"}
        for cmd, key in cmds.items():
            try:
                r = httpx.get(f"http://{target_ip}/cm?cmnd={cmd}", timeout=2, auth=auth)
                val = r.json().get(cmd)
                if val is not None:
                    factors[key] = int(val)
            except: pass
        return factors

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()