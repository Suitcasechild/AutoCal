
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

    def set_credentials(self, identifier, user, password):
        """
        # English: Stores the credentials for a specific device identifier (IP or hostname).
        # Deutsch: Speichert die Zugangsdaten für einen bestimmten Geräte-Identifier (IP oder Hostname).
        """
        self._credentials[identifier] = {'user': user, 'password': password}

    def get_credentials(self, identifier):
        """
        # English: Retrieves the credentials for a specific device identifier (IP or hostname).
        # Deutsch: Ruft die Zugangsdaten für einen bestimmten Geräte-Identifier (IP oder Hostname) ab.
        
        # Returns: A dict with 'user' and 'password' or None if not found.
        # Gibt ein Dict mit 'user' und 'password' zurück oder None, wenn nichts gefunden wurde.
        """
        return self._credentials.get(identifier)

    def has_credentials(self, identifier):
        """
        # English: Checks if credentials exist for a specific device identifier (IP or hostname).
        # Deutsch: Prüft, ob für einen bestimmten Geräte-Identifier (IP oder Hostname) Zugangsdaten vorhanden sind.
        """
        return identifier in self._credentials

    def clear_all_credentials(self):
        """
        # English: Clears all stored credentials from memory.
        # Deutsch: Löscht alle gespeicherten Zugangsdaten aus dem Speicher.
        """
        self._credentials.clear()
        print(_("INFO: All temporary credentials have been cleared."))

