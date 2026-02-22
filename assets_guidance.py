# -*- coding: utf-8 -*-
"""
# English: Contains the instructional content for the application in HTML format (Dark Mode).
# Deutsch: Enthält den Anleitungstext für die Anwendung im HTML-Format (Dark Mode).
"""

GUIDANCE_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { 
        font-family: sans-serif; 
        line-height: 1.6; 
        color: #e0e0e0; 
        padding: 25px; 
        background-color: #1e1e1e; 
    }
    h1 { 
        color: #4a9eff; 
        border-bottom: 2px solid #4a9eff; 
        padding-bottom: 10px; 
    }
    h2 { 
        color: #4a9eff; 
        margin-top: 40px; 
        background-color: #2d2d2d; 
        padding: 8px 15px; 
        border-left: 5px solid #4a9eff; 
        border-radius: 0 4px 4px 0;
    }
    h3 { 
        color: #ffffff; 
        margin-top: 25px; 
        border-bottom: 1px solid #444;
        padding-bottom: 5px;
    }
    h4 {
        color: #4a9eff;
        margin-top: 20px;
        margin-bottom: 5px;
    }
    .index { 
        background-color: #252525; 
        padding: 20px; 
        border-radius: 8px; 
        border: 1px solid #444; 
        margin-bottom: 30px;
    }
    .index ul { list-style-type: none; padding-left: 0; }
    .index li { margin-bottom: 10px; }
    .index a { text-decoration: none; color: #4a9eff; font-weight: bold; }
    .index a:hover { text-decoration: underline; color: #82c0ff; }
    
    .action-box { 
        background-color: #3a321a; 
        border-left: 5px solid #d4a017; 
        padding: 12px; 
        margin: 15px 0; 
        color: #ffffff;
        border-radius: 0 4px 4px 0;
    }
    .background-info { 
        font-style: italic; 
        color: #aaaaaa; 
        margin-left: 25px; 
        margin-bottom: 20px; 
        display: block; 
        font-size: 0.95em;
    }
    .tip { 
        background-color: #1b3a22; 
        border-left: 5px solid #28a745; 
        padding: 12px; 
        margin: 15px 0; 
        border-radius: 0 4px 4px 0;
    }
    .warning { 
        background-color: #3d1a1d; 
        border-left: 5px solid #dc3545; 
        padding: 12px; 
        margin: 15px 0; 
        border-radius: 0 4px 4px 0;
    }
    code { 
        background-color: #333; 
        padding: 2px 5px; 
        border-radius: 3px; 
        color: #ff7b72;
        font-family: monospace;
    }
    .footer { 
        margin-top: 60px; 
        text-align: center; 
        font-size: 0.9em; 
        color: #777; 
        border-top: 1px solid #444; 
        padding-top: 25px; 
    }
    a { color: #4a9eff; }
</style>
</head>
<body>

<h1 id="top">📘 {_("Bedienungsanleitung: Tasmota Precision Calibrator")}</h1>

<p>{_("Willkommen beim <b>Tasmota Precision Calibrator</b>. Dieses Werkzeug wurde entwickelt, um die Kalibrierung von Tasmota-Energiemessgeräten auf ein professionelles Niveau zu heben.")}</p>

<div class="index">
    <h2>📌 {_("Inhaltsverzeichnis")}</h2>
    <ul>
        <li><a href="#ch1">🔬 {_("1. Technischer Hintergrund: Warum \"Cal\"-Befehle?")}</a>
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
        <li><a href="#ch3">🖥️ {_("3. Menü-Referenz & Funktionen")}</a></li>
        <li><a href="#ch4">📂 {_("4. Das Report-Verzeichnis & Messdaten")}</a></li>
        <li><a href="#ch5">🚀 {_("5. Der Kalibrierungsprozess (Schritt für Schritt)")}</a>
            <ul>
                <li><a href="#ch5_1">{_("5.1 🛠️ Vorbereitung & Initialisierung")}</a></li>
                <li><a href="#ch5_2">{_("5.2 ▶️ Start der Messsequenz")}</a></li>
                <li><a href="#ch5_3">{_("5.3 🔄 Ermittlung des Eigenverbrauchs (Offset)")}</a></li>
                <li><a href="#ch5_4">{_("5.4 📉 Messung unter Last")}</a></li>
                <li><a href="#ch5_5">{_("5.5 ✅ Analyse und Finalisierung")}</a></li>
            </ul>
        </li>
        <li><a href="#ch6">🛠️ {_("6. Troubleshooting & Expertentipps")}</a></li>
    </ul>
</div>

<hr style="border: 0; border-top: 1px solid #444;">

<h2 id="ch1">🔬 {_("1. Technischer Hintergrund: Warum \"Cal\"-Befehle?")}</h2>
<p>{_("In Tasmota gibt es zwei Wege zur Kalibrierung: Die <code>Set</code>-Befehle (z.B. <code>VoltSet</code>) und die <code>Cal</code>-Befehle (z.B. <code>VoltageCal</code>). Dieses Programm nutzt ausschließlich die <code>Cal</code>-Befehle.")}</p>

<h3 id="ch1_1">{_("1.1 Der Vorteil gegenüber Set-Befehlen")}</h3>
<p>{_("Bei der herkömmlichen Methode mit <code>Set</code>-Befehlen muss der Benutzer einen Wert ablesen und manuell eingeben. In dieser Zeitspanne kann sich die Netzspannung oder die Last bereits leicht verändert haben, was zu einer ungenauen Kalibrierung führt.")}</p>

<h3 id="ch1_2">{_("1.2 Messunsicherheit und zeitlicher Ablauf")}</h3>
<ul>
    <li><b>⚖️ {_("Statistische Sicherheit:")}</b> {_("Die Software erfasst viele Datenpunkte gleichzeitig von der Referenz und dem Prüfling.")}</li>
    <li><b>📈 {_("Regression:")}</b> {_("Statt einer einfachen Punkt-Kalibrierung wird eine lineare Regression durchgeführt. Dies gleicht Schwankungen im Stromnetz mathematisch aus und minimiert die Messunsicherheit drastisch.")}</li>
</ul>

<h2 id="ch2">🔌 {_("2. Hardware-Vorbereitung & Messaufbau")}</h2>

<h3 id="ch2_1">{_("2.1 Der physikalische Messaufbau (WICHTIG!)")}</h3>
<p>{_("Der korrekte Aufbau unterscheidet sich je nachdem, welches Referenzgerät Sie verwenden.")}</p>

<h4>{_("A) Aufbau mit Tasmota-Referenzdose (HOME-Modus)")}</h4>
<p>{_("In diesem Modus misst die Referenzdose den Eigenverbrauch des Prüflings mit, der später automatisch abgezogen wird.")}</p>
<ol>
    <li><b>🏠 {_("Wandsteckdose:")}</b> {_("Stromquelle.")}</li>
    <li><b>📏 {_("Referenz-Dose:")}</b> {_("Ihre bereits kalibrierte Tasmota-Dose.")}</li>
    <li><b>🔌 {_("Prüfling (DUT):")}</b> {_("Die neu zu kalibrierende Tasmota-Dose.")}</li>
    <li><b>💡 {_("Last:")}</b> {_("Ein stabiler Verbraucher (z.B. Glühbirne).")}</li>
</ol>

<h4>{_("B) Aufbau mit Fluke 45 (PRO-Modus)")}</h4>
<p>{_("Hier wird das Fluke mit einem Messadapter direkt hinter den Prüfling geschaltet, um dessen Ausgangswerte präzise zu erfassen.")}</p>
<ol>
    <li><b>🏠 {_("Wandsteckdose:")}</b> {_("Stromquelle.")}</li>
    <li><b>🔌 {_("Prüfling (DUT):")}</b> {_("Die zu kalibrierende Tasmota-Dose.")}</li>
    <li><b>📏 {_("Fluke 45:")}</b> {_("Anschluss über Messadapter (zwischen Prüfling und Last).")}</li>
    <li><b>💡 {_("Last:")}</b> {_("Ein stabiler Verbraucher (z.B. Glühbirne).")}</li>
</ol>

<div class="warning">
    ⚠️ <b>{_("Wichtiger Hinweis:")}</b> {_("Achte in beiden Fällen auf möglichst <b>kurze Verbindungsleitungen</b> zwischen dem Prüfling (DUT) und dem Messgerät/Adapter, um Messfehler durch Leitungsverluste zu minimieren.")}
</div>

<div class="tip">
    💡 <b>{_("Tipp:")}</b> {_("Verwende eine ohmsche Last (Glühfaden), keine Schaltnetzteile.")}
</div>

<h3 id="ch2_2">{_("2.2 Fluke 45 Einstellungen")}</h3>
<ul>
    <li>{_("Verbinde das Gerät via RS232 mit dem PC.")}</li>
    <li><b>{_("Menü-Bedienung am Gerät:")}</b>
        <ul>
            <li>{_("Drücken Sie nacheinander <b>\"2nd\"</b> und <b>\"RATE\"</b> (BAUD), um in das Setup zu gelangen.")}</li>
            <li>{_("Nutzen Sie die <b>Pfeiltasten</b> zur Wertänderung.")}</li>
            <li>{_("Bestätigen Sie mit der Taste <b>\"AUTO\"</b>.")}</li>
        </ul>
    </li>
    <li><b>{_("Wichtig: PRINT-Modus ausschalten:")}</b>
        <ul>
            <li>{_("Drücken Sie nacheinander <b>\"2nd\"</b> und <b>\"MIN MAX\"</b> (ADDR).")}</li>
            <li>{_("Stellen Sie den Wert unter \"PRINT\" auf <b>\"0\"</b> (Aus).")}</li>
            <li>{_("Bestätigen Sie mit <b>\"AUTO\"</b>.")}</li>
        </ul>
    </li>
    <li><b>{_("Optimale Parameter:")}</b>
        <ul>
            <li>{_("Baudrate: <b>9600</b> (empfohlen)")}</li>
            <li>{_("Parität: <b>None</b> (Keine)")}</li>
            <li>{_("Echo: <b>Off</b> (Aus)")}</li>
        </ul>
    </li>
    <li>{_("Das Programm setzt das Gerät automatisch in den Dual-Display-Modus (Primär-Anzeige: <b>VAC</b>, Sekundär-Anzeige: <b>AAC</b>).")}</li>
</ul>

<h2 id="ch3">🖥️ {_("3. Menü-Referenz & Funktionen")}</h2>
<h3>📁 {_("Menü: Datei")}</h3>
<ul>
    <li><b>💾 {_("Log Speichern:")}</b> {_("Sichert den kompletten Textverlauf des Log-Fensters.")}</li>
    <li><b>📂 {_("Report-Ordner öffnen:")}</b> {_("Öffnet den Explorer direkt im Verzeichnis der Messberichte.")}</li>
</ul>
<h3>⚙️ {_("Menü: Setup")}</h3>
<ul>
    <li><b>🌐 {_("Allgemein:")}</b> {_("Festlegen des Report-Pfads und Definition der <b>Toleranzgrenzen</b> (ab welcher Abweichung eine Kalibrierung empfohlen wird).")}</li>
    <li><b>📟 {_("Fluke 45:")}</b> {_("RS232-Konfiguration (inkl. \"Fluke finden\" Auto-Scan).")}</li>
    <li><b>🔌 {_("Tasmota-Referenz:")}</b> {_("IP-Adresse Ihrer kalibrierten Referenzdose.")}</li>
</ul>

<h2 id="ch4">📂 {_("4. Das Report-Verzeichnis & Messdaten")}</h2>
<p>{_("Jedes Gerät erhält einen Unterordner benannt nach der MAC-Adresse.")}</p>
<ul>
    <li><b>📊 {_("CSV-Dateien:")}</b> {_("Tabellarische Messwerte jeder einzelnen Sekunde.")}</li>
    <li><b>📄 {_("Protokolle:")}</b> {_("Zusammenfassender Bericht mit As-Found/As-Left Vergleich.")}</li>
</ul>

<h2 id="ch5">🚀 {_("5. Der Kalibrierungsprozess (Schritt für Schritt)")}</h2>

<h3 id="ch5_1">{_("5.1 🛠️ Vorbereitung & Initialisierung")}</h3>
<div class="action-box"><b>⌨️ {_("Aktion:")}</b> {_("Geben Sie die <b>IP-Adresse des Prüflings</b> ein und klicken Sie auf <b>\"Online Check\"</b>.")}</div>
<span class="background-info">
    {_("Hintergrund: Die Software prüft Erreichbarkeit und liest die MAC-Adresse aus. <b>Wichtig:</b> Falls die Dose passwortgeschützt ist, geben Sie hier einmalig die Zugangsdaten ein. Diese werden für die gesamte Sitzung gespeichert.")}
</span>

<div class="action-box"><b>⚙️ {_("Aktion:")}</b> {_("Stellen Sie die <b>Messparameter</b> ein (Stufen & Messungen pro Stufe).")}</div>
<span class="background-info">
    • <b>🏠 {_("HOME-Modus:")}</b> {_("Die Anzahl der Messstufen ist fest auf <b>1</b> eingestellt und deaktiviert. Eine einzige Stufe mit ca. 30 Messungen ist hier der Standard für höchste Präzision.")}<br>
    • <b>🔬 {_("PRO-Modus:")}</b> {_("Hier können Sie mehrere Stufen wählen (z.B. für eine Kennlinien-Aufnahme). 3 Stufen mit 25 Messungen bieten im Regelfall ein exzellentes Verhältnis zwischen Zeitaufwand und Präzision.")}
</span>

<h3 id="ch5_2">{_("5.2 ▶️ Start der Messsequenz")}</h3>
<div class="action-box"><b>🖱️ {_("Aktion:")}</b> {_("Klicken Sie auf den Button <b>\"Kalibrierung Starten\"</b>.")}</div>

<h3 id="ch5_3">{_("5.3 🔄 Ermittlung des Eigenverbrauchs — [Nur Tasmota-Referenz]")}</h3>
<div class="action-box"><b>🔌 {_("Aktion:")}</b> {_("Warten Sie auf die automatische Abschaltung des Prüflings.")}</div>
<span class="background-info">{_("Hintergrund: Das Programm schaltet den DUT AUS, um dessen Eigenverbrauch (Offset) zu messen.")}</span>

<h3 id="ch5_4">{_("5.4 📉 Messung unter Last")}</h3>
<div class="action-box"><b>📢 {_("Aktion:")}</b> {_("Popup erscheint: Schalten Sie den Prüfling nun EIN. Beobachten Sie die <b>Live-Graphen</b> und den neuen <b>Fortschrittsbalken</b>.")}</div>
<span class="background-info">{_("Hintergrund: Die Software wartet 7 Sek. (Inrush-Filter) und sammelt dann die validen Messdaten. Der Fortschrittsbalken zeigt den Status der aktuellen Stufe in Echtzeit an.")}</span>

<h3 id="ch5_5">{_("5.5 ✅ Analyse und Finalisierung")}</h3>
<div class="action-box"><b>📋 {_("Aktion:")}</b> {_("Prüfen Sie die farbigen Info-Labels im Abschluss-Dialog.")}</div>
<span class="background-info">{_("Hintergrund: Die Software vergleicht die neuen Werte mit den alten. 🟢 Grün bedeutet innerhalb der Toleranz, 🟠 Orange bedeutet Kalibrierung empfohlen.")}</span>

<div class="action-box"><b>☑️ {_("Aktion:")}</b> {_("Wählen Sie die gewünschten Faktoren über die Checkboxen aus.")}</div>
<span class="background-info">
    • <b>🏠 {_("HOME-Modus:")}</b> {_("Nur die relevante Leistungsoption (<b>PowerCal</b>) wird angezeigt. Regressions-Analyse und Graph sind ausgeblendet.")}<br>
    • <b>🔬 {_("PRO-Modus:")}</b> {_("Sie haben die Wahl zwischen Mean (Mittelwert) und Regression. Über den Button <b>\"📊 REGRESSIONS-GRAPH\"</b> können Sie die Messkurve visuell prüfen.")}
</span>

<div class="action-box"><b>📤 {_("Aktion:")}</b> {_("Klicken Sie auf <b>\"Auswahl Kalibrieren\"</b>.")}</div>
<span class="background-info">{_("Hintergrund: Die ausgewählten Werte werden übertragen und sofort verifiziert.")}</span>

<h2 id="ch6">🛠️ {_("6. Troubleshooting & Expertentipps")}</h2>
<div class="warning">
    ⚠️ <b>{_("Problem:")}</b> {_("\"HTTP 401 Unauthorized\" (Login fehlgeschlagen).")}<br>
    <b>{_("Lösung:")}</b> {_("Die Dose ist passwortgeschützt. Geben Sie die Daten im Popup ein. Der Standardbenutzer ist \"admin\".")}
</div>

<div class="tip">
    🔐 <b>{_("Tipp zu Zugangsdaten:")}</b> {_("Die App speichert eingegebene Passwörter im Arbeitsspeicher, bis das Programm geschlossen wird. Nutzen Sie den <b>\"Online Check\"</b> vor der Messung, um die Daten einmalig zu hinterlegen.")}
</div>

<div class="tip">
    🌡️ <b>{_("Tipp für Experten:")}</b> {_("Lassen Sie die Messanordnung ca. 5 Minuten \"warmlaufen\". Eine Kalibrierung im warmen Betriebszustand ist präziser.")}
</div>

<div class="footer">
    <a href="#top">🏠 {_("Zurück zum Index")}</a>
</div>

</body>
</html>
"""
