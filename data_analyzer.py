# -*- coding: utf-8 -*-
"""
# English: This module provides tools for analyzing measurement data, focusing on linear regression.
# Deutsch: Dieses Modul stellt Werkzeuge zur Analyse von Messdaten bereit, mit Fokus auf linearer Regression.
"""
import pandas as pd
import numpy as np
import glob
import os

class DataAnalyzer:
    """
    # English:
    # A utility class that contains static methods for data analysis tasks.
    # Currently, it's used to calculate the linear regression for power measurements.
    # Deutsch:
    # Eine Hilfsklasse, die statische Methoden für Datenanalyse-Aufgaben enthält.
    # Derzeit wird sie zur Berechnung der linearen Regression für Leistungsmessungen verwendet.
    """
    @staticmethod
    def calculate_regression(device_path, session_ts):
        """
        # English:
        # Calculates the linear regression for power values across all measurement steps.
        # It reads all CSV files from a session, concatenates them, and performs a
        # least-squares regression forced through the origin (y = m * x).
        # Deutsch:
        # Berechnet die lineare Regression für die Leistungswerte über alle Messstufen hinweg.
        # Liest alle CSV-Dateien einer Sitzung, fügt sie zusammen und führt eine
        # Regression der kleinsten Quadrate mit Nullpunkterzwingung (y = m * x) durch.

        :param device_path: (str) The path to the device's data directory.
                            (str) Der Pfad zum Datenverzeichnis des Geräts.
        :param session_ts: (str) The timestamp identifying the measurement session.
                           (str) Der Zeitstempel, der die Messsitzung identifiziert.
        :return: (dict or None) A dictionary with regression results ('slope', 'r_squared')
                                or None if no data files are found.
                 (dict oder None) Ein Dictionary mit Regressionsergebnissen ('slope', 'r_squared')
                                  oder None, wenn keine Datendateien gefunden werden.
        """
        # English: Construct the search path for all CSV files of the session.
        # Deutsch: Konstruiere den Suchpfad für alle CSV-Dateien der Sitzung.
        search_path = os.path.join(device_path, f"{session_ts}_Stufe_*.csv")
        files = glob.glob(search_path)
        
        # English: If no files were found, return None.
        # Deutsch: Wenn keine Dateien gefunden wurden, gib None zurück.
        if not files:
            return None

        # English: Read all found CSV files into a list of pandas DataFrames.
        # Deutsch: Lese alle gefundenen CSV-Dateien in eine Liste von pandas DataFrames.
        df_list = [pd.read_csv(f) for f in files]
        
        # English: Concatenate all DataFrames into a single one.
        # Deutsch: Füge alle DataFrames zu einem einzigen zusammen.
        full_df = pd.concat(df_list, ignore_index=True)

        # English: If DataFrame is empty after concatenation, abort.
        # Deutsch: Wenn der DataFrame nach dem Zusammenfügen leer ist, abbrechen.
        if full_df.empty:
            return None

        results = {}
        
        # --- ONLY CALCULATE FOR POWER ---
        # --- NUR NOCH LEISTUNG (POWER) BERECHNEN ---
        # English: Ist-Werte (DUT) on x-axis, Soll-Werte (Ref) on y-axis.
        # Deutsch: Ist-Werte (DUT) auf der x-Achse, Soll-Werte (Ref) auf der y-Achse.
        x = full_df['Target_Watt'].values
        y = full_df['Ref_Watt'].values
        
        # English: Reshape x for the least-squares algorithm.
        # Deutsch: Forme x für den Algorithmus der kleinsten Quadrate um.
        x_reshaped = x[:, np.newaxis]
        
        # English: Perform least-squares regression forced through the origin.
        # Deutsch: Führe die Regression der kleinsten Quadrate mit Nullpunkterzwingung durch.
        m, residuals, rank, s = np.linalg.lstsq(x_reshaped, y, rcond=None)
        slope = float(m[0])
        
        # English: Calculate R^2 only if there is more than one point to avoid NaN.
        # Deutsch: R^2 nur berechnen, wenn mehr als ein Punkt vorhanden ist, um NaN zu vermeiden.
        r_squared = 1.0
        if len(x) > 1:
            correlation_matrix = np.corrcoef(x, y)
            # English: Ensure we don't get NaN if variance is zero.
            # Deutsch: Sicherstellen, dass wir bei Varianz Null kein NaN bekommen.
            if not np.isnan(correlation_matrix[0, 1]):
                r_squared = correlation_matrix[0, 1]**2
        
        results['Power'] = {
            'slope': slope,
            'r_squared': r_squared
        }
            
        return results