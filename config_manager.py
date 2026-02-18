import configparser
import os
import httpx

class ConfigManager:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.root_dir = self.config['GENERAL']['root_report_dir']

    def get_target_mac(self):
        """Fragt die MAC-Adresse der Ziel-Dose via Tasmota API ab."""
        target_ip = self.config['TARGET']['ip_address']
        try:
            # Status 5 liefert Netzwerk-Infos inkl. MAC
            response = httpx.get(f"http://{target_ip}/cm?cmnd=Status%205", timeout=5)
            data = response.json()
            # MAC Adresse extrahieren (z.B. 40:F5:20:...)
            mac = data['StatusNET']['Mac']
            return mac.replace(":", "") # Doppelpunkte für Ordnernamen entfernen
        except Exception as e:
            print(f"Fehler beim Abrufen der MAC: {e}")
            return "Unknown_Device"

    def setup_device_directory(self):
        """Erstellt den Ordner für das spezifische Gerät."""
        mac = self.get_target_mac()
        device_path = os.path.join(self.root_dir, mac)
        
        if not os.path.exists(device_path):
            os.makedirs(device_path)
            print(f"Verzeichnis erstellt: {device_path}")
        
        return device_path

# Test-Bereich
if __name__ == "__main__":
    cm = ConfigManager()
    path = cm.setup_device_directory()
    print(f"Messdaten landen in: {path}")