# English:
# This file contains the logic for the manual calibration workflow.
# It is responsible for processing user-entered measurement data,
# creating a CSV file in the correct format, and preparing it for the analysis functions.

# Deutsch:
# Diese Datei enthält die Logik für den manuellen Kalibrier-Workflow.
# Sie ist verantwortlich für die Verarbeitung der vom Benutzer eingegebenen Messdaten,
# das Erstellen einer CSV-Datei im korrekten Format und deren Vorbereitung für die Analysefunktionen.

import pandas as pd
import os
from datetime import datetime

class ManualCalibrationEngine:
    """
    # English:
    # A class to handle the processing of manually entered calibration data.
    # Deutsch:
    # Eine Klasse zur Verarbeitung von manuell eingegebenen Kalibrierungsdaten.
    """
    def process_manual_data(self, data_dict: dict, device_path: str):
        """
        # English:
        # Takes a dictionary of manually entered values, structures them into a DataFrame,
        # and saves them as a CSV file. Invalid or empty fields are converted to 0.0.
        # Deutsch:
        # Nimmt ein Dictionary mit manuell eingegebenen Werten, strukturiert sie
        # in einen DataFrame und speichert sie als CSV. Ungültige oder leere Felder werden zu 0.0.

        :param data_dict: The dictionary containing measurement values from the UI.
        :param device_path: The path to the report directory for the specific device.
        :return: A tuple (csv_path, session_ts) or (None, None) on failure.
        """
        try:
            records = []
            for i in range(1, 4): # There are 3 measurements
                record = {}
                # English: Safely convert each value to float, defaulting to 0.0 on any error.
                # Deutsch: Konvertiere jeden Wert sicher zu float, bei Fehlern wird 0.0 verwendet.
                for key_prefix in ['vref', 'vtas', 'aref', 'atas', 'wref', 'wtas']:
                    ui_key = f'{key_prefix}_{i}'
                    try:
                        value = float(data_dict.get(ui_key, '0').replace(',', '.') or '0')
                    except (ValueError, TypeError):
                        value = 0.0
                    
                    # English: Map UI key to DataFrame column name
                    # Deutsch: Bilde UI-Schlüssel auf DataFrame-Spaltennamen ab
                    col_map = {
                        'vref': 'Ref_Volt', 'vtas': 'Target_Volt',
                        'aref': 'Ref_Amp', 'atas': 'Target_Amp',
                        'wref': 'Ref_Watt', 'wtas': 'Target_Watt'
                    }
                    df_key = col_map[key_prefix]
                    record[df_key] = value
                records.append(record)

            df = pd.DataFrame(records)

            for col in df.columns:
                if df[col].dtype == 'float64':
                    df[col] = df[col].round(3)

            session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{session_ts}_manuell_Stufe_1.csv"
            csv_path = os.path.join(device_path, file_name)
            df.to_csv(csv_path, index=False)
            
            print(f"INFO: Manuelle Messdaten erfolgreich in {file_name} gespeichert.")
            return csv_path, session_ts

        except Exception as e:
            print(f"FEHLER: Ein unerwarteter Fehler ist bei der Erstellung der manuellen CSV aufgetreten: {e}")
            return None, None
