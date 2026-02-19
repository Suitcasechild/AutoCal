
# English: This module provides a simple in-memory manager for Tasmota credentials.
# Deutsch: Dieses Modul stellt einen einfachen In-Memory-Manager für Tasmota-Zugangsdaten bereit.

class CredentialsManager:
    """
    # English: A class to manage Tasmota credentials temporarily in memory.
    # Deutsch: Eine Klasse, um Tasmota-Zugangsdaten temporär im Speicher zu verwalten.
    """
    def __init__(self):
        # English: Initialize an empty dictionary to store credentials.
        # Deutsch: Initialisiert ein leeres Dictionary zum Speichern der Zugangsdaten.
        self._credentials = {}

    def set_credentials(self, device_hostname, user, password):
        """
        # English: Stores the credentials for a specific device hostname.
        # Deutsch: Speichert die Zugangsdaten für einen bestimmten Geräte-Hostnamen.
        """
        self._credentials[device_hostname] = {'user': user, 'password': password}

    def get_credentials(self, device_hostname):
        """
        # English: Retrieves the credentials for a specific device hostname.
        # Deutsch: Ruft die Zugangsdaten für einen bestimmten Geräte-Hostnamen ab.
        
        # Returns: A dict with 'user' and 'password' or None if not found.
        # Gibt ein Dict mit 'user' und 'password' zurück oder None, wenn nichts gefunden wurde.
        """
        return self._credentials.get(device_hostname)

    def has_credentials(self, device_hostname):
        """
        # English: Checks if credentials exist for a specific device hostname.
        # Deutsch: Prüft, ob für einen bestimmten Geräte-Hostnamen Zugangsdaten vorhanden sind.
        """
        return device_hostname in self._credentials

    def clear_all_credentials(self):
        """
        # English: Clears all stored credentials from memory.
        # Deutsch: Löscht alle gespeicherten Zugangsdaten aus dem Speicher.
        """
        self._credentials.clear()
        print("INFO: All temporary credentials have been cleared.")

