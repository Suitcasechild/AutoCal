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
                               QDialog, QTextEdit, QHBoxLayout, QPushButton, QFileDialog)
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
            from calibration_engine import CalibrationEngine

            dut_ip = self.params['dut_ip']
            ref_ip = self.params['ref_ip']
            mode = self.params['mode']
            data_ts = self.params['session_ts']
            use_existing = self.params.get('use_existing', False)
            
            self.log_signal.emit("🔄 Prüfe Erreichbarkeit der Ziel-Dose...")
            if not check_device_availability(dut_ip, "Ziel-Dose"):
                self.finished_signal.emit("❌ ABBRUCH: Ziel-Dose nicht erreichbar!")
                return
            
            ref_manager = ReferenceManager(self.config)
            old_cal = ref_manager.get_current_cal_factors(dut_ip)
            engine = CalibrationEngine(self.params['device_path'])
            all_results = []

            # =========================================================
            # NEU: ABLAUF WENN "VORHANDENE DATEN NUTZEN" GEWÄHLT WURDE
            # =========================================================
            if use_existing:
                self.log_signal.emit(f"🔄 Berechne Kalibrierung aus vorhandenen Daten ({data_ts})...")
                steps_files = sorted(glob.glob(os.path.join(self.params['device_path'], f"{data_ts}_Stufe_*.csv")))
                
                # Methode auslesen, falls altes Protokoll existiert
                cal_method_text = "Professionell (Fluke 45)" if mode == "PRO" else "Heimanwender (HTTP)"
                old_report_path = os.path.join(self.params['device_path'], f"{data_ts}_Protokoll.txt")
                if os.path.exists(old_report_path):
                    try:
                        with open(old_report_path, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.startswith("Methode:"):
                                    cal_method_text = line.split(":", 1)[1].strip()
                                    break
                    except: pass

                # CSVs sofort ohne Hardware-Schleife verarbeiten
                for i, csv_file in enumerate(steps_files, 1):
                    if not self.is_running: return
                    res = engine.calculate_new_calibration(csv_file, old_cal)
                    res['Stufe'] = i
                    all_results.append(res)
                    
                if all_results and self.is_running:
                    report_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    report_file = engine.write_summary(all_results, data_ts, report_ts=report_ts, cal_mode=cal_method_text, old_cal=old_cal)
                    self.log_signal.emit("\n" + "="*40)
                    self.log_signal.emit("BERECHNUNG AUS ALTEN DATEN ABGESCHLOSSEN")
                    self.log_signal.emit("="*40)
                    self.apply_request_signal.emit(report_file, dut_ip, all_results, self.params['device_path'], data_ts)
                
                if not self.is_running:
                    self.finished_signal.emit("⚠️ Vorgang durch Benutzer abgebrochen.")
                else:
                    self.finished_signal.emit("") # Beendet sauber den Worker
                return

            # =========================================================
            # NORMALER ABLAUF (Neue Messung mit Hardware)
            # =========================================================
            if mode == "HOME" and not check_device_availability(ref_ip, "Tasmota-Referenz"):
                self.finished_signal.emit("❌ ABBRUCH: Referenz-Dose nicht erreichbar!")
                return

            self.log_signal.emit("🔄 Initialisiere Referenz-Hardware...")
            if mode == "PRO":
                if not ref_manager.set_mode('PRO'):
                    self.finished_signal.emit("❌ ABBRUCH: COM-Port Fehler! Fluke antwortet nicht oder Kabel fehlt.")
                    return
            else:
                ref_manager.set_mode('HOME')

            from main import prepare_dut
            prepare_dut(dut_ip)

            if mode == "HOME":
                self.log_signal.emit("🔌 Schalte Ziel-Dose für Offset-Messung AUS...")
                try:
                    httpx.get(f"http://{dut_ip}/cm?cmnd=Power%20OFF", timeout=2)
                    time.sleep(2) 
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Warnung: Automatisches Ausschalten fehlgeschlagen: {e}")

                if not self.is_running: return
                from refhome_offset import ermittle_offset
                offset_a, offset_w = ermittle_offset(ref_ip)
                ref_manager.set_home_offset(offset_a, offset_w)

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
                        # LOGIK: Wenn Dose aus (Watt <= 0), dann LCDs auf Striche (None)
                        if dut_w <= 0:
                            v_send, a_send, w_send = None, None, None
                        else:
                            v_send, a_send, w_send = ref_v, ref_a, ref_w              
                    except: 
                        dut_v, dut_a, dut_w = 0.0, 0.0, 0.0
                        v_send, a_send, w_send = None, None, None

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
                        # ZWINGEND: Sofort Striche an die GUI senden
                        self.data_signal.emit({
                        'volt_ref': None, 'volt_dut': 0.0,
                        'amp_ref': None,  'amp_dut': 0.0,
                        'watt_ref': None, 'watt_dut': 0.0
                        })
                        time.sleep(3.0)
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ Warnung: Konnte Ziel-Dose nicht ausschalten: {e}")

            if all_results and self.is_running:
                report_file = engine.write_summary(all_results, data_ts, report_ts=data_ts, cal_mode=mode, old_cal=old_cal)
                self.log_signal.emit("\n" + "="*40)
                self.log_signal.emit("ERMITTLUNG DER KALIBRIERWERTE ABGESCHLOSSEN")
                self.log_signal.emit("="*40)
                self.apply_request_signal.emit(report_file, dut_ip, all_results, self.params['device_path'], data_ts)
            
            if not self.is_running:
                self.finished_signal.emit("⚠️ Messung wurde vom Benutzer abgebrochen.")

        except Exception as e:
            self.finished_signal.emit(f"❌ Schwerer Fehler: {str(e)}")

    def stop(self):
        self.is_running = False

# ---------------------------------------------------------
# 3. DAS PROTOKOLL-POPUP (Custom Dialog)
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
        self.text_edit.setStyleSheet("font-family: Consolas, 'Courier New', monospace; font-size: 12px; background-color: #1e1e1e; color: #d4d4d4;")
        self.layout.addWidget(self.text_edit)

        self.load_report_text()

        self.btn_layout = QHBoxLayout()

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

        self.btn_layout.addWidget(self.btn_graph)
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
        search_path = os.path.join(self.device_path, f"{self.session_ts}_Stufe_*.csv")
        files = glob.glob(search_path)
        
        if not files:
            QMessageBox.warning(self, "Keine Daten", "Es konnten keine CSV-Dateien für den Graphen gefunden werden.")
            return

        df_list = [pd.read_csv(f) for f in files]
        full_df = pd.concat(df_list, ignore_index=True)

        x = full_df['Target_Watt'].values 
        y = full_df['Ref_Watt'].values    

        if len(x) == 0:
            return

        m, _, _, _ = np.linalg.lstsq(x[:, np.newaxis], y, rcond=None)
        slope = float(m[0])

        graph_dialog = QDialog(self)
        graph_dialog.setWindowTitle(f"Regressions-Analyse (Leistung) | Steigung m = {slope:.5f}")
        graph_dialog.resize(800, 600)
        
        layout = QVBoxLayout(graph_dialog)
        
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('#1e1e1e')
        plot_widget.setLabel('left', 'Referenz Leistung (Soll)', units='W')
        plot_widget.setLabel('bottom', 'Dose Leistung (Ist)', units='W')
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_widget.addLegend(offset=(30, 30))
        layout.addWidget(plot_widget)

        plot_widget.plot(x, y, pen=None, symbol='o', symbolSize=7, 
                         symbolBrush=(255, 255, 255, 150), name="Messpunkte (Vorher)")

        max_val = max(max(x), max(y)) * 1.05
        x_line = np.array([0, max_val])
        plot_widget.plot(x_line, x_line, pen=pg.mkPen('y', width=2, style=Qt.DashLine), 
                         name="Idealzustand (1:1)")

        y_reg = x_line * slope
        plot_widget.plot(x_line, y_reg, pen=pg.mkPen('g', width=3), 
                         name=f"Ausgleichsgerade (m={slope:.5f})")

        info_label = QTextEdit()
        info_label.setReadOnly(True)
        info_label.setMaximumHeight(80)
        info_label.setStyleSheet("background-color: #2b2b2b; color: #a9b7c6; font-size: 13px; border: none;")
        info_label.setPlainText("Erklärung:\nDie gelbe Linie ist der Idealzustand. Die weißen Punkte sind die echten Messwerte der Dose.\n"
                                "Die grüne Linie ist die Regression (Berechnung des Programms). Der Faktor, um den die grüne von der gelben Linie abweicht, ist die Korrektur!")
        layout.addWidget(info_label)

        graph_dialog.exec()

    def apply_calibration_action(self):
        self.btn_calibrate.hide()
        self.btn_cancel.hide()
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
        self.reset_lcd_displays() 

        if hasattr(self.ui, 'split_info'):
            self.ui.split_info.setVisible(False)
        
        # Den "Online Check" Button verknüpfen
        if hasattr(self.ui, 'btn_onlinechk'):
            self.ui.btn_onlinechk.clicked.connect(self.on_online_check_clicked)
        # Styling für 7-Segment Look
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

    
    def update_live_data(self, data):
        """Aktualisiert LCDs (mit Strichen) und Graphen (mit Zahlen)."""
        
        # 1. LCD-LOGIK (Hier ist None für die Striche gewollt)
        v_ref = data.get('volt_ref')
        a_ref = data.get('amp_ref')
        w_ref = data.get('watt_ref')

        if v_ref is None:
            # Falls Dose AUS -> LCDs zeigen Striche
            if hasattr(self.ui, 'lcd_volt'): self.ui.lcd_volt.display("---")
            if hasattr(self.ui, 'lcd_amp'):  self.ui.lcd_amp.display("---")
            if hasattr(self.ui, 'lcd_watt'): self.ui.lcd_watt.display("---")
        else:
            # Falls Dose AN -> LCDs zeigen Zahlen
            if hasattr(self.ui, 'lcd_volt'): self.ui.lcd_volt.display(f"{v_ref:.2f}")
            if hasattr(self.ui, 'lcd_amp'):  self.ui.lcd_amp.display(f"{a_ref:.3f}")
            if hasattr(self.ui, 'lcd_watt'): self.ui.lcd_watt.display(f"{w_ref:.2f}")

        # 2. GRAPH-LOGIK (Hier korrigieren wir das 'None' Problem!)
        # Wir loopen durch alle Schlüssel und stellen sicher, dass nur Zahlen in die Listen kommen
        for key in ['volt_ref', 'volt_dut', 'amp_ref', 'amp_dut', 'watt_ref', 'watt_dut']:
            raw_val = data.get(key)
            
            # WICHTIG: Wenn der Wert None ist (für LCD-Striche), machen wir 0.0 für den Graphen daraus
            val = float(raw_val) if raw_val is not None else 0.0
            
            # Nur hinzufügen, wenn die Liste existiert
            if key in self.graph_data:
                self.graph_data[key].append(val)

        # 3. DAS ZEICHNEN (Der Teil, der vorher gecrasht ist)
        # Wir mappen die graph_data Keys auf die Bezeichnungen deiner curves
        mapping = {
            'volt_ref': 'volt_ref', 'volt_dut': 'volt_dut',
            'amp_ref': 'amp_ref',   'amp_dut': 'amp_dut',
            'watt_ref': 'watt_ref', 'watt_dut': 'watt_dut'
        }

        for data_key, curve_key in mapping.items():
            if curve_key in self.curves:
                # Hole die letzten 100 sauberen Zahlenwerte
                plot_data = self.graph_data[data_key][-100:]
                #setData() bekommt jetzt garantiert nur Zahlen (0.0 statt None)
                self.curves[curve_key].setData(plot_data)


    def setup_ui_logic(self):
        self.ui.btn_start.clicked.connect(self.toggle_measurement)
        self.ui.check_ref_pro.toggled.connect(lambda c: self.ui.check_ref_home.setChecked(False) if c else None)
        self.ui.check_ref_home.toggled.connect(lambda c: self.ui.check_ref_pro.setChecked(False) if c else None)

        # --- Setup-Menü Verknüpfungen ---
        if hasattr(self.ui, 'action_setup_general'):
            self.ui.action_setup_general.triggered.connect(self.open_setup_general)
        if hasattr(self.ui, 'action_setup_fluke'):
            self.ui.action_setup_fluke.triggered.connect(self.open_setup_fluke)
        if hasattr(self.ui, 'action_setup_tasmota'):
            self.ui.action_setup_tasmota.triggered.connect(self.open_setup_tasmota)

        # ---  Datei-Menü Verknüpfungen ---
        if hasattr(self.ui, 'action_save_log'):
            self.ui.action_save_log.triggered.connect(self.save_log_to_file)
        if hasattr(self.ui, 'action_open_report_dir'):
            self.ui.action_open_report_dir.triggered.connect(self.open_report_folder)
        if hasattr(self.ui, 'action_exit_program'):
            self.ui.action_exit_program.triggered.connect(self.close)

        # ---  Hilfe-Menü Verknüpfung ---
        if hasattr(self.ui, 'action_show_license'):
            self.ui.action_show_license.triggered.connect(self.show_license_info)

    def load_values_from_config(self):
        try:
            if hasattr(self.ui, 'edit_dut_ip'): self.ui.edit_dut_ip.setText(self.cm.config.get('TARGET', 'ip_address', fallback='0.0.0.0'))
            if hasattr(self.ui, 'spin_steps'): self.ui.spin_steps.setValue(self.cm.config.getint('TARGET', 'measurement_steps', fallback=3))
            if hasattr(self.ui, 'spin_duration'): self.ui.spin_duration.setValue(self.cm.config.getint('TARGET', 'duration_per_step', fallback=15))
        except Exception as e:
            self.ui.log_output.appendPlainText(f"❌ Fehler beim Laden der INI: {e}")

    def open_setup_general(self):
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
            
            with open('config.ini', 'w') as f: self.cm.config.write(f)
            self.ui.log_output.appendPlainText("✅ Allgemeines Setup in config.ini gespeichert.")
            dialog.accept()
            
        dialog.btn_save.clicked.connect(save_and_close)
        dialog.btn_close.clicked.connect(dialog.reject)
        dialog.exec()

    def open_setup_fluke(self):
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
        
        def save_and_close():
            if hasattr(dialog, 'edit_com_port'):
                self.cm.config['REFERENCE_PRO']['com_port'] = dialog.edit_com_port.text().strip()
            if hasattr(dialog, 'edit_baudrate'):
                self.cm.config['REFERENCE_PRO']['baudrate'] = dialog.edit_baudrate.text().strip()
                
            with open('config.ini', 'w') as f: self.cm.config.write(f)
            self.ui.log_output.appendPlainText("✅ Fluke Setup in config.ini gespeichert.")
            dialog.accept()
            
        dialog.btn_save.clicked.connect(save_and_close)
        dialog.btn_close.clicked.connect(dialog.reject)
        dialog.exec()

    def open_setup_tasmota(self):
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
                
            with open('config.ini', 'w') as f: self.cm.config.write(f)
            self.ui.log_output.appendPlainText("✅ Tasmota Setup in config.ini gespeichert.")
            dialog.accept()
            
        dialog.btn_save.clicked.connect(save_and_close)
        dialog.btn_close.clicked.connect(dialog.reject)
        dialog.exec()

    # --- NEU: FUNKTIONEN FÜR DAS DATEI-MENÜ ---

    def open_report_folder(self):
        """Öffnet das im Setup definierte Reportverzeichnis im Windows Explorer."""
        # Hol den absoluten Pfad aus der Config
        report_path = os.path.abspath(self.cm.root_dir)
        if os.path.exists(report_path):
            os.startfile(report_path) # Öffnet den Windows Explorer
        else:
            QMessageBox.warning(self, "Ordner nicht gefunden", 
                                f"Der Pfad existiert noch nicht oder wurde noch nicht erstellt:\n{report_path}")

    def save_log_to_file(self):
        """Speichert den aktuellen Inhalt des Log-Fensters in eine .txt Datei."""
        log_content = self.ui.log_output.toPlainText()
        if not log_content.strip():
            return QMessageBox.information(self, "Log leer", "Es gibt noch keine Einträge zum Speichern.")

        # Vorschlag für Dateiname mit aktuellem Zeitstempel
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

        dut_ip = self.ui.edit_dut_ip.text().strip()
        steps = self.ui.spin_steps.value()
        duration = self.ui.spin_duration.value()

        com_port = self.cm.config.get('REFERENCE_PRO', 'com_port', fallback='')
        ref_ip = self.cm.config.get('REFERENCE_HOME', 'ip_address', fallback='')

        if is_pro and not com_port: return self.ui.log_output.appendPlainText("❌ ABBRUCH: COM-Port in Setup->Fluke fehlt!")
        if is_home and not ref_ip: return self.ui.log_output.appendPlainText("❌ ABBRUCH: Tasmota-Referenz IP in Setup->Tasmota fehlt!")
        # --- Hinweis-Popup für Tasmota-Referenz-Aufbau ---
        if is_home:
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
            msg_box.setDefaultButton(QMessageBox.Ok)
            
            if msg_box.exec() == QMessageBox.Cancel:
                self.ui.log_output.appendPlainText("⚠️ Abbruch: Messaufbau wird korrigiert.")
                return
        
        if not dut_ip: return self.ui.log_output.appendPlainText("❌ ABBRUCH: Ziel-Dose IP fehlt!")

        try:
            #self.cm.config['TARGET']['ip_address'] = dut_ip
            self.cm.config['TARGET']['measurement_steps'] = str(steps)
            self.cm.config['TARGET']['duration_per_step'] = str(duration)
            # Die IP-Adresse setzen wir in der INI auf leer oder 0.0.0.0, 
            # damit sie beim nächsten Start nicht mehr geladen wird.
           # self.cm.config['TARGET']['ip_address'] = "0.0.0.0"
            with open('config.ini', 'w') as configfile: self.cm.config.write(configfile)
        except: return

        mac = self.cm.get_target_mac()
        device_path = os.path.join(self.cm.root_dir, mac)
        os.makedirs(device_path, exist_ok=True)

        # =========================================================
        # NEU: PRÜFUNG AUF ALTE MESSDATEN (CSVs) IM ORDNER
        # =========================================================
        existing_csvs = glob.glob(os.path.join(device_path, "*_Stufe_*.csv"))
        use_existing = False
        session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if existing_csvs:
            latest_csv = max(existing_csvs, key=os.path.getctime)
            last_session_ts = os.path.basename(latest_csv).split('_Stufe_')[0]
            
            # Formatiere den Zeitstempel für eine schönere Anzeige (aus YYYYMMDD_HHMMSS)
            try:
                dt_obj = datetime.strptime(last_session_ts, "%Y%m%d_%H%M%S")
                display_time = dt_obj.strftime("%d.%m.%Y um %H:%M:%S Uhr")
            except:
                display_time = last_session_ts

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("Alte Messdaten gefunden")
            msg_box.setText(f"Für diese Tasmota-Dose ({mac}) existieren bereits Messdaten vom:\n\n{display_time}\n\nMöchtest du komplett neue Daten aufzeichnen oder das letzte Protokoll neu generieren?")
            
            btn_new = msg_box.addButton("Neue Messung", QMessageBox.AcceptRole)
            btn_old = msg_box.addButton("Alte Daten nutzen", QMessageBox.AcceptRole)
            btn_cancel = msg_box.addButton("Abbrechen", QMessageBox.RejectRole)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == btn_cancel:
                self.ui.log_output.appendPlainText("⚠️ Messungs-Start durch Benutzer abgebrochen.")
                return
            elif msg_box.clickedButton() == btn_old:
                use_existing = True
                session_ts = last_session_ts
                self.ui.log_output.appendPlainText(f"ℹ️ Überspringe Testlauf. Nutze vorhandene Daten von: {display_time}")
            else:
                self.ui.log_output.appendPlainText("ℹ️ Alte Daten werden ignoriert. Starte neuen Testlauf.")
        # =========================================================

        params = {
            'mode': "PRO" if is_pro else "HOME", 'steps': steps, 'duration': duration,
            'ref_ip': ref_ip, 'com_port': com_port, 'dut_ip': dut_ip,
            'device_path': device_path, 'session_ts': session_ts,
            'use_existing': use_existing # Übergibt die Nutzer-Entscheidung an den Worker
        }

        # Graphen leeren
        for key in self.graph_data: self.graph_data[key] = []
        
        self.worker = MeasurementWorker(self.cm.config, params)
        
        self.worker.data_signal.connect(self.update_live_data)  
        self.worker.log_signal.connect(self.ui.log_output.appendPlainText)
        self.worker.data_signal.connect(self.update_plots)
        self.worker.finished_signal.connect(self.measurement_finished)
        self.worker.apply_request_signal.connect(self.prompt_apply_calibration)
        self.worker.show_popup_signal.connect(self.show_power_popup)
        self.worker.hide_popup_signal.connect(self.hide_power_popup)
        
        self.ui.btn_start.setText("⛔ Messung abbrechen")
        self.ui.btn_start.setStyleSheet("background-color: darkred; color: white; font-weight: bold;")
        self.ui.log_output.appendPlainText("-" * 50)
        self.worker.finished_signal.connect(self.on_measurement_finished)
        self.worker.start()

    def update_plots(self, data):
        for key, value in data.items():
            self.graph_data[key].append(value)
            self.curves[key].setData(self.graph_data[key][-100:])

    def measurement_finished(self, message):
        if message: # Gibt es nur aus, wenn der Worker nicht stumm beendet wurde
            self.ui.log_output.appendPlainText(message)
        self.ui.btn_start.setText("Kalibrierung Starten")
        self.ui.btn_start.setStyleSheet("") 
        self.ui.btn_start.setEnabled(True)
        self.hide_power_popup()

    def prompt_apply_calibration(self, report_file, target_ip, all_results, device_path, session_ts):
        dialog = CalibrationReportDialog(self, report_file, target_ip, all_results, 
                                         self.ui.log_output.appendPlainText, device_path, session_ts)
        result = dialog.exec()
        
        if result == QDialog.Rejected:
            self.ui.log_output.appendPlainText("⚠️ Übertragung abgebrochen. Werte nur im Protokoll gespeichert.")
        
        self.measurement_finished("🏁 Der gesamte Kalibrierprozess ist beendet.")

    def show_license_info(self):
        """Zeigt ein Fenster mit Lizenz-, Haftungs- und KI-Informationen an."""
        license_text = (
            "Tasmota Precision Calibrator v5.0\n"
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
            "Gemini 3 Flash (Google DeepMind) entwickelt und optimiert."
        )
        QMessageBox.about(self, "Lizenz & Info", license_text)

    def on_online_check_clicked(self):
        """Wird aufgerufen, wenn der Button 'Online Check' gedrückt wird."""
        ip = self.ui.edit_dut_ip.text().strip()
        
        # Validierung der IP (mind. x.x.x.x)
        if len(ip) >= 7 and ip.count('.') == 3:
            self.ui.log_output.appendPlainText(f"🌐 Starte Online-Check für {ip}...")
            self.fetch_tasmota_info(ip)
        else:
            self.ui.log_output.appendPlainText("⚠️ Bitte erst eine gültige IP-Adresse eingeben.")
            if hasattr(self.ui, 'split_info'):
                self.ui.split_info.setVisible(False)

    def fetch_tasmota_info(self, ip):
        """Holt Daten und schaltet den Splitter bei Erfolg sichtbar."""
        try:
            # Timeout etwas höher (2s), da der Nutzer aktiv wartet
            r = httpx.get(f"http://{ip}/cm?cmnd=Status%200", timeout=2.0)
            
            if r.status_code == 200:
                data = r.json()
                
                # Daten-Extraktion (wie gehabt)
                device_name = data.get('Status', {}).get('DeviceName', 'Tasmota')
                raw_version = data.get('StatusFWR', {}).get('Version', 'Unbekannt')
                clean_version = raw_version.split('(')[0]
                hostname = data.get('StatusNET', {}).get('Hostname', 'Unbekannt')
                mac_addr = data.get('StatusNET', {}).get('Mac', 'Unbekannt')

                # Labels befüllen
                self.ui.lbl_name.setText(f"{device_name}")
                self.ui.lbl_version.setText(f"{clean_version}")
                self.ui.lbl_host.setText(f"{hostname}")
                self.ui.lbl_mac.setText(f"{mac_addr}")

                # Splitter sichtbar machen
                if hasattr(self.ui, 'split_info'):
                    self.ui.split_info.setVisible(True)
                
                self.ui.log_output.appendPlainText(f"✅ Dose '{device_name}' erfolgreich gefunden.")
            else:
                self.ui.log_output.appendPlainText(f"❌ Fehler: Dose antwortet mit Status {r.status_code}")
                if hasattr(self.ui, 'split_info'): self.ui.split_info.setVisible(False)
                
        except Exception as e:
            self.ui.log_output.appendPlainText(f"❌ Dose nicht erreichbar: {str(e)}")
            if hasattr(self.ui, 'split_info'):
                self.ui.split_info.setVisible(False)

    def reset_lcd_displays(self):
        """Setzt alle LCD-Anzeigen auf das 'Keine Daten' Format."""
        for lcd_name in ['lcd_volt', 'lcd_amp', 'lcd_watt']:
            if hasattr(self.ui, lcd_name):
                lcd = getattr(self.ui, lcd_name)
                # QLCDNumber kann Strings anzeigen, sofern sie in die digitCount passen
                lcd.display("---")

    def on_measurement_finished(self, message):
        """Wird aufgerufen, wenn der Worker fertig ist oder abbricht."""
        if message:
            self.ui.log_output.appendPlainText(message)
        
        # Hier werden die LCDs nach der Messung auf Striche gesetzt
        self.reset_lcd_displays()
        
        # Button wieder freigeben
        self.ui.btn_start.setEnabled(True)
        self.ui.btn_start.setText("Kalibrierung Starten")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())