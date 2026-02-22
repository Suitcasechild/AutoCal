# -*- coding: utf-8 -*-
"""
# English: This module provides a manager for handling different reference measurement devices (Fluke or Tasmota).
# Deutsch: Dieses Modul stellt einen Manager zur Handhabung verschiedener Referenz-Messgeräte (Fluke oder Tasmota) bereit.
"""
import serial
import httpx
import time

class ReferenceManager:
    """
    # English:
    # Manages the connection to and data acquisition from a reference device.
    # It supports a professional mode ('PRO') for Fluke multimeters and a
    # home user mode ('HOME') for another Tasmota device.
    # Deutsch:
    # Verwaltet die Verbindung und Datenerfassung von einem Referenzgerät.
    # Unterstützt einen professionellen Modus ('PRO') für Fluke-Multimeter und
    # einen Heimanwender-Modus ('HOME') für ein anderes Tasmota-Gerät.
    """
    def __init__(self, config):
        """
        # English: Initializes the ReferenceManager.
        # Deutsch: Initialisiert den ReferenceManager.

        :param config: (ConfigParser) The application's configuration object.
                       (ConfigParser) Das Konfigurationsobjekt der Anwendung.
        """
        self.config = config
        self.ser = None
        self.mode = None
        self.offset_a = 0.0
        self.offset_w = 0.0

    def set_mode(self, mode):
        """
        # English: Sets the measurement mode ('PRO' or 'HOME') and initializes the device if necessary.
        # Deutsch: Stellt den Messmodus ('PRO' oder 'HOME') ein und initialisiert ggf. das Gerät.

        :param mode: (str) The mode to set, either 'PRO' or 'HOME'.
                     (str) Der einzustellende Modus, entweder 'PRO' oder 'HOME'.
        :return: (bool) True on success, False on failure (e.g., Fluke init failed).
                 (bool) True bei Erfolg, False bei einem Fehler (z.B. Fluke-Initialisierung fehlgeschlagen).
        """
        self.mode = mode
        if self.mode == 'PRO':
            return self._setup_fluke()
        return True
    
    def set_home_offset(self, a, w):
        """
        # English: Stores the determined offset values for current and power (HOME mode only).
        # Deutsch: Speichert die ermittelten Offset-Werte für Strom und Leistung (nur im HOME-Modus).

        :param a: (float) The current offset in Amperes.
                  (float) Der Strom-Offset in Ampere.
        :param w: (float) The power offset in Watts.
                  (float) Der Leistungs-Offset in Watt.
        """
        self.offset_a = a
        self.offset_w = w

    def _setup_fluke(self):
        """
        # English: Initializes the Fluke 45 multimeter via serial connection.
        # Deutsch: Initialisiert das Fluke 45 Multimeter über die serielle Verbindung.
        
        :return: (bool) True if initialization is successful, False otherwise.
                 (bool) True, wenn die Initialisierung erfolgreich war, sonst False.
        """
        port = self.config['REFERENCE_PRO']['com_port']
        baud = int(self.config['REFERENCE_PRO']['baudrate'])
        try:
            # English: Open serial connection. This usually succeeds if the USB adapter is plugged in.
            # Deutsch: Öffne die serielle Verbindung (klappt i.d.R., solange der USB-Adapter steckt).
            self.ser = serial.Serial(port, baud, timeout=3)
            
            print(_("--- Initialisiere Fluke 45 auf {port} ---").format(port=port))
            
            # English: Perform a hardware ping to see if a device is actually responding.
            # Deutsch: Führe einen Hardware-Ping durch, um zu sehen, ob ein Gerät tatsächlich antwortet.
            self.ser.write(b"*IDN?\r")
            time.sleep(1.0) # Etwas mehr Zeit für die Antwort / A bit more time for response
            test_resp = self.ser.read_all().decode('utf-8', errors='replace').strip()
            
            if not test_resp or "FLUKE" not in test_resp.upper():
                error_msg = _("Keine gültige Antwort vom Fluke.")
                if test_resp:
                    error_msg += _(" (Empfangen: {test_resp_repr})").format(test_resp_repr=repr(test_resp))
                else:
                    error_msg += _(" (Gerät antwortet nicht)")
                raise Exception(error_msg)
            
            print(_("Verbindung bestätigt: {test_resp}").format(test_resp=test_resp))
            print(_("Setze Modus (VAC Fix-Range + AAC2)..."))
            
            # English: Send reset command, set to VAC, fix range to 300V, set secondary to AAC.
            # Deutsch: Sende Reset-Befehl, setze auf VAC, fixiere Bereich auf 300V, setze Sekundäranzeige auf AAC.
            self.ser.write(b"*RST\r")
            time.sleep(1)
            self.ser.write(b"VAC\r")
            time.sleep(0.5)
            self.ser.write(b"RANGE 4\r")
            time.sleep(1)
            self.ser.write(b"AAC2\r")
            
            print(_("Warte 3s auf stabile Messung..."))
            time.sleep(3)
            self.ser.reset_input_buffer()
            
            print(_("[OK] Fluke 45 ({port}) ist online und bereit.").format(port=port))
            return True
        except Exception as e:
            print(_("[FEHLER] Fluke 45 Initialisierung fehlgeschlagen: {e}").format(e=e))
            if self.ser and self.ser.is_open:
                try:
                    self.ser.close()
                except:
                    pass
            return False

    def get_reference_data(self, auth=None):
        """
        # English: Gets measurement data from the currently active reference device.
        # Deutsch: Ruft Messdaten vom aktuell aktiven Referenzgerät ab.

        :param auth: (tuple, optional) Auth tuple for HTTP requests (used in HOME mode).
                     (tuple, optional) Auth-Tupel für HTTP-Anfragen (im HOME-Modus verwendet).
        :return: (tuple) A tuple of (voltage, current, power) or (None, None, None) on error.
                 (tuple) Ein Tupel mit (Spannung, Strom, Leistung) oder (None, None, None) bei einem Fehler.
        """
        if self.mode == 'PRO':
            return self._get_fluke_data()
        return self._get_tasmota_ref_data(auth)

    def _get_fluke_data(self):
        """
        # English: Reads Voltage and Current from the Fluke 45 and calculates Power.
        # Deutsch: Liest Spannung und Strom vom Fluke 45 und berechnet die Leistung.

        :return: (tuple) A tuple of (voltage, current, power) or (None, None, None) on error.
                 (tuple) Ein Tupel mit (Spannung, Strom, Leistung) oder (None, None, None) bei einem Fehler.
        """
        try:
            # English: Clear the input buffer to ensure we don't read stale data or prompts.
            # Deutsch: Leere den Eingangspuffer, um keine alten Daten oder Prompts zu lesen.
            self.ser.reset_input_buffer()
            
            # English: Request values from both displays.
            # Deutsch: Fordere die Werte von beiden Anzeigen an.
            self.ser.write(b"VAL?\r")
            
            # English: Read the line. Using readline is robust as it waits for the termination character.
            # Deutsch: Lese die Zeile. Readline ist robust, da es auf das Abschlusszeichen wartet.
            raw_bytes = self.ser.readline()
            raw = raw_bytes.decode('utf-8', errors='replace').strip()
            
            if raw:
                # English: Remove prompt and split by comma.
                # Deutsch: Entferne Prompt und teile am Komma.
                parts = raw.replace("=>", "").strip().split(",")
                if len(parts) >= 2:
                    v = float(parts[0].strip())
                    a = float(parts[1].strip())
                    return v, a, v * a
            return None, None, None
        except Exception as e:
            print(_("❌ Fehler beim Lesen der Fluke-Daten: {e}").format(e=e))
            return None, None, None

    def _get_tasmota_ref_data(self, auth=None):
        """
        # English: Reads sensor data from the Tasmota reference device and subtracts the offset.
        # Deutsch: Liest Sensordaten vom Tasmota-Referenzgerät und zieht den Offset ab.

        :param auth: (tuple, optional) Auth tuple for the HTTP request.
                     (tuple, optional) Auth-Tupel für die HTTP-Anfrage.
        :return: (tuple) A tuple of (voltage, current, power) or (None, None, None) on error.
                 (tuple) Ein Tupel mit (Spannung, Strom, Leistung) oder (None, None, None) bei einem Fehler.
        """
        ip = self.config['REFERENCE_HOME']['ip_address']
        try:
            r = httpx.get(f"http://{ip}/cm?cmnd=Status%208", timeout=2, auth=auth)
            d = r.json()['StatusSNS']['ENERGY']
            
            # English: Read raw values from the reference device.
            # Deutsch: Rohwerte von der Referenzdose lesen.
            v_raw = float(d['Voltage'])
            a_raw = float(d['Current'])
            w_raw = float(d['Power'])
            
            # English: Subtract the offset (idle consumption of the DUT).
            # Deutsch: Ziehe den Offset ab (Eigenverbrauch der Ziel-Dose).
            v = v_raw
            a = max(0.0, a_raw - self.offset_a)
            w = max(0.0, w_raw - self.offset_w)
            
            return v, a, w
        except Exception as e:
            # English: On any error (e.g., timeout), print it and return None.
            # Deutsch: Falls ein Fehler auftritt (z.B. Timeout), gib ihn aus und gib None zurück.
            print(_("❌ Fehler beim Lesen der Tasmota-Referenz ({ip}): {e}").format(ip=ip, e=e))
            return None, None, None

    def get_current_cal_factors(self, target_ip, auth=None):
        """
        # English: Reads the current calibration factors (VCal, ACal, WCal) from a Tasmota device.
        # Deutsch: Liest die aktuellen Kalibrierfaktoren (VCal, ACal, WCal) von einem Tasmota-Gerät aus.

        :param target_ip: (str) The IP address of the target Tasmota device.
                          (str) Die IP-Adresse des Ziel-Tasmota-Geräts.
        :param auth: (tuple, optional) Auth tuple for the HTTP requests.
                     (tuple, optional) Auth-Tupel für die HTTP-Anfragen.
        :return: (dict) A dictionary with the current factors, with fallbacks.
                 (dict) Ein Dictionary mit den aktuellen Faktoren, mit Standardwerten als Fallback.
        """
        factors = {"VCal": 20230, "ACal": 2500, "WCal": 12500}
        cmds = {"VoltageCal": "VCal", "CurrentCal": "ACal", "PowerCal": "WCal"}
        for cmd, key in cmds.items():
            try:
                r = httpx.get(f"http://{target_ip}/cm?cmnd={cmd}", timeout=2, auth=auth)
                val = r.json().get(cmd)
                if val is not None:
                    factors[key] = int(val)
            except Exception as e:
                print(_("⚠️ Warnung: Konnte '{cmd}' von {target_ip} nicht abrufen. Nutze Standardwert. Fehler: {e}").format(cmd=cmd, target_ip=target_ip, e=e))
                pass
        return factors

    def close(self):
        """
        # English: Closes the serial connection if it is open.
        # Deutsch: Schließt die serielle Verbindung, falls sie offen ist.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()