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
        # Calculates new calibration factors. It validates each measurement type (V, A, W)
        # series independently. Power is mandatory. V and A are optional and will be
        # skipped if their data series is incomplete (contains zeros).
        # Deutsch:
        # Berechnet neue Kalibrierfaktoren. Validiert jede Mess-Art (V, A, W)
        # unabhängig. Leistung ist obligatorisch. V und A sind optional und werden
        # übersprungen, wenn ihre Datenreihen unvollständig sind (Nullen enthalten).

        :param csv_file: Path to the CSV file with measurement data.
        :param old_cal: The existing calibration factors of the device.
        :return: A dictionary with calculated results, or None on failure.
        """
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"❌ Fehler beim Lesen der CSV {csv_file}: {e}")
            return None

        required_cols = ['Ref_Volt', 'Ref_Amp', 'Ref_Watt', 'Target_Volt', 'Target_Amp', 'Target_Watt']
        if not all(col in df.columns for col in required_cols):
            print(f"❌ Fehler: CSV {csv_file} enthält nicht alle erforderlichen Spalten.")
            return None

        if len(df) == 0:
            print(f"⚠️ Warnung: CSV {csv_file} ist leer.")
            return None

        # --- VALIDATION ---
        # English: Power series is mandatory. Abort if any value is zero.
        # Deutsch: Leistungs-Reihe ist obligatorisch. Abbruch, wenn ein Wert Null ist.
        if (df['Ref_Watt'] <= 0).any() or (df['Target_Watt'] <= 0).any():
            print("❌ FEHLER: Die Leistungs-Messreihe (Watt) ist unvollständig oder enthält Nullwerte. Dies ist ein Pflichtfeld. Berechnung abgebrochen.")
            return None

        # English: Voltage series is optional. Check if it's complete.
        # Deutsch: Spannungs-Reihe ist optional. Prüfe, ob sie vollständig ist.
        is_voltage_valid = (df['Ref_Volt'] > 0).all() and (df['Target_Volt'] > 0).all()
        if not is_voltage_valid:
            print("ℹ️ Hinweis: Spannungs-Messreihe (Volt) ist unvollständig. VCal-Berechnung wird übersprungen.")

        # English: Current series is optional. Check if it's complete.
        # Deutsch: Strom-Reihe ist optional. Prüfe, ob sie vollständig ist.
        is_current_valid = (df['Ref_Amp'] > 0).all() and (df['Target_Amp'] > 0).all()
        if not is_current_valid:
            print("ℹ️ Hinweis: Strom-Messreihe (Ampere) ist unvollständig. ACal-Berechnung wird übersprungen.")
            
        # --- CALCULATION OF MEAN VALUES ---
        # English: Use simple mean for manual calibration (max 3 values).
        # Deutsch: Einfachen Mittelwert für manuelle Kalibrierung nutzen (max. 3 Werte).
        soll = { "V": df['Ref_Volt'].mean(), "A": df['Ref_Amp'].mean(), "W": df['Ref_Watt'].mean() }
        ist = { "V": df['Target_Volt'].mean(), "A": df['Target_Amp'].mean(), "W": df['Target_Watt'].mean() }

        # --- CALCULATION OF NEW CALIBRATION FACTORS ---
        stufen_cal = {}
        
        # English: Calculate VCal only if the voltage series was valid.
        # Deutsch: VCal nur berechnen, wenn die Spannungs-Reihe gültig war.
        if is_voltage_valid:
            stufen_cal['VCal'] = int(old_cal['VCal'] * (soll['V'] / ist['V'])) if ist['V'] > 0 else old_cal['VCal']
        else:
            stufen_cal['VCal'] = old_cal['VCal'] # Pass through old value

        # English: Calculate ACal only if the current series was valid.
        # Deutsch: ACal nur berechnen, wenn die Strom-Reihe gültig war.
        if is_current_valid:
            stufen_cal['ACal'] = int(old_cal['ACal'] * (soll['A'] / ist['A'])) if ist['A'] > 0 else old_cal['ACal']
        else:
            stufen_cal['ACal'] = old_cal['ACal'] # Pass through old value

        # English: Power is always calculated as it's mandatory.
        # Deutsch: Leistung wird immer berechnet, da obligatorisch.
        stufen_cal['WCal'] = int(old_cal['WCal'] * (soll['W'] / ist['W'])) if ist['W'] > 0 else old_cal['WCal']

        # --- CALCULATE DIFFERENCES FOR REPORTING ---
        # English: Set diffs to 0 if calculation was skipped, to avoid errors in the report.
        # Deutsch: Setze Diffs auf 0, wenn die Berechnung übersprungen wurde, um Fehler im Report zu vermeiden.
        diff_abs = {
            'V': (ist['V'] - soll['V']) if is_voltage_valid else 0,
            'A': (ist['A'] - soll['A']) if is_current_valid else 0,
            'W': ist['W'] - soll['W']
        }
        diff_rel = {
            'V': (diff_abs['V'] / soll['V'] * 100) if is_voltage_valid and soll['V'] > 0 else 0,
            'A': (diff_abs['A'] / soll['A'] * 100) if is_current_valid and soll['A'] > 0 else 0,
            'W': (diff_abs['W'] / soll['W'] * 100) if soll['W'] > 0 else 0
        }

        # English: If a value was not calculated, don't show it in the 'Ist'/'Soll' report part.
        # Deutsch: Wenn ein Wert nicht berechnet wurde, zeige ihn nicht im 'Ist'/'Soll'-Teil des Reports.
        if not is_voltage_valid: soll['V'], ist['V'] = 0, 0
        if not is_current_valid: soll['A'], ist['A'] = 0, 0

        return {
            "Stufe": None, "Soll": soll, "Ist": ist,
            "Diff_Abs": diff_abs, "Diff_Rel": diff_rel,
            "Alt_Cal": old_cal, "Stufen_Cal": stufen_cal
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
            f.write(_("TASMOTA PRECISION CALIBRATION REPORT") + "\n")
            f.write("="*85 + "\n")
            
            # --- DEVICE HEADER ---
            # --- GERÄTE-HEADER ---
            if dut_info:
                f.write(_("[PRÜFLING (DUT)]") + "\n")
                f.write(_("  Device Name: {name}\n").format(name=dut_info.get('name', _('k.A.'))))
                f.write(_("  Hostname:    {host}\n").format(host=dut_info.get('host', _('k.A.'))))
                f.write(_("  MAC Address: {mac}\n").format(mac=dut_info.get('mac', _('k.A.'))))
                f.write("\n")

            if ref_info:
                f.write(_("[REFERENZ]") + "\n")
                if cal_mode == "PRO":
                    f.write(_("  Device: FLUKE 45 DUAL Mode Calculated Power (P)") + "\n")
                else: # HOME
                    f.write(_("  Device Name: {name}\n").format(name=ref_info.get('name', _('k.A.'))))
                    f.write(_("  Hostname:    {host}\n").format(host=ref_info.get('host', _('k.A.'))))
                    f.write(_("  MAC Address: {mac}\n").format(mac=ref_info.get('mac', _('k.A.'))))
            f.write("="*85 + "\n\n")
            # --- END HEADER ---

            f.write(_("MESSUNGSDETAILS") + "\n")
            f.write(_("  Kalibrier-Modus:  {cal_mode}\n").format(cal_mode=cal_mode))
            f.write(_("  Datenquelle (CSV): {data_ts}\n").format(data_ts=data_ts))
            f.write(_("  Report erstellt:    {actual_report_ts}\n").format(actual_report_ts=actual_report_ts))
            
            if cal_mode == "MANUAL":
                f.write("\n" + "="*85 + "\n")
                f.write(_("HINWEIS: Diese Kalibrierung wurde auf Basis manuell eingegebener Referenzwerte durchgeführt.") + "\n")

            f.write("="*85 + "\n")

            f.write("\n" + _("[1] EINZEL-AUSWERTUNG (Mittelwerte & Abweichungen pro Laststufe)") + "\n")
            for res in all_results:
                f.write(_("\nSTUFE {stufe}:\n").format(stufe=res['Stufe']))
                
                # English: Only show lines if the corresponding values are not zero.
                # Deutsch: Zeilen nur anzeigen, wenn die zugehörigen Werte nicht Null sind.
                if res['Soll']['V'] != 0 and res['Ist']['V'] != 0:
                    f.write(_("  Spannung: Ref {ref_v:>7.2f}V | DUT {dut_v:>7.2f}V | "
                            "Err: {err_abs_v:>+6.2f}V ({err_rel_v:>+6.2f}%) -> Cal-Vorschlag: {cal_v}\n").format(
                                ref_v=res['Soll']['V'], dut_v=res['Ist']['V'], 
                                err_abs_v=res['Diff_Abs']['V'], err_rel_v=res['Diff_Rel']['V'], cal_v=res['Stufen_Cal']['VCal']))
                
                if res['Soll']['A'] != 0 and res['Ist']['A'] != 0:
                    f.write(_("  Strom:    Ref {ref_a:>7.3f}A | DUT {dut_a:>7.3f}A | "
                            "Err: {err_abs_a:>+6.3f}A ({err_rel_a:>+6.2f}%) -> Cal-Vorschlag: {cal_a}\n").format(
                                ref_a=res['Soll']['A'], dut_a=res['Ist']['A'], 
                                err_abs_a=res['Diff_Abs']['A'], err_rel_a=res['Diff_Rel']['A'], cal_a=res['Stufen_Cal']['ACal']))

                f.write(_("  Leistung: Ref {ref_w:>7.2f}W | DUT {dut_w:>7.2f}W | "
                        "Err: {err_abs_w:>+6.2f}W ({err_rel_w:>+6.2f}%) -> Cal-Vorschlag: {cal_w}\n").format(
                            ref_w=res['Soll']['W'], dut_w=res['Ist']['W'], 
                            err_abs_w=res['Diff_Abs']['W'], err_rel_w=res['Diff_Rel']['W'], cal_w=res['Stufen_Cal']['WCal']))

            # English: Suppress regression section for HOME and MANUAL mode as it's not applicable.
            # Deutsch: Regressions-Abschnitt für HOME- und MANUAL-Modus unterdrücken, da nicht anwendbar.
            if reg_data and cal_mode == "PRO":
                f.write("\n" + "="*85 + "\n")
                f.write(_("[2] ANALYSE DER AUSGLEICHSGERADE (NUR LEISTUNG)") + "\n")
                f.write(_("Die Regression optimiert die Steigung m über alle Stufen hinweg (Nullpunkt-erzwungen).") + "\n")
                p_reg = reg_data['Power']
                f.write(_("  Leistung (W): Steigung m = {slope:.6f} | Bestimmtheitsmaß R2 = {r_squared:.6f}\n").format(slope=p_reg['slope'], r_squared=p_reg['r_squared']))

            f.write("\n" + "="*85 + "\n")
            f.write(_("[3]    BESTEHENDE KALIBRIERWERTE            VORGESCHLAGENE KALIBRIERWERTE") + "\n\n")
        
            oc_v = old_cal.get('VCal', _('????')) if old_cal else _('????')
            oc_a = old_cal.get('ACal', _('????')) if old_cal else _('????')
            oc_w = old_cal.get('WCal', _('????')) if old_cal else _('????')

            # English: Display suggestions (always show Voltage/Current for completeness).
            # Deutsch: Vorschläge anzeigen (Spannung/Strom zur Vollständigkeit immer einblenden).
            f.write(_("    VoltageCal {oc_v:<15}          VoltageCal {avg_v} (Mittelwert der Stufen)\n").format(oc_v=str(oc_v), avg_v=avg_v))
            f.write(_("    CurrentCal {oc_a:<15}          CurrentCal {avg_a} (Mittelwert der Stufen)\n").format(oc_a=str(oc_a), avg_a=avg_a))

            if cal_mode == "PRO":
                f.write(_("      PowerCal {oc_w:<15}            PowerCal {pcal_from_regression} (aus Regression, empfohlen)\n").format(oc_w=str(oc_w), pcal_from_regression=pcal_from_regression))
                f.write(_("                                          └─ Alternative: {pcal_from_avg} (Mittelwert der Stufen)\n").format(pcal_from_avg=pcal_from_avg))
            else: # HOME or MANUAL
                f.write(_("      PowerCal {oc_w:<15}            PowerCal {pcal_from_avg} (Mittelwert)\n").format(oc_w=str(oc_w), pcal_from_avg=pcal_from_avg))

            f.write("\n" + "="*85 + "\n")
            f.write(_("ENDE DES PROTOKOLLS") + "\n")
        
        print(_("\n[FERTIG] Detailliertes Protokoll erstellt: {path}").format(path=path))
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
            f.write(_("TASMOTA RE-APPLY CALIBRATION REPORT") + "\n")
            f.write("="*85 + "\n")
            
            if dut_info:
                f.write(_("[PRÜFLING (DUT)]") + "\n")
                f.write(_("  Device Name: {name}\n").format(name=dut_info.get('name', _('k.A.'))))
                f.write(_("  Hostname:    {host}\n").format(host=dut_info.get('host', _('k.A.'))))
                f.write(_("  MAC Address: {mac}\n").format(mac=dut_info.get('mac', _('k.A.'))))
                f.write("\n")

            f.write(_("[KALIBRIERUNGSQUELLE]") + "\n")
            f.write(_("  Die angewendeten Kalibrierwerte wurden aus dem folgenden, bestehenden Report entnommen:\n") + "\n")
            f.write(_("  -> {original_report_path_basename}\n").format(original_report_path_basename=os.path.basename(original_report_path)))
            f.write("="*85 + "\n")
        
        print(_("\n[FERTIG] Gekürztes Re-Apply Protokoll erstellt: {new_report_path}").format(new_report_path=new_report_path))
        return new_report_path