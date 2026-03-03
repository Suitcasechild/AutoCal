import sys
import os
import time
import re
import json
import httpx
import glob
import numpy as np
import pandas as pd
from datetime import datetime
from collections import deque
import pyqtgraph as pg
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QMessageBox, 
                               QDialog, QTextEdit, QHBoxLayout, QPushButton, QFileDialog,
                               QLabel, QLineEdit, QTextBrowser, QCheckBox, QFrame)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QThread, Signal, QObject, Qt
from PySide6.QtGui import QActionGroup # Corrected import for QActionGroup

# Internationalisierung / Internationalization
from i18n_manager import setup_translation
# Set up translation as early as possible
_ = setup_translation()

# Import deiner bestehenden Konfigurations-Logik
from config_manager import ConfigManager
from reference_manager import ReferenceManager
from data_analyzer import DataAnalyzer
from credential_manager import CredentialsManager
from fluke_scan import find_fluke
from assets_guidance import get_guidance_html
from assets_manual_info import MANUAL_INFO_HTML
from man_calib_engine import ManualCalibrationEngine
from dynamic_cal_dialog import DynamicCalDialog

# ---------------------------------------------------------
# 1. DER LOG-SPION (Log Spy)
# ---------------------------------------------------------
class OutputStreamProxy(QObject):
    """
    # English:
    # A proxy object that captures stdout/stderr and emits it as a Qt signal.
    # This allows redirecting console output (like print statements) to a GUI widget.
    # Deutsch:
    # Ein Proxy-Objekt, das stdout/stderr abfängt und als Qt-Signal aussendet.
    # Dies ermöglicht die Umleitung von Konsolenausgaben (wie print-Anweisungen) in ein GUI-Widget.
    """
    message_signal = Signal(str)

    def write(self, text):
        """
        # English:
        # This method is called whenever something is written to the proxied stream.
        # It emits the text via the message_signal.
        # Deutsch:
        # Diese Methode wird aufgerufen, wann immer etwas in den umgeleiteten Stream geschrieben wird.
        # Sie sendet den Text über das message_signal aus.
        """
        if text and text.strip():
            self.message_signal.emit(text.strip())

    def flush(self):
        """
        # English: A required method for a stream-like object, does nothing here.
        # Deutsch: Eine erforderliche Methode für ein stream-artiges Objekt, macht hier nichts.
        """
        pass

# ---------------------------------------------------------
# 2. DER MESS-ARBEITER (Hintergrund-Thread)
# ---------------------------------------------------------
class BaseWorker(QThread):
    """
    # English: Base class for background workers, providing common signals and methods.
    # Deutsch: Basisklasse für Hintergrund-Worker, die gemeinsame Signale und Methoden bereitstellt.
    """
    log_signal = Signal(str)
    finished_signal = Signal(str)
    show_popup_signal = Signal(str)
    hide_popup_signal = Signal()

    def __init__(self, credentials_manager):
        super().__init__()
        self.credentials_manager = credentials_manager
        self.is_running = True

    def _get_auth(self, ip):
        creds = self.credentials_manager.get_credentials(ip)
        if creds:
            return (creds['user'], creds['password'])
        return None

    def wait_for_power(self, ip, stufe):
        msg = _("STUFE {stufe}:\nWarte auf Leistung...\n\nBitte Ziel-Dose jetzt EINSCHALTEN!").format(stufe=stufe)
        self.log_signal.emit(f"⏳ STUFE {stufe}: Warte auf Leistung...")
        self.show_popup_signal.emit(msg)
        auth = self._get_auth(ip)
        while self.is_running:
            try:
                r = httpx.get(f"http://{ip}/cm?cmnd=Status%2011", timeout=2.0, auth=auth)
                r.raise_for_status()
                if r.json()['StatusSTS']['POWER'] == 'ON':
                    self.log_signal.emit(f"✅ Power ON erkannt! Starte Inrush-Filter (7s)...")
                    self.hide_popup_signal.emit()
                    return True
            except Exception as e:
                self.log_signal.emit(f"Fehler in wait_for_power: {e}")
                time.sleep(1)
        self.hide_popup_signal.emit()
        return False 

    def stop(self):
        self.is_running = False

class MeasurementWorker(BaseWorker):
    """
    # English: Worker for the main automated measurement process.
    # Deutsch: Worker für den automatischen Haupt-Messprozess.
    """
    data_signal = Signal(dict)
    apply_request_signal = Signal(str, str, list, str, str, str) 
    step_progress_signal = Signal(int)
    
    def __init__(self, config, params, credentials_manager):
        super().__init__(credentials_manager)
        self.config = config
        self.params = params

    def run(self):
        try:
            from calibration_engine import CalibrationEngine
            dut_ip = self.params['dut_ip']
            ref_ip = self.params['ref_ip']
            mode = self.params['mode']
            data_ts = self.params['session_ts']
            use_existing = self.params.get('use_existing', False)
            dut_info_str = json.dumps(self.params.get('dut_info'))
            ref_info_str = json.dumps(self.params.get('ref_info'))
            dut_auth = self._get_auth(dut_ip)
            ref_auth = self._get_auth(ref_ip)

            if use_existing:
                self.log_signal.emit(f"🔄 Lese alten Report ({data_ts})...")
                old_report_path = os.path.join(self.params['device_path'], f"{data_ts}_Protokoll.txt")
                if not os.path.exists(old_report_path):
                    self.finished_signal.emit(f"❌ Fehler: Der ursprüngliche Report '{old_report_path}' wurde nicht gefunden.")
                    return
                self.apply_request_signal.emit(old_report_path, dut_ip, [], dut_info_str, ref_info_str, mode)
                return

            ref_manager = ReferenceManager(self.config)
            old_cal = ref_manager.get_current_cal_factors(dut_ip, dut_auth)
            engine = CalibrationEngine(self.params['device_path'])
            all_results = []

            self.log_signal.emit("🔄 Initialisiere Referenz-Hardware...")
            if mode == "PRO":
                if not ref_manager.set_mode('PRO'):
                    self.finished_signal.emit("❌ ABBRUCH: COM-Port Fehler! Fluke antwortet nicht oder Kabel fehlt.")
                    return
            else:
                ref_manager.set_mode('HOME')

            from main import prepare_dut
            prepare_dut(dut_ip, dut_auth)

            if mode == "HOME":
                self.log_signal.emit("🔌 Schalte Ziel-Dose für Offset-Messung AUS...")
                try:
                    httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2, auth=dut_auth)
                    time.sleep(2) 
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Warnung: Automatisches Ausschalten fehlgeschlagen: {e}")
                if not self.is_running: return
                self.log_signal.emit("⏳ Warte 5 Sekunden, bis Ziel-Dose vollständig AUS ist...")
                time.sleep(5)
                from refhome_offset import ermittle_offset
                offset_a, offset_w = ermittle_offset(ref_ip, ref_auth)
                ref_manager.set_home_offset(offset_a, offset_w)

            num_measurements_compensated = self.params['measurements'] + 2

            for stufe in range(1, self.params['steps'] + 1):
                if not self.is_running: break
                if not self.wait_for_power(dut_ip, stufe): break 
                time.sleep(7) 
                if not self.is_running: break

                self.log_signal.emit(f"\n▶️ Zeichne Messdaten auf (Stufe {stufe}/{self.params['steps']} | {num_measurements_compensated} Messungen)...")
                step_data_list = []
                
                while len(step_data_list) < num_measurements_compensated:
                    if not self.is_running: break
                    try:
                        ref_v, ref_a, ref_w = ref_manager.get_reference_data(ref_auth)
                        r = httpx.get(f"http://{dut_ip}/cm?cmnd=Status%208", timeout=2, auth=dut_auth)
                        r.raise_for_status()
                        d = r.json()['StatusSNS']['ENERGY']
                        dut_v, dut_a, dut_w = float(d['Voltage']), float(d['Current']), float(d['Power'])
                        
                        if any(val == 0 for val in [ref_v, ref_a, ref_w, dut_v, dut_a, dut_w] if val is not None):
                            self.log_signal.emit(f"[WARN] Ungültige Messung (0-Wert). Wiederhole...")
                            time.sleep(0.5)
                            continue

                        self.data_signal.emit({'volt_ref': ref_v, 'volt_dut': dut_v, 'amp_ref': ref_a, 'amp_dut': dut_a, 'watt_ref': ref_w, 'watt_dut': dut_w, 'dut_off': (dut_w <= 0) })
                        step_data_list.append({'Ref_Volt': ref_v, 'Ref_Amp': ref_a, 'Ref_Watt': ref_w, 'Target_Volt': dut_v, 'Target_Amp': dut_a, 'Target_Watt': dut_w})
                        progress_val = int((len(step_data_list) / num_measurements_compensated) * 100)
                        self.step_progress_signal.emit(progress_val)
                        time.sleep(1)
                    except Exception as e:
                        self.log_signal.emit(f"❌ Fehler beim Lesen der Messwerte: {e}. Wiederhole...")
                        time.sleep(0.5)
                        continue

                if step_data_list and self.is_running:
                    df = pd.DataFrame(step_data_list)
                    for col in ["Ref_Volt", "Ref_Amp", "Ref_Watt", "Target_Volt", "Target_Amp", "Target_Watt"]:
                        if col in df.columns: df[col] = df[col].round(3)
                    csv_name = f"{data_ts}_Stufe_{stufe}.csv"
                    csv_path = os.path.join(self.params['device_path'], csv_name)
                    df.to_csv(csv_path, index=False)
                    self.log_signal.emit(f"💾 {csv_name} gespeichert.")
                    res = engine.calculate_new_calibration(csv_path, old_cal)
                    res['Stufe'] = stufe
                    all_results.append(res)
                    try:
                        self.log_signal.emit(f"🔌 Schalte Ziel-Dose nach Stufe {stufe} AUS...")
                        self.data_signal.emit({'volt_ref': None, 'volt_dut': 0.0, 'amp_ref': None, 'amp_dut': 0.0, 'watt_ref': None, 'watt_dut': 0.0, 'dut_off': True})
                        httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2, auth=dut_auth)
                        time.sleep(3.0)
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ Warnung: Konnte Ziel-Dose nicht ausschalten: {e}")

            if all_results and self.is_running:
                self.data_signal.emit({'volt_ref': None, 'volt_dut': 0.0, 'amp_ref': None, 'amp_dut': 0.0, 'watt_ref': None, 'watt_dut': 0.0, 'dut_off': True})
                report_file = engine.write_summary(
                    all_results, data_ts, report_ts=data_ts, cal_mode=mode,
                    old_cal=old_cal, dut_info=self.params.get('dut_info'), ref_info=self.params.get('ref_info')
                )
                self.log_signal.emit("\n" + "="*40 + "\nERMITTLUNG DER KALIBRIERWERTE ABGESCHLOSSEN\n" + "="*40)
                self.apply_request_signal.emit(report_file, dut_ip, all_results, dut_info_str, ref_info_str, mode)
            elif not self.is_running:
                try:
                    self.log_signal.emit("🔌 Abbruch erkannt: Schalte Ziel-Dose AUS...")
                    httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2, auth=dut_auth)
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Warnung: Zieldose konnte beim Abbruch nicht ausgeschaltet werden: {e}")
                self.finished_signal.emit("⚠️ Messung wurde vom Benutzer abgebrochen.")
            else:
                self.finished_signal.emit("ℹ️ Messung beendet, aber es wurden keine Ergebnisse zum Anwenden generiert.")
        except Exception as e:
            self.finished_signal.emit(f"❌ Schwerer Fehler im Worker: {str(e)}")

class ManualSetupWorker(BaseWorker):
    """
    # English: Worker to prepare the DUT and wait for power-on in manual mode.
    # Deutsch: Worker, der die DUT im manuellen Modus vorbereitet und auf das Einschalten wartet.
    """
    def __init__(self, dut_ip, dut_auth, credentials_manager):
        super().__init__(credentials_manager)
        self.dut_ip = dut_ip
        self.dut_auth = dut_auth

    def run(self):
        try:
            from main import prepare_dut
            self.log_signal.emit(_("INFO: Bereite Ziel-Dose (DUT) vor..."))
            prepare_dut(self.dut_ip, self.dut_auth)
            if self.wait_for_power(self.dut_ip, 1):
                self.finished_signal.emit("SUCCESS")
            else:
                self.finished_signal.emit(_("INFO: Vorbereitung durch Benutzer abgebrochen oder fehlgeschlagen."))
        except Exception as e:
            self.finished_signal.emit(_("FEHLER bei der Vorbereitung: {e}").format(e=e))

# ---------------------------------------------------------
# 3. DAS PROTOKOLL-POPUP (Custom Dialog)
# ---------------------------------------------------------
class CalibrationReportDialog(QDialog):
    """
    # English:
    # A custom dialog to display the calibration report. It allows selective 
    # application of calibration factors via checkboxes.
    # Deutsch:
    # Ein benutzerdefinierter Dialog zur Anzeige des Kalibrierungsprotokolls. 
    # Erlaubt die selektive Anwendung von Kalibrierfaktoren über Checkboxen.
    """
    def __init__(self, parent, target_ip, final_values, old_factors, is_reapply, report_info, credentials_manager, config):
        super().__init__(parent)
        self.target_ip = target_ip
        self.final_values = final_values
        self.old_factors = old_factors
        self.is_reapply = is_reapply
        self.report_info = report_info 
        self.credentials_manager = credentials_manager
        self.config = config
        self.log_callback = parent.ui.log_output.appendPlainText
        self.current_report_path = report_info['original_path']

        self.setWindowTitle(_("Kalibrierungsprotokoll & Auswahl"))
        self.resize(900, 800) 
        self.layout = QVBoxLayout(self)

        # English: Report display (Text Area)
        # Deutsch: Protokoll-Anzeige (Textbereich)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("font-family: Consolas, 'Courier New', monospace; font-size: 12px; background-color: #1e1e1e; color: #d4d4d4;")
        self.layout.addWidget(self.text_edit)
        self.load_report_text()

        # --- INFO AREA (Deviations) ---
        self.info_frame = QFrame(self)
        self.info_frame.setFrameShape(QFrame.StyledPanel)
        self.info_frame.setStyleSheet("background-color: #252525; border-radius: 5px; padding: 5px;")
        self.info_layout = QVBoxLayout(self.info_frame)
        self.layout.addWidget(self.info_frame)

        self.lbl_v_info = QLabel(self)
        self.lbl_a_info = QLabel(self)
        self.lbl_w_info = QLabel(self)
        for lbl in [self.lbl_v_info, self.lbl_a_info, self.lbl_w_info]:
            lbl.setStyleSheet("font-weight: bold;")
            self.info_layout.addWidget(lbl)

        # --- CHECKBOX AREA ---
        self.check_layout = QHBoxLayout()
        self.check_v = QCheckBox("VoltageCal")
        self.check_a = QCheckBox("CurrentCal")
        self.check_w_mean = QCheckBox("PowerCal (Mean)")
        self.check_w_regr = QCheckBox("PowerCal (Regression)")
        
        for cb in [self.check_v, self.check_a, self.check_w_mean, self.check_w_regr]:
            self.check_layout.addWidget(cb)
        self.layout.addLayout(self.check_layout)

        # English: Exclusive logic for PowerCal.
        # Deutsch: Exklusive Logik für PowerCal.
        self.check_w_mean.toggled.connect(lambda c: self.check_w_regr.setChecked(False) if c else None)
        self.check_w_regr.toggled.connect(lambda c: self.check_w_mean.setChecked(False) if c else None)

        # --- Calculate Deviations and Init UI ---
        self.init_selection_logic()

        # --- BUTTON AREA ---
        self.btn_layout = QHBoxLayout()
        self.btn_graph = QPushButton(_("📊 REGRESSIONS-GRAPH"))
        self.btn_graph.setStyleSheet("background-color: #0055a4; color: white; font-weight: bold; padding: 10px;")
        self.btn_graph.clicked.connect(self.show_regression_graph)
        
        self.btn_cancel = QPushButton(_("ABBRECHEN"))
        self.btn_cancel.setStyleSheet("background-color: #444; color: white; font-weight: bold; padding: 10px;")
        self.btn_cancel.clicked.connect(self.reject) 

        self.btn_calibrate = QPushButton(_("AUSWAHL KALIBRIEREN"))
        self.btn_calibrate.setStyleSheet("background-color: darkgreen; color: white; font-weight: bold; padding: 10px;")
        self.btn_calibrate.clicked.connect(self.apply_calibration_action)

        self.btn_close = QPushButton(_("SCHLIESSEN"))
        self.btn_close.setStyleSheet("background-color: #444; color: white; font-weight: bold; padding: 10px;")
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.hide()

        self.btn_layout.addWidget(self.btn_graph)
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addWidget(self.btn_calibrate)
        self.btn_layout.addWidget(self.btn_close)
        self.layout.addLayout(self.btn_layout)

        # English: Hide regression-related elements in HOME or MANUAL mode.
        # Deutsch: Regressions-bezogene Elemente im HOME- oder MANUAL-Modus ausblenden.
        cal_mode = self.report_info.get('mode')
        if cal_mode == "HOME" or cal_mode == "MANUAL":
            self.btn_graph.hide()
            self.check_w_regr.hide()
            self.check_w_mean.setText("PowerCal")

    def init_selection_logic(self):
        """
        # English: Calculates deviations and sets checkboxes/labels accordingly.
        # Deutsch: Berechnet Abweichungen und setzt Checkboxen/Labels entsprechend.
        """
        def get_dev(new, old):
            if not old or old == 0: return 0.0
            return ((new / old) - 1) * 100

        dev_v = get_dev(self.final_values['vcal'], self.old_factors.get('VCal', 20230))
        dev_a = get_dev(self.final_values['acal'], self.old_factors.get('ACal', 2500))
        dev_w = get_dev(self.final_values['pcal_avg'], self.old_factors.get('WCal', 12500))

        # English: Read limits from config with fallbacks.
        # Deutsch: Lese Limits aus der Konfiguration mit Fallbacks.
        limit_v = self.config.getfloat('TOLERANCE abs%', 'voltage_limit', fallback=0.5)
        limit_a = self.config.getfloat('TOLERANCE abs%', 'current_limit', fallback=0.5)
        limit_w = self.config.getfloat('TOLERANCE abs%', 'power_limit', fallback=5.0)

        # --- Voltage ---
        if abs(dev_v) <= limit_v:
            self.lbl_v_info.setText(_("✅ Spannungsmessung: Abweichung {dev_v:+.2f}% im Toleranzbereich ({limit_v}%). Kalibrierung optional.").format(dev_v=dev_v, limit_v=limit_v))
            self.lbl_v_info.setStyleSheet("color: #4caf50;")
            self.check_v.setChecked(False)
        else:
            self.lbl_v_info.setText(_("⚠️ Spannungsmessung: Abweichung {dev_v:+.2f}% außerhalb Toleranz ({limit_v}%). Kalibrierung empfohlen!").format(dev_v=dev_v, limit_v=limit_v))
            self.lbl_v_info.setStyleSheet("color: #ff9800;")
            self.check_v.setChecked(True)

        # --- Current ---
        if abs(dev_a) <= limit_a:
            self.lbl_a_info.setText(_("✅ Strommessung: Abweichung {dev_a:+.2f}% im Toleranzbereich ({limit_a}%). Kalibrierung optional.").format(dev_a=dev_a, limit_a=limit_a))
            self.lbl_a_info.setStyleSheet("color: #4caf50;")
            self.check_a.setChecked(False)
        else:
            self.lbl_a_info.setText(_("⚠️ Strommessung: Abweichung {dev_a:+.2f}% außerhalb Toleranz ({limit_a}%). Kalibrierung empfohlen!").format(dev_a=dev_a, limit_a=limit_a))
            self.lbl_a_info.setStyleSheet("color: #ff9800;")
            self.check_a.setChecked(True)

        # --- Power ---
        if abs(dev_w) <= limit_w:
            self.lbl_w_info.setText(_("✅ Leistungsmessung: Abweichung {dev_w:+.2f}% im Toleranzbereich ({limit_w}%). Kalibrierung optional.").format(dev_w=dev_w, limit_w=limit_w))
            self.lbl_w_info.setStyleSheet("color: #4caf50;")
            self.check_w_mean.setChecked(False)
        else:
            self.lbl_w_info.setText(_("⚠️ Leistungsmessung: Abweichung {dev_w:+.2f}% außerhalb Toleranz ({limit_w}%). Kalibrierung empfohlen!").format(dev_w=dev_w, limit_w=limit_w))
            self.lbl_w_info.setStyleSheet("color: #ff9800;")
            self.check_w_mean.setChecked(True)

    def load_report_text(self):
        try:
            with open(self.current_report_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            self.text_edit.setPlainText(content)
            self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        except Exception as e:
            self.text_edit.setPlainText(f"Fehler beim Laden des Berichts:\n{e}")

    def show_regression_graph(self):
        if self.is_reapply:
            QMessageBox.warning(self, _("Keine Daten"), _("Die Regressions-Grafik ist nur bei einer neuen Messung verfügbar."))
            return
        search_path = os.path.join(self.report_info['device_path'], f"{self.report_info['session_ts']}_Stufe_*.csv")
        files = glob.glob(search_path)
        if not files: return
        df_list = [pd.read_csv(f) for f in files]
        full_df = pd.concat(df_list, ignore_index=True)
        x, y = full_df['Target_Watt'].values, full_df['Ref_Watt'].values
        if len(x) == 0: return
        m, unused_residuals, unused_rank, unused_s = np.linalg.lstsq(x[:, np.newaxis], y, rcond=None)
        slope = float(m[0])
        graph_dialog = QDialog(self)
        graph_dialog.setWindowTitle(_("Regressions-Analyse (Leistung) | Steigung m = {slope:.5f}").format(slope=slope))
        graph_dialog.resize(800, 600)
        layout = QVBoxLayout(graph_dialog)
        plot_widget = pg.PlotWidget(background='#1e1e1e')
        layout.addWidget(plot_widget)
        plot_widget.plot(x, y, pen=None, symbol='o', symbolSize=7, symbolBrush=(255, 255, 255, 150))
        max_val = max(max(x), max(y)) * 1.05
        x_line = np.array([0, max_val])
        plot_widget.plot(x_line, x_line, pen=pg.mkPen('y', width=2, style=Qt.DashLine))
        plot_widget.plot(x_line, x_line * slope, pen=pg.mkPen('g', width=3))
        graph_dialog.exec()

    def apply_calibration_action(self):
        """
        # English: Reads checkbox states and applies the selected values.
        # Deutsch: Liest Checkbox-Zustände aus und wendet die gewählten Werte an.
        """
        v_val = self.final_values['vcal'] if self.check_v.isChecked() else None
        a_val = self.final_values['acal'] if self.check_a.isChecked() else None
        
        w_val = None
        if self.check_w_mean.isChecked():
            w_val = self.final_values['pcal_avg']
        elif self.check_w_regr.isChecked():
            w_val = self.final_values['pcal_regression']

        if v_val is None and a_val is None and w_val is None:
            return QMessageBox.warning(self, _("Keine Auswahl"), _("Bitte wählen Sie mindestens einen Wert zur Kalibrierung aus."))

        self.btn_calibrate.hide()
        self.btn_cancel.hide()
        QApplication.processEvents()

        from send_cal import apply_calibration
        from calibration_engine import CalibrationEngine

        self.log_callback(_("\n🚀 Starte selektive Übertragung an die Dose..."))
        
        try:
            auth = None
            creds = self.credentials_manager.get_credentials(self.target_ip)
            if creds: auth = (creds['user'], creds['password'])
                
            as_found_left_string = apply_calibration(self.target_ip, v_val, a_val, w_val, auth=auth)

            if as_found_left_string:
                self.log_callback("✅ Übertragung abgeschlossen.")
                report_to_update = self.report_info['original_path']
                engine = CalibrationEngine(self.report_info['device_path'])

                if self.is_reapply:
                    new_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_report_path = os.path.join(self.report_info['device_path'], f"{new_ts}_ReApply_Protokoll.txt")
                    engine.write_reapply_summary(new_report_path, self.report_info['original_path'], self.report_info['dut_info'], self.report_info['ref_info'])
                    report_to_update = new_report_path
                
                try:
                    with open(report_to_update, "a", encoding="utf-8") as f:
                        f.write(as_found_left_string)
                    self.current_report_path = report_to_update
                    self.load_report_text()
                except Exception as e:
                    self.log_callback(f"❌ Fehler beim Aktualisieren des Reports: {e}")
            else:
                self.log_callback("❌ Übertragung fehlgeschlagen.")
        except Exception as e:
            self.log_callback(f"❌ Unerwarteter Fehler: {e}")
        finally:
            self.btn_close.show()


# ---------------------------------------------------------
# 3. DER FLUKE-SUCHER (Hintergrund-Thread)
# ---------------------------------------------------------
class FlukeScanWorker(QThread):
    """
    # English:
    # A QThread worker that scans all serial ports for a Fluke 45 multimeter
    # in the background to keep the GUI responsive.
    # Deutsch:
    # Ein QThread-Worker, der im Hintergrund alle seriellen Ports nach einem
    # Fluke 45 Multimeter scannt, um die GUI reaktionsfähig zu halten.
    """
    progress_signal = Signal(int)
    finished_signal = Signal(dict) # Returns result dict or None

    def __init__(self, current_port=None, current_baud=None):
        super().__init__()
        self.current_port = current_port
        self.current_baud = current_baud

    def run(self):
        # English: Call the scan logic from fluke_scan.py.
        # Deutsch: Rufe die Scan-Logik aus fluke_scan.py auf.
        result = find_fluke(
            current_port=self.current_port, 
            current_baud=self.current_baud, 
            progress_callback=self.progress_signal.emit
        )
        self.finished_signal.emit(result if result else {})


# ---------------------------------------------------------
# 4. DAS CREDENTIAL-POPUP (Custom Dialog)
# ---------------------------------------------------------
class CredentialDialog(QDialog):
    """
    # English: A dialog to ask the user for username and password.
    # Deutsch: Ein Dialog, um den Benutzer nach Benutzername und Passwort zu fragen.
    """
    def __init__(self, device_name, attempt=1, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Zugangsdaten für {device_name}").format(device_name=device_name))
        self.setModal(True)

        self.layout = QVBoxLayout(self)

        # English: Add a descriptive label
        # Deutsch: Füge ein beschreibendes Label hinzu
        self.info_label = QLabel(_("Zugangsdaten für '{device_name}' erforderlich (Versuch {attempt}/3).").format(device_name=device_name, attempt=attempt))
        self.layout.addWidget(self.info_label)

        # English: Username field
        # Deutsch: Benutzername-Feld
        self.user_label = QLabel(_("Benutzername:"))
        self.user_input = QLineEdit(self)
        self.user_input.setText("admin") # English: Default Tasmota user. / Deutsch: Standard Tasmota-User.
        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.user_input)

        # English: Password field
        # Deutsch: Passwort-Feld
        self.pass_label = QLabel(_("Passwort:"))
        self.pass_input = QLineEdit(self)
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFocus() # English: Focus on password field for faster typing. / Deutsch: Fokus auf Passwortfeld.
        self.layout.addWidget(self.pass_label)
        self.layout.addWidget(self.pass_input)
        
        # Deutsch: Hinweis zur Speicherung der Zugangsdaten.
        self.disclaimer_label = QLabel(
            _("<i>Die Zugangsdaten werden für die Dauer dieser Programmsitzung sicher im Arbeitsspeicher gehalten und beim Beenden der Anwendung automatisch gelöscht.</i>")
        )
        self.disclaimer_label.setWordWrap(True)
        self.layout.addWidget(self.disclaimer_label)

        # English: OK and Cancel buttons
        # Deutsch: OK- und Abbrechen-Buttons
        self.btn_layout = QHBoxLayout()
        self.ok_button = QPushButton(_("OK"), self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton(_("Abbrechen"), self)
        self.cancel_button.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.ok_button)
        self.btn_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.btn_layout)

    def get_credentials(self):
        """
        # English: Returns the entered username and password.
        # Deutsch: Gibt den eingegebenen Benutzernamen und das Passwort zurück.
        """
        return self.user_input.text().strip(), self.pass_input.text()


# ---------------------------------------------------------
# 5. DAS HILFE-FENSTER (Anleitung)
# ---------------------------------------------------------
class GuidanceWindow(QDialog):
    """
    # English: A separate window for displaying the instructional manual in HTML format.
    # Deutsch: Ein separates Fenster zur Anzeige der Bedienungsanleitung im HTML-Format.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Bedienungsanleitung"))
        self.resize(800, 700)
        
        # English: Non-modal, so main window stays interactive.
        # Deutsch: Nicht-modal, damit das Hauptfenster interaktiv bleibt.
        self.setModal(False)
        
        self.layout = QVBoxLayout(self)
        
        # English: Create a QTextBrowser to render HTML content.
        # Deutsch: Erstelle einen QTextBrowser zum Rendern von HTML-Inhalten.
        self.browser = QTextBrowser(self)
        self.browser.setHtml(get_guidance_html(_))
        
        # English: Enable internal link navigation (anchors).
        # Deutsch: Aktiviere die Navigation für interne Links (Anker).
        self.browser.setOpenLinks(False)
        self.browser.anchorClicked.connect(self.browser.setSource)
        
        self.layout.addWidget(self.browser)
        
        # English: Add a close button.
        # Deutsch: Füge einen Schließen-Button hinzu.
        self.btn_close = QPushButton(_("Schließen"), self)
        self.btn_close.clicked.connect(self.close)
        self.layout.addWidget(self.btn_close)


# ---------------------------------------------------------
# 6. DAS HAUPTFENSTER (GUI)
# ---------------------------------------------------------
class MainWindow(QMainWindow):
    """
    # English:
    # The main window of the application. It loads the UI, sets up all connections,
    # handles user interactions, and manages the measurement process.
    # Deutsch:
    # Das Hauptfenster der Anwendung. Es lädt die Benutzeroberfläche, richtet alle
    # Verbindungen ein, behandelt Benutzerinteraktionen und verwaltet den Messprozess.
    """
    def __init__(self):
        """
        # English: Initializes the main window, loads the UI file, and sets up all components.
        # Deutsch: Initialisiert das Hauptfenster, lädt die UI-Datei und richtet alle Komponenten ein.
        """
        super().__init__()
        self.cm = ConfigManager()
        self.credentials_manager = CredentialsManager()
        self.wait_msgbox = None   
        self.guidance_window = None
        self.manual_worker = None
        self.is_in_manual_entry_mode = False
        
        # English: Load the UI from the .ui file created with Qt Designer.
        # Deutsch: Lade die Benutzeroberfläche aus der .ui-Datei, die mit dem Qt Designer erstellt wurde.
        ui_path = os.path.join(os.path.dirname(__file__), "main_gui.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.setCentralWidget(self.ui)
        self.resize(self.ui.size())
        self.setWindowTitle(_("Tasmota Precision Calibrator")) # No version here, i18n friendly

        # English: Redirect stdout to the log widget in the GUI.
        # Deutsch: Leite stdout an das Log-Widget in der GUI um.
        self.log_proxy = OutputStreamProxy()
        self.log_proxy.message_signal.connect(self.ui.log_output.appendPlainText)
        sys.stdout = self.log_proxy

        # English: Use deque with maxlen to prevent memory leaks from infinite growth.
        # Deutsch: Nutze deque mit maxlen, um Speicherlecks durch unbegrenztes Wachstum zu verhindern.
        self.graph_data = {
            'volt_ref': deque(maxlen=1000), 'volt_dut': deque(maxlen=1000), 
            'amp_ref':  deque(maxlen=1000), 'amp_dut':  deque(maxlen=1000), 
            'watt_ref': deque(maxlen=1000), 'watt_dut': deque(maxlen=1000)
        }
        
        self.setup_graphs()
        self.setup_ui_logic()
        self.load_values_from_config()
        self.reset_lcd_displays() 

        # English: UI Mode Switching Setup
        # Deutsch: UI Modus Umschaltung Setup
        self.ui_mode_group = QActionGroup(self)
        self.ui_mode_group.setExclusive(True) # Ensure only one action can be checked at a time

        if hasattr(self.ui, 'action_ui_mode_home_only'):
            self.ui_mode_group.addAction(self.ui.action_ui_mode_home_only)
            self.ui.action_ui_mode_home_only.triggered.connect(lambda: self._set_ui_mode('home_only'))
            
        if hasattr(self.ui, 'action_ui_mode_pro_home'):
            self.ui_mode_group.addAction(self.ui.action_ui_mode_pro_home)
            self.ui.action_ui_mode_pro_home.triggered.connect(lambda: self._set_ui_mode('pro_home'))

        # English: Set initial checked state and apply settings from config
        # Deutsch: Setze initialen aktivierten Zustand und wende Einstellungen aus der Konfig an
        current_ui_mode = self.cm.config.get('GENERAL', 'ui_mode', fallback='home_only')
        if current_ui_mode == 'home_only' and hasattr(self.ui, 'action_ui_mode_home_only'):
            self.ui.action_ui_mode_home_only.setChecked(True)
        elif current_ui_mode == 'pro_home' and hasattr(self.ui, 'action_ui_mode_pro_home'):
            self.ui.action_ui_mode_pro_home.setChecked(True)
        else: # Fallback to default if config value is invalid
            if hasattr(self.ui, 'action_ui_mode_home_only'):
                self.ui.action_ui_mode_home_only.setChecked(True)
                self._set_ui_mode('home_only') # Save to config
        
        self._apply_ui_mode_settings() # Apply initial settings

        if hasattr(self.ui, 'split_info'):
            self.ui.split_info.setVisible(False)
        
        if hasattr(self.ui, 'progress_status'):
            self.ui.progress_status.setVisible(False)
        
        # English: Initialize visibility of reference frames based on checkbox state.
        # Deutsch: Initialisiere Sichtbarkeit der Referenz-Frames basierend auf dem Checkbox-Status.
        if hasattr(self.ui, 'frame_fluke'):
            self.ui.frame_fluke.setVisible(self.ui.check_ref_pro.isChecked())
        if hasattr(self.ui, 'frame_tasref'):
            self.ui.frame_tasref.setVisible(self.ui.check_ref_home.isChecked())
            
        if hasattr(self.ui, 'btn_onlinechk'):
            self.ui.btn_onlinechk.clicked.connect(self.on_online_check_clicked)
            
        # English: QButtonGroup for exclusive reference selection (Fluke, Tasmota, Manual)
        # Deutsch: QButtonGroup für exklusive Referenzauswahl (Fluke, Tasmota, Manuell)
        from PySide6.QtWidgets import QButtonGroup
        self.ref_selection_group = QButtonGroup(self)
        self.ref_selection_group.setExclusive(True)
        if hasattr(self.ui, 'check_ref_pro'):
            self.ref_selection_group.addButton(self.ui.check_ref_pro)
        if hasattr(self.ui, 'check_ref_home'):
            self.ref_selection_group.addButton(self.ui.check_ref_home)
        if hasattr(self.ui, 'check_ref_manual'):
            self.ref_selection_group.addButton(self.ui.check_ref_manual)

        lcd_style = """
            QLCDNumber { 
                background-color: black; 
                color: #00FF00; 
                border: 1px solid #333; 
            }
        """
        for lcd in ['lcd_volt', 'lcd_amp', 'lcd_watt']:
            if hasattr(self.ui, lcd):
                getattr(self.ui, lcd).setStyleSheet(lcd_style)
                getattr(self.ui, lcd).setSegmentStyle(pg.QtWidgets.QLCDNumber.Flat)

        self.set_manual_fields_enabled(False)

        # English: Programmatically create and add the manual info button
        # Deutsch: Programmatisch den Info-Button für die manuelle Anleitung erstellen und hinzufügen
        if hasattr(self.ui, 'frame_manuell'):
            # English: Assuming frame_manuell has a layout. If not, one might need to be set.
            # Deutsch: Annahme, dass frame_manuell ein Layout hat. Ansonsten müsste eines gesetzt werden.
            if self.ui.frame_manuell.layout():
                self.ui.btn_man_info = QPushButton(" ℹ️ Anleitung")
                self.ui.btn_man_info.setToolTip(_("Anleitung zur manuellen Messwerterfassung öffnen"))
                # English: Add to the top of the layout, with stretch to push other items down.
                # Deutsch: Oben im Layout hinzufügen, mit einem Stretch, um andere Elemente nach unten zu schieben.
                self.ui.frame_manuell.layout().insertWidget(0, self.ui.btn_man_info)
    
    def _set_ui_mode(self, mode):
        """
        # English: Sets the UI mode in config and applies the settings.
        # Deutsch: Setzt den UI-Modus in der Konfig und wendet die Einstellungen an.
        """
        self.cm.config['GENERAL']['ui_mode'] = mode
        with open(self.cm.config_path, 'w') as configfile: self.cm.config.write(configfile)
        self._apply_ui_mode_settings()

    def _apply_ui_mode_settings(self):
        """
        # English: Applies UI settings based on the current ui_mode from config.
        # Deutsch: Wendet UI-Einstellungen basierend auf dem aktuellen ui_mode aus der Konfig an.
        """
        current_ui_mode = self.cm.config.get('GENERAL', 'ui_mode', fallback='home_only')
        
        
        # Elements to manage: check_ref_pro, spin_steps, check_ref_manual, check_ref_home, frame_reference_selection
        # Note: check_ref_pro, check_ref_home, check_ref_manual are now exclusive via QButtonGroup

        if current_ui_mode == 'home_only':
            # 0. Hide Tools menu / Werkzeuge-Menü ausblenden
            if hasattr(self.ui, 'menuWerkzeuge'): self.ui.menuWerkzeuge.menuAction().setVisible(False)
            
            # 1. Hide Fluke checkbox
            if hasattr(self.ui, 'check_ref_pro'): self.ui.check_ref_pro.setVisible(False)
            
            # 2. Hide Steps spinner and its corresponding label
            if hasattr(self.ui, 'spin_steps'): self.ui.spin_steps.setVisible(False)
            if hasattr(self.ui, 'label_3'): self.ui.label_3.setVisible(False) # Hide "Anzahl der Messstufen" label
            
            # 3. Checkbox "Manuell" (check_ref_manual) must be visible and pre-selected.
            if hasattr(self.ui, 'check_ref_manual'): 
                self.ui.check_ref_manual.setVisible(True) # Ensure visibility
                self.ui.check_ref_manual.setChecked(True) # Pre-select, this will uncheck others in the exclusive group
            
            # 4. Checkbox for Tasmota (check_ref_home) must be visible.
            if hasattr(self.ui, 'check_ref_home'): 
                self.ui.check_ref_home.setVisible(True) # Ensure visibility
                # It will be unchecked by QButtonGroup due to check_ref_manual being checked
            
            # The frame containing reference selections should remain visible as check_ref_home and check_ref_manual are visible
            if hasattr(self.ui, 'frame_reference_selection'): self.ui.frame_reference_selection.setVisible(True)

        elif current_ui_mode == 'pro_home':
            # 0. Show Tools menu / Werkzeuge-Menü einblenden
            if hasattr(self.ui, 'menuWerkzeuge'): self.ui.menuWerkzeuge.menuAction().setVisible(True)
            
            # All elements should be visible and in their default behavior.
            if hasattr(self.ui, 'check_ref_pro'): self.ui.check_ref_pro.setVisible(True)
            if hasattr(self.ui, 'spin_steps'): self.ui.spin_steps.setVisible(True)
            if hasattr(self.ui, 'label_3'): self.ui.label_3.setVisible(True) # Show "Anzahl der Messstufen" label
            if hasattr(self.ui, 'check_ref_manual'): 
                self.ui.check_ref_manual.setVisible(True) # Ensure visibility
                self.ui.check_ref_manual.setChecked(False) # Default to unselected
            if hasattr(self.ui, 'check_ref_home'): self.ui.check_ref_home.setVisible(True)
            if hasattr(self.ui, 'frame_reference_selection'): self.ui.frame_reference_selection.setVisible(True)

    def setup_graphs(self):
        """
        # English: Initializes the live-data plotting graphs.
        # Deutsch: Initialisiert die Graphen für die Live-Daten-Darstellung.
        """
        pg.setConfigOption('background', '#1e1e1e')
        pg.setConfigOption('foreground', 'w')
        self.curves = {}
        configs = {
            'chart_volt': ('volt', _('Spannung'), 'V', 'y', 'w'),
            'chart_amp':  ('amp',  _('Strom'),    'A', 'c', 'w'),
            'chart_watt': ('watt', _('Leistung'), 'W', 'm', 'w')
        }
        for widget_name, (key, title, unit, col_dut, col_ref) in configs.items():
            if hasattr(self.ui, widget_name):
                widget = getattr(self.ui, widget_name)
                layout = QVBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                plot_widget = pg.PlotWidget()
                plot_widget.setLabel('left', title, units=unit)
                plot_widget.setLabel('bottom', _('Messung'), units='#')
                plot_widget.showGrid(x=True, y=True)
                plot_widget.addLegend(offset=(30, 10))
                
                pen_ref = pg.mkPen(col_ref, width=1, style=pg.QtCore.Qt.DashLine)
                self.curves[f"{key}_ref"] = plot_widget.plot(pen=pen_ref, name=_("Soll (Ref)"))
                
                pen_dut = pg.mkPen(col_dut, width=2)
                self.curves[f"{key}_dut"] = plot_widget.plot(pen=pen_dut, name=_("Ist (DUT)"))
                
                layout.addWidget(plot_widget)

    def set_ui_locked(self, locked: bool):
        """
        # English: Locks or unlocks the UI frames during measurement.
        # Deutsch: Sperrt oder entsperrt die UI-Frames während der Messung.
        """
        state = not locked
        if hasattr(self.ui, 'frame_2'): self.ui.frame_2.setEnabled(state)
        if hasattr(self.ui, 'frame_3'): self.ui.frame_3.setEnabled(state)
        if hasattr(self.ui, 'frame_4'): self.ui.frame_4.setEnabled(state)
        
        # English: Also disable setup actions in the menu
        # Deutsch: Deaktiviere auch die Setup-Aktionen im Menü
        if hasattr(self.ui, 'menuSetup'): self.ui.menuSetup.setEnabled(state)

    def update_live_data(self, data):
        """
        # English: Updates the LCD displays and labels with the latest measurement data.
        # Deutsch: Aktualisiert die LCD-Anzeigen und Labels mit den neuesten Messdaten.
        """
        dut_is_off = data.get('dut_off', False)
        v_ref = data.get('volt_ref')
        v_dut = data.get('volt_dut')
        
        # --- Referenz-LCDs aktualisieren (Soll-Werte) ---
        # English: Show reference values if available and DUT is not powered off
        # Deutsch: Zeige Referenzwerte an, wenn verfügbar und die Dose nicht ausgeschaltet ist
        if v_ref is not None and not dut_is_off:
            if hasattr(self.ui, 'lcd_volt'): self.ui.lcd_volt.display(f"{v_ref:.2f}")
            if hasattr(self.ui, 'lcd_amp'):  self.ui.lcd_amp.display(f"{data.get('amp_ref', 0):.3f}")
            if hasattr(self.ui, 'lcd_watt'): self.ui.lcd_watt.display(f"{data.get('watt_ref', 0):.2f}")
            
            # English: Also update the new reference labels
            # Deutsch: Aktualisiere auch die neuen Referenz-Labels
            if hasattr(self.ui, 'lbl_v_ref'): self.ui.lbl_v_ref.setText(f"{v_ref:.2f}V")
            if hasattr(self.ui, 'lbl_a_ref'): self.ui.lbl_a_ref.setText(f"{data.get('amp_ref', 0):.3f}A")
            if hasattr(self.ui, 'lbl_w_ref'): self.ui.lbl_w_ref.setText(f"{data.get('watt_ref', 0):.2f}W")
        else:
            for lcd_name in ['lcd_volt', 'lcd_amp', 'lcd_watt']:
                if hasattr(self.ui, lcd_name):
                    getattr(self.ui, lcd_name).display("------")
            
            # English: Reset reference labels
            # Deutsch: Referenz-Labels zurücksetzen
            if hasattr(self.ui, 'lbl_v_ref'): self.ui.lbl_v_ref.setText("----")
            if hasattr(self.ui, 'lbl_a_ref'): self.ui.lbl_a_ref.setText("----")
            if hasattr(self.ui, 'lbl_w_ref'): self.ui.lbl_w_ref.setText("----")
                    
        # --- Prüfling-Labels aktualisieren (Ist-Werte) ---
        # English: Show DUT values if available and DUT is not powered off
        # Deutsch: Zeige DUT-Werte an, wenn verfügbar und die Dose nicht ausgeschaltet ist
        if v_dut is not None and not dut_is_off:
            if hasattr(self.ui, 'lbl_v_dut'): self.ui.lbl_v_dut.setText(f"{v_dut:.2f}V")
            if hasattr(self.ui, 'lbl_a_dut'): self.ui.lbl_a_dut.setText(f"{data.get('amp_dut', 0):.3f}A")
            if hasattr(self.ui, 'lbl_w_dut'): self.ui.lbl_w_dut.setText(f"{data.get('watt_dut', 0):.2f}W")
        else:
            if hasattr(self.ui, 'lbl_v_dut'): self.ui.lbl_v_dut.setText("----")
            if hasattr(self.ui, 'lbl_a_dut'): self.ui.lbl_a_dut.setText("----")
            if hasattr(self.ui, 'lbl_w_dut'): self.ui.lbl_w_dut.setText("----")

        # --- Graphen-Daten aktualisieren ---
        # English: Return early if no data is available to avoid graph errors
        # Deutsch: Frühzeitiger Abbruch, wenn keine Daten vorhanden sind, um Graphen-Fehler zu vermeiden
        if v_ref is None and v_dut is None:
            return

        for key in ['volt_ref', 'volt_dut', 'amp_ref', 'amp_dut', 'watt_ref', 'watt_dut']:
            val = data.get(key)
            
            # English: Safely convert to float first, then check for > 0 to prevent TypeError if val is a string.
            # Deutsch: Zuerst sicher in Float umwandeln, dann auf > 0 prüfen, um einen TypeError zu verhindern, falls val ein String ist.
            try:
                val_float = float(val) if val is not None else None
            except (ValueError, TypeError):
                val_float = None

            if val_float is not None and val_float > 0:
                if key in self.graph_data:
                    self.graph_data[key].append(val_float)
            elif key in self.graph_data and len(self.graph_data[key]) > 0:
                self.graph_data[key].append(self.graph_data[key][-1])
            elif key in self.graph_data:
                self.graph_data[key].append(0.0)

        mapping = {
            'volt_ref': 'volt_ref', 'volt_dut': 'volt_dut',
            'amp_ref': 'amp_ref',   'amp_dut': 'amp_dut',
            'watt_ref': 'watt_ref', 'watt_dut': 'watt_dut'
        }

        for data_key, curve_key in mapping.items():
            if curve_key in self.curves:
                # English: Convert deque to a list for plotting (only last 100 entries).
                # Deutsch: Deque für die Darstellung in eine Liste umwandeln (nur die letzten 100 Einträge).
                plot_data = list(self.graph_data[data_key])[-100:]
                if plot_data:
                    # English: Generate 1-based x-values for plotting.
                    # Deutsch: Erzeuge 1-basierte X-Werte für die Plot-Darstellung.
                    x_values = list(range(1, len(plot_data) + 1))
                    self.curves[curve_key].setData(x=x_values, y=plot_data)



    def setup_ui_logic(self):
        """
        # English: Connects all UI element signals (like button clicks) to their corresponding slots (methods).
        # Deutsch: Verbindet alle Signale der UI-Elemente (wie Button-Klicks) mit den zugehörigen Slots (Methoden).
        """
        self.ui.btn_start.clicked.connect(self.toggle_measurement)
        # Old exclusivity logic removed, QButtonGroup will handle this for check_ref_pro, check_ref_home, check_ref_manual
        
        # English: Connect HOME-mode to steps restriction logic.
        # Deutsch: HOME-Modus mit der Logik zur Stufenbeschränkung verbinden.
        self.ui.check_ref_home.toggled.connect(self.update_steps_restriction)
        # English: Perform initial check. / Deutsch: Initiale Prüfung durchführen.
        self.update_steps_restriction(self.ui.check_ref_home.isChecked())

        # English: Connect MANUAL-mode to its logic handler.
        # Deutsch: MANUELL-Modus mit seinem Logik-Handler verbinden.
        if hasattr(self.ui, 'check_ref_manual'):
            self.ui.check_ref_manual.toggled.connect(self.on_manual_ref_toggled)
            # English: Perform initial check for manual mode.
            # Deutsch: Initiale Prüfung für den manuellen Modus durchführen.
            self.on_manual_ref_toggled(self.ui.check_ref_manual.isChecked())

        if hasattr(self.ui, 'frame_fluke'):
            self.ui.check_ref_pro.toggled.connect(self.ui.frame_fluke.setVisible)
            self.ui.frame_fluke.setVisible(self.ui.check_ref_pro.isChecked())

        if hasattr(self.ui, 'frame_tasref'):
            self.ui.check_ref_home.toggled.connect(self.ui.frame_tasref.setVisible)
            self.ui.frame_tasref.setVisible(self.ui.check_ref_home.isChecked())

        if hasattr(self.ui, 'action_setup_general'):
            self.ui.action_setup_general.triggered.connect(self.open_setup_general)
        if hasattr(self.ui, 'action_setup_fluke'):
            self.ui.action_setup_fluke.triggered.connect(self.open_setup_fluke)
        if hasattr(self.ui, 'action_setup_tasmota'):
            self.ui.action_setup_tasmota.triggered.connect(self.open_setup_tasmota)

        if hasattr(self.ui, 'action_save_log'):
            self.ui.action_save_log.triggered.connect(self.save_log_to_file)
        if hasattr(self.ui, 'action_open_report_dir'):
            self.ui.action_open_report_dir.triggered.connect(self.open_report_folder)
        if hasattr(self.ui, 'action_exit_program'):
            self.ui.action_exit_program.triggered.connect(self.close)

        if hasattr(self.ui, 'action_show_license'):
            self.ui.action_show_license.triggered.connect(self.show_license_info)

        if hasattr(self.ui, 'action_guide'):
            self.ui.action_guide.triggered.connect(self.open_guidance)

        if hasattr(self.ui, 'action_dynamic_cal'):
            self.ui.action_dynamic_cal.triggered.connect(self.open_dynamic_cal_dialog)
        
        # English: Update the menu text for UI mode selection
        # Deutsch: Aktualisiere den Menütext für die UI-Modus-Auswahl
        if hasattr(self.ui, 'menu_mode_selection'): # Use the correct objectName
            self.ui.menu_mode_selection.setTitle(_("Modus")) # Translate the menu title
        if hasattr(self.ui, 'action_ui_mode_home_only'):
            self.ui.action_ui_mode_home_only.setText(_("Einfacher Modus")) # Translate the action text
        if hasattr(self.ui, 'action_ui_mode_pro_home'):
            self.ui.action_ui_mode_pro_home.setText(_("Professioneller Modus")) # Translate the action text

        if hasattr(self.ui, 'btn_man_ubernehmen'):
            self.ui.btn_man_ubernehmen.setVisible(False)
            self.ui.btn_man_ubernehmen.clicked.connect(self.on_manual_apply_clicked)

            all_manual_fields = [
                'edit_vtas_1', 'edit_vtas_2', 'edit_vtas_3', 'edit_vref_1', 'edit_vref_2', 'edit_vref_3',
                'edit_atas_1', 'edit_atas_2', 'edit_atas_3', 'edit_aref_1', 'edit_aref_2', 'edit_aref_3',
                'edit_wtas_1', 'edit_wtas_2', 'edit_wtas_3', 'edit_wref_1', 'edit_wref_2', 'edit_wref_3'
            ]
            for field_name in all_manual_fields:
                if hasattr(self.ui, field_name):
                    widget = getattr(self.ui, field_name)
                    
                    if field_name.startswith('edit_a'):
                        widget.setToolTip(_("Wert mit drei Nachkommastellen eingeben (z.B. 1.234)"))
                    else:
                        widget.setToolTip(_("Wert mit zwei Nachkommastellen eingeben (z.B. 123.45)"))

                    widget.setProperty("original_style", widget.styleSheet())
                    widget.setProperty("is_invalid", False)
                    
                    widget.editingFinished.connect(self._validate_field_format)
                    widget.editingFinished.connect(self._on_manual_input_changed)
                else:
                    print(f"DEBUG: Startup - UI element {field_name} not found for validation connection.")
            if hasattr(self.ui, 'btn_man_info'):
                self.ui.btn_man_info.clicked.connect(self.show_manual_info_dialog)

    def show_manual_info_dialog(self):
        """
        # English: Shows a modeless dialog with instructions for manual calibration from the asset file.
        # Deutsch: Zeigt einen nicht-modalen Dialog mit der Anleitung für die manuelle Kalibrierung aus der Asset-Datei an.
        """
        dialog_exists = False
        if hasattr(self, 'manual_info_dialog'):
            try:
                if self.manual_info_dialog.isVisible():
                    dialog_exists = True
            except RuntimeError:
                dialog_exists = False

        if not dialog_exists:
            self.manual_info_dialog = QMessageBox(self)
            self.manual_info_dialog.setAttribute(Qt.WA_DeleteOnClose)
            self.manual_info_dialog.setWindowModality(Qt.NonModal)
            self.manual_info_dialog.setIcon(QMessageBox.Information)
            self.manual_info_dialog.setWindowTitle(_("Anleitung: Manuelle Messwerterfassung"))
            self.manual_info_dialog.setTextFormat(Qt.RichText)
            self.manual_info_dialog.setText(MANUAL_INFO_HTML)
            self.manual_info_dialog.show()
        else:
            self.manual_info_dialog.activateWindow()

    def load_values_from_config(self):
        """
        # English: Loads default values from the config.ini file into the UI widgets.
        # Deutsch: Lädt Standardwerte aus der config.ini-Datei in die UI-Widgets.
        """
        try:
            if hasattr(self.ui, 'edit_dut_ip'): self.ui.edit_dut_ip.setText(self.cm.config.get('TARGET', 'ip_address', fallback='0.0.0.0'))
            if hasattr(self.ui, 'spin_steps'): self.ui.spin_steps.setValue(self.cm.config.getint('TARGET', 'measurement_steps', fallback=3))
            if hasattr(self.ui, 'spin_measurements'): self.ui.spin_measurements.setValue(self.cm.config.getint('TARGET', 'measurements_per_step', fallback=15))
        except Exception as e:
            self.ui.log_output.appendPlainText(f"❌ Fehler beim Laden der INI: {e}")

    def open_setup_general(self):
        """
        # English: Opens the general setup dialog from a .ui file.
        # Deutsch: Öffnet den Dialog für die allgemeinen Einstellungen aus einer .ui-Datei.
        """
        ui_path = os.path.join(os.path.dirname(__file__), "setup_general.ui")
        if not os.path.exists(ui_path):
            return QMessageBox.warning(self, _("Fehler"), _("Datei setup_general.ui nicht gefunden!"))
            
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        dialog = QUiLoader().load(ui_file, self)
        ui_file.close()
        
        if hasattr(dialog, 'edit_report_dir'):
            dialog.edit_report_dir.setText(self.cm.config.get('GENERAL', 'root_report_dir', fallback='./Reports'))
            
            def open_directory_browser():
                start_dir = dialog.edit_report_dir.text()
                folder = QFileDialog.getExistingDirectory(dialog, _("Report Ordner auswählen"), start_dir)
                if folder:
                    dialog.edit_report_dir.setText(folder)

            if hasattr(dialog, 'btn_browse_dir'):
                dialog.btn_browse_dir.clicked.connect(open_directory_browser)

        # English: Load tolerance limits into the new fields.
        # Deutsch: Lade Toleranzgrenzen in die neuen Felder.
        if hasattr(dialog, 'edit_devV'):
            dialog.edit_devV.setText(self.cm.config.get('TOLERANCE abs%', 'voltage_limit', fallback='0.5'))
        if hasattr(dialog, 'edit_devI'):
            dialog.edit_devI.setText(self.cm.config.get('TOLERANCE abs%', 'current_limit', fallback='0.5'))
        if hasattr(dialog, 'edit_devP'):
            dialog.edit_devP.setText(self.cm.config.get('TOLERANCE abs%', 'power_limit', fallback='5.0'))
            
        def save_and_close():
            if hasattr(dialog, 'edit_report_dir'):
                self.cm.config['GENERAL']['root_report_dir'] = dialog.edit_report_dir.text().strip()
                self.cm.root_dir = self.cm.config['GENERAL']['root_report_dir'] 
            
            # English: Save updated tolerance limits.
            # Deutsch: Speichere aktualisierte Toleranzgrenzen.
            if 'TOLERANCE abs%' not in self.cm.config:
                self.cm.config['TOLERANCE abs%'] = {}
            
            if hasattr(dialog, 'edit_devV'):
                self.cm.config['TOLERANCE abs%']['voltage_limit'] = dialog.edit_devV.text().strip().replace(',', '.')
            if hasattr(dialog, 'edit_devI'):
                self.cm.config['TOLERANCE abs%']['current_limit'] = dialog.edit_devI.text().strip().replace(',', '.')
            if hasattr(dialog, 'edit_devP'):
                self.cm.config['TOLERANCE abs%']['power_limit'] = dialog.edit_devP.text().strip().replace(',', '.')
            
            with open(self.cm.config_path, 'w') as f: self.cm.config.write(f)
            self.ui.log_output.appendPlainText(_("✅ Allgemeines Setup in config.ini gespeichert."))
            dialog.accept()
            
        dialog.btn_save.clicked.connect(save_and_close)
        dialog.btn_close.clicked.connect(dialog.reject)
        dialog.exec()

    def open_setup_fluke(self):
        """
        # English: Opens the Fluke setup dialog from a .ui file.
        # Deutsch: Öffnet den Dialog für die Fluke-Einstellungen aus einer .ui-Datei.
        """
        ui_path = os.path.join(os.path.dirname(__file__), "setup_fluke.ui")
        if not os.path.exists(ui_path):
            return QMessageBox.warning(self, _("Fehler"), _("Datei setup_fluke.ui nicht gefunden!"))
            
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        dialog = QUiLoader().load(ui_file, self)
        ui_file.close()

        # English: Ensure the progress bar is hidden by default.
        # Deutsch: Stelle sicher, dass der Fortschrittsbalken standardmäßig ausgeblendet ist.
        if hasattr(dialog, 'progress_scan'):
            dialog.progress_scan.setVisible(False)
        
        if hasattr(dialog, 'edit_com_port'):
            dialog.edit_com_port.setText(self.cm.config.get('REFERENCE_PRO', 'com_port', fallback='COM3'))
        if hasattr(dialog, 'edit_baudrate'):
            dialog.edit_baudrate.setText(self.cm.config.get('REFERENCE_PRO', 'baudrate', fallback='9600'))
        
        # --- Auto-Scan Logic ---
        def start_fluke_scan():
            current_port = dialog.edit_com_port.text().strip() if hasattr(dialog, 'edit_com_port') else None
            current_baud = dialog.edit_baudrate.text().strip() if hasattr(dialog, 'edit_baudrate') else None
            
            # English: Disable buttons and show progress bar during scan.
            # Deutsch: Buttons deaktivieren und Fortschrittsbalken während des Scans anzeigen.
            dialog.btn_search_fluke.setEnabled(False)
            dialog.btn_save.setEnabled(False)
            if hasattr(dialog, 'progress_scan'):
                dialog.progress_scan.setVisible(True)
                dialog.progress_scan.setValue(0)
            
            self.scan_worker = FlukeScanWorker(current_port, current_baud)
            
            def on_scan_finished(result):
                dialog.btn_search_fluke.setEnabled(True)
                dialog.btn_save.setEnabled(True)
                if hasattr(dialog, 'progress_scan'):
                    dialog.progress_scan.setVisible(False)
                
                if result and 'port' in result:
                    if hasattr(dialog, 'edit_com_port'): dialog.edit_com_port.setText(result['port'])
                    if hasattr(dialog, 'edit_baudrate'): dialog.edit_baudrate.setText(result['baud'])
                    QMessageBox.information(dialog, "Erfolg", f"Fluke 45 erfolgreich gefunden!\n\nPort: {result['port']}\nBaudrate: {result['baud']}\n\nInfo: {result.get('info', '')}")
                else:
                    QMessageBox.warning(dialog, "Fehlgeschlagen", "Es konnte kein Fluke 45 Multimeter an den verfügbaren Schnittstellen gefunden werden.\n\nBitte prüfe die Kabelverbindung und ob das Gerät eingeschaltet ist.")
            
            self.scan_worker.progress_signal.connect(dialog.progress_scan.setValue if hasattr(dialog, 'progress_scan') else lambda x: None)
            self.scan_worker.finished_signal.connect(on_scan_finished)
            self.scan_worker.start()

        if hasattr(dialog, 'btn_search_fluke'):
            dialog.btn_search_fluke.clicked.connect(start_fluke_scan)
        
        def save_and_close():
            if hasattr(dialog, 'edit_com_port'):
                self.cm.config['REFERENCE_PRO']['com_port'] = dialog.edit_com_port.text().strip()
            if hasattr(dialog, 'edit_baudrate'):
                self.cm.config['REFERENCE_PRO']['baudrate'] = dialog.edit_baudrate.text().strip()
                
            with open(self.cm.config_path, 'w') as f: self.cm.config.write(f)
            self.ui.log_output.appendPlainText("✅ Fluke Setup in config.ini gespeichert.")
            dialog.accept()
            
        dialog.btn_save.clicked.connect(save_and_close)
        dialog.btn_close.clicked.connect(dialog.reject)
        dialog.exec()

    def open_setup_tasmota(self):
        """
        # English: Opens the Tasmota reference setup dialog from a .ui file.
        # Deutsch: Öffnet den Dialog für die Tasmota-Referenz-Einstellungen aus einer .ui-Datei.
        """
        ui_path = os.path.join(os.path.dirname(__file__), "setup_tasmota.ui")
        if not os.path.exists(ui_path):
            return QMessageBox.warning(self, "Fehler", "Datei setup_tasmota.ui nicht gefunden!")
            
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        dialog = QUiLoader().load(ui_file, self)
        ui_file.close()
        
        if hasattr(dialog, 'edit_ref_ip'):
            dialog.edit_ref_ip.setText(self.cm.config.get('REFERENCE_HOME', 'ip_address', fallback='10.0.0.202'))
        
        def save_and_close():
            if hasattr(dialog, 'edit_ref_ip'):
                self.cm.config['REFERENCE_HOME']['ip_address'] = dialog.edit_ref_ip.text().strip()
                
            with open(self.cm.config_path, 'w') as f: self.cm.config.write(f)
            self.ui.log_output.appendPlainText("✅ Tasmota Setup in config.ini gespeichert.")
            dialog.accept()
            
        dialog.btn_save.clicked.connect(save_and_close)
        dialog.btn_close.clicked.connect(dialog.reject)
        dialog.exec()

    def open_report_folder(self):
        """
        # English: Opens the root directory for reports in the system's file explorer.
        # Deutsch: Öffnet das Stammverzeichnis für Protokolle im Datei-Explorer des Systems.
        """
        report_path = os.path.abspath(self.cm.root_dir)
        if os.path.exists(report_path):
            os.startfile(report_path) 
        else:
            QMessageBox.warning(self, "Ordner nicht gefunden", f"Der Pfad existiert noch nicht oder wurde noch nicht erstellt:\n{report_path}")

    def save_log_to_file(self):
        """
        # English: Saves the content of the log widget to a text file.
        # Deutsch: Speichert den Inhalt des Log-Widgets in eine Textdatei.
        """
        log_content = self.ui.log_output.toPlainText()
        if not log_content.strip():
            return QMessageBox.information(self, "Log leer", "Es gibt noch keine Einträge zum Speichern.")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"Log_{ts}.txt"
        file_path, filter_used = QFileDialog.getSaveFileName(self, "Log sichern", default_name, "Textdateien (*.txt)")
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(log_content)
                self.ui.log_output.appendPlainText(f"✅ Log erfolgreich gespeichert: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Log konnte nicht gespeichert werden:\n{e}")

    def show_power_popup(self, message):
        """
        # English: Shows a non-blocking popup to ask the user to turn on the power.
        # Deutsch: Zeigt ein nicht-blockierendes Popup an, das den Benutzer zum Einschalten auffordert.
        """
        if self.wait_msgbox is not None:
            self.wait_msgbox.accept()
            
        self.wait_msgbox = QMessageBox(self)
        self.wait_msgbox.setIcon(QMessageBox.Information)
        self.wait_msgbox.setWindowTitle("Aktion erforderlich")
        self.wait_msgbox.setText(message)
        self.wait_msgbox.addButton("Messung Abbrechen", QMessageBox.RejectRole)
        self.wait_msgbox.rejected.connect(self.cancel_from_popup)
        self.wait_msgbox.setWindowModality(Qt.WindowModal)
        self.wait_msgbox.show()

    def hide_power_popup(self):
        """
        # English: Hides the power-on popup if it is visible.
        # Deutsch: Schließt das Einschalt-Popup, falls es sichtbar ist.
        """
        if self.wait_msgbox is not None:
            try:
                self.wait_msgbox.rejected.disconnect(self.cancel_from_popup)
            except:
                pass
            self.wait_msgbox.accept()
            self.wait_msgbox = None

    def cancel_from_popup(self):
        """
        # English: Slot that is called when the user clicks 'Cancel' in the power-on popup.
        # Deutsch: Slot, der aufgerufen wird, wenn der Benutzer im Einschalt-Popup auf 'Abbrechen' klickt.
        """
        self.ui.log_output.appendPlainText("⚠️ Abbruch durch Benutzer im Popup-Fenster.")
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
            self.ui.btn_start.setEnabled(False) 

    def toggle_measurement(self):
        """
        # English: Starts the measurement if not running, or stops it if it is running.
        # Deutsch: Startet die Messung, wenn sie nicht läuft, oder stoppt sie, wenn sie läuft.
        """
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.ui.log_output.appendPlainText("⚠️ Sende Abbruch-Signal an Haupt-Worker...")
            self.worker.stop()
            self.ui.btn_start.setEnabled(False) 
        elif hasattr(self, 'manual_worker') and self.manual_worker and self.manual_worker.isRunning():
            self.ui.log_output.appendPlainText("⚠️ Sende Abbruch-Signal an Vorbereitungs-Worker...")
            self.manual_worker.stop()
            self.ui.btn_start.setEnabled(False)
        elif self.is_in_manual_entry_mode:
            self.ui.log_output.appendPlainText(_("ℹ️ Manueller Eingabemodus durch Benutzer abgebrochen."))
            self._cancel_manual_entry_mode()
        else:
            self.start_measurement()

    def start_measurement(self):
        """
        # English:
        # Prepares and starts the measurement process. It validates inputs,
        # checks device availability, and starts the MeasurementWorker thread.
        # Deutsch:
        # Bereitet den Messprozess vor und startet ihn. Validiert Eingaben,
        # prüft die Geräteverfügbarkeit und startet den MeasurementWorker-Thread.
        """
        # English: Check if manual calibration is selected and branch off.
        # Deutsch: Prüfen, ob manuelle Kalibrierung gewählt ist und abzweigen.
        if hasattr(self.ui, 'check_ref_manual') and self.ui.check_ref_manual.isChecked():
            return self.start_manual_calibration()

        is_pro = self.ui.check_ref_pro.isChecked()
        is_home = self.ui.check_ref_home.isChecked()
        if not is_pro and not is_home:
            return self.ui.log_output.appendPlainText("❌ ABBRUCH: Keine Referenzquelle ausgewählt!")

        dut_ip = self.ui.edit_dut_ip.text().strip()
        if not dut_ip: return self.ui.log_output.appendPlainText("❌ ABBRUCH: Ziel-Dose IP fehlt!")

        dut_info = self.fetch_tasmota_info(dut_ip, is_dut=True)
        if not dut_info: return self.ui.log_output.appendPlainText("❌ ABBRUCH: Ziel-Dose nicht erreichbar!")

        steps = self.ui.spin_steps.value()
        measurements = self.ui.spin_measurements.value()

        com_port = self.cm.config.get('REFERENCE_PRO', 'com_port', fallback='')
        ref_ip = self.cm.config.get('REFERENCE_HOME', 'ip_address', fallback='')
        ref_info = None

        if is_pro:
            if not com_port: return self.ui.log_output.appendPlainText("❌ ABBRUCH: COM-Port in Setup->Fluke fehlt!")
            ref_info = {"name": "FLUKE 45 DUAL Mode", "host": f"Serial Port {com_port}", "mac": "N/A"}
        
        if is_home:
            if not ref_ip: return self.ui.log_output.appendPlainText("❌ ABBRUCH: Tasmota-Referenz IP in Setup->Tasmota fehlt!")
            
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Messaufbau kontrollieren")
            msg_box.setText("<b>Ist der Messaufbau korrekt verkabelt?</b>")
            msg_box.setInformativeText(
                "Die korrekte Reihenfolge ist zwingend erforderlich:\n\n"
                "Wandsteckdose → Referenz-Dose → Prüfling (DUT) → Last\n\n"
                "Nur so kann das Programm den Eigenverbrauch des Prüflings ermitteln und abziehen."
            )
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            if msg_box.exec() == QMessageBox.Cancel:
                return self.ui.log_output.appendPlainText("⚠️ Abbruch: Messaufbau wird korrigiert.")

            ref_info = self.fetch_tasmota_info(ref_ip, is_dut=False)
            if not ref_info: return self.ui.log_output.appendPlainText("❌ ABBRUCH: Referenz-Dose nicht erreichbar!")

        try:
            # English: Save measurement parameters, but NOT the DUT IP address as requested.
            # Deutsch: Speichere Messparameter, aber NICHT die DUT-IP-Adresse (wie gewünscht).
            self.cm.config['TARGET']['measurement_steps'] = str(steps)
            self.cm.config['TARGET']['measurements_per_step'] = str(measurements)
            # English: Use the centralized config path from the manager.
            # Deutsch: Nutze den zentralen Konfigurationspfad aus dem Manager.
            with open(self.cm.config_path, 'w') as configfile: self.cm.config.write(configfile)
        except: return

        # English: Use the ConfigManager to determine MAC and setup directory (ip is passed explicitly).
        # Deutsch: Nutze den ConfigManager zur MAC-Ermittlung und Verzeichnis-Erstellung (IP wird explizit übergeben).
        dut_auth = None
        creds = self.credentials_manager.get_credentials(dut_ip)
        if creds:
            dut_auth = (creds['user'], creds['password'])
            
        # English: Use the MAC from dut_info if available to avoid a redundant call.
        # Deutsch: Nutze die MAC aus dut_info, falls verfügbar, um einen redundanten Aufruf zu vermeiden.
        mac_param = dut_info.get('mac').replace(":", "-") if dut_info and dut_info.get('mac') else None
        device_path = self.cm.setup_device_directory(ip=dut_ip, auth=dut_auth, mac=mac_param)
        mac_display = os.path.basename(device_path)

        existing_csvs = glob.glob(os.path.join(device_path, "*_Stufe_*.csv"))
        use_existing = False
        session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if existing_csvs:
            report_files = glob.glob(os.path.join(device_path, "*_Protokoll.txt"))
            if report_files:
                latest_report = max(report_files, key=os.path.getctime)
                last_session_ts = os.path.basename(latest_report).split('_Protokoll.txt')[0].replace('_ReApply','')
            
                try:
                    dt_obj = datetime.strptime(last_session_ts, "%Y%m%d_%H%M%S")
                    display_time = dt_obj.strftime("%d.%m.%Y um %H:%M:%S Uhr")
                except:
                    display_time = last_session_ts

                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Question)
                msg_box.setWindowTitle("Alte Messdaten gefunden")
                msg_box.setText(f"Für diese Tasmota-Dose ({mac_display}) existieren bereits Messdaten vom:\n\n{display_time}\n\nMöchtest du komplett neue Daten aufzeichnen oder die Werte des letzten Reports erneut anwenden?")
                
                btn_new = msg_box.addButton("Neue Messung", QMessageBox.AcceptRole)
                btn_old = msg_box.addButton("Alten Report nutzen", QMessageBox.AcceptRole)
                btn_cancel = msg_box.addButton("Abbrechen", QMessageBox.RejectRole)
                
                msg_box.exec()
                
                if msg_box.clickedButton() == btn_cancel:
                    return self.ui.log_output.appendPlainText("⚠️ Messungs-Start durch Benutzer abgebrochen.")
                elif msg_box.clickedButton() == btn_old:
                    use_existing = True
                    session_ts = last_session_ts
                    self.ui.log_output.appendPlainText(f"ℹ️ Überspringe Messung. Nutze Report von: {display_time}")
                else:
                    self.ui.log_output.appendPlainText("ℹ️ Alte Daten werden ignoriert. Starte neuen Testlauf.")

        params = {
            'mode': "PRO" if is_pro else "HOME", 'steps': steps, 'measurements': measurements,
            'ref_ip': ref_ip, 'com_port': com_port, 'dut_ip': dut_ip,
            'device_path': device_path, 'session_ts': session_ts,
            'use_existing': use_existing,
            'dut_info': dut_info,
            'ref_info': ref_info
        }

        for key in self.graph_data: 
            self.graph_data[key].clear()
        
        self.worker = MeasurementWorker(self.cm.config, params, self.credentials_manager)
        
        self.worker.log_signal.connect(self.ui.log_output.appendPlainText)
        self.worker.data_signal.connect(self.update_live_data)
        self.worker.apply_request_signal.connect(self.prompt_apply_calibration)
        self.worker.show_popup_signal.connect(self.show_power_popup)
        self.worker.hide_popup_signal.connect(self.hide_power_popup)
        
        # English: Connect step progress to the new progress bar widget.
        # Deutsch: Verbinde den Stufen-Fortschritt mit dem neuen Progress-Bar Widget.
        if hasattr(self.ui, 'progress_status'):
            self.ui.progress_status.setValue(0)
            self.ui.progress_status.setVisible(True)
            self.worker.step_progress_signal.connect(self.ui.progress_status.setValue)
        
        # English: Lock relevant UI frames and the setup menu during measurement.
        # Deutsch: Sperre relevante UI-Frames und das Setup-Menü während der Messung.
        self.set_ui_locked(True)

        self.ui.btn_start.setText("⛔ Messung abbrechen")
        self.ui.btn_start.setStyleSheet("background-color: darkred; color: white; font-weight: bold;")
        self.ui.log_output.appendPlainText("-" * 50)
        self.worker.finished_signal.connect(self.measurement_finished)
        self.worker.start()

    def measurement_finished(self, message):
        """
        # English: Slot that is called when the measurement worker is finished or has been aborted.
        # Deutsch: Slot, der aufgerufen wird, wenn der Mess-Worker fertig oder abgebrochen wurde.
        """
        if message: 
            self.ui.log_output.appendPlainText(message)
        self.ui.btn_start.setText("Kalibrierung Starten")
        self.ui.btn_start.setStyleSheet("") 
        self.ui.btn_start.setEnabled(True)
        
        # English: Re-enable UI frames and menu after measurement.
        # Deutsch: Gebe UI-Frames und Menü nach der Messung wieder frei.
        self.set_ui_locked(False)

        if hasattr(self.ui, 'progress_status'):
            self.ui.progress_status.setValue(0)
            self.ui.progress_status.setVisible(False)

        self.hide_power_popup()
        self.reset_lcd_displays()

    def _parse_report_for_values(self, report_path):
        """
        # English: Parses a report file to extract both the old and suggested new calibration values.
        # Deutsch: Parst eine Protokolldatei, um sowohl die alten als auch die vorgeschlagenen neuen Kalibrierwerte zu extrahieren.
        """
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # English: Matches for NEW values
            vcal_match = re.search(r"VoltageCal \d+\s+VoltageCal (\d+)", content)
            acal_match = re.search(r"CurrentCal \d+\s+CurrentCal (\d+)", content)
            pcal_reg_match = re.search(r"PowerCal \d+\s+PowerCal (\d+)", content)
            pcal_avg_match = re.search(r"Alternative: (\d+)", content)

            # English: Matches for OLD values (from the first step's 'Alt_Cal' info in report)
            vold_match = re.search(r"VoltageCal (\d+)\s+VoltageCal \d+", content)
            aold_match = re.search(r"CurrentCal (\d+)\s+CurrentCal \d+", content)
            wold_match = re.search(r"PowerCal (\d+)\s+PowerCal \d+", content)

            if vcal_match and acal_match and pcal_reg_match and pcal_avg_match:
                final = {
                    "vcal": int(vcal_match.group(1)),
                    "acal": int(acal_match.group(1)),
                    "pcal_regression": int(pcal_reg_match.group(1)),
                    "pcal_avg": int(pcal_avg_match.group(1))
                }
                old = {
                    "VCal": int(vold_match.group(1)) if vold_match else 20230,
                    "ACal": int(aold_match.group(1)) if aold_match else 2500,
                    "WCal": int(wold_match.group(1)) if wold_match else 12500
                }
                return final, old
        except Exception as e:
            self.ui.log_output.appendPlainText(f"❌ Fehler beim Parsen des Reports: {e}")
        return None, None

    def prompt_apply_calibration(self, original_report_path, target_ip, all_results, dut_info_str, ref_info_str, mode=None):
        """
        # English:
        # This slot is called when the worker has finished processing. It prepares the final values
        # and shows the CalibrationReportDialog to the user.
        # Deutsch:
        # Dieser Slot wird aufgerufen, wenn der Worker mit der Verarbeitung fertig ist. Er bereitet die
        # finalen Werte vor und zeigt dem Benutzer den CalibrationReportDialog an.
        """
        is_reapply = not all_results
        final_values = None
        old_factors = None
        
        device_path = os.path.dirname(original_report_path)
        try:
            session_ts = os.path.basename(original_report_path).split('_Protokoll.txt')[0].split('_ReApply')[0]
        except Exception:
            session_ts = None 

        dut_info = json.loads(dut_info_str) if dut_info_str and dut_info_str != 'null' else {}
        ref_info = json.loads(ref_info_str) if ref_info_str and ref_info_str != 'null' else {}
        
        # English: Determine mode for the report dialog.
        # Deutsch: Bestimme den Modus für den Report-Dialog.
        current_mode = mode if mode else "PRO"
        
        # English: Try to detect mode from report content (highest priority)
        # Deutsch: Versuche zuerst den Modus aus dem Berichtsinhalt zu erkennen (höchste Priorität)
        try:
            with open(original_report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "Kalibrier-Modus:  HOME" in content:
                    current_mode = "HOME"
                elif "Kalibrier-Modus:  MANUAL" in content:
                    current_mode = "MANUAL"
        except:
            pass

        if not is_reapply and not mode and current_mode == "PRO":
            # English: Fallback for new measurements if no explicit mode was provided
            # Deutsch: Fallback für neue Messungen, falls kein expliziter Modus übergeben wurde
            current_mode = "HOME" if self.ui.check_ref_home.isChecked() else "PRO"

        if is_reapply:
            self.ui.log_output.appendPlainText("-> Kalibrierung auf Basis eines alten Reports (Re-Apply).")
            final_values, old_factors = self._parse_report_for_values(original_report_path)
            if not final_values:
                QMessageBox.critical(self, "Fehler", f"Die Kalibrierwerte konnten nicht aus dem Report '{os.path.basename(original_report_path)}' gelesen werden.")
                self.measurement_finished("")
                return
        else: # New measurement
            self.ui.log_output.appendPlainText("-> Kalibrierung auf Basis einer neuen Messung.")
            vcal = int(sum(r['Stufen_Cal']['VCal'] for r in all_results) / len(all_results))
            acal = int(sum(r['Stufen_Cal']['ACal'] for r in all_results) / len(all_results))
            pcal_avg = int(sum(r['Stufen_Cal']['WCal'] for r in all_results) / len(all_results))
            pcal_regression = 0
            
            old_factors = all_results[0].get('Alt_Cal', {"VCal": 20230, "ACal": 2500, "WCal": 12500})

            reg_data = DataAnalyzer.calculate_regression(device_path, session_ts)
            if reg_data and all_results:
                p_reg = reg_data['Power']
                pcal_regression = int(old_factors.get('WCal', 12500) * p_reg['slope'])
                
            final_values = { "vcal": vcal, "acal": acal, "pcal_avg": pcal_avg, "pcal_regression": pcal_regression }
        
        report_info = {
            'original_path': original_report_path,
            'device_path': device_path,
            'session_ts': session_ts,
            'dut_info': dut_info,
            'ref_info': ref_info,
            'mode': current_mode
        }

        dialog = CalibrationReportDialog(self, target_ip, final_values, old_factors, is_reapply, report_info, self.credentials_manager, self.cm.config)
        dialog.exec()
        
        self.measurement_finished("🏁 Der gesamte Kalibrierprozess ist beendet.")

    def show_license_info(self):
        """
        # English: Displays a message box with license and author information.
        # Deutsch: Zeigt eine Message-Box mit Lizenz- und Autoreninformationen an.
        """
        license_text = (
            "Tasmota Precision Calibrator v5.4.1\n"
            "Erstellt von: Arnulf Greilberger\n\n"
            "----------------------------------------------------------\n"
            "LIZENZ:\n"
            "Creative Commons BY-NC-SA 4.0\n"
            "Freie Nutzung, Teilung und Veränderung unter Namensnennung.\n"
            "Keine kommerzielle Nutzung erlaubt.\n\n"
            "----------------------------------------------------------\n"
            "WICHTIGER HINWEIS:\n"
            "Die Benutzung dieses Programms erfolgt auf EIGENE GEFAHR.\n"
            "Der Autor übernimmt keinerlei Haftung für Schäden an Hardware,\n"
            "Software oder für Unfälle, die durch die Kalibrierung oder\n"
            "den Betrieb der Geräte entstehen können.\n\n"
            "----------------------------------------------------------\n"
            "ENTWICKLUNGSHINWEIS:\n"
            "Dieser Code wurde in enger Zusammenarbeit mit der KI\n"
            "Gemini sowie dem Author erstellt und optimiert."
        )
        QMessageBox.about(self, "Lizenz & Info", license_text)

    def open_guidance(self):
        """
        # English: Opens the instructional manual in a separate window.
        # Deutsch: Öffnet die Bedienungsanleitung in einem separaten Fenster.
        """
        if self.guidance_window is None:
            # English: Create the window instance if it doesn't exist yet.
            # Deutsch: Erstelle die Fenster-Instanz, falls sie noch nicht existiert.
            self.guidance_window = GuidanceWindow(self)
        
        # English: Show and bring to front.
        # Deutsch: Anzeigen und nach vorne bringen.
        self.guidance_window.show()
        self.guidance_window.raise_()
        self.guidance_window.activateWindow()

    def update_steps_restriction(self, is_home):
        """
        # English: 
        # Restricts the number of measurement steps to 1 in HOME mode (Tasmota reference)
        # and disables the input field. In PRO mode, restores the config value and enables it.
        # Deutsch:
        # Begrenzt im HOME-Modus (Tasmota-Referenz) die Anzahl der Messstufen fest auf 1 
        # und deaktiviert das Eingabefeld. Im PRO-Modus wird der Konfigurationswert geladen.
        """
        if hasattr(self.ui, 'spin_steps'):
            # English: Only change if not in manual mode, which has higher priority.
            # Deutsch: Nur ändern, wenn nicht im manuellen Modus, der höhere Priorität hat.
            if hasattr(self.ui, 'check_ref_manual') and self.ui.check_ref_manual.isChecked():
                return

            if is_home:
                # English: Fixed to 1 step in HOME mode. / Deutsch: Fest auf 1 Stufe im HOME-Modus.
                self.ui.spin_steps.setValue(1)
                self.ui.spin_steps.setEnabled(False)
            else:
                # English: Restore value from config and enable in PRO/other mode.
                # Deutsch: Wert aus Config wiederherstellen und im PRO/anderen Modus freigeben.
                config_val = self.cm.config.getint('TARGET', 'measurement_steps', fallback=3)
                self.ui.spin_steps.setValue(config_val)
                self.ui.spin_steps.setEnabled(True)

    def on_manual_ref_toggled(self, is_manual):
        """
        # English: 
        # Handles the logic when the manual reference checkbox is toggled.
        # It shows/hides the manual input frame and restricts step/measurement counts.
        # Deutsch:
        # Behandelt die Logik, wenn die Checkbox für die manuelle Referenz umgeschaltet wird.
        # Blendet den manuellen Eingabe-Frame ein/aus und beschränkt die Stufen/Messanzahl.
        """
        if hasattr(self.ui, 'frame_manuell'):
            self.ui.frame_manuell.setVisible(is_manual)

        if hasattr(self.ui, 'spin_steps') and hasattr(self.ui, 'spin_measurements'):
            if is_manual:
                self.ui.spin_steps.setValue(1)
                self.ui.spin_steps.setEnabled(False)
                self.ui.spin_measurements.setValue(3)
                self.ui.spin_measurements.setEnabled(False)
            else:
                self.ui.spin_steps.setEnabled(True)
                self.ui.spin_measurements.setEnabled(True)
                self.load_values_from_config()
                self.update_steps_restriction(self.ui.check_ref_home.isChecked())

    def start_manual_calibration(self):
        """
        # English: 
        # Starts the manual calibration workflow. It first checks for existing reports for the DUT
        # and asks the user if they want to re-apply old data or start a new manual entry.
        # Deutsch:
        # Startet den manuellen Kalibrier-Workflow. Prüft zuerst auf existierende Reports für die DUT
        # und fragt den Benutzer, ob alte Daten erneut angewendet oder eine neue manuelle Eingabe gestartet werden soll.
        """
        self.ui.log_output.appendPlainText(_("INFO: Starte manuellen Kalibrier-Workflow..."))

        dut_ip = self.ui.edit_dut_ip.text().strip()
        if not dut_ip:
            return self.ui.log_output.appendPlainText("FEHLER: Ziel-Dose IP fehlt!")

        dut_info = self.fetch_tasmota_info(dut_ip, is_dut=True)
        if not dut_info:
            return self.ui.log_output.appendPlainText("❌ ABBRUCH: Ziel-Dose nicht erreichbar!")

        dut_auth = self.credentials_manager.get_credentials(dut_ip)
        auth_tuple = (dut_auth['user'], dut_auth['password']) if dut_auth else None
        mac_param = dut_info.get('mac').replace(":", "-") if dut_info.get('mac') else None
        device_path = self.cm.setup_device_directory(ip=dut_ip, auth=auth_tuple, mac=mac_param)
        mac_display = os.path.basename(device_path)

        report_files = glob.glob(os.path.join(device_path, "*_Protokoll.txt"))
        
        # --- Logic to ask user about re-using old data ---
        if report_files:
            latest_report = max(report_files, key=os.path.getctime)
            last_session_ts = os.path.basename(latest_report).split('_Protokoll.txt')[0].replace('_ReApply','')
            
            try:
                dt_obj = datetime.strptime(last_session_ts, "%Y%m%d_%H%M%S")
                display_time = dt_obj.strftime("%d.%m.%Y um %H:%M:%S Uhr")
            except:
                display_time = last_session_ts

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("Alte Messdaten gefunden")
            msg_box.setText(f"Für diese Tasmota-Dose ({mac_display}) existieren bereits Messdaten vom:\n\n{display_time}\n\nMöchtest du eine komplett neue manuelle Eingabe starten oder die Werte des letzten Reports erneut anwenden?")
            
            btn_new = msg_box.addButton("Neue manuelle Eingabe", QMessageBox.AcceptRole)
            btn_old = msg_box.addButton("Alten Report nutzen", QMessageBox.AcceptRole)
            btn_cancel = msg_box.addButton("Abbrechen", QMessageBox.RejectRole)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == btn_cancel:
                return self.ui.log_output.appendPlainText("⚠️ Vorgang durch Benutzer abgebrochen.")
            
            elif msg_box.clickedButton() == btn_old:
                self.ui.log_output.appendPlainText(f"ℹ️ Überspringe manuelle Eingabe. Nutze alten Report: {os.path.basename(latest_report)}")
                ref_info = {"name": "Manuelle Eingabe"}
                self.prompt_apply_calibration(
                    original_report_path=latest_report,
                    target_ip=dut_ip,
                    all_results=[], # Signifies re-apply
                    dut_info_str=json.dumps(dut_info),
                    ref_info_str=json.dumps(ref_info),
                    mode="MANUAL"
                )
                return

        # --- If no reports or "New manual entry" was chosen ---
        self.ui.log_output.appendPlainText("ℹ️ Bereite die manuelle Eingabe vor...")
        self.set_ui_locked(True)
        self.ui.btn_start.setText(_("⛔ Vorbereitung abbrechen"))
        self.ui.btn_start.setStyleSheet("background-color: darkred; color: white; font-weight: bold;")

        self.manual_worker = ManualSetupWorker(dut_ip, auth_tuple, self.credentials_manager)
        self.manual_worker.log_signal.connect(self.ui.log_output.appendPlainText)
        self.manual_worker.show_popup_signal.connect(self.show_power_popup)
        self.manual_worker.hide_popup_signal.connect(self.hide_power_popup)
        self.manual_worker.finished_signal.connect(self.on_manual_setup_finished)
        self.manual_worker.start()

    def on_manual_setup_finished(self, message):
        """
        # English: Called when the ManualSetupWorker is finished. Enables fields on success.
        # Deutsch: Wird aufgerufen, wenn der ManualSetupWorker fertig ist. Aktiviert bei Erfolg die Felder.
        """
        self.hide_power_popup()

        if "SUCCESS" in message:
            self.ui.log_output.appendPlainText(_("HINWEIS: Bitte geben Sie die 3 Messwert-Paare in die Felder ein."))
            self.set_manual_fields_enabled(True)
            self.is_in_manual_entry_mode = True
            self.ui.btn_start.setText(_("⛔ Manuellen Modus abbrechen"))
            self.ui.btn_start.setStyleSheet("background-color: darkred; color: white; font-weight: bold;")
            self.ui.btn_start.setEnabled(True)
        else:
            self.set_ui_locked(False)
            self.ui.log_output.appendPlainText(message)
            self.ui.btn_start.setText(_("Kalibrierung Starten"))
            self.ui.btn_start.setStyleSheet("")
            self.ui.btn_start.setEnabled(True)
        
        self.manual_worker = None

    def _cancel_manual_entry_mode(self):
        """
        # English: Clears and disables all manual input fields, powers off the DUT, and resets the UI state.
        # Deutsch: Leert und deaktiviert alle manuellen Eingabefelder, schaltet die DUT aus und setzt den UI-Zustand zurück.
        """
        if not self.is_in_manual_entry_mode:
            return

        self.ui.log_output.appendPlainText("INFO: Manueller Eingabemodus wird zurückgesetzt.")

        # --- Power off DUT ---
        dut_ip = self.ui.edit_dut_ip.text().strip()
        if dut_ip:
            try:
                self.ui.log_output.appendPlainText(_("🔌 Sende AUS-Befehl an die Ziel-Dose (DUT)..."))
                creds = self.credentials_manager.get_credentials(dut_ip)
                auth = (creds['user'], creds['password']) if creds else None
                httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2, auth=auth)
                self.ui.log_output.appendPlainText(_("✅ AUS-Befehl gesendet."))
            except Exception as e:
                self.ui.log_output.appendPlainText(_("⚠️ Warnung: AUS-Befehl konnte nicht gesendet werden: {e}").format(e=e))

        self.is_in_manual_entry_mode = False
        self.set_manual_fields_enabled(False)
        self.set_ui_locked(False)

        all_field_keys = [
            'vtas_1', 'vtas_2', 'vtas_3', 'vref_1', 'vref_2', 'vref_3',
            'atas_1', 'atas_2', 'atas_3', 'aref_1', 'aref_2', 'aref_3',
            'wtas_1', 'wtas_2', 'wtas_3', 'wref_1', 'wref_2', 'wref_3'
        ]
        for key in all_field_keys:
            widget_name = f'edit_{key}'
            if hasattr(self.ui, widget_name):
                widget = getattr(self.ui, widget_name)
                widget.setStyleSheet(widget.property("original_style"))
                widget.clear()
        
        self.ui.btn_start.setText(_("Kalibrierung Starten"))
        self.ui.btn_start.setStyleSheet("")
        self.ui.btn_start.setEnabled(True)
        
        if hasattr(self.ui, 'btn_man_ubernehmen'):
            self.ui.btn_man_ubernehmen.setVisible(False)

    def on_manual_apply_clicked(self):
        """
        # English:
        # Handles the click of the 'Apply' button in the manual calibration frame.
        # It reads the values, triggers processing, and powers off the DUT.
        # Deutsch:
        # Behandelt den Klick des 'Übernehmen'-Buttons im manuellen Kalibrier-Frame.
        # Liest die Werte aus, stößt die Verarbeitung an und schaltet die Zieldose ab.
        """
        # English: Disable fields immediately to prevent further editing.
        # Deutsch: Felder sofort deaktivieren, um weitere Bearbeitung zu verhindern.
        self.set_manual_fields_enabled(False)
        self.ui.log_output.appendPlainText(_("INFO: Manuelle Messwerte werden übernommen..."))

        # 1. Read all 18 fields into a dictionary
        all_field_keys = [
            'vtas_1', 'vtas_2', 'vtas_3', 'vref_1', 'vref_2', 'vref_3',
            'atas_1', 'atas_2', 'atas_3', 'aref_1', 'aref_2', 'aref_3',
            'wtas_1', 'wtas_2', 'wtas_3', 'wref_1', 'wref_2', 'wref_3'
        ]
        data_dict = {}
        for key in all_field_keys:
            widget_name = f'edit_{key}'
            if hasattr(self.ui, widget_name):
                data_dict[key] = getattr(self.ui, widget_name).text().strip().replace(',', '.')

        # 2. Get device path
        dut_ip = self.ui.edit_dut_ip.text().strip()
        if not dut_ip:
            self.ui.log_output.appendPlainText(_("FEHLER: Keine IP-Adresse für die Zieldose angegeben."))
            self.set_manual_fields_enabled(True) # Re-enable fields on error
            return

        dut_auth = None
        creds = self.credentials_manager.get_credentials(dut_ip)
        if creds:
            dut_auth = (creds['user'], creds['password'])
            
        dut_info = self.fetch_tasmota_info(dut_ip, is_dut=True)
        if not dut_info:
            self.ui.log_output.appendPlainText(_("FEHLER: Zieldose konnte nicht identifiziert werden."))
            self.set_manual_fields_enabled(True)
            return

        mac_addr = dut_info.get('mac', None)
        mac_param = mac_addr.replace(":", "-") if mac_addr else None
        device_path = self.cm.setup_device_directory(ip=dut_ip, auth=dut_auth, mac=mac_param)

        # 3. Process data using ManualCalibrationEngine
        man_cal_engine = ManualCalibrationEngine()
        csv_path, session_ts = man_cal_engine.process_manual_data(data_dict, device_path)

        if not csv_path:
            self.ui.log_output.appendPlainText(_("FEHLER: Manuelle Daten konnten nicht verarbeitet oder gespeichert werden."))
            self.set_manual_fields_enabled(True) # Re-enable fields on error
            return

        # 4. Run analysis using the main CalibrationEngine
        try:
            from calibration_engine import CalibrationEngine
            ref_manager = ReferenceManager(self.cm.config)
            old_cal = ref_manager.get_current_cal_factors(dut_ip, dut_auth)
            
            engine = CalibrationEngine(device_path)
            step_result = engine.calculate_new_calibration(csv_path, old_cal)
            
            if step_result is None:
                self.ui.log_output.appendPlainText(_("FEHLER: Analyse der manuellen Daten fehlgeschlagen. CSV möglicherweise leer oder fehlerhaft."))
                self.set_manual_fields_enabled(True)
                return

            step_result['Stufe'] = 1
            all_results = [step_result]
            
            dut_info = self.fetch_tasmota_info(dut_ip, is_dut=True)
            ref_info = {"name": "Manuelle Eingabe"}
            current_mode = "MANUAL"

            # 5. FIRST, write the summary to create the report file
            report_file_path = engine.write_summary(
                all_results, session_ts, report_ts=session_ts, cal_mode=current_mode, 
                old_cal=old_cal, dut_info=dut_info, ref_info=ref_info
            )

            # Power off the DUT immediately
            self.ui.log_output.appendPlainText(_("🔌 Schalte Ziel-Dose (DUT) aus..."))
            httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2, auth=dut_auth)
            self.ui.log_output.appendPlainText(_("✅ Ziel-Dose wurde abgeschaltet."))

            # 6. THEN, trigger the dialog with the REAL report path
            self.prompt_apply_calibration(
                original_report_path=report_file_path,
                target_ip=dut_ip,
                all_results=all_results,
                dut_info_str=json.dumps(dut_info),
                ref_info_str=json.dumps(ref_info),
                mode=current_mode
            )

        except Exception as e:
            self.ui.log_output.appendPlainText(_("FEHLER: Unerwarteter Fehler bei der Analyse der manuellen Daten: {e}").format(e=e))
            self.set_manual_fields_enabled(True)
            return
            
        for key in all_field_keys:
            widget_name = f'edit_{key}'
            if hasattr(self.ui, widget_name):
                getattr(self.ui, widget_name).clear()

    def _validate_field_format(self):
        """
        # English: Validates the format of a manual input field (2 or 3 decimals).
        # Deutsch: Validiert das Format eines manuellen Eingabefeldes (2 oder 3 Dezimalen).
        """
        widget = self.sender()
        if not widget: return

        text = widget.text().strip().replace(',', '.')
        field_name = widget.objectName()
        
        if field_name.startswith('edit_a'):
            is_valid_format = bool(re.match(r'^\d+\.\d{3}$', text))
        else:
            is_valid_format = bool(re.match(r'^\d+\.\d{2}$', text))

        original_style = widget.property("original_style")

        if not text:
            widget.setStyleSheet(original_style)
            widget.setProperty("is_invalid", False)
        elif is_valid_format:
            widget.setStyleSheet(original_style)
            widget.setProperty("is_invalid", False)
        else:
            widget.setStyleSheet(original_style + "border: 1px solid red;")
            widget.setProperty("is_invalid", True)

    def _validate_manual_inputs(self):
        """
        # English: Validates content AND format of mandatory power fields.
        # Deutsch: Validiert Inhalt UND Format der obligatorischen Leistungsfelder.
        """
        power_fields = ['edit_wtas_1', 'edit_wtas_2', 'edit_wtas_3', 'edit_wref_1', 'edit_wref_2', 'edit_wref_3']
        all_mandatory_valid = True
        for field_name in power_fields:
            if hasattr(self.ui, field_name):
                widget = getattr(self.ui, field_name)
                if not widget.text().strip() or widget.property("is_invalid"):
                    all_mandatory_valid = False
                    break
        return all_mandatory_valid

    def _on_manual_input_changed(self):
        """
        # English: Slot called when a manual input field's text changes.
        # It triggers validation and updates the visibility of the 'Apply' button.
        # Deutsch: Slot, der bei Textänderung eines manuellen Eingabefeldes aufgerufen wird.
        # Stößt die Validierung an und aktualisiert die Sichtbarkeit des 'Übernehmen'-Buttons.
        """
        is_valid = self._validate_manual_inputs()
        if hasattr(self.ui, 'btn_man_ubernehmen'):
            self.ui.btn_man_ubernehmen.setVisible(is_valid)

    def set_manual_fields_enabled(self, enabled: bool):
        """
        # English: Enables or disables all 18 manual input fields.
        # Deutsch: Aktiviert oder deaktiviert alle 18 manuellen Eingabefelder.
        """
        all_fields = [
            'edit_vtas_1', 'edit_vtas_2', 'edit_vtas_3', 'edit_vref_1', 'edit_vref_2', 'edit_vref_3',
            'edit_atas_1', 'edit_atas_2', 'edit_atas_3', 'edit_aref_1', 'edit_aref_2', 'edit_aref_3',
            'edit_wtas_1', 'edit_wtas_2', 'edit_wtas_3', 'edit_wref_1', 'edit_wref_2', 'edit_wref_3'
        ]
        for field_name in all_fields:
            if hasattr(self.ui, field_name):
                getattr(self.ui, field_name).setEnabled(enabled)

    def on_online_check_clicked(self):
        """
        # English: Slot for the 'Online Check' button. Fetches and displays info from the DUT.
        # Deutsch: Slot für den 'Online Check'-Button. Holt und zeigt Infos vom DUT an.
        """
        ip = self.ui.edit_dut_ip.text().strip()
        
        if len(ip) >= 7 and ip.count('.') == 3:
            self.ui.log_output.appendPlainText(f"🌐 Starte Online-Check für {ip}...")
            self.fetch_tasmota_info(ip, is_dut=True)
        else:
            self.ui.log_output.appendPlainText("⚠️ Bitte erst eine gültige IP-Adresse eingeben.")
            if hasattr(self.ui, 'split_info'):
                self.ui.split_info.setVisible(False)

    def _handle_auth_error(self, ip, attempt):
        """
        # English:
        # Shows a dialog to get credentials from the user and stores them in the manager.
        # This is called when a 401 Unauthorized error is detected.
        # Deutsch:
        # Zeigt einen Dialog an, um Zugangsdaten vom Benutzer zu erhalten und speichert diese im Manager.
        # Wird aufgerufen, wenn ein 401 Unauthorized-Fehler erkannt wird.
        
        :param ip: (str) The IP of the device that requires authentication.
        :param attempt: (int) The current attempt number (1-3).
        :return: (bool) True if the user provided credentials, False if they cancelled.
        """
        device_name = f"Gerät bei IP {ip}"
        dialog = CredentialDialog(device_name, attempt, self)
        
        if dialog.exec() == QDialog.Accepted:
            user, password = dialog.get_credentials()
            if user: # Password can be empty
                self.credentials_manager.set_credentials(ip, user, password)
                self.ui.log_output.appendPlainText(f"ℹ️ Zugangsdaten für {ip} erhalten. Versuche erneut...")
                return True # continue loop
        
        # English: User cancelled the dialog
        # Deutsch: Benutzer hat den Dialog abgebrochen
        return False # break loop

    def fetch_tasmota_info(self, ip, is_dut=True):
        """
        # English:
        # Fetches status information from a Tasmota device.
        # Handles authentication by retrying up to 3 times if a 401 error occurs.
        # Deutsch:
        # Holt Status-Informationen von einem Tasmota-Gerät.
        # Behandelt die Authentifizierung durch bis zu 3 Wiederholungsversuche bei einem 401-Fehler.

        :param ip: (str) The IP address of the device.
        :param is_dut: (bool) True if the device is the DUT (to update specific UI labels).
        :return: (dict or None) A dictionary with device info on success, otherwise None.
        """
        auth = None
        for attempt in range(1, 4):
            try:
                # English: Get credentials from manager if they exist
                # Deutsch: Hole Zugangsdaten aus dem Manager, falls vorhanden
                creds = self.credentials_manager.get_credentials(ip)
                if creds:
                    auth = (creds['user'], creds['password'])

                # English: Make the request
                # Deutsch: Führe die Anfrage durch
                r = httpx.get(f"http://{ip}/cm?cmnd=Status%200", timeout=2.0, auth=auth)
                r.raise_for_status() # Raise exception for 4xx/5xx errors

                # English: Success! Process data.
                # Deutsch: Erfolg! Verarbeite die Daten.
                data = r.json()
                device_name = data.get('Status', {}).get('DeviceName', 'Tasmota')
                hostname = data.get('StatusNET', {}).get('Hostname', 'Unbekannt')
                mac_addr = data.get('StatusNET', {}).get('Mac', 'Unbekannt')
                
                info = {"name": device_name, "host": hostname, "mac": mac_addr}

                if is_dut:
                    raw_version = data.get('StatusFWR', {}).get('Version', 'Unbekannt')
                    clean_version = raw_version.split('(')[0]
                    
                    self.ui.lbl_name.setText(f"{device_name}")
                    self.ui.lbl_version.setText(f"{clean_version}")
                    self.ui.lbl_host.setText(f"{hostname}")
                    self.ui.lbl_mac.setText(f"{mac_addr}")

                    if hasattr(self.ui, 'split_info'):
                        self.ui.split_info.setVisible(True)
                else:
                    # English: Update reference-specific labels
                    # Deutsch: Aktualisiere referenzspezifische Labels
                    raw_version = data.get('StatusFWR', {}).get('Version', 'Unbekannt')
                    clean_version = raw_version.split('(')[0]
                    
                    if hasattr(self.ui, 'lbl_name_ref'): self.ui.lbl_name_ref.setText(f"{device_name}")
                    if hasattr(self.ui, 'lbl_version_ref'): self.ui.lbl_version_ref.setText(f"{clean_version}")
                    if hasattr(self.ui, 'lbl_host_ref'): self.ui.lbl_host_ref.setText(f"{hostname}")
                    if hasattr(self.ui, 'lbl_mac_ref'): self.ui.lbl_mac_ref.setText(f"{mac_addr}")

                self.ui.log_output.appendPlainText(f"✅ Dose '{device_name}' ({ip}) erfolgreich gefunden.")
                return info

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.ui.log_output.appendPlainText(f"🔑 Authentifizierung für {ip} erforderlich.")
                    if not self._handle_auth_error(ip, attempt):
                        # User cancelled
                        break 
                else:
                    self.ui.log_output.appendPlainText(f"❌ Fehler: Dose ({ip}) antwortet mit Status {e.response.status_code}")
                    break # Break on other HTTP errors
            
            except Exception as e:
                self.ui.log_output.appendPlainText(f"❌ Dose ({ip}) nicht erreichbar: {str(e)}")
                break # Break on connection errors etc.

        # English: If the loop finishes without success
        # Deutsch: Wenn die Schleife ohne Erfolg endet
        self.ui.log_output.appendPlainText(f"❌ Verbindung zu {ip} endgültig fehlgeschlagen.")
        if is_dut and hasattr(self.ui, 'split_info'):
            self.ui.split_info.setVisible(False)
        return None

    def reset_lcd_displays(self):
        """
        # English: Resets all reference LCD displays and labels to a 'no data' state.
        # Deutsch: Setzt alle Referenz-LCD-Anzeigen und Labels auf einen 'Keine Daten'-Zustand zurück.
        """
        for lcd_name in ['lcd_volt', 'lcd_amp', 'lcd_watt']:
            if hasattr(self.ui, lcd_name):
                lcd = getattr(self.ui, lcd_name)
                #lcd.setDigitCount(7)
                lcd.display("------")
        
        # English: Reset DUT measurement labels.
        # Deutsch: Setze DUT-Messwert-Labels zurück.
        if hasattr(self.ui, 'lbl_v_dut'): self.ui.lbl_v_dut.setText("----")
        if hasattr(self.ui, 'lbl_a_dut'): self.ui.lbl_a_dut.setText("----")
        if hasattr(self.ui, 'lbl_w_dut'): self.ui.lbl_w_dut.setText("----")

        # English: Reset Reference measurement labels.
        # Deutsch: Setze Referenz-Messwert-Labels zurück.
        if hasattr(self.ui, 'lbl_v_ref'): self.ui.lbl_v_ref.setText("----")
        if hasattr(self.ui, 'lbl_a_ref'): self.ui.lbl_a_ref.setText("----")
        if hasattr(self.ui, 'lbl_w_ref'): self.ui.lbl_w_ref.setText("----")

        # English: Reset Reference device info labels.
        # Deutsch: Setze Referenz-Geräte-Info-Labels zurück.
        if hasattr(self.ui, 'lbl_name_ref'): self.ui.lbl_name_ref.setText("Devicename")
        if hasattr(self.ui, 'lbl_host_ref'): self.ui.lbl_host_ref.setText("Hostname")
        if hasattr(self.ui, 'lbl_mac_ref'): self.ui.lbl_mac_ref.setText("MAC")
        if hasattr(self.ui, 'lbl_version_ref'): self.ui.lbl_version_ref.setText("Version")

    def open_dynamic_cal_dialog(self):
        """
        # English: Opens the dialog for dynamic power calibration.
        # Deutsch: Öffnet den Dialog für die dynamische Power-Kalibrierung.
        """
        dialog = DynamicCalDialog(self, self.cm, self.credentials_manager)
        
        # English: Pre-fill the IP address if available in the main GUI.
        # Deutsch: IP-Adresse vorausfüllen, falls in der Haupt-GUI vorhanden.
        if hasattr(self.ui, 'edit_dut_ip'):
            ip = self.ui.edit_dut_ip.text().strip()
            if ip and ip != "0.0.0.0":
                dialog.ui.edit_ip.setText(ip)
                
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
