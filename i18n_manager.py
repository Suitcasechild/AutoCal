# -*- coding: utf-8 -*-
"""
# English: Manages the internationalization (i18n) of the application.
# Deutsch: Verwaltet die Internationalisierung (i18n) der Anwendung.
"""
import gettext
import locale
import os
from config_manager import ConfigManager

def setup_translation():
    """
    # English:
    # Sets up the translation services based on the language setting in config.ini.
    # It makes the translation function '_' available globally.
    # Deutsch:
    # Richtet die Übersetzungsdienste basierend auf der Spracheinstellung in der config.ini ein.
    # Macht die Übersetzungsfunktion '_' global verfügbar.
    """
    try:
        cm = ConfigManager()
        lang_setting = cm.config.get('GENERAL', 'language', fallback='auto').lower()
        
        languages = None
        if lang_setting in ['de', 'en']:
            languages = [lang_setting]
        elif lang_setting == 'auto':
            # English: If set to 'auto', try to get the system's default language.
            # Deutsch: Wenn auf 'auto' gesetzt, versuche die Standardsprache des Systems zu ermitteln.
            try:
                sys_lang = locale.getdefaultlocale()[0]
                if sys_lang:
                    languages = [sys_lang.split('_')[0]]
            except Exception:
                languages = ['de'] # Fallback to German if auto-detection fails
        
        # English: The path to the 'locale' directory.
        # Deutsch: Der Pfad zum 'locale'-Verzeichnis.
        localedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale')

        # English: Find and install the translation.
        # Deutsch: Finde und installiere die Übersetzung.
        if languages:
            translation = gettext.translation('messages', localedir=localedir, languages=languages, fallback=True)
            translation.install()
            return translation.gettext
        
    except Exception as e:
        print(f"I18N-Fehler: {e}")

    # English: If everything fails, return a dummy function that just returns the original text.
    # Deutsch: Wenn alles fehlschlägt, gib eine Dummy-Funktion zurück, die nur den Originaltext zurückgibt.
    import builtins
    builtins._ = lambda text: text
    return builtins._
