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

<h1 id="top">📘 Bedienungsanleitung: Tasmota Precision Calibrator</h1>

<p>Willkommen beim <b>Tasmota Precision Calibrator</b>. Dieses Werkzeug wurde entwickelt, um die Kalibrierung von Tasmota-Energiemessgeräten auf ein professionelles Niveau zu heben.</p>

<div class="index">
    <h2>📌 Inhaltsverzeichnis</h2>
    <ul>
        <li><a href="#ch1">🔬 1. Technischer Hintergrund: Warum "Cal"-Befehle?</a>
            <ul>
                <li><a href="#ch1_1">1.1 Der Vorteil gegenüber Set-Befehlen</a></li>
                <li><a href="#ch1_2">1.2 Messunsicherheit und zeitlicher Ablauf</a></li>
            </ul>
        </li>
        <li><a href="#ch2">🔌 2. Hardware-Vorbereitung & Messaufbau</a>
            <ul>
                <li><a href="#ch2_1">2.1 Der physikalische Messaufbau (WICHTIG!)</a></li>
                <li><a href="#ch2_2">2.2 Fluke 45 Einstellungen</a></li>
            </ul>
        </li>
        <li><a href="#ch3">🖥️ 3. Menü-Referenz & Funktionen</a></li>
        <li><a href="#ch4">📂 4. Das Report-Verzeichnis & Messdaten</a></li>
        <li><a href="#ch5">🚀 5. Der Kalibrierungsprozess (Schritt für Schritt)</a>
            <ul>
                <li><a href="#ch5_1">5.1 🛠️ Vorbereitung & Initialisierung</a></li>
                <li><a href="#ch5_2">5.2 ▶️ Start der Messsequenz</a></li>
                <li><a href="#ch5_3">5.3 🔄 Ermittlung des Eigenverbrauchs (Offset)</a></li>
                <li><a href="#ch5_4">5.4 📉 Messung unter Last</a></li>
                <li><a href="#ch5_5">5.5 ✅ Analyse und Finalisierung</a></li>
            </ul>
        </li>
        <li><a href="#ch6">🛠️ 6. Troubleshooting & Expertentipps</a></li>
    </ul>
</div>

<hr style="border: 0; border-top: 1px solid #444;">

<h2 id="ch1">🔬 1. Technischer Hintergrund: Warum "Cal"-Befehle?</h2>
<p>In Tasmota gibt es zwei Wege zur Kalibrierung: Die <code>Set</code>-Befehle (z.B. <code>VoltSet</code>) und die <code>Cal</code>-Befehle (z.B. <code>VoltageCal</code>). Dieses Programm nutzt ausschließlich die <code>Cal</code>-Befehle.</p>

<h3 id="ch1_1">1.1 Der Vorteil gegenüber Set-Befehlen</h3>
<p>Bei der herkömmlichen Methode mit <code>Set</code>-Befehlen muss der Benutzer einen Wert ablesen und manuell eingeben. In dieser Zeitspanne kann sich die Netzspannung oder die Last bereits leicht verändert haben, was zu einer ungenauen Kalibrierung führt.</p>

<h3 id="ch1_2">1.2 Messunsicherheit und zeitlicher Ablauf</h3>
<ul>
    <li><b>⚖️ Statistische Sicherheit:</b> Die Software erfasst viele Datenpunkte gleichzeitig von der Referenz und dem Prüfling.</li>
    <li><b>📈 Regression:</b> Statt einer einfachen Punkt-Kalibrierung wird eine lineare Regression durchgeführt. Dies gleicht Schwankungen im Stromnetz mathematisch aus und minimiert die Messunsicherheit drastisch.</li>
</ul>

<h2 id="ch2">🔌 2. Hardware-Vorbereitung & Messaufbau</h2>

<h3 id="ch2_1">2.1 Der physikalische Messaufbau (WICHTIG!)</h3>
<p>Der korrekte Aufbau unterscheidet sich je nachdem, welches Referenzgerät Sie verwenden.</p>

<h4>A) Aufbau mit Tasmota-Referenzdose (HOME-Modus)</h4>
<p>In diesem Modus misst die Referenzdose den Eigenverbrauch des Prüflings mit, der später automatisch abgezogen wird.</p>
<ol>
    <li><b>🏠 Wandsteckdose:</b> Stromquelle.</li>
    <li><b>📏 Referenz-Dose:</b> Ihre bereits kalibrierte Tasmota-Dose.</li>
    <li><b>🔌 Prüfling (DUT):</b> Die neu zu kalibrierende Tasmota-Dose.</li>
    <li><b>💡 Last:</b> Ein stabiler Verbraucher (z.B. Glühbirne).</li>
</ol>

<h4>B) Aufbau mit Fluke 45 (PRO-Modus)</h4>
<p>Hier wird das Fluke mit einem Messadapter direkt hinter den Prüfling geschaltet, um dessen Ausgangswerte präzise zu erfassen.</p>
<ol>
    <li><b>🏠 Wandsteckdose:</b> Stromquelle.</li>
    <li><b>🔌 Prüfling (DUT):</b> Die zu kalibrierende Tasmota-Dose.</li>
    <li><b>📏 Fluke 45:</b> Anschluss über Messadapter (zwischen Prüfling und Last).</li>
    <li><b>💡 Last:</b> Ein stabiler Verbraucher (z.B. Glühbirne).</li>
</ol>

<div class="warning">
    ⚠️ <b>Wichtiger Hinweis:</b> Achte in beiden Fällen auf möglichst <b>kurze Verbindungsleitungen</b> zwischen dem Prüfling (DUT) und dem Messgerät/Adapter, um Messfehler durch Leitungsverluste zu minimieren.
</div>

<div class="tip">
    💡 <b>Tipp:</b> Verwende eine ohmsche Last (Glühfaden), keine Schaltnetzteile.
</div>

<h3 id="ch2_2">2.2 Fluke 45 Einstellungen</h3>
<ul>
    <li>Verbinde das Gerät via RS232 mit dem PC.</li>
    <li><b>Menü-Bedienung am Gerät:</b>
        <ul>
            <li>Drücken Sie nacheinander <b>"2nd"</b> und <b>"RATE"</b> (BAUD), um in das Setup zu gelangen.</li>
            <li>Nutzen Sie die <b>Pfeiltasten</b> zur Wertänderung.</li>
            <li>Bestätigen Sie mit der Taste <b>"AUTO"</b>.</li>
        </ul>
    </li>
    <li><b>Wichtig: PRINT-Modus ausschalten:</b>
        <ul>
            <li>Drücken Sie nacheinander <b>"2nd"</b> und <b>"MIN MAX"</b> (ADDR).</li>
            <li>Stellen Sie den Wert unter "PRINT" auf <b>"0"</b> (Aus).</li>
            <li>Bestätigen Sie mit <b>"AUTO"</b>.</li>
        </ul>
    </li>
    <li><b>Optimale Parameter:</b>
        <ul>
            <li>Baudrate: <b>9600</b> (empfohlen)</li>
            <li>Parität: <b>None</b> (Keine)</li>
            <li>Echo: <b>Off</b> (Aus)</li>
        </ul>
    </li>
    <li>Das Programm setzt das Gerät automatisch in den Dual-Display-Modus (Primär-Anzeige: <b>VAC</b>, Sekundär-Anzeige: <b>AAC</b>).</li>
</ul>

<h2 id="ch3">🖥️ 3. Menü-Referenz & Funktionen</h2>
<h3>📁 Menü: Datei</h3>
<ul>
    <li><b>💾 Log Speichern:</b> Sichert den kompletten Textverlauf des Log-Fensters.</li>
    <li><b>📂 Report-Ordner öffnen:</b> Öffnet den Explorer direkt im Verzeichnis der Messberichte.</li>
</ul>
<h3>⚙️ Menü: Setup</h3>
<ul>
    <li><b>🌐 Allgemein:</b> Festlegen des Report-Pfads und Definition der <b>Toleranzgrenzen</b> (ab welcher Abweichung eine Kalibrierung empfohlen wird).</li>
    <li><b>📟 Fluke 45:</b> RS232-Konfiguration (inkl. "Fluke finden" Auto-Scan).</li>
    <li><b>🔌 Tasmota-Referenz:</b> IP-Adresse Ihrer kalibrierten Referenzdose.</li>
</ul>

<h2 id="ch4">📂 4. Das Report-Verzeichnis & Messdaten</h2>
<p>Jedes Gerät erhält einen Unterordner benannt nach der MAC-Adresse.</p>
<ul>
    <li><b>📊 CSV-Dateien:</b> Tabellarische Messwerte jeder einzelnen Sekunde.</li>
    <li><b>📄 Protokolle:</b> Zusammenfassender Bericht mit As-Found/As-Left Vergleich.</li>
</ul>

<h2 id="ch5">🚀 5. Der Kalibrierungsprozess (Schritt für Schritt)</h2>

<h3 id="ch5_1">5.1 🛠️ Vorbereitung & Initialisierung</h3>
<div class="action-box"><b>⌨️ Aktion:</b> Geben Sie die <b>IP-Adresse des Prüflings</b> ein und klicken Sie auf <b>"Online Check"</b>.</div>
<span class="background-info">Hintergrund: Die Software prüft Erreichbarkeit und liest die MAC-Adresse aus. <b>Wichtig:</b> Falls die Dose passwortgeschützt ist, geben Sie hier einmalig die Zugangsdaten ein. Diese werden für die gesamte Sitzung gespeichert.</span>

<h3 id="ch5_2">5.2 ▶️ Start der Messsequenz</h3>
<div class="action-box"><b>🖱️ Aktion:</b> Klicken Sie auf den Button <b>"Kalibrierung Starten"</b>.</div>

<h3 id="ch5_3">5.3 🔄 Ermittlung des Eigenverbrauchs — [Nur Tasmota-Referenz]</h3>
<div class="action-box"><b>🔌 Aktion:</b> Warten Sie auf die automatische Abschaltung des Prüflings.</div>
<span class="background-info">Hintergrund: Das Programm schaltet den DUT AUS, um dessen Eigenverbrauch (Offset) zu messen.</span>

<h3 id="ch5_4">5.4 📉 Messung unter Last</h3>
<div class="action-box"><b>📢 Aktion:</b> Popup erscheint: Schalten Sie den Prüfling nun EIN. Beobachten Sie die <b>Live-Graphen</b> und den neuen <b>Fortschrittsbalken</b>.</div>
<span class="background-info">Hintergrund: Die Software wartet 7 Sek. (Inrush-Filter) und sammelt dann die validen Messdaten. Der Fortschrittsbalken zeigt den Status der aktuellen Stufe in Echtzeit an.</span>

<h3 id="ch5_5">5.5 ✅ Analyse und Finalisierung</h3>
<div class="action-box"><b>📋 Aktion:</b> Prüfen Sie die farbigen Info-Labels im Abschluss-Dialog.</div>
<span class="background-info">Hintergrund: Die Software vergleicht die neuen Werte mit den alten. 🟢 Grün bedeutet innerhalb der Toleranz, 🟠 Orange bedeutet Kalibrierung empfohlen.</span>

<div class="action-box"><b>☑️ Aktion:</b> Wählen Sie die gewünschten Faktoren über die Checkboxen aus.</div>
<span class="background-info">Hinweis: Sie können VoltageCal, CurrentCal und PowerCal (Mean oder Regression) selektiv wählen.</span>

<div class="action-box"><b>📤 Aktion:</b> Klicken Sie auf <b>"Auswahl Kalibrieren"</b>.</div>
<span class="background-info">Hintergrund: Die ausgewählten Werte werden übertragen und sofort verifiziert.</span>

<h2 id="ch6">🛠️ 6. Troubleshooting & Expertentipps</h2>
<div class="warning">
    ⚠️ <b>Problem:</b> "HTTP 401 Unauthorized" (Login fehlgeschlagen).<br>
    <b>Lösung:</b> Die Dose ist passwortgeschützt. Geben Sie die Daten im Popup ein. Der Standardbenutzer ist "admin".
</div>

<div class="tip">
    🔐 <b>Tipp zu Zugangsdaten:</b> Die App speichert eingegebene Passwörter im Arbeitsspeicher, bis das Programm geschlossen wird. Nutzen Sie den <b>"Online Check"</b> vor der Messung, um die Daten einmalig zu hinterlegen.
</div>

<div class="tip">
    🌡️ <b>Tipp für Experten:</b> Lassen Sie die Messanordnung ca. 5 Minuten "warmlaufen". Eine Kalibrierung im warmen Betriebszustand ist präziser.
</div>

<div class="footer">
    <a href="#top">🏠 Zurück zum Index</a>
</div>

</body>
</html>
"""
