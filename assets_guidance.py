# -*- coding: utf-8 -*-
"""
# English: Contains the instructional content for the application in HTML format (Dark Mode).
# Deutsch: Enthält den Anleitungstext für die Anwendung im HTML-Format (Dark Mode).
"""

def get_guidance_html(_):
    """
    # English: Returns the translated HTML guidance text.
    # Deutsch: Gibt den übersetzten HTML-Anleitungstext zurück.
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: sans-serif; line-height: 1.6; color: #e0e0e0; padding: 25px; background-color: #1e1e1e; }}
    h1 {{ color: #4a9eff; border-bottom: 2px solid #4a9eff; padding-bottom: 10px; }}
    h2 {{ color: #4a9eff; margin-top: 40px; background-color: #2d2d2d; padding: 8px 15px; border-left: 5px solid #4a9eff; border-radius: 0 4px 4px 0;}}
    h3 {{ color: #ffffff; margin-top: 25px; border-bottom: 1px solid #444; padding-bottom: 5px; }}
    .index {{ background-color: #252525; padding: 20px; border-radius: 8px; border: 1px solid #444; margin-bottom: 30px; }}
    .index ul {{ list-style-type: none; padding-left: 0; }}
    .index ul ul {{ padding-left: 20px; list-style-type: disc; }}
    .index a {{ text-decoration: none; color: #4a9eff; font-weight: bold; }}
    .warning {{ background-color: #3d1a1d; border-left: 5px solid #dc3545; padding: 12px; margin: 15px 0; }}
    .tip {{ background-color: #1b3a22; border-left: 5px solid #28a745; padding: 12px; margin: 15px 0; }}
    .footer {{ margin-top: 60px; text-align: center; color: #777; border-top: 1px solid #444; padding-top: 25px; }}
    code {{ background-color: #333; padding: 2px 5px; border-radius: 3px; font-family: monospace; color: #ffcc00; }}
</style>
</head>
<body>
<a name="top"></a>
<h1>📘 {_("Bedienungsanleitung: Tasmota Precision Calibrator")}</h1>
<p>{_("Willkommen beim Tasmota Precision Calibrator. Dieses Werkzeug wurde entwickelt, um die Kalibrierung von Tasmota-Energiemessgeräten auf ein professionelles Niveau zu heben.")}</p>

<div class="index">
    <h2>📌 {_("Inhaltsverzeichnis")}</h2>
    <ul>
        <li><a href="#ch1">🔬 {_("1. Technischer Hintergrund: Warum 'Cal'-Befehle?")}</a>
            <ul>
                <li><a href="#ch1_1">{_("1.1 Der Vorteil gegenüber Set-Befehlen")}</a></li>
                <li><a href="#ch1_2">{_("1.2 Messunsicherheit und zeitlicher Ablauf")}</a></li>
            </ul>
        </li>
        <li><a href="#ch2">🔌 {_("2. Hardware-Vorbereitung & Messaufbau")}</a>
            <ul>
                <li><a href="#ch2_1">{_("2.1 Der physikalische Messaufbau (WICHTIG!)")}</a></li>
                <li><a href="#ch2_2">{_("2.2 Fluke 45 Einstellungen")}</a></li>
            </ul>
        </li>
        <li><a href="#ch3">🖥️ {_("3. Menü-Referenz & Funktionen")}</a>
            <ul>
                <li><a href="#ch3_1">{_("3.1 Menü: Datei")}</a></li>
                <li><a href="#ch3_2">{_("3.2 Menü: Setup")}</a></li>
                <li><a href="#ch3_3">{_("3.3 Menü: Hilfe")}</a></li>
            </ul>
        </li>
        <li><a href="#ch4">📂 {_("4. Das Report-Verzeichnis & Messdaten")}</a>
            <ul>
                <li><a href="#ch4_1">{_("4.1 Ordnerstruktur (MAC-basiert)")}</a></li>
                <li><a href="#ch4_2">{_("4.2 Dateitypen und Inhalte")}</a></li>
                <li><a href="#ch4_3">{_("4.3 Verwendung vorhandener Messdaten")}</a></li>
            </ul>
        </li>
        <li><a href="#ch5">🚀 {_("5. Der Kalibrierungsprozess (Schritt für Schritt)")}</a>
            <ul>
                <li><a href="#ch5_1">{_("5.1 Vorbereitung & Initialisierung")}</a></li>
                <li><a href="#ch5_2">{_("5.2 Start der Messsequenz")}</a></li>
                <li><a href="#ch5_3">{_("5.3 Ermittlung des Eigenverbrauchs")}</a></li>
                <li><a href="#ch5_4">{_("5.4 Messung unter Last")}</a></li>
                <li><a href="#ch5_5">{_("5.5 Analyse und Finalisierung")}</a></li>
            </ul>
        </li>
        <li><a href="#ch6">🛠️ {_("6. Troubleshooting & Expertentipps")}</a></li>
    </ul>
</div>

<h2 id="ch1">🔬 {_("1. Technischer Hintergrund: Warum 'Cal'-Befehle?")}</h2>
<p>{_("In Tasmota gibt es zwei Wege zur Kalibrierung: Die Set-Befehle (z.B. VoltSet) und die Cal-Befehle (z.B. VoltageCal). Dieses Programm nutzt ausschließlich die Cal-Befehle.")}</p>

<h3 id="ch1_1">{_("1.1 Der Vorteil gegenüber Set-Befehlen")}</h3>
<p>{_("Bei der herkömmlichen Methode mit Set-Befehlen muss der Benutzer einen Wert ablesen und manuell eingeben. In dieser Zeitspanne kann sich die Netzspannung oder die Last bereits leicht verändert haben, was zu einer ungenauen Kalibrierung führt.")}</p>

<h3 id="ch1_2">{_("1.2 Messunsicherheit und zeitlicher Ablauf")}</h3>
<ul>
    <li><b>⚖️ {_("Statistische Sicherheit:")}</b> {_("Die Software erfasst viele Datenpunkte (z.B. 30 Messungen) gleichzeitig von der Referenz und dem Prüfling.")}</li>
    <li><b>📈 {_("Regression:")}</b> {_("Statt einer einfachen Punkt-Kalibrierung wird eine lineare Regression durchgeführt. Dies gleicht Schwankungen im Stromnetz mathematisch aus und minimiert die Messunsicherheit drastisch.")}</li>
    <li><b>⏱️ {_("Zeitvorteil:")}</b> {_("Da die Software die Werte automatisiert abfragt, entfällt das Fehlerrisiko durch menschliche Ablese- oder Tippfehler.")}</li>
</ul>

<h2 id="ch2">🔌 {_("2. Hardware-Vorbereitung & Messaufbau")}</h2>

<h3 id="ch2_1">{_("2.1 Der physikalische Messaufbau (WICHTIG!)")}</h3>
<p>{_("Der korrekte Aufbau unterscheidet sich je nachdem, welches Referenzgerät Sie verwenden.")}</p>

<h4>{_("A) Aufbau mit Tasmota-Referenzdose (HOME-Modus)")}</h4>
<ol>
    <li><b>🏠 {_("Wandsteckdose:")}</b> {_("Stromquelle.")}</li>
    <li><b>📏 {_("Referenz-Dose:")}</b> {_("Ihre bereits kalibrierte Tasmota-Dose.")}</li>
    <li><b>🔌 {_("Prüfling (DUT):")}</b> {_("Die neu zu kalibrierende Tasmota-Dose.")}</li>
    <li><b>💡 {_("Last:")}</b> {_("Ein stabiler Verbraucher (z.B. Glühbirne).")}</li>
</ol>

<h4>{_("B) Aufbau mit Fluke 45 (PRO-Modus)")}</h4>
<ol>
    <li><b>🏠 {_("Wandsteckdose:")}</b> {_("Stromquelle.")}</li>
    <li><b>🔌 {_("Prüfling (DUT):")}</b> {_("Die zu kalibrierende Tasmota-Dose.")}</li>
    <li><b>📏 {_("Fluke 45:")}</b> {_("Anschluss über Messadapter (zwischen Prüfling und Last).")}</li>
    <li><b>💡 {_("Last:")}</b> {_("Ein stabiler Verbraucher (z.B. Glühbirne).")}</li>
</ol>

<div class="warning">⚠️ <b>{_("Wichtiger Hinweis:")}</b> {_("Achte in beiden Fällen auf möglichst kurze Verbindungsleitungen zwischen dem Prüfling (DUT) und dem Messgerät/Adapter, um Messfehler durch Leitungsverluste zu minimieren.")}</div>

<div class="tip">💡 <b>{_("Tipp:")}</b> {_("Verwende keine Schaltnetzteile oder Motoren als Last, da diese instabile Werte liefern. Eine ohmsche Last (Glühfaden) ist ideal.")}</div>

<h3 id="ch2_2">{_("2.2 Fluke 45 Einstellungen")}</h3>
<ul>
    <li>{_("Verbinde das Gerät via RS232 mit dem PC.")}</li>
    <li><b>{_("Menü-Bedienung am Gerät:")}</b>
        <ul>
            <li>{_("Drücken Sie nacheinander die Tasten '2nd' und 'RATE' (BAUD), um in das Setup-Menü zu gelangen.")}</li>
            <li>{_("Nutzen Sie die Pfeiltasten, um die Werte zu ändern.")}</li>
            <li>{_("Bestätigen Sie jede Einstellung mit der Taste 'AUTO'.")}</li>
        </ul>
    </li>
    <li><b>{_("Wichtig: PRINT-Modus ausschalten:")}</b>
        <ul>
            <li>{_("Drücken Sie nacheinander '2nd' und 'MIN MAX' (ADDR).")}</li>
            <li>{_("Stellen Sie den Wert unter 'PRINT' auf '0' (Aus).")}</li>
            <li>{_("Bestätigen Sie mit 'AUTO'.")}</li>
        </ul>
    </li>
</ul>

<h2 id="ch3">🖥️ {_("3. Menü-Referenz & Funktionen")}</h2>

<h3 id="ch3_1">{_("3.1 Menü: Datei")}</h3>
<ul>
    <li><b>💾 {_("Log Speichern:")}</b> {_("Sichert den kompletten Textverlauf des Log-Fensters.")}</li>
    <li><b>📂 {_("Report-Ordner öffnen:")}</b> {_("Öffnet den Windows-Explorer direkt im Verzeichnis Ihrer Messberichte.")}</li>
    <li><b>❌ {_("Beenden:")}</b> {_("Schließt das Programm.")}</li>
</ul>

<h3 id="ch3_2">{_("3.2 Menü: Setup")}</h3>
<ul>
    <li><b>🌐 {_("Allgemein:")}</b> {_("Report-Pfad, Sprache und Toleranzgrenzen festlegen.")}</li>
    <li><b>📟 {_("Fluke 45:")}</b> {_("RS232-Schnittstelle konfigurieren.")}</li>
    <li><b>🔌 {_("Tasmota-Referenz:")}</b> {_("IP-Adresse der Referenzdose eingeben.")}</li>
</ul>

<h3 id="ch3_3">{_("3.3 Menü: Hilfe")}</h3>
<ul>
    <li><b>📘 {_("Anleitung:")}</b> {_("Öffnet dieses Dokument.")}</li>
    <li><b>ℹ️ {_("Lizenz & Info:")}</b> {_("Zeigt Softwareversion und Entwickler-Infos.")}</li>
</ul>

<h2 id="ch4">📂 {_("4. Das Report-Verzeichnis & Messdaten")}</h2>

<h3 id="ch4_1">{_("4.1 Ordnerstruktur (MAC-basiert)")}</h3>
<p>{_("Die Software erstellt für jede Dose einen eigenen Unterordner, benannt nach der MAC-Adresse.")}</p>

<h3 id="ch4_2">{_("4.2 Dateitypen und Inhalte")}</h3>
<ul>
    <li><b>📊 {_("CSV-Dateien:")}</b> {_("Tabellarische Messwerte jeder einzelnen Sekunde.")}</li>
    <li><b>📄 {_("Protokolle:")}</b> {_("Zusammenfassender Bericht mit As-Found und As-Left Faktoren.")}</li>
</ul>

<h3 id="ch4_3">{_("4.3 Verwendung vorhandener Messdaten")}</h3>
<p>{_("Existieren bereits Daten, fragt die Software, ob diese genutzt werden sollen (spart Zeit).")}</p>

<h2 id="ch5">🚀 {_("5. Der Kalibrierungsprozess (Schritt für Schritt)")}</h2>

<h3 id="ch5_1">{_("5.1 Vorbereitung & Initialisierung")}</h3>
<ol>
    <li>{_("IP-Adresse des Prüflings (DUT) eingeben.")}</li>
    <li>{_("Auf 'Online Check' klicken.")}</li>
    <li>{_("Referenz-Quelle wählen.")}</li>
    <li>{_("Messparameter einstellen.")}</li>
</ol>

<h3 id="ch5_2">{_("5.2 Start der Messsequenz")}</h3>
<p>{_("Klicken Sie auf 'Kalibrierung Starten'. Die Eingabefelder werden während der Messung gesperrt.")}</p>

<h3 id="ch5_3">{_("5.3 Ermittlung des Eigenverbrauchs (Offset-Messung)")}</h3>
<p>{_("Nur bei Tasmota-Referenz: Der Prüfling wird automatisch abgeschaltet, um dessen Eigenverbrauch zu messen.")}</p>

<h3 id="ch5_4">{_("5.4 Messung unter Last")}</h3>
<p>{_("Schalten Sie den Prüfling ein, wenn das Popup erscheint. Beobachten Sie die Live-Graphen.")}</p>

<h3 id="ch5_5">{_("5.5 Analyse und Finalisierung")}</h3>
<p>{_("Nach Abschluss öffnet sich das Protokoll-Fenster. Wählen Sie die gewünschten Korrekturwerte (Checkboxen) und klicken Sie auf 'Auswahl Kalibrieren'.")}</p>

<h2 id="ch6">🛠️ {_("6. Troubleshooting & Expertentipps")}</h2>
<ul>
    <li><b>❌ {_("Problem:")}</b> {_("'Keine serielle Antwort vom Fluke' -> Kabel und COM-Port prüfen.")}</li>
    <li><b>⚠️ {_("Problem:")}</b> {_("'HTTP 401 Unauthorized' -> Zugangsdaten im Popup eingeben.")}</li>
    <li><b>🔐 {_("Tipp:")}</b> {_("Nutzen Sie den Online-Check vorab, um Zugangsdaten einmalig zu hinterlegen.")}</li>
    <li><b>🌡️ {_("Tipp:")}</b> {_("Anlage 5 Minuten 'warmlaufen' lassen für höchste Präzision.")}</li>
</ul>

<div class="footer">
    <a href="#top" style="color: #4a9eff;">🏠 {_("Zurück zum Index")}</a>
</div>
</body>
</html>
"""
