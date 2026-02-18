import sys
import os
import time
import httpx
import glob
import numpy as np
import pandas as pd
from datetime import datetime
import pyqtgraph as pg
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QMessageBox, 
                               QDialog, QTextEdit, QHBoxLayout, QPushButton)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QThread, Signal, QObject, Qt

# Import deiner bestehenden Konfigurations-Logik
from config_manager import ConfigManager
from reference_manager import ReferenceManager

# ---------------------------------------------------------
# 1. DER LOG-SPION
# ---------------------------------------------------------
class OutputStreamProxy(QObject):
    message_signal = Signal(str)
    def write(self, text):
        if text and text.strip():
            self.message_signal.emit(text.strip())
    def flush(self):
        pass

# ---------------------------------------------------------
# 2. DER MESS-ARBEITER (Hintergrund-Thread)
# ---------------------------------------------------------
class MeasurementWorker(QThread):
    log_signal = Signal(str)
    data_signal = Signal(dict)
    finished_signal = Signal(str)
    
    # NEU: Wir geben jetzt auch Pfad und Zeitstempel an die GUI weiter
    apply_request_signal = Signal(str, str, list, str, str) 
    
    show_popup_signal = Signal(str)
    hide_popup_signal = Signal()

    def __init__(self, config, params):
        super().__init__()
        self.config = config
        self.params = params
        self.is_running = True

    def wait_for_power(self, ip, stufe):
        msg = f"STUFE {stufe}:\nWarte auf Leistung...\n\nBitte Ziel-Dose jetzt EINSCHALTEN!"
        self.log_signal.emit(f"⏳ STUFE {stufe}: Warte auf Leistung...")
        
        self.show_popup_signal.emit(msg)
        
        while self.is_running:
            try:
                r = httpx.get(f"http://{ip}/cm?cmnd=Status%2011", timeout=2.0)
                if r.json()['StatusSTS']['POWER'] == 'ON':
                    self.log_signal.emit(f"✅ Power ON erkannt! Starte Inrush-Filter (7s)...")
                    self.hide_popup_signal.emit()
                    return True
            except:
                pass
            time.sleep(1)
            
        self.hide_popup_signal.emit()
        return False 

    def run(self):
        try:
            from main import check_device_availability
            from refhome_offset import ermittle_offset
            from calibration_engine import CalibrationEngine

            dut_ip = self.params['dut_ip']
            ref_ip = self.params['ref_ip']
            mode = self.params['mode']
            data_ts = self.params['session_ts']
            
            # --- 1. PRE-CHECK: ONLINE STATUS ---
            self.log_signal.emit("🔄 Prüfe Erreichbarkeit der Geräte...")
            if not check_device_availability(dut_ip, "Ziel-Dose"):
                self.finished_signal.emit("❌ ABBRUCH: Ziel-Dose nicht erreichbar!")
                return
            if mode == "HOME" and not check_device_availability(ref_ip, "Tasmota-Referenz"):
                self.finished_signal.emit("❌ ABBRUCH: Referenz-Dose nicht erreichbar!")
                return

            # --- 2. HARDWARE & COM-PORT CHECK ---
            self.log_signal.emit("🔄 Initialisiere Referenz-Hardware...")
            ref_manager = ReferenceManager(self.config)
            
            if mode == "PRO":
                if not ref_manager.set_mode('PRO'):
                    self.finished_signal.emit("❌ ABBRUCH: COM-Port Fehler! Fluke antwortet nicht oder Kabel fehlt.")
                    return
            else:
                ref_manager.set_mode('HOME')

            # --- 3. VORBEREITUNG & OFFSET ---
            from main import prepare_dut
            prepare_dut(dut_ip)
            old_cal = ref_manager.get_current_cal_factors(dut_ip)

            if mode == "HOME":
                self.log_signal.emit("🔌 Schalte Ziel-Dose für Offset-Messung AUS...")
                try:
                    httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2)
                    time.sleep(2) 
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Warnung: Automatisches Ausschalten fehlgeschlagen: {e}")

                if not self.is_running: return
                offset_a, offset_w = ermittle_offset(ref_ip)
                ref_manager.set_home_offset(offset_a, offset_w)

            # --- 4. MESS-SCHLEIFE ---
            engine = CalibrationEngine(self.params['device_path'])
            all_results = []

            for stufe in range(1, self.params['steps'] + 1):
                if not self.is_running: break

                if not self.wait_for_power(dut_ip, stufe): 
                    break 
                
                for _ in range(7):
                    if not self.is_running: return
                    time.sleep(1)

                if not self.is_running: break

                self.log_signal.emit(f"\n▶️ Zeichne Messdaten auf (Stufe {stufe}/{self.params['steps']} | {self.params['duration']}s)...")
                step_data_list = []
                start_time = time.time()

                while (time.time() - start_time) < self.params['duration']:
                    if not self.is_running: break
                    
                    try:
                        ref_v, ref_a, ref_w = ref_manager.get_reference_data()
                        if ref_v is None:
                            ref_v, ref_a, ref_w = 0.0, 0.0, 0.0
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ REFERENZ LESE-FEHLER: {e}")
                        ref_v, ref_a, ref_w = 0.0, 0.0, 0.0
                    
                    try:
                        r = httpx.get(f"http://{dut_ip}/cm?cmnd=Status%208", timeout=2)
                        d = r.json()['StatusSNS']['ENERGY']
                        dut_v, dut_a, dut_w = float(d['Voltage']), float(d['Current']), float(d['Power'])
                    except: 
                        dut_v, dut_a, dut_w = 0.0, 0.0, 0.0

                    self.data_signal.emit({
                        'volt_ref': ref_v, 'volt_dut': dut_v,
                        'amp_ref': ref_a,  'amp_dut': dut_a,
                        'watt_ref': ref_w, 'watt_dut': dut_w
                    })

                    step_data_list.append({
                        'Ref_Volt': ref_v, 'Ref_Amp': ref_a, 'Ref_Watt': ref_w,
                        'Target_Volt': dut_v, 'Target_Amp': dut_a, 'Target_Watt': dut_w
                    })
                    time.sleep(1)

                if step_data_list and self.is_running:
                    df = pd.DataFrame(step_data_list)
                    csv_name = f"{data_ts}_Stufe_{stufe}.csv"
                    csv_path = os.path.join(self.params['device_path'], csv_name)
                    df.to_csv(csv_path, index=False)
                    self.log_signal.emit(f"💾 {csv_name} gespeichert.")

                    res = engine.calculate_new_calibration(csv_path, old_cal)
                    res['Stufe'] = stufe
                    all_results.append(res)
                    
                    try:
                        self.log_signal.emit(f"🔌 Schalte Ziel-Dose nach Stufe {stufe} AUS...")
                        httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2)
                        time.sleep(3.0) 
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ Warnung: Konnte Ziel-Dose nicht ausschalten: {e}")

            # --- 5. PROTOKOLL & ABSCHLUSS ---
            if all_results and self.is_running:
                report_file = engine.write_summary(all_results, data_ts, report_ts=data_ts, cal_mode=mode, old_cal=old_cal)
                self.log_signal.emit("\n" + "="*40)
                self.log_signal.emit("ERMITTLUNG DER KALIBRIERWERTE ABGESCHLOSSEN")
                self.log_signal.emit("="*40)
                
                # Sende zusätzlich device_path und session_ts für den Graphen!
                self.apply_request_signal.emit(report_file, dut_ip, all_results, self.params['device_path'], data_ts)
            
            if not self.is_running:
                self.finished_signal.emit("⚠️ Messung wurde vom Benutzer abgebrochen.")

        except Exception as e:
            self.finished_signal.emit(f"❌ Schwerer Fehler: {str(e)}")

    def stop(self):
        self.is_running = False

# ---------------------------------------------------------
# 3. DAS NEUE PROTOKOLL-POPUP (Custom Dialog)
# ---------------------------------------------------------
class CalibrationReportDialog(QDialog):
    def __init__(self, parent, report_file, target_ip, all_results, log_callback, device_path, session_ts):
        super().__init__(parent)
        self.report_file = report_file
        self.target_ip = target_ip
        self.all_results = all_results
        self.log_callback = log_callback
        self.device_path = device_path
        self.session_ts = session_ts

        self.setWindowTitle("Kalibrierungsprotokoll & Anwendung")
        self.resize(850, 700) 

        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        # Fixierter Courier New Font gegen Windows-Warnungen
        self.text_edit.setStyleSheet("font-family: Consolas, 'Courier New', monospace; font-size: 12px; background-color: #1e1e1e; color: #d4d4d4;")
        self.layout.addWidget(self.text_edit)

        self.load_report_text()

        self.btn_layout = QHBoxLayout()

        # NEU: Der Button für den Graphen
        self.btn_graph = QPushButton("📊 REGRESSIONS-GRAPH")
        self.btn_graph.setStyleSheet("background-color: #0055a4; color: white; font-weight: bold; padding: 10px;")
        self.btn_graph.clicked.connect(self.show_regression_graph)

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

        self.btn_layout.addWidget(self.btn_graph) # Links anordnen
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addWidget(self.btn_calibrate)
        self.btn_layout.addWidget(self.btn_close)

        self.layout.addLayout(self.btn_layout)

    def load_report_text(self):
        try:
            with open(self.report_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                self.text_edit.setPlainText(content)
                
                scrollbar = self.text_edit.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            self.text_edit.setPlainText(f"Fehler beim Laden des Berichts:\n{e}")

    def show_regression_graph(self):
        """Liest die CSVs und zeichnet die Regressionsgerade in ein neues Popup."""
        search_path = os.path.join(self.device_path, f"{self.session_ts}_Stufe_*.csv")
        files = glob.glob(search_path)
        
        if not files:
            QMessageBox.warning(self, "Keine Daten", "Es konnten keine CSV-Dateien für den Graphen gefunden werden.")
            return

        # Daten aus allen Stufen zusammenführen
        df_list = [pd.read_csv(f) for f in files]
        full_df = pd.concat(df_list, ignore_index=True)

        x = full_df['Target_Watt'].values  # Ist-Werte (DUT)
        y = full_df['Ref_Watt'].values     # Soll-Werte (Ref)

        if len(x) == 0:
            return

        # Berechnung der Regression (exakt wie in deinem DataAnalyzer)
        m, _, _, _ = np.linalg.lstsq(x[:, np.newaxis], y, rcond=None)
        slope = float(m[0])

        # Neues Popup-Fenster erstellen
        graph_dialog = QDialog(self)
        graph_dialog.setWindowTitle(f"Regressions-Analyse (Leistung) | Steigung m = {slope:.5f}")
        graph_dialog.resize(800, 600)
        
        layout = QVBoxLayout(graph_dialog)
        
        # Plot-Widget initialisieren
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('#1e1e1e')
        plot_widget.setLabel('left', 'Referenz Leistung (Soll)', units='W')
        plot_widget.setLabel('bottom', 'Dose Leistung (Ist)', units='W')
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_widget.addLegend(offset=(30, 30))
        layout.addWidget(plot_widget)

        # 1. Messwerte (Streudiagramm als Punkte)
        plot_widget.plot(x, y, pen=None, symbol='o', symbolSize=7, 
                         symbolBrush=(255, 255, 255, 150), name="Messpunkte (Vorher)")

        # 2. Die Ideal-Linie (1:1), wie es ohne Messfehler sein sollte
        max_val = max(max(x), max(y)) * 1.05
        x_line = np.array([0, max_val])
        plot_widget.plot(x_line, x_line, pen=pg.mkPen('y', width=2, style=Qt.DashLine), 
                         name="Idealzustand (1:1)")

        # 3. Die Ausgleichsgerade (Regression), die das Programm berechnet hat
        y_reg = x_line * slope
        plot_widget.plot(x_line, y_reg, pen=pg.mkPen('g', width=3), 
                         name=f"Ausgleichsgerade (m={slope:.5f})")

        # Info-Label unter dem Graphen
        info_label = QTextEdit()
        info_label.setReadOnly(True)
        info_label.setMaximumHeight(80)
        info_label.setStyleSheet("background-color: #2b2b2b; color: #a9b7c6; font-size: 13px; border: none;")
        info_label.setPlainText("Erklärung:\nDie gelbe Linie ist der Idealzustand. Die weißen Punkte sind die echten Messwerte der Dose.\n"
                                "Die grüne Linie ist die Regression (Berechnung des Programms). Der Faktor, um den die grüne von der gelben Linie abweicht, ist die Korrektur!")
        layout.addWidget(info_label)

        # Zeige das Fenster
        graph_dialog.exec()

    def apply_calibration_action(self):
        self.btn_calibrate.hide()
        self.btn_cancel.hide()
        # Hinweis: Den Graphen-Button lassen wir sichtbar, falls man ihn nach dem Flashen nochmal ansehen will!
        QApplication.processEvents() 
        
        self.log_callback("\n🚀 Starte Übertragung an die Dose...")
        from send_cal import apply_calibration
        
        apply_calibration(self.target_ip, self.all_results, self.report_file)
        self.log_callback("✅ Übertragung abgeschlossen.")
        
        self.load_report_text()
        self.btn_close.show()

# ---------------------------------------------------------
# 4. DAS HAUPTFENSTER (GUI)
# ---------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cm = ConfigManager()
        self.wait_msgbox = None 
        
        ui_path = os.path.join(os.path.dirname(__file__), "main_gui.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.setCentralWidget(self.ui)
        self.resize(self.ui.size())
        self.setWindowTitle("Tasmota Precision Calibrator v5.0")

        self.log_proxy = OutputStreamProxy()
        self.log_proxy.message_signal.connect(self.ui.log_output.appendPlainText)
        sys.stdout = self.log_proxy

        self.graph_data = {'volt_ref': [], 'volt_dut': [], 'amp_ref': [], 'amp_dut': [], 'watt_ref': [], 'watt_dut': []}
        
        self.setup_graphs()
        self.setup_ui_logic()
        self.load_values_from_config()

    def setup_graphs(self):
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
                plot_widget.setLabel('bottom', 'Zeit', units='s')
                plot_widget.showGrid(x=True, y=True)
                plot_widget.addLegend(offset=(30, 10))
                
                pen_ref = pg.mkPen(col_ref, width=1, style=pg.QtCore.Qt.DashLine)
                self.curves[f"{key}_ref"] = plot_widget.plot(pen=pen_ref, name=f"Soll (Ref)")
                
                pen_dut = pg.mkPen(col_dut, width=2)
                self.curves[f"{key}_dut"] = plot_widget.plot(pen=pen_dut, name=f"Ist (DUT)")
                
                layout.addWidget(plot_widget)

    def setup_ui_logic(self):
        self.ui.btn_start.clicked.connect(self.toggle_measurement)
        self.ui.check_ref_pro.toggled.connect(lambda c: self.ui.check_ref_home.setChecked(False) if c else None)
        self.ui.check_ref_home.toggled.connect(lambda c: self.ui.check_ref_pro.setChecked(False) if c else None)

    def load_values_from_config(self):
        try:
            if hasattr(self.ui, 'edit_com_port'): self.ui.edit_com_port.setText(self.cm.config.get('REFERENCE_PRO', 'com_port', fallback='COM3'))
            if hasattr(self.ui, 'edit_ref_ip'): self.ui.edit_ref_ip.setText(self.cm.config.get('REFERENCE_HOME', 'ip_address', fallback='10.0.0.202'))
            if hasattr(self.ui, 'edit_dut_ip'): self.ui.edit_dut_ip.setText(self.cm.config.get('TARGET', 'ip_address', fallback='10.0.0.200'))
            if hasattr(self.ui, 'spin_steps'): self.ui.spin_steps.setValue(self.cm.config.getint('TARGET', 'measurement_steps', fallback=3))
            if hasattr(self.ui, 'spin_duration'): self.ui.spin_duration.setValue(self.cm.config.getint('TARGET', 'duration_per_step', fallback=15))
        except Exception as e:
            self.ui.log_output.appendPlainText(f"❌ Fehler beim Laden der INI: {e}")

    def show_power_popup(self, message):
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
        if self.wait_msgbox is not None:
            try:
                self.wait_msgbox.rejected.disconnect(self.cancel_from_popup)
            except:
                pass
            self.wait_msgbox.accept()
            self.wait_msgbox = None

    def cancel_from_popup(self):
        self.ui.log_output.appendPlainText("⚠️ Abbruch durch Benutzer im Popup-Fenster.")
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
            self.ui.btn_start.setEnabled(False) 

    def toggle_measurement(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.ui.log_output.appendPlainText("⚠️ Sende Abbruch-Signal... Bitte warten.")
            self.worker.stop()
            self.ui.btn_start.setEnabled(False) 
        else:
            self.start_measurement()

    def start_measurement(self):
        is_pro = self.ui.check_ref_pro.isChecked()
        is_home = self.ui.check_ref_home.isChecked()
        if not is_pro and not is_home:
            return self.ui.log_output.appendPlainText("❌ ABBRUCH: Keine Referenzquelle ausgewählt!")

        com_port, ref_ip, dut_ip = self.ui.edit_com_port.text().strip(), self.ui.edit_ref_ip.text().strip(), self.ui.edit_dut_ip.text().strip()
        steps, duration = self.ui.spin_steps.value(), self.ui.spin_duration.value()

        if is_pro and not com_port: return self.ui.log_output.appendPlainText("❌ ABBRUCH: COM-Port fehlt!")
        if is_home and not ref_ip: return self.ui.log_output.appendPlainText("❌ ABBRUCH: Tasmota-Referenz IP fehlt!")
        if not dut_ip: return self.ui.log_output.appendPlainText("❌ ABBRUCH: Ziel-Dose IP fehlt!")

        try:
            self.cm.config['REFERENCE_PRO']['com_port'] = com_port
            self.cm.config['REFERENCE_HOME']['ip_address'] = ref_ip
            self.cm.config['TARGET']['ip_address'] = dut_ip
            self.cm.config['TARGET']['measurement_steps'] = str(steps)
            self.cm.config['TARGET']['duration_per_step'] = str(duration)
            with open('config.ini', 'w') as configfile: self.cm.config.write(configfile)
        except: return

        mac = self.cm.get_target_mac()
        device_path = os.path.join(self.cm.root_dir, mac)
        os.makedirs(device_path, exist_ok=True)

        params = {
            'mode': "PRO" if is_pro else "HOME", 'steps': steps, 'duration': duration,
            'ref_ip': ref_ip, 'com_port': com_port, 'dut_ip': dut_ip,
            'device_path': device_path, 'session_ts': datetime.now().strftime("%Y%m%d_%H%M%S")
        }

        for key in self.graph_data: self.graph_data[key] = []
            
        self.worker = MeasurementWorker(self.cm.config, params)
        self.worker.log_signal.connect(self.ui.log_output.appendPlainText)
        self.worker.data_signal.connect(self.update_plots)
        self.worker.finished_signal.connect(self.measurement_finished)
        
        # NEU: Der Worker übergibt nun auch Pfad und Zeit für das Finden der CSVs
        self.worker.apply_request_signal.connect(self.prompt_apply_calibration)
        
        self.worker.show_popup_signal.connect(self.show_power_popup)
        self.worker.hide_popup_signal.connect(self.hide_power_popup)
        
        self.ui.btn_start.setText("⛔ Messung abbrechen")
        self.ui.btn_start.setStyleSheet("background-color: darkred; color: white; font-weight: bold;")
        self.ui.log_output.appendPlainText("-" * 50)
        self.worker.start()

    def update_plots(self, data):
        for key, value in data.items():
            self.graph_data[key].append(value)
            self.curves[key].setData(self.graph_data[key][-100:])

    def measurement_finished(self, message):
        self.ui.log_output.appendPlainText(message)
        self.ui.btn_start.setText("Kalibrierung Starten")
        self.ui.btn_start.setStyleSheet("") 
        self.ui.btn_start.setEnabled(True)
        self.hide_power_popup()

    def prompt_apply_calibration(self, report_file, target_ip, all_results, device_path, session_ts):
        # Wir geben die neuen Parameter (Pfad & Zeit) an den Dialog weiter
        dialog = CalibrationReportDialog(self, report_file, target_ip, all_results, 
                                         self.ui.log_output.appendPlainText, device_path, session_ts)
        result = dialog.exec()
        
        if result == QDialog.Rejected:
            self.ui.log_output.appendPlainText("⚠️ Übertragung abgebrochen. Werte nur im Protokoll gespeichert.")
        
        self.measurement_finished("🏁 Der gesamte Kalibrierprozess ist beendet.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())