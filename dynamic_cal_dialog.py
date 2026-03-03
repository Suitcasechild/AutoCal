import os
import re
import httpx
import glob
from datetime import datetime
from PySide6 import QtWidgets, QtCore, QtUiTools
from i18n_manager import setup_translation

_ = setup_translation()

class RuleWarningDialog(QtWidgets.QDialog):
    def __init__(self, current_rule, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Bestehende Rule erkannt"))
        self.setMinimumWidth(450)
        layout = QtWidgets.QVBoxLayout(self)
        
        msg = _("<b>Achtung:</b> Auf dem Gerät wurde bereits eine Rule1 gefunden.<br>"
                "Diese wird bei Durchführung der Operation überschrieben.<br><br>"
                "Aktuelle Rule (hier kopieren und sichern):")
        
        label = QtWidgets.QLabel(msg)
        label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(label)
        
        self.text_edit = QtWidgets.QPlainTextEdit(self)
        self.text_edit.setPlainText(current_rule)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        self.ok_button = QtWidgets.QPushButton(_("Verstanden & Bestätigen"), self)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

class CredentialDialog(QtWidgets.QDialog):
    def __init__(self, device_name, attempt=1, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Zugangsdaten für {device_name}").format(device_name=device_name))
        self.setModal(True)
        layout = QtWidgets.QVBoxLayout(self)
        self.info_label = QtWidgets.QLabel(_("Zugangsdaten für '{device_name}' erforderlich (Versuch {attempt}/3).").format(device_name=device_name, attempt=attempt))
        layout.addWidget(self.info_label)
        layout.addWidget(QtWidgets.QLabel(_("Benutzername:")))
        self.user_input = QtWidgets.QLineEdit(self)
        self.user_input.setText("admin")
        layout.addWidget(self.user_input)
        layout.addWidget(QtWidgets.QLabel(_("Passwort:")))
        self.pass_input = QtWidgets.QLineEdit(self)
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass_input.setFocus()
        layout.addWidget(self.pass_input)
        disclaimer = QtWidgets.QLabel(_("<i>Die Zugangsdaten werden für die Dauer dieser Programmsitzung sicher im Arbeitsspeicher gehalten.</i>"))
        disclaimer.setWordWrap(True)
        layout.addWidget(disclaimer)
        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton(_("OK"), self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QtWidgets.QPushButton(_("Abbrechen"), self)
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

    def get_credentials(self):
        return self.user_input.text().strip(), self.pass_input.text()

class DynamicCalDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, config_manager=None, credentials_manager=None):
        super().__init__(parent)
        self.cm = config_manager
        self.cred_m = credentials_manager
        self.original_savedata = None
        self.device_mac = None
        self.latest_report_path = None
        self.steps_data = [] 
        self.final_rule = ""
        self.rule_sent_successfully = False 
        
        loader = QtUiTools.QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), 'dynamic_cal.ui')
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)
        self.setLayout(main_layout)
        
        self.ui.btn_search_report.clicked.connect(self.on_search_report)
        self.ui.btn_send_rule.clicked.connect(self.on_send_rule)
        self.ui.btn_close.clicked.connect(self.close)
        
        if hasattr(self.ui, 'spin_hysteresis'):
            self.ui.spin_hysteresis.valueChanged.connect(self.generate_rule)
        
        self.setWindowTitle(_("Dynamische Power-Kalibrierung (Tasmota Rules)"))
        self.resize(self.ui.size())
        
        if hasattr(self.ui, 'lbl_warning'):
            self.ui.lbl_warning.setStyleSheet("color: red;")
            self.ui.lbl_warning.setText("")
            
        self.log_message(_("Dialog initialisiert."))

    def log_message(self, message):
        if hasattr(self.ui, 'txt_log'):
            self.ui.txt_log.appendPlainText(message)

    def _handle_auth_error(self, ip, attempt):
        dialog = CredentialDialog(f"IP {ip}", attempt, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            user, password = dialog.get_credentials()
            if user:
                self.cred_m.set_credentials(ip, user, password)
                return True
        return False

    def fetch_tasmota_data(self, ip, command):
        auth = None
        for attempt in range(1, 4):
            try:
                creds = self.cred_m.get_credentials(ip)
                if creds: auth = (creds['user'], creds['password'])
                url = f"http://{ip}/cm?cmnd={command}"
                r = httpx.get(url, timeout=5.0, auth=auth)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    if not self._handle_auth_error(ip, attempt): break
                else: raise e
            except Exception as e: raise e
        return None

    def on_search_report(self):
        ip = self.ui.edit_ip.text().strip()
        if not ip:
            QtWidgets.QMessageBox.warning(self, _("Fehler"), _("Bitte eine IP-Adresse eingeben."))
            return

        self.log_message("-" * 30)
        self.log_message(_("Starte Online-Check für IP: ") + ip)
        try:
            res = self.fetch_tasmota_data(ip, "Status")
            if not res: return
            name = res.get("Status", {}).get("DeviceName", "Unknown")
            self.ui.lbl_info_name.setText(f"Name: {name}")
            
            res = self.fetch_tasmota_data(ip, "Status 5")
            if res:
                self.device_mac = res.get("StatusNET", {}).get("Mac", "").replace(":", "-").upper()
                host = res.get("StatusNET", {}).get("Hostname", "-")
                self.ui.lbl_info_mac.setText(f"MAC: {self.device_mac}")
                if hasattr(self.ui, 'lbl_info_host'): self.ui.lbl_info_host.setText(f"Hostname: {host}")

            res = self.fetch_tasmota_data(ip, "Status 2")
            if res:
                version = res.get("StatusFWR", {}).get("Version", "-")
                self.ui.lbl_info_version.setText(f"Version: {version}")

            res = self.fetch_tasmota_data(ip, "SaveData")
            if res:
                self.original_savedata = res.get("SaveData")
                self.ui.lbl_info_savedata.setText(f"SaveData: {self.original_savedata}")

            # Very Robust Rule1 Check / Extrem robuster Rule1 Check
            res = self.fetch_tasmota_data(ip, "Rule1")
            self.log_message(_("Prüfe Rule1 Status..."))
            
            rule_text = ""
            rule_active = "OFF"
            
            if res and "Rule1" in res:
                rule_data = res["Rule1"]
                if isinstance(rule_data, dict):
                    # Tasmota uses 'Rules' or 'Text' depending on version
                    rule_text = rule_data.get("Rules") or rule_data.get("Text") or ""
                    rule_active = rule_data.get("State", "OFF")
                else:
                    # Fallback for simple string responses
                    rule_active = str(rule_data)
                    # If it's more than a simple state, it's likely the text
                    if rule_active.upper() not in ["ON", "OFF", "0", "1"]:
                        rule_text = rule_active
            
            self.ui.lbl_info_rule1.setText(f"Rule1: {rule_active}")
            
            # Popup logic: Show if ANY text is found / Zeigen sobald IRGENDEIN Text da ist
            if rule_text and rule_text.strip():
                self.ui.lbl_warning.setText(_("WARNUNG: Rule1 ist belegt!"))
                self.log_message(_("Bestehende Rule1 gefunden. Öffne Warn-Dialog..."))
                warning_dlg = RuleWarningDialog(rule_text, self)
                warning_dlg.exec()
            else:
                self.log_message(_("Rule1 ist leer oder nicht vorhanden."))
                self.ui.lbl_warning.setText("")
            
            self.log_message(_("Online-Check erfolgreich abgeschlossen."))
            self.find_and_parse_report()
        except Exception as e:
            self.log_message(_("Fehler beim Online-Check: ") + str(e))
            QtWidgets.QMessageBox.critical(self, _("Verbindungsfehler"), str(e))

    def find_and_parse_report(self):
        if not self.device_mac: return
        report_dir = os.path.join(self.cm.root_dir, self.device_mac)
        if not os.path.exists(report_dir):
            self.log_message(_("Kein Report-Verzeichnis für MAC {mac} gefunden.").format(mac=self.device_mac))
            return
        reports = glob.glob(os.path.join(report_dir, "*_Protokoll.txt"))
        if not reports: return
        self.latest_report_path = max(reports, key=os.path.getctime)
        self.log_message(_("Lese neuesten Report: ") + os.path.basename(self.latest_report_path))
        try:
            with open(self.latest_report_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            steps = []
            step_blocks = re.split(r'STUFE \d+:', content)[1:]
            for block in step_blocks:
                amp_match = re.search(r'Strom:\s+Ref\s+([\d.]+)\s*A', block)
                pcal_match = re.search(r'Leistung:.*?Cal-Vorschlag:\s*(\d+)', block)
                if amp_match and pcal_match:
                    steps.append({'amp': float(amp_match.group(1)), 'pcal': int(pcal_match.group(1))})
            if not steps: return
            self.steps_data = sorted(steps, key=lambda x: x['amp'])
            self.validate_steps()
            self.generate_rule() 
        except Exception as e:
            self.log_message(_("Fehler beim Parsen des Reports: ") + str(e))

    def validate_steps(self):
        if len(self.steps_data) < 3: self.log_message(_("Hinweis: Weniger als 3 Stufen gefunden."))
        min_diff = 0.2
        warnings = []
        for i in range(len(self.steps_data) - 1):
            diff = self.steps_data[i+1]['amp'] - self.steps_data[i]['amp']
            if diff < min_diff:
                warnings.append(_("Stufe {i} und {j} liegen nah beieinander ({diff:.3f}A).").format(i=i+1, j=i+2, diff=diff))
        if warnings: self.ui.lbl_warning.setText(_("Abstände der Stromstufen sehr gering!"))

    def generate_rule(self):
        if len(self.steps_data) < 2:
            self.ui.txt_rule_preview.setPlainText(_("Zu wenige Daten für eine Rule (mind. 2 Stufen nötig)."))
            self.ui.btn_send_rule.setEnabled(False)
            return
        hysteresis = self.ui.spin_hysteresis.value()
        rule_parts = []
        thresholds = [] 
        rule_parts.append(f"ON Energy#Current>0 DO PowerCal {self.steps_data[0]['pcal']} ENDON")
        upshift_triggers = []
        downshift_triggers = []
        for i in range(len(self.steps_data) - 1):
            a_curr = self.steps_data[i]['amp']
            a_next = self.steps_data[i+1]['amp']
            p_curr = self.steps_data[i]['pcal']
            p_next = self.steps_data[i+1]['pcal']
            switch_point = (a_curr + a_next) / 2
            thresholds.append(switch_point)
            upshift_triggers.append(f"ON Energy#Current>{switch_point:.3f} DO PowerCal {p_next} ENDON")
            down_point = switch_point - hysteresis
            if down_point < 0.05: down_point = 0.05
            downshift_triggers.append(f"ON Energy#Current<{down_point:.3f} DO PowerCal {p_curr} ENDON")
        self.final_rule = "Rule1 " + " ".join(rule_parts + upshift_triggers + sorted(downshift_triggers, reverse=True))
        self.ui.txt_rule_preview.setPlainText(self.final_rule)
        self.update_steps_table(thresholds, hysteresis)
        length = len(self.final_rule)
        if length > 511:
            self.log_message(_("WARNUNG: Rule ist zu lang ({len}/511 Zeichen).").format(len=length))
            self.ui.btn_send_rule.setEnabled(False)
        else:
            self.ui.btn_send_rule.setEnabled(True)

    def update_steps_table(self, thresholds, hysteresis):
        if not hasattr(self.ui, 'table_steps'): return
        self.ui.table_steps.setRowCount(0)
        max_amp = 10.0
        for i, step in enumerate(self.steps_data):
            self.ui.table_steps.insertRow(i)
            self.ui.table_steps.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{step['amp']:.3f}"))
            self.ui.table_steps.setItem(i, 1, QtWidgets.QTableWidgetItem(str(step['pcal'])))
            if i == 0: range_text = f"0.000 - {thresholds[0]:.3f} A"
            elif i < len(thresholds):
                start = thresholds[i-1] - hysteresis
                if start < 0: start = 0.0
                range_text = f"{start:.3f} - {thresholds[i]:.3f} A"
            else:
                start = thresholds[i-1] - hysteresis
                range_text = f"{start:.3f} - {max_amp:.3f} A"
            self.ui.table_steps.setItem(i, 2, QtWidgets.QTableWidgetItem(range_text))

    def on_send_rule(self):
        ip = self.ui.edit_ip.text().strip()
        if not self.final_rule: return
        reply = QtWidgets.QMessageBox.question(self, _("Senden bestätigen"), 
            _("Die dynamische Rule wird nun an das Gerät gesendet und aktiviert.\n\nHinweis: SaveData wird zum Schutz auf 0 gesetzt.\n\nFortfahren?"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.No: return
        self.log_message("-" * 30)
        self.log_message(_("Starte Übertragung an IP: ") + ip)
        try:
            self.log_message(_("Setze SaveData 1 (Vorbereitung)..."))
            self.fetch_tasmota_data(ip, "SaveData 1")
            self.log_message(_("Sende Rule1 an Gerät..."))
            url = f"http://{ip}/cm"
            creds = self.cred_m.get_credentials(ip)
            auth = (creds['user'], creds['password']) if creds else None
            r = httpx.get(url, params={"cmnd": self.final_rule}, timeout=10.0, auth=auth)
            r.raise_for_status()
            self.log_message(_("Aktiviere Rule1 (Modus 5 - Once Mode)..."))
            self.fetch_tasmota_data(ip, "Rule1 5")
            check = self.fetch_tasmota_data(ip, "Rule1")
            if check and check.get("Rule1", {}).get("State") == "ON":
                self.log_message(_("✅ Rule1 erfolgreich aktiviert."))
            else:
                self.log_message(_("⚠️ Warnung: Rule1 Status konnte nicht verifiziert werden."))
            self.log_message(_("Setze SaveData 0 (Flash-Schutz)..."))
            self.fetch_tasmota_data(ip, "SaveData 0")
            self.rule_sent_successfully = True
            self.document_in_report()
            QtWidgets.QMessageBox.information(self, _("Erfolg"), 
                _("Dynamische Kalibrierung erfolgreich abgeschlossen.\n\nDie Rule ist aktiv und SaveData wurde auf 0 gesetzt.\nDetails wurden im Protokoll hinterlegt."))
            self.ui.btn_send_rule.setEnabled(False)
        except Exception as e:
            self.log_message(_("❌ Fehler beim Senden: ") + str(e))
            QtWidgets.QMessageBox.critical(self, _("Fehler"), str(e))

    def document_in_report(self):
        if not self.latest_report_path or not os.path.exists(self.latest_report_path): return
        try:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hyst = self.ui.spin_hysteresis.value()
            doc_text = f"\n\n" + "="*85 + "\n"
            doc_text += f"[DYNAMISCHE KALIBRIERUNG (RULES)] - {ts}\n"
            doc_text += f"Hysterese: {hyst:.3f} A\n"
            doc_text += f"Gesendete Rule:\n{self.final_rule}\n"
            doc_text += "="*85 + "\n"
            with open(self.latest_report_path, "a", encoding="utf-8") as f:
                f.write(doc_text)
            self.log_message(_("Dokumentation im Report hinterlegt."))
        except Exception as e:
            self.log_message(_("Fehler bei Dokumentation: ") + str(e))

    def closeEvent(self, event):
        ip = self.ui.edit_ip.text().strip()
        if not self.rule_sent_successfully and ip and self.original_savedata is not None:
            try:
                self.fetch_tasmota_data(ip, f"SaveData {self.original_savedata}")
            except: pass
        super().closeEvent(event)
