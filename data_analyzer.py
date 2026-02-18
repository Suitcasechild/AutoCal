import pandas as pd
import numpy as np
import glob
import os

class DataAnalyzer:
    @staticmethod
    def calculate_regression(device_path, session_ts):
        search_path = os.path.join(device_path, f"{session_ts}_Stufe_*.csv")
        files = glob.glob(search_path)
        
        if not files:
            return None

        df_list = [pd.read_csv(f) for f in files]
        full_df = pd.concat(df_list, ignore_index=True)

        results = {}
        
        # --- NUR NOCH LEISTUNG (POWER) BERECHNEN ---
        x = full_df['Target_Watt'].values  # Ist-Werte (DUT)
        y = full_df['Ref_Watt'].values     # Soll-Werte (Ref)
        
        # Regression durch den Ursprung (y = m * x) für Tasmota-Faktor
        x_reshaped = x[:, np.newaxis]
        m, _, _, _ = np.linalg.lstsq(x_reshaped, y, rcond=None)
        slope = float(m[0])
        
        # Bestimmtheitsmaß R^2 zur Qualitätskontrolle
        correlation_matrix = np.corrcoef(x, y)
        r_squared = correlation_matrix[0, 1]**2
        
        results['Power'] = {
            'slope': slope,
            'r_squared': r_squared
        }
            
        return results