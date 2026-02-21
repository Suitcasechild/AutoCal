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
                               QLabel, QLineEdit)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QThread, Signal, QObject, Qt

# Import deiner bestehenden Konfigurations-Logik
from config_manager import ConfigManager
from reference_manager import ReferenceManager
from data_analyzer import DataAnalyzer
from credential_manager import CredentialsManager
from fluke_scan import find_fluke

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
class MeasurementWorker(QThread):
    """
    # English:
    # A QThread worker that performs the entire measurement and calibration process in the background,
    # preventing the GUI from freezing. It communicates with the main window via signals.
    # Deutsch:
    # Ein QThread-Worker, der den gesamten Mess- und Kalibrierprozess im Hintergrund ausführt,
    # um ein Einfrieren der GUI zu verhindern. Er kommuniziert über Signale mit dem Hauptfenster.
    """
    log_signal = Signal(str)
    data_signal = Signal(dict)
    finished_signal = Signal(str)
    apply_request_signal = Signal(str, str, list, str, str) 
    
    show_popup_signal = Signal(str)
    hide_popup_signal = Signal()

    def __init__(self, config, params, credentials_manager):
        """
        # English: Initializes the worker.
        # Deutsch: Initialisiert den Worker.

        :param config: The application's configuration object.
        :param params: A dictionary of parameters for the measurement run.
        :param credentials_manager: The manager for handling device credentials.
        """
        super().__init__()
        self.config = config
        self.params = params
        self.credentials_manager = credentials_manager
        self.is_running = True

    def _get_auth(self, ip):
        """
        # English: Gets the authentication tuple for a given IP from the credentials manager.
        # Deutsch: Holt das Authentifizierungs-Tupel für eine gegebene IP aus dem Credential-Manager.
        """
        creds = self.credentials_manager.get_credentials(ip)
        if creds:
            return (creds['user'], creds['password'])
        return None

    def wait_for_power(self, ip, stufe):
        """
        # English:
        # Waits for the target device to be powered on by polling its status.
        # Shows a popup to the user to prompt them to turn the device on.
        # Deutsch:
        # Wartet darauf, dass das Zielgerät eingeschaltet wird, indem es dessen Status abfragt.
        # Zeigt dem Benutzer ein Popup an, um ihn zum Einschalten des Geräts aufzufordern.
        """
        msg = f"STUFE {stufe}:\nWarte auf Leistung...\n\nBitte Ziel-Dose jetzt EINSCHALTEN!"
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
                # English: No break here, as it might just be a temporary read error. The loop will retry.
                # Deutsch: Kein Abbruch hier, da es nur ein temporärer Lesefehler sein könnte. Die Schleife versucht es erneut.
            time.sleep(1)
            
        self.hide_popup_signal.emit()
        return False 

    def run(self):
        """
        # English: The main execution method of the thread. Contains the entire measurement logic.
        # Deutsch: Die Haupt-Ausführungsmethode des Threads. Enthält die gesamte Messlogik.
        """
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

            # English: Handle the "Re-Apply" case where existing data is used.
            # Deutsch: Behandle den "Re-Apply"-Fall, bei dem bestehende Daten verwendet werden.
            if use_existing:
                self.log_signal.emit(f"🔄 Lese alten Report ({data_ts})...")
                old_report_path = os.path.join(self.params['device_path'], f"{data_ts}_Protokoll.txt")
                
                if not os.path.exists(old_report_path):
                    self.finished_signal.emit(f"❌ Fehler: Der ursprüngliche Report '{old_report_path}' wurde nicht gefunden.")
                    return
                
                # English: Signal the main thread to show the apply-dialog. Then the worker's job is done.
                # Deutsch: Signalisiere dem Haupt-Thread, den Anwenden-Dialog zu zeigen. Dann ist die Arbeit des Workers erledigt.
                self.apply_request_signal.emit(old_report_path, dut_ip, [], dut_info_str, ref_info_str)
                return

            # English: Normal workflow with new hardware measurements.
            # Deutsch: Normaler Ablauf mit neuen Hardware-Messungen.
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

            # English: For HOME mode, determine the DUT's idle consumption offset.
            # Deutsch: Im HOME-Modus, bestimme den Offset durch den Eigenverbrauch des DUT.
            if mode == "HOME":
                self.log_signal.emit("🔌 Schalte Ziel-Dose für Offset-Messung AUS...")
                try:
                    httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2, auth=dut_auth)
                    time.sleep(2) 
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Warnung: Automatisches Ausschalten fehlgeschlagen: {e}")

                if not self.is_running: return
                
                # English: Wait for 5 seconds to ensure DUT is fully off before measuring offset.
                # Deutsch: Warte 5 Sekunden, um sicherzustellen, dass die DUT vollständig ausgeschaltet ist, bevor der Offset gemessen wird.
                self.log_signal.emit("⏳ Warte 5 Sekunden, bis Ziel-Dose vollständig AUS ist...")
                time.sleep(5)
                
                from refhome_offset import ermittle_offset
                offset_a, offset_w = ermittle_offset(ref_ip, ref_auth)
                ref_manager.set_home_offset(offset_a, offset_w)

            # English: Adjust requested measurements for min/max exclusion.
            # Deutsch: Angefragte Messungen für Min/Max-Ausschluss anpassen.
            num_measurements_base = self.params['measurements']
            num_measurements_compensated = num_measurements_base + 2

            # English: Loop through all measurement steps.
            # Deutsch: Schleife durch alle Messstufen.
            for stufe in range(1, self.params['steps'] + 1):
                if not self.is_running: break
                if not self.wait_for_power(dut_ip, stufe): break 
                
                # English: Wait for the inrush current to stabilize.
                # Deutsch: Warte, bis sich der Einschaltstrom stabilisiert hat.
                time.sleep(7) 

                if not self.is_running: break

                self.log_signal.emit(f"\n▶️ Zeichne Messdaten auf (Stufe {stufe}/{self.params['steps']} | {num_measurements_compensated} Messungen)...")
                step_data_list = []
                
                # English: Inner loop for taking multiple measurements per step.
                # Deutsch: Innere Schleife für mehrere Messungen pro Stufe.
                measurement_attempt_count = 0
                while len(step_data_list) < num_measurements_compensated:
                    measurement_attempt_count += 1
                    ref_v, ref_a, ref_w = None, None, None
                    dut_v, dut_a, dut_w = None, None, None
                    
                    try:
                        ref_v, ref_a, ref_w = ref_manager.get_reference_data(ref_auth)
                        if ref_v is None: 
                            self.log_signal.emit(f"[WARN] Messversuch {measurement_attempt_count}: Referenzdaten unvollständig. Wiederhole... ({len(step_data_list)}/{num_measurements_compensated})")
                            time.sleep(0.5)
                            continue
                    except Exception as e:
                        self.log_signal.emit(f"[WARN] Messversuch {measurement_attempt_count}: REFERENZ LESE-FEHLER: {e}. Wiederhole... ({len(step_data_list)}/{num_measurements_compensated})")
                        time.sleep(0.5)
                        continue
                    
                    # English: Check for abort signal before potentially blocking I/O (DUT data).
                    # Deutsch: Prüfe auf Abbruchsignal vor potenziell blockierendem I/O (DUT-Daten).
                    if not self.is_running: break 
                    try:
                        r = httpx.get(f"http://{dut_ip}/cm?cmnd=Status%208", timeout=2, auth=dut_auth)
                        r.raise_for_status()
                        d = r.json()['StatusSNS']['ENERGY']
                        dut_v, dut_a, dut_w = float(d['Voltage']), float(d['Current']), float(d['Power'])
                    except Exception as e: 
                        self.log_signal.emit(f"❌ Messversuch {measurement_attempt_count}: Fehler beim Lesen der Zieldose: {e}. Wiederhole... ({len(step_data_list)}/{num_measurements_compensated})")
                        time.sleep(0.5)
                        continue

                    # English: Check for zero values, which are considered invalid.
                    # Deutsch: Prüfe auf Nullwerte, die als ungültig gelten.
                    if any(val == 0 for val in [ref_v, ref_a, ref_w, dut_v, dut_a, dut_w] if val is not None):
                        self.log_signal.emit(f"[WARN] Messversuch {measurement_attempt_count}: Ungültige Messung (0-Wert). Wiederhole... ({len(step_data_list)}/{num_measurements_compensated})")
                        time.sleep(0.5)
                        continue
                    
                    # English: If everything is valid, add to list and emit signal.
                    # Deutsch: Wenn alles gültig ist, zur Liste hinzufügen und Signal senden.
                    # English: Check for abort signal before emitting and appending valid data.
                    # Deutsch: Prüfe auf Abbruchsignal vor dem Emittieren und Anhängen gültiger Daten.
                    if not self.is_running: break
                    self.data_signal.emit({'volt_ref': ref_v, 'volt_dut': dut_v, 'amp_ref': ref_a, 'amp_dut': dut_a, 'watt_ref': ref_w, 'watt_dut': dut_w, 'dut_off': (dut_w <= 0) })
                    step_data_list.append({'Ref_Volt': ref_v, 'Ref_Amp': ref_a, 'Ref_Watt': ref_w, 'Target_Volt': dut_v, 'Target_Amp': dut_a, 'Target_Watt': dut_w})
                    # English: Removed logging of individual measurement values as requested by the user.
                    # Deutsch: Protokollierung der einzelnen Messwerte wurde auf Benutzerwunsch entfernt.
                    # self.log_signal.emit(f"[{len(step_data_list):>3}/{num_measurements_compensated}] Ref: {ref_w:.2f}W | DUT: {dut_w:.2f}W")
                    time.sleep(1) # Wait for 1 second between valid measurements (original value)


                if step_data_list and self.is_running:
                    df = pd.DataFrame(step_data_list)
                    # English: Round relevant columns to 3 decimal places.
                    # Deutsch: Runde relevante Spalten auf 3 Nachkommastellen.
                    for col in ["Ref_Volt", "Ref_Amp", "Ref_Watt", "Target_Volt", "Target_Amp", "Target_Watt"]:
                        if col in df.columns:
                            df[col] = df[col].round(3)
                    
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
                self.apply_request_signal.emit(report_file, dut_ip, all_results, dut_info_str, ref_info_str)
                return # Job is done, main thread takes over via dialog.

            if not self.is_running:
                # English: Attempt to power off the DUT automatically on manual abort.
                # Deutsch: Versuche die Zieldose bei manuellem Abbruch automatisch auszuschalten.
                try:
                    self.log_signal.emit("🔌 Abbruch erkannt: Schalte Ziel-Dose AUS...")
                    self.data_signal.emit({'volt_ref': None, 'volt_dut': 0.0, 'amp_ref': None, 'amp_dut': 0.0, 'watt_ref': None, 'watt_dut': 0.0, 'dut_off': True})
                    httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2, auth=dut_auth)
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Warnung: Zieldose konnte beim Abbruch nicht ausgeschaltet werden: {e}")
                
                self.finished_signal.emit("⚠️ Messung wurde vom Benutzer abgebrochen.")
            else:
                self.finished_signal.emit("ℹ️ Messung beendet, aber es wurden keine Ergebnisse zum Anwenden generiert.")

        except Exception as e:
            self.finished_signal.emit(f"❌ Schwerer Fehler im Worker: {str(e)}")

    def stop(self):
        """
        # English: Stops the execution of the worker thread.
        # Deutsch: Stoppt die Ausführung des Worker-Threads.
        """
        self.is_running = False


# ---------------------------------------------------------
# 3. DAS PROTOKOLL-POPUP (Custom Dialog)
# ---------------------------------------------------------
class CalibrationReportDialog(QDialog):
    """
    # English:
    # A custom dialog to display the calibration report. It allows the user
    # to view the results, show a regression graph, and decide whether to
    # apply the new calibration values to the device.
    # Deutsch:
    # Ein benutzerdefinierter Dialog zur Anzeige des Kalibrierungsprotokolls. Er ermöglicht
    # dem Benutzer, die Ergebnisse anzusehen, einen Regressionsgraphen anzuzeigen und
    # zu entscheiden, ob die neuen Kalibrierwerte auf das Gerät angewendet werden sollen.
    """
    def __init__(self, parent, target_ip, final_values, is_reapply, report_info, credentials_manager):
        """
        # English: Initializes the CalibrationReportDialog.
        # Deutsch: Initialisiert den CalibrationReportDialog.

        :param parent: The parent widget.
        :param target_ip: (str) IP address of the target device.
        :param final_values: (dict) Dictionary with the calculated final calibration values.
        :param is_reapply: (bool) True if this is a re-apply action on an old report.
        :param report_info: (dict) A dictionary containing metadata about the report.
        :param credentials_manager: The manager for handling device credentials.
        """
        super().__init__(parent)
        self.target_ip = target_ip
        self.final_values = final_values
        self.is_reapply = is_reapply
        self.report_info = report_info 
        self.credentials_manager = credentials_manager
        self.log_callback = parent.ui.log_output.appendPlainText
        self.chosen_pcal = 0
        self.current_report_path = report_info['original_path']

        self.setWindowTitle("Kalibrierungsprotokoll & Anwendung")
        self.resize(850, 700) 
        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("font-family: Consolas, 'Courier New', monospace; font-size: 12px; background-color: #1e1e1e; color: #d4d4d4;")
        self.layout.addWidget(self.text_edit)

        self.load_report_text()

        self.btn_layout = QHBoxLayout()
        self.btn_graph = QPushButton("📊 REGRESSIONS-GRAPH")
        self.btn_graph.setStyleSheet("background-color: #0055a4; color: white; font-weight: bold; padding: 10px;")
        self.btn_graph.clicked.connect(self.show_regression_graph)
        if self.is_reapply:
            self.btn_graph.setEnabled(False)
            self.btn_graph.setToolTip("Grafik ist nur bei einer neuen Messung verfügbar.")

        self.btn_cancel = QPushButton("NICHT KALIBRIEREN")
        self.btn_cancel.setStyleSheet("background-color: darkred; color: white; font-weight: bold; padding: 10px;")
        self.btn_cancel.clicked.connect(self.reject) 

        self.btn_calibrate = QPushButton("KALIBRIEREN")
        self.btn_calibrate.setStyleSheet("background-color: darkgreen; color: white; font-weight: bold; padding: 10px;")
        self.btn_calibrate.clicked.connect(self.apply_calibration_action)

        self.btn_close = QPushButton("SCHLIESSEN")
        self.btn_close.setStyleSheet("background-color: #444; color: white; font-weight: bold; padding: 10px;")
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.hide()

        self.btn_layout.addWidget(self.btn_graph)
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addWidget(self.btn_calibrate)
        self.btn_layout.addWidget(self.btn_close)
        self.layout.addLayout(self.btn_layout)

    def load_report_text(self):
        """
        # English: Loads the content of the report file into the text edit widget.
        # Deutsch: Lädt den Inhalt der Protokolldatei in das Text-Edit-Widget.
        """
        try:
            with open(self.current_report_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            self.text_edit.setPlainText(content)
            self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        except Exception as e:
            self.text_edit.setPlainText(f"Fehler beim Laden des Berichts:\n{e}")

    def show_regression_graph(self):
        """
        # English:
        # Reads all CSV data for the session and displays a regression plot for power values.
        # Deutsch:
        # Liest alle CSV-Daten der Sitzung und zeigt einen Regressions-Plot für die Leistungswerte an.
        """
        if self.is_reapply:
            QMessageBox.warning(self, "Keine Daten", "Die Regressions-Grafik ist nur bei einer neuen Messung verfügbar.")
            return

        search_path = os.path.join(self.report_info['device_path'], f"{self.report_info['session_ts']}_Stufe_*.csv")
        files = glob.glob(search_path)
        if not files:
            QMessageBox.warning(self, "Keine Daten", "Es konnten keine CSV-Dateien für den Graphen gefunden werden.")
            return

        df_list = [pd.read_csv(f) for f in files]
        full_df = pd.concat(df_list, ignore_index=True)
        x, y = full_df['Target_Watt'].values, full_df['Ref_Watt'].values
        if len(x) == 0: return

        m, _, _, _ = np.linalg.lstsq(x[:, np.newaxis], y, rcond=None)
        slope = float(m[0])
        
        graph_dialog = QDialog(self)
        graph_dialog.setWindowTitle(f"Regressions-Analyse (Leistung) | Steigung m = {slope:.5f}")
        graph_dialog.resize(800, 600)
        layout = QVBoxLayout(graph_dialog)
        plot_widget = pg.PlotWidget(background='#1e1e1e')
        plot_widget.setLabel('left', 'Referenz Leistung (Soll)', units='W')
        plot_widget.setLabel('bottom', 'Dose Leistung (Ist)', units='W')
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_widget.addLegend(offset=(30, 30))
        layout.addWidget(plot_widget)

        plot_widget.plot(x, y, pen=None, symbol='o', symbolSize=7, symbolBrush=(255, 255, 255, 150), name="Messpunkte (Vorher)")
        max_val = max(max(x), max(y)) * 1.05 if len(x) > 0 and len(y) > 0 else 1
        x_line = np.array([0, max_val])
        plot_widget.plot(x_line, x_line, pen=pg.mkPen('y', width=2, style=Qt.DashLine), name="Idealzustand (1:1)")
        plot_widget.plot(x_line, x_line * slope, pen=pg.mkPen('g', width=3), name=f"Ausgleichsgerade (m={slope:.5f})")
        graph_dialog.exec()

    def apply_calibration_action(self):
        """
        # English:
        # Handles the user's decision to apply the calibration. It asks for the PowerCal method,
        # then calls the function to send the data to the device.
        # Deutsch:
        # Behandelt die Entscheidung des Benutzers, die Kalibrierung anzuwenden. Fragt nach der
        # PowerCal-Methode und ruft dann die Funktion zum Senden der Daten an das Gerät auf.
        """
        # English: Show a dialog to choose the PowerCal method.
        # Deutsch: Zeige einen Dialog zur Auswahl der PowerCal-Methode an.
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("PowerCal-Methode wählen")
        msg_box.setText("Welcher Wert soll für <b>PowerCal</b> verwendet werden?")
        msg_box.setIcon(QMessageBox.Question)
        btn_regression = msg_box.addButton(f"Regression ({self.final_values['pcal_regression']})", QMessageBox.AcceptRole)
        btn_mittelwert = msg_box.addButton(f"Mittelwert ({self.final_values['pcal_avg']})", QMessageBox.AcceptRole)
        msg_box.addButton("Abbrechen", QMessageBox.RejectRole)
        msg_box.setDefaultButton(btn_regression)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        if clicked_button == btn_regression:
            self.chosen_pcal = self.final_values['pcal_regression']
            self.log_callback("ℹ️ PowerCal-Methode: Regression ausgewählt.")
        elif clicked_button == btn_mittelwert:
            self.chosen_pcal = self.final_values['pcal_avg']
            self.log_callback("ℹ️ PowerCal-Methode: Mittelwert ausgewählt.")
        else:
            self.log_callback("ℹ️ Kalibrierung im Auswahl-Dialog abgebrochen.")
            return

        # English: Toggle buttons to prevent multiple clicks.
        # Deutsch: Schalte die Buttons um, um Mehrfachklicks zu verhindern.
        self.btn_calibrate.hide()
        self.btn_cancel.hide()
        QApplication.processEvents()

        from send_cal import apply_calibration
        from calibration_engine import CalibrationEngine

        self.log_callback("\n🚀 Starte Übertragung an die Dose...")
        
        # English: Get auth tuple from manager.
        # Deutsch: Hole Auth-Tupel aus dem Manager.
        auth = None
        creds = self.credentials_manager.get_credentials(self.target_ip)
        if creds:
            auth = (creds['user'], creds['password'])
            
        as_found_left_string = apply_calibration(self.target_ip, self.final_values['vcal'], self.final_values['acal'], self.chosen_pcal, auth=auth)

        if as_found_left_string:
            self.log_callback("✅ Übertragung abgeschlossen.")
            
            report_to_update = self.report_info['original_path']
            engine = CalibrationEngine(self.report_info['device_path'])

            # English: If re-applying, create a new, short report.
            # Deutsch: Bei einer Wiederanwendung, erstelle ein neues, kurzes Protokoll.
            if self.is_reapply:
                new_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_report_path = os.path.join(self.report_info['device_path'], f"{new_ts}_ReApply_Protokoll.txt")
                engine.write_reapply_summary(new_report_path, self.report_info['original_path'], self.report_info['dut_info'], self.report_info['ref_info'])
                report_to_update = new_report_path
            
            # English: Append the "As Found/Left" block to the correct report.
            # Deutsch: Hänge den "As Found/Left"-Block an das korrekte Protokoll an.
            try:
                with open(report_to_update, "a", encoding="utf-8") as f:
                    f.write(as_found_left_string)
                self.log_callback(f"✅ Report '{os.path.basename(report_to_update)}' aktualisiert.")
                self.current_report_path = report_to_update
                self.load_report_text()
            except Exception as e:
                self.log_callback(f"❌ Fehler beim Aktualisieren des Reports: {e}")
        else:
            self.log_callback("❌ Übertragung fehlgeschlagen. Siehe Log für Details.")
        
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
        self.setWindowTitle(f"Zugangsdaten für {device_name}")
        self.setModal(True)

        self.layout = QVBoxLayout(self)

        # English: Add a descriptive label
        # Deutsch: Füge ein beschreibendes Label hinzu
        self.info_label = QLabel(f"Zugangsdaten für '{device_name}' erforderlich (Versuch {attempt}/3).")
        self.layout.addWidget(self.info_label)

        # English: Username field
        # Deutsch: Benutzername-Feld
        self.user_label = QLabel("Benutzername:")
        self.user_input = QLineEdit(self)
        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.user_input)

        # English: Password field
        # Deutsch: Passwort-Feld
        self.pass_label = QLabel("Passwort:")
        self.pass_input = QLineEdit(self)
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.pass_label)
        self.layout.addWidget(self.pass_input)
        
        # English: Add a disclaimer that the credentials are not stored permanently.
        # Deutsch: Füge einen Hinweis hinzu, dass die Zugangsdaten nicht dauerhaft gespeichert werden.
        self.disclaimer_label = QLabel(
            "<i>Die Zugangsdaten werden nicht dauerhaft gespeichert und nur für diesen Kalibrierprozess verwendet.</i>"
        )
        self.disclaimer_label.setWordWrap(True)
        self.layout.addWidget(self.disclaimer_label)

        # English: OK and Cancel buttons
        # Deutsch: OK- und Abbrechen-Buttons
        self.btn_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Abbrechen", self)
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
# 5. DAS HAUPTFENSTER (GUI)
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
        self.setWindowTitle("Tasmota Precision Calibrator v5.3.0") # Will be updated later

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

        if hasattr(self.ui, 'split_info'):
            self.ui.split_info.setVisible(False)
        
        # English: Initialize visibility of reference frames based on checkbox state.
        # Deutsch: Initialisiere Sichtbarkeit der Referenz-Frames basierend auf dem Checkbox-Status.
        if hasattr(self.ui, 'frame_fluke'):
            self.ui.frame_fluke.setVisible(self.ui.check_ref_pro.isChecked())
        if hasattr(self.ui, 'frame_tasref'):
            self.ui.frame_tasref.setVisible(self.ui.check_ref_home.isChecked())
            
        if hasattr(self.ui, 'btn_onlinechk'):
            self.ui.btn_onlinechk.clicked.connect(self.on_online_check_clicked)
            
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

    def setup_graphs(self):
        """
        # English: Initializes the live-data plotting graphs.
        # Deutsch: Initialisiert die Graphen für die Live-Daten-Darstellung.
        """
        pg.setConfigOption('background', '#1e1e1e')
        pg.setConfigOption('foreground', 'w')
        self.curves = {}
        configs = {
            'chart_volt': ('volt', 'Spannung', 'V', 'y', 'w'),
            'chart_amp':  ('amp',  'Strom',    'A', 'c', 'w'),
            'chart_watt': ('watt', 'Leistung', 'W', 'm', 'w')
        }
        for widget_name, (key, title, unit, col_dut, col_ref) in configs.items():
            if hasattr(self.ui, widget_name):
                widget = getattr(self.ui, widget_name)
                layout = QVBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                plot_widget = pg.PlotWidget()
                plot_widget.setLabel('left', title, units=unit)
                plot_widget.setLabel('bottom', 'Messung', units='#')
                plot_widget.showGrid(x=True, y=True)
                plot_widget.addLegend(offset=(30, 10))
                
                pen_ref = pg.mkPen(col_ref, width=1, style=pg.QtCore.Qt.DashLine)
                self.curves[f"{key}_ref"] = plot_widget.plot(pen=pen_ref, name=f"Soll (Ref)")
                
                pen_dut = pg.mkPen(col_dut, width=2)
                self.curves[f"{key}_dut"] = plot_widget.plot(pen=pen_dut, name=f"Ist (DUT)")
                
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
        self.ui.check_ref_pro.toggled.connect(lambda c: self.ui.check_ref_home.setChecked(False) if c else None)
        self.ui.check_ref_home.toggled.connect(lambda c: self.ui.check_ref_pro.setChecked(False) if c else None)

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
            return QMessageBox.warning(self, "Fehler", "Datei setup_general.ui nicht gefunden!")
            
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        dialog = QUiLoader().load(ui_file, self)
        ui_file.close()
        
        if hasattr(dialog, 'edit_report_dir'):
            dialog.edit_report_dir.setText(self.cm.config.get('GENERAL', 'root_report_dir', fallback='./Reports'))
            
            def open_directory_browser():
                start_dir = dialog.edit_report_dir.text()
                folder = QFileDialog.getExistingDirectory(dialog, "Report Ordner auswählen", start_dir)
                if folder:
                    dialog.edit_report_dir.setText(folder)

            if hasattr(dialog, 'btn_browse_dir'):
                dialog.btn_browse_dir.clicked.connect(open_directory_browser)
            
        def save_and_close():
            if hasattr(dialog, 'edit_report_dir'):
                self.cm.config['GENERAL']['root_report_dir'] = dialog.edit_report_dir.text().strip()
                self.cm.root_dir = self.cm.config['GENERAL']['root_report_dir'] 
            
            with open(self.cm.config_path, 'w') as f: self.cm.config.write(f)
            self.ui.log_output.appendPlainText("✅ Allgemeines Setup in config.ini gespeichert.")
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
            return QMessageBox.warning(self, "Fehler", "Datei setup_fluke.ui nicht gefunden!")
            
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        dialog = QUiLoader().load(ui_file, self)
        ui_file.close()
        
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
        file_path, _ = QFileDialog.getSaveFileName(self, "Log sichern", default_name, "Textdateien (*.txt)")
        
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
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.ui.log_output.appendPlainText("⚠️ Sende Abbruch-Signal... Bitte warten.")
            self.worker.stop()
            self.ui.btn_start.setEnabled(False) 
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
        self.credentials_manager.clear_all_credentials()
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
        self.credentials_manager.clear_all_credentials()
        if message: 
            self.ui.log_output.appendPlainText(message)
        self.ui.btn_start.setText("Kalibrierung Starten")
        self.ui.btn_start.setStyleSheet("") 
        self.ui.btn_start.setEnabled(True)
        
        # English: Re-enable UI frames and menu after measurement.
        # Deutsch: Gebe UI-Frames und Menü nach der Messung wieder frei.
        self.set_ui_locked(False)

        self.hide_power_popup()
        self.reset_lcd_displays()

    def _parse_report_for_values(self, report_path):
        """
        # English: Parses a report file to extract the final suggested calibration values.
        # Deutsch: Parst eine Protokolldatei, um die finalen vorgeschlagenen Kalibrierwerte zu extrahieren.
        """
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            vcal_match = re.search(r"VoltageCal \d+\s+VoltageCal (\d+)", content)
            acal_match = re.search(r"CurrentCal \d+\s+CurrentCal (\d+)", content)
            pcal_reg_match = re.search(r"PowerCal \d+\s+PowerCal (\d+)", content)
            pcal_avg_match = re.search(r"Alternative: (\d+)", content)

            if vcal_match and acal_match and pcal_reg_match and pcal_avg_match:
                return {
                    "vcal": int(vcal_match.group(1)),
                    "acal": int(acal_match.group(1)),
                    "pcal_regression": int(pcal_reg_match.group(1)),
                    "pcal_avg": int(pcal_avg_match.group(1))
                }
        except Exception as e:
            self.ui.log_output.appendPlainText(f"❌ Fehler beim Parsen des Reports: {e}")
        return None

    def prompt_apply_calibration(self, original_report_path, target_ip, all_results, dut_info_str, ref_info_str):
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
        
        device_path = os.path.dirname(original_report_path)
        try:
            session_ts = os.path.basename(original_report_path).split('_Protokoll.txt')[0].split('_ReApply')[0]
        except Exception:
            session_ts = None 

        dut_info = json.loads(dut_info_str) if dut_info_str and dut_info_str != 'null' else {}
        ref_info = json.loads(ref_info_str) if ref_info_str and ref_info_str != 'null' else {}

        if is_reapply:
            self.ui.log_output.appendPlainText("-> Kalibrierung auf Basis eines alten Reports (Re-Apply).")
            final_values = self._parse_report_for_values(original_report_path)
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
            
            reg_data = DataAnalyzer.calculate_regression(device_path, session_ts)
            if reg_data and all_results:
                old_cal = all_results[0].get('Alt_Cal', {})
                p_reg = reg_data['Power']
                pcal_regression = int(old_cal.get('WCal', 12500) * p_reg['slope'])
                
            final_values = { "vcal": vcal, "acal": acal, "pcal_avg": pcal_avg, "pcal_regression": pcal_regression }
        
        report_info = {
            'original_path': original_report_path,
            'device_path': device_path,
            'session_ts': session_ts,
            'dut_info': dut_info,
            'ref_info': ref_info
        }

        dialog = CalibrationReportDialog(self, target_ip, final_values, is_reapply, report_info, self.credentials_manager)
        dialog.exec()
        
        self.measurement_finished("🏁 Der gesamte Kalibrierprozess ist beendet.")

    def show_license_info(self):
        """
        # English: Displays a message box with license and author information.
        # Deutsch: Zeigt eine Message-Box mit Lizenz- und Autoreninformationen an.
        """
        license_text = (
            "Tasmota Precision Calibrator v5.3.0\n"
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
