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
        
        # English: Read the specified config file.
        # Deutsch: Lese die angegebene Konfigurationsdatei.
        self.config.read(self.config_path)
        
        # English: Store the root directory for reports from the config.
        # Deutsch: Speichere das Stammverzeichnis für Protokolle aus der Konfiguration.
        self.root_dir = self.config['GENERAL']['root_report_dir']

    def get_target_mac(self, auth=None):
        """
        # English:
        # Queries the MAC address of the target device via the Tasmota API.
        # This is used for creating a unique directory for the device.
        # Deutsch:
        # Fragt die MAC-Adresse der Ziel-Dose via Tasmota API ab.
        # Dies wird zur Erstellung eines eindeutigen Verzeichnisses für das Gerät verwendet.

        :param auth: (tuple, optional) Auth tuple (user, password) for the device.
        :return: (str) The MAC address without colons, or "Unknown_Device" on error.
                 (str) Die MAC-Adresse ohne Doppelpunkte oder "Unknown_Device" bei einem Fehler.
        """
        # English: Get the IP address of the target device from the config.
        # Deutsch: Hole die IP-Adresse des Zielgeräts aus der Konfiguration.
        target_ip = self.config['TARGET']['ip_address']
        try:
            # English: Status 5 provides network info including the MAC address.
            # Deutsch: Status 5 liefert Netzwerk-Infos inklusive der MAC-Adresse.
            response = httpx.get(f"http://{target_ip}/cm?cmnd=Status%205", timeout=5, auth=auth)
            data = response.json()
            
            # English: Extract the MAC address (e.g., 40:F5:20:...).
            # Deutsch: Extrahiere die MAC-Adresse (z.B. 40:F5:20:...).
            mac = data['StatusNET']['Mac']
            
            # English: Remove colons for use as a folder name.
            # Deutsch: Entferne Doppelpunkte für die Verwendung als Ordnername.
            return mac.replace(":", "") 
        except Exception as e:
            # English: If any error occurs, print it and return a default name.
            # Deutsch: Falls ein Fehler auftritt, gib ihn aus und gib einen Standardnamen zurück.
            print(f"Fehler beim Abrufen der MAC: {e}")
            return "Unknown_Device"

    def setup_device_directory(self, auth=None):
        """
        # English:
        # Creates a directory for the specific device based on its MAC address.
        # If the directory already exists, it does nothing.
        # Deutsch:
        # Erstellt den Ordner für das spezifische Gerät basierend auf seiner MAC-Adresse.
        # Falls das Verzeichnis bereits existiert, wird nichts unternommen.

        :param auth: (tuple, optional) Auth tuple for the device.
        :return: (str) The path to the device-specific directory.
                 (str) Der Pfad zum gerätespezifischen Verzeichnis.
        """
        # English: Get the MAC address to use for the folder name.
        # Deutsch: Hole die MAC-Adresse, die als Ordnername verwendet wird.
        mac = self.get_target_mac(auth=auth)
        
        # English: Construct the full path.
        # Deutsch: Konstruiere den vollständigen Pfad.
        device_path = os.path.join(self.root_dir, mac)
        
        # English: If the path does not exist, create it.
        # Deutsch: Wenn der Pfad nicht existiert, erstelle ihn.
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