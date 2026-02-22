# -*- coding: utf-8 -*-
"""
# English: This module provides a manager for handling the application's configuration via a .ini file.
# Deutsch: Dieses Modul stellt einen Manager zur Handhabung der Anwendungskonfiguration über eine .ini-Datei bereit.
"""
import configparser
import os
import httpx

class ConfigManager:
    """
    # English:
    # Manages loading and accessing configuration from the config.ini file.
    # It also handles the creation of device-specific directories.
    # Deutsch:
    # Verwaltet das Laden und den Zugriff auf die Konfiguration aus der config.ini-Datei.
    # Übernimmt auch die Erstellung von gerätespezifischen Verzeichnissen.
    """
    def __init__(self, config_file='config.ini'):
        """
        # English: Initializes the ConfigManager and loads the configuration file.
        # Deutsch: Initialisiert den ConfigManager und lädt die Konfigurationsdatei.

        :param config_file: (str) The name of the configuration file to load.
                            (str) Der Name der zu ladenden Konfigurationsdatei.
        """
        # English: Use an absolute path to the config file to ensure it's found regardless of the working directory.
        # Deutsch: Nutze einen absoluten Pfad zur Konfigurationsdatei, um sicherzustellen, dass sie unabhängig vom Arbeitsverzeichnis gefunden wird.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(base_dir, config_file)

        # English: Create a new ConfigParser instance.
        # Deutsch: Erstelle eine neue ConfigParser-Instanz.
        self.config = configparser.ConfigParser()
        
        # English: If the config file is missing, create it with default values.
        # Deutsch: Wenn die Konfigurationsdatei fehlt, erstelle sie mit Standardwerten.
        if not os.path.exists(self.config_path):
            print(f"ℹ️ {config_file} fehlt. Erstelle Standard-Konfiguration...")
            self.config['GENERAL'] = {'root_report_dir': './Reports', 'language': 'auto', 'ui_mode': 'home_only'}
            self.config['REFERENCE_PRO'] = {'com_port': 'COM1', 'baudrate': '9600'}
            self.config['REFERENCE_HOME'] = {'ip_address': ''}
            # English: ip_address for TARGET is intentionally left empty for privacy/security.
            # Deutsch: ip_address für TARGET bleibt aus Datenschutzgründen absichtlich leer.
            self.config['TARGET'] = {'ip_address': '', 'measurement_steps': '1', 'measurements_per_step': '15'}
            self.config['TOLERANCE abs%'] = {'voltage_limit': '0.5', 'current_limit': '0.5', 'power_limit': '5.0'}
            
            try:
                with open(self.config_path, 'w') as f:
                    self.config.write(f)
            except Exception as e:
                print(f"❌ Fehler beim Erstellen der config.ini: {e}")
        else:
            # English: Read the specified config file.
            # Deutsch: Lese die angegebene Konfigurationsdatei.
            self.config.read(self.config_path)
        
        # English: Store the root directory for reports from the config.
        # Deutsch: Speichere das Stammverzeichnis für Protokolle aus der Konfiguration.
        self.root_dir = self.config['GENERAL']['root_report_dir']

    def get_target_mac(self, ip=None, auth=None, mac=None):
        """
        # English:
        # Queries the MAC address of a Tasmota device via its API.
        # Deutsch:
        # Fragt die MAC-Adresse einer Tasmota-Dose via API ab.

        :param ip: (str, optional) The IP address. If None, uses the one from config.
        :param auth: (tuple, optional) Auth tuple (user, password) for the device.
        :param mac: (str, optional) Already known MAC address to avoid API call.
        :return: (str) The MAC address without colons, or "Unknown_Device" on error.
        """
        if mac:
            # English: If MAC is provided, ensure colons are replaced by hyphens.
            # Deutsch: Wenn die MAC übergeben wurde, sicherstellen, dass Doppelpunkte durch Bindestriche ersetzt werden.
            return mac.replace(":", "-")

        target_ip = ip if ip else self.config['TARGET']['ip_address']
        
        # English: Ensure the IP has a protocol prefix.
        # Deutsch: Stelle sicher, dass die IP ein Protokoll-Präfix hat.
        if target_ip and not target_ip.startswith(("http://", "https://")):
            url = f"http://{target_ip}/cm?cmnd=Status%205"
        else:
            url = f"{target_ip}/cm?cmnd=Status%205"

        try:
            response = httpx.get(url, timeout=5, auth=auth)
            data = response.json()
            mac = data['StatusNET']['Mac']
            # English: Use hyphens for use as a folder name (compatible with old structure).
            # Deutsch: Nutze Bindestriche für die Verwendung als Ordnername (kompatibel mit alter Struktur).
            return mac.replace(":", "-") 
        except Exception as e:
            print(f"Fehler beim Abrufen der MAC von {target_ip}: {e}")
            return "Unknown_Device"

    def setup_device_directory(self, ip=None, auth=None, mac=None):
        """
        # English:
        # Creates a directory for the specific device based on its MAC address.
        # Deutsch:
        # Erstellt den Ordner für das spezifische Gerät basierend auf seiner MAC-Adresse.

        :param ip: (str, optional) The IP address of the device.
        :param auth: (tuple, optional) Auth tuple for the device.
        :param mac: (str, optional) Already known MAC address to avoid API call.
        :return: (str) The path to the device-specific directory.
        """
        mac = self.get_target_mac(ip=ip, auth=auth, mac=mac)
        device_path = os.path.join(self.root_dir, mac)
        
        if not os.path.exists(device_path):
            os.makedirs(device_path)
            print(f"Verzeichnis erstellt: {device_path}")
        
        return device_path

# English: Test section that runs only when the script is executed directly.
# Deutsch: Test-Bereich, der nur läuft, wenn das Skript direkt ausgeführt wird.
if __name__ == "__main__":
    cm = ConfigManager()
    path = cm.setup_device_directory()
    print(f"Messdaten landen in: {path}")