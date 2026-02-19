# -*- coding: utf-8 -*-
"""
# English: This module contains the core logic for calculating calibration values and generating reports.
# Deutsch: Dieses Modul enthält die Kernlogik für die Berechnung von Kalibrierwerten und die Erstellung von Protokollen.
"""
import os
import pandas as pd
from data_analyzer import DataAnalyzer

class CalibrationEngine:
    """
    # English:
    # Handles the calculation of new calibration values based on measurement data
    # and generates summary reports.
    # Deutsch:
    # Übernimmt die Berechnung neuer Kalibrierwerte basierend auf Messdaten
    # und erstellt zusammenfassende Protokolle.
    """
    def __init__(self, device_path):
        """
        # English: Initializes the CalibrationEngine.
        # Deutsch: Initialisiert die CalibrationEngine.

        :param device_path: (str) The path to the directory where device-specific files are stored.
                            (str) Der Pfad zum Verzeichnis, in dem gerätespezifische Dateien gespeichert werden.
        """
        self.device_path = device_path

    def calculate_new_calibration(self, csv_file, old_cal):
        """
        # English:
        # Calculates new calibration factor suggestions for a single measurement step (one CSV file).
        # It compares the mean values of the reference (Soll) and the device-under-test (Ist).
        # Deutsch:
        # Berechnet neue Kalibrierfaktor-Vorschläge für eine einzelne Messstufe (eine CSV-Datei).
        # Vergleicht die Mittelwerte der Referenz (Soll) und des Prüflings (Ist).

        :param csv_file: (str) Path to the CSV file containing measurement data for one step.
                         (str) Pfad zur CSV-Datei mit den Messdaten einer Stufe.
        :param old_cal: (dict) The existing calibration factors of the device.
                        (dict) Die bestehenden Kalibrierfaktoren des Geräts.
        :return: (dict) A dictionary containing all calculated results for this step.
                 (dict) Ein Dictionary mit allen berechneten Ergebnissen für diese Stufe.
        """
        # English: Read the measurement data from the CSV file.
        # Deutsch: Lese die Messdaten aus der CSV-Datei.
        df = pd.read_csv(csv_file)
        
        # English: Calculate the mean values for reference (Soll) and DUT (Ist).
        # Deutsch: Berechne die Mittelwerte für Referenz (Soll) und Prüfling (Ist).
        soll = {"V": df['Ref_Volt'].mean(), "A": df['Ref_Amp'].mean(), "W": df['Ref_Watt'].mean()}
        ist = {"V": df['Target_Volt'].mean(), "A": df['Target_Amp'].mean(), "W": df['Target_Watt'].mean()}

        # English: Calculate absolute and relative differences.
        # Deutsch: Berechne die absoluten und relativen Abweichungen.
        diff_abs = {k: ist[k] - soll[k] for k in soll}
        diff_rel = {k: (diff_abs[k] / soll[k] * 100) if soll[k] > 0 else 0 for k in soll}

        # English: Calculate the suggested calibration factors for this specific step.
        # Deutsch: Berechne die vorgeschlagenen Kalibrierfaktoren für diese spezifische Stufe.
        stufen_cal = {
            "VCal": int(old_cal['VCal'] * (soll['V'] / ist['V'])) if ist['V'] > 0 else old_cal['VCal'],
            "ACal": int(old_cal['ACal'] * (soll['A'] / ist['A'])) if ist['A'] > 0 else old_cal['ACal'],
            "WCal": int(old_cal['WCal'] * (soll['W'] / ist['W'])) if ist['W'] > 0 else old_cal['WCal']
        }

        # English: Return a structured dictionary with all results for this step.
        # Deutsch: Gib ein strukturiertes Dictionary mit allen Ergebnissen dieser Stufe zurück.
        return {
            "Stufe": None,
            "Soll": soll,
            "Ist": ist,
            "Diff_Abs": diff_abs,
            "Diff_Rel": diff_rel,
            "Alt_Cal": old_cal,
            "Stufen_Cal": stufen_cal
        }

    def write_summary(self, all_results, data_ts, report_ts=None, cal_mode="Unbekannt", old_cal=None, dut_info=None, ref_info=None):
        """
        # English:
        # Writes a detailed summary report (.txt) based on the results of all measurement steps.
        # It calculates final suggestions for calibration values (averaged and from regression).
        # Deutsch:
        # Schreibt ein detailliertes Zusammenfassungsprotokoll (.txt) basierend auf den Ergebnissen aller Messstufen.
        # Es berechnet endgültige Vorschläge für Kalibrierwerte (gemittelt und aus der Regression).

        :param all_results: (list) A list of result dictionaries from `calculate_new_calibration`.
                            (list) Eine Liste von Ergebnis-Dictionaries aus `calculate_new_calibration`.
        :param data_ts: (str) The timestamp of the source CSV data.
                        (str) Der Zeitstempel der zugrundeliegenden CSV-Daten.
        :param report_ts: (str, optional) The timestamp for the report file itself. Defaults to data_ts.
                          (str, optional) Der Zeitstempel für die Protokolldatei selbst. Standard ist data_ts.
        :param cal_mode: (str, optional) The calibration mode used ("PRO" or "HOME").
                         (str, optional) Der verwendete Kalibriermodus ("PRO" oder "HOME").
        :param old_cal: (dict, optional) The existing calibration factors.
                        (dict, optional) Die bestehenden Kalibrierfaktoren.
        :param dut_info: (dict, optional) Information about the device under test.
                         (dict, optional) Informationen über den Prüfling.
        :param ref_info: (dict, optional) Information about the reference device.
                         (dict, optional) Informationen über das Referenzgerät.
        :return: (str) The path to the generated report file.
                 (str) Der Pfad zur erstellten Protokolldatei.
        """
        # English: Use the report timestamp if provided, otherwise fall back to the data timestamp.
        # Deutsch: Verwende den Protokoll-Zeitstempel, falls vorhanden, ansonsten den Daten-Zeitstempel.
        actual_report_ts = report_ts if report_ts else data_ts

        # English: Get regression analysis data for power values.
        # Deutsch: Hole die Regressionsanalyse-Daten für die Leistungswerte.
        reg_data = DataAnalyzer.calculate_regression(self.device_path, data_ts)
        
        # --- FINAL SUGGESTION CALCULATION ---
        # --- BERECHNUNG DER FINALEN VORSCHLÄGE ---
        
        # English: VCal and ACal are always averaged across all steps.
        # Deutsch: VCal und ACal werden immer über alle Stufen gemittelt.
        avg_v = int(sum(r['Stufen_Cal']['VCal'] for r in all_results) / len(all_results))
        avg_a = int(sum(r['Stufen_Cal']['ACal'] for r in all_results) / len(all_results))
        
        # English: Calculate PowerCal using both methods (average and regression).
        # Deutsch: Berechne PowerCal über beide Methoden (Mittelwert und Regression).
        pcal_from_regression = 0
        pcal_from_avg = int(sum(r['Stufen_Cal']['WCal'] for r in all_results) / len(all_results))

        if reg_data and old_cal:
            p_reg = reg_data['Power']
            # English: The formula: Old value * slope of the correction.
            # Deutsch: Die eigentliche Formel: Alter Wert * Steigung der Korrektur.
            pcal_from_regression = int(old_cal.get('WCal', 12500) * p_reg['slope'])
                
        path = os.path.join(self.device_path, f"{actual_report_ts}_Protokoll.txt")

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"TASMOTA PRECISION CALIBRATION REPORT\n")
            f.write("="*85 + "\n")
            
            # --- DEVICE HEADER ---
            # --- GERÄTE-HEADER ---
            if dut_info:
                f.write("[PRÜFLING (DUT)]\n")
                f.write(f"  Device Name: {dut_info.get('name', 'k.A.')}\n")
                f.write(f"  Hostname:    {dut_info.get('host', 'k.A.')}\n")
                f.write(f"  MAC Address: {dut_info.get('mac', 'k.A.')}\n")
                f.write("\n")

            if ref_info:
                f.write("[REFERENZ]\n")
                if cal_mode == "PRO":
                    f.write("  Device: FLUKE 45 DUAL Mode Calculated Power (P)\n")
                else: # HOME
                    f.write(f"  Device Name: {ref_info.get('name', 'k.A.')}\n")
                    f.write(f"  Hostname:    {ref_info.get('host', 'k.A.')}\n")
                    f.write(f"  MAC Address: {ref_info.get('mac', 'k.A.')}\n")
            f.write("="*85 + "\n\n")
            # --- END HEADER ---

            f.write(f"MESSUNGSDETAILS\n")
            f.write(f"  Kalibrier-Modus:  {cal_mode}\n")
            f.write(f"  Datenquelle (CSV): {data_ts}\n")
            f.write(f"  Report erstellt:    {actual_report_ts}\n")
            f.write("="*85 + "\n")

            f.write("\n[1] EINZEL-AUSWERTUNG (Mittelwerte & Abweichungen pro Laststufe)\n")
            for res in all_results:
                f.write(f"\nSTUFE {res['Stufe']}:\n")
                f.write(f"  Spannung: Ref {res['Soll']['V']:>7.2f}V | DUT {res['Ist']['V']:>7.2f}V | "
                        f"Err: {res['Diff_Abs']['V']:>+6.2f}V ({res['Diff_Rel']['V']:>+6.2f}%) -> Cal-Vorschlag: {res['Stufen_Cal']['VCal']}\n")
                f.write(f"  Strom:    Ref {res['Soll']['A']:>7.3f}A | DUT {res['Ist']['A']:>7.3f}A | "
                        f"Err: {res['Diff_Abs']['A']:>+6.3f}A ({res['Diff_Rel']['A']:>+6.2f}%) -> Cal-Vorschlag: {res['Stufen_Cal']['ACal']}\n")
                f.write(f"  Leistung: Ref {res['Soll']['W']:>7.2f}W | DUT {res['Ist']['W']:>7.2f}W | "
                        f"Err: {res['Diff_Abs']['W']:>+6.2f}W ({res['Diff_Rel']['W']:>+6.2f}%) -> Cal-Vorschlag: {res['Stufen_Cal']['WCal']}\n")

            if reg_data:
                f.write("\n" + "="*85 + "\n")
                f.write("[2] ANALYSE DER AUSGLEICHSGERADE (NUR LEISTUNG)\n")
                f.write("Die Regression optimiert die Steigung m über alle Stufen hinweg (Nullpunkt-erzwungen).\n")
                p_reg = reg_data['Power']
                f.write(f"  Leistung (W): Steigung m = {p_reg['slope']:.6f} | Bestimmtheitsmaß R2 = {p_reg['r_squared']:.6f}\n")

                f.write("\n" + "="*85 + "\n")
                f.write("[3]    BESTEHENDE KALIBRIERWERTE            VORGESCHLAGENE KALIBRIERWERTE\n\n")
            
                oc_v = old_cal.get('VCal', '????') if old_cal else '????'
                oc_a = old_cal.get('ACal', '????') if old_cal else '????'
                oc_w = old_cal.get('WCal', '????') if old_cal else '????'

                f.write(f"    VoltageCal {str(oc_v):<15}          VoltageCal {avg_v} (Mittelwert der Stufen)\n")
                f.write(f"    CurrentCal {str(oc_a):<15}          CurrentCal {avg_a} (Mittelwert der Stufen)\n")
                f.write(f"      PowerCal {str(oc_w):<15}            PowerCal {pcal_from_regression} (aus Regression, empfohlen)\n")
                f.write(f"                                          └─ Alternative: {pcal_from_avg} (Mittelwert der Stufen)\n")

            f.write("\n" + "="*85 + "\n")
            f.write("ENDE DES PROTOKOLLS\n")
        
        print(f"\n[FERTIG] Detailliertes Protokoll erstellt: {path}")
        return path

    def write_reapply_summary(self, new_report_path, original_report_path, dut_info, ref_info):
        """
        # English:
        # Writes a short summary report for a "Re-Apply" action.
        # This report only documents that values from a previous report were applied.
        # Deutsch:
        # Schreibt ein kurzes Protokoll für eine "Re-Apply"-Aktion.
        # Dieses Protokoll dokumentiert nur, dass Werte aus einem früheren Protokoll angewendet wurden.

        :param new_report_path: (str) Path for the new, short report.
                                (str) Pfad für das neue, kurze Protokoll.
        :param original_report_path: (str) Path to the original report that was used.
                                     (str) Pfad zum ursprünglichen Protokoll, das verwendet wurde.
        :param dut_info: (dict) Information about the device under test.
                         (dict) Informationen über den Prüfling.
        :param ref_info: (dict) Information about the reference device (can be None).
                         (dict) Informationen über das Referenzgerät (kann None sein).
        :return: (str) The path to the generated report file.
                 (str) Der Pfad zur erstellten Protokolldatei.
        """
        with open(new_report_path, "w", encoding="utf-8") as f:
            f.write(f"TASMOTA RE-APPLY CALIBRATION REPORT\n")
            f.write("="*85 + "\n")
            
            if dut_info:
                f.write("[PRÜFLING (DUT)]\n")
                f.write(f"  Device Name: {dut_info.get('name', 'k.A.')}\n")
                f.write(f"  Hostname:    {dut_info.get('host', 'k.A.')}\n")
                f.write(f"  MAC Address: {dut_info.get('mac', 'k.A.')}\n")
                f.write("\n")

            f.write("[KALIBRIERUNGSQUELLE]\n")
            f.write(f"  Die angewendeten Kalibrierwerte wurden aus dem folgenden, bestehenden Report entnommen:\n")
            f.write(f"  -> {os.path.basename(original_report_path)}\n")
            f.write("="*85 + "\n")
        
        print(f"\n[FERTIG] Gekürztes Re-Apply Protokoll erstellt: {new_report_path}")
        return new_report_path