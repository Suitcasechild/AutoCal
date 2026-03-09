# -*- coding: utf-8 -*-

# English: This file contains the embedded documentation for dynamic power calibration.
# Deutsch: Diese Datei enthält die eingebettete Dokumentation für die dynamische Power-Kalibrierung.

DYNAMIC_CAL_HELP_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
    body {
        background-color: #1e1e1e;
        color: #d4d4d4;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        padding: 20px;
    }
    h1 { color: #569cd6; border-bottom: 2px solid #3e3e42; padding-bottom: 10px; }
    h2 { color: #4ec9b0; margin-top: 30px; border-left: 4px solid #4ec9b0; padding-left: 10px; }
    h3 { color: #ce9178; }
    a { color: #3794ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    code { background-color: #2d2d2d; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; color: #d7ba7d; }
    pre { background-color: #2d2d2d; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid #3e3e42; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; background-color: #252526; }
    th, td { border: 1px solid #3e3e42; padding: 12px; text-align: left; }
    th { background-color: #333337; color: #569cd6; }
    tr:nth-child(even) { background-color: #2a2a2b; }
    .warning { color: #f44336; font-weight: bold; }
    .info { color: #2196F3; font-style: italic; }
    hr { border: 0; border-top: 1px solid #3e3e42; margin: 20px 0; }
    .toc { background-color: #252526; padding: 15px; border-radius: 5px; border: 1px solid #3e3e42; margin-bottom: 30px; }
    .toc-title { font-weight: bold; margin-bottom: 10px; color: #dcdcdc; }
</style>
</head>
<body>

<h1 id="top">🚀 Dokumentation: Dynamische Power-Kalibrierung (Tasmota Rules)</h1>

<p>Dieses Dokument beschreibt die Funktionsweise, die mathematische Logik und die Sicherheitsmechanismen der dynamischen <b>Power-Kalibrierung</b> für Tasmota-Geräte.</p>

<div class="toc">
    <div class="toc-title">📋 Inhaltsverzeichnis</div>
    <ol>
        <li><a href="#1-einfuehrung">Einführung & Zielsetzung</a></li>
        <li><a href="#2-problematik">Die Problematik der statischen Power-Kalibrierung</a></li>
        <li><a href="#3-funktionsweise">Funktionsweise der dynamischen Regelung</a></li>
        <li><a href="#4-anatomie">Anatomie der Tasmota-Rule (Praxisbeispiel)</a></li>
        <li><a href="#5-savedata">Dauerbetrieb mit SaveData 0</a></li>
        <li><a href="#6-auswirkungen">Auswirkungen auf die Energiemessung (Zählerstände)</a></li>
        <li><a href="#7-wichtig">WICHTIG: Zusammenfassung & Sicherheit</a></li>
        <li><a href="#8-workflow">Workflow und Traceability</a></li>
    </ol>
</div>

<hr>

<h2 id="1-einfuehrung">1. 💡 Einführung & Zielsetzung</h2>
<p>Die dynamische <b>Power-Kalibrierung</b> ist ein Experten-Feature, das die Messgenauigkeit der Wirkleistung (<code>Power</code>) über den gesamten Lastbereich hinweg drastisch erhöht. Anstatt einen einzigen, festen Kalibrierwert (<code>PowerCal</code>) zu verwenden, nutzt dieses System die internen Rules von Tasmota, um den <b>PowerCal-Wert</b> in Echtzeit an den fließenden Strom anzupassen.</p>

<h2 id="2-problematik">2. ⚠️ Die Problematik der statischen Power-Kalibrierung</h2>
<p>Sensoren zur Leistungsmessung arbeiten oft nicht linear. Ein Gerät, das bei hoher Last (z. B. 2000W) perfekt <b>Power-kalibriert</b> ist, weist bei geringen Lasten oft signifikante Abweichungen auf. Ein statischer Wert ist daher immer nur ein Kompromiss.</p>

<h2 id="3-funktionsweise">3. ⚙️ Funktionsweise der dynamischen Regelung</h2>

<h3 id="3-1-berechnung">3.1 Berechnung der Umschaltpunkte (Strom-Schwellen)</h3>
<p>Um fließende Übergänge zwischen den Messstufen zu schaffen, berechnet das System die Mitte zwischen zwei benachbarten Messpunkten.</p>
<ul>
    <li><b>Beispiel:</b> 
        <ul>
            <li>Stufe 1 gemessen bei <b>1.0A</b></li>
            <li>Stufe 2 gemessen bei <b>4.0A</b></li>
            <li><b>Umschaltpunkt:</b> (1.0 + 4.0) / 2 = <b>2.5A</b></li>
        </ul>
    </li>
</ul>

<h3 id="3-2-warum-strom">3.2 Warum Strom (A) als Triggerquelle?</h3>
<p>Die Umschaltung der <b>Power-Kalibrierung</b> erfolgt ausschließlich auf Basis der <b>Strommesswerte (Energy#Current)</b>.</p>
<ul>
    <li><b>Stabilität:</b> Der Stromwert ist bei den meisten Sensoren über den gesamten Bereich linear und unabhängig von der gerade durchgeführten Leistungskorrektur.</li>
    <li><b>Kein Zirkelbezug:</b> Da wir die Leistung (<code>Power</code>) gerade erst korrigieren, würde sie als Trigger zu instabilen Zuständen führen.</li>
</ul>

<h3 id="3-3-hysterese">3.3 Hysterese-Logik (Anti-Flackern)</h3>
<p>Damit das System an einem Umschaltpunkt nicht ständig zwischen den Werten springt, wird eine <b>Hysterese</b> (Standard: 0.15A) angewendet.</p>
<ul>
    <li><b>Hochschalten:</b> Erfolgt exakt am Strom-Umschaltpunkt (z. B. 2.50A).</li>
    <li><b>Runterschalten:</b> Erfolgt erst, wenn der Strom den Umschaltpunkt minus der Hysterese unterschreitet (z. B. 2.50A - 0.15A = 2.35A).</li>
</ul>

<h2 id="4-anatomie">4. 🔍 Anatomie der Tasmota-Rule (Praxisbeispiel)</h2>

<h3 id="4-1-beispiel-tabelle">4.1 Beispiel-Tabelle (Programmansicht)</h3>
<p>Angenommen, es wurden drei Messstufen durchgeführt (Hysterese 0.15A):</p>

<table>
    <thead>
        <tr>
            <th>Strom (A) [Referenz]</th>
            <th>PowerCal [Vorschlag]</th>
            <th>Bereich (A) [Gültigkeit]</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>0.894 A</td>
            <td><b>9576</b></td>
            <td>0.000 - 2.587 A</td>
        </tr>
        <tr>
            <td>4.280 A</td>
            <td><b>9413</b></td>
            <td>2.437 - 6.623 A</td>
        </tr>
        <tr>
            <td>8.966 A</td>
            <td><b>9361</b></td>
            <td>6.473 - 10.000 A</td>
        </tr>
    </tbody>
</table>

<ul>
    <li><b>Schwelle 1 (2.587A):</b> Mitte zwischen 0.894A und 4.280A.</li>
    <li><b>Schwelle 2 (6.623A):</b> Mitte zwischen 4.280A und 8.966A.</li>
</ul>

<h3 id="4-2-rule-string">4.2 Der generierte Rule-String</h3>
<p>Der resultierende Befehl für Tasmota lautet:</p>

<pre>Rule1 ON Energy#Current>0 DO PowerCal 9576 ENDON ON Energy#Current>2.587 DO PowerCal 9413 ENDON ON Energy#Current>6.623 DO PowerCal 9361 ENDON ON Energy#Current&lt;6.473 DO PowerCal 9413 ENDON ON Energy#Current&lt;2.437 DO PowerCal 9576 ENDON</pre>

<ul>
    <li><code>Energy#Current>X.XXX</code>: Schaltet bei steigender Last hoch.</li>
    <li><code>Energy#Current&lt;X.XXX</code>: Schaltet bei sinkender Last (Hysterese) wieder runter.</li>
</ul>

<h3 id="4-3-rule-modus">4.3 Rule-Modus 5 (Once Mode)</h3>
<p>Durch den Befehl <code>Rule1 5</code> wird der "Once Mode" aktiviert. Ein Trigger wird nur ausgeführt, wenn sich der Zustand von "Falsch" auf "Wahr" ändert. Dies verhindert redundante Befehle bei jeder sekündlichen Messung.</p>

<h2 id="5-savedata">5. 🛡️ Dauerbetrieb mit SaveData 0</h2>

<h3 id="5-1-warum-savedata">5.1 Warum SaveData 0? (Flash-Schutz)</h3>
<p>Hardware-Speicher (Flash) hat begrenzte Schreibzyklen. Da die Rule den <b>PowerCal-Wert</b> bei jedem Lastwechsel ändert, würde der Speicher ohne Schutz schnell zerstört werden.</p>
<ul>
    <li><b>AutoCal setzt das Gerät permanent auf <code>SaveData 0</code></b>.</li>
    <li>Änderungen erfolgen nur im <b>RAM (Arbeitsspeicher)</b>. Der Flash bleibt geschützt.</li>
</ul>

<h3 id="5-2-manuelle-aenderungen">5.2 Manuelle Änderungen am Gerät</h3>
<p class="warning">ACHTUNG: Im Modus SaveData 0 gehen manuelle Änderungen (WLAN, Timer, Name) nach einem Neustart verloren!</p>
<ol>
    <li>Befehl: <code>SaveData 1</code> in Konsole eingeben.</li>
    <li>Änderungen durchführen.</li>
    <li><b>WICHTIG:</b> Danach wieder <code>SaveData 0</code> eingeben.</li>
</ol>

<h2 id="6-auswirkungen">6. <span style="color:red">⚡ Auswirkungen auf die Energiemessung (Zählerstände)</span></h2>
<p>Eine Folge des Modus <code>SaveData 0</code> betrifft die Energiezähler der Dose (<code>Total</code>, <code>Today</code>, <code>Yesterday</code>).</p>

<ol>
    <li><b>Speicherort:</b> Tasmota verwaltet Zählerstände im selben Bereich wie Systemeinstellungen.</li>
    <li><b>Verhalten im Betrieb:</b> Wh werden im RAM korrekt weitergezählt und angezeigt.</li>
    <li><b>Verhalten bei Neustart:</b> Ohne das "Einbrennen" in den Flash gehen die seit dem letzten Speichervorgang aufgelaufenen Daten verloren.</li>
    <li><b>Notwendigkeit:</b> Ohne <code>SaveData 0</code> würde jede Rule-Aktion den Flash-Speicher physisch zerstören.</li>
</ol>

<h2 id="7-wichtig">7. <span style="color:red">🛑 WICHTIG: Zusammenfassung & Sicherheit</span></h2>

<ul>
    <li><b>Der Kompromiss:</b> Höchste Präzision der <b>Power-Kalibrierung</b> erfordert den Verzicht auf automatische Dauer-Speicherung von Zählerständen im Gerät.</li>
    <li><b>Datensicherung:</b> Nutzen Sie externe Systeme (Home Assistant, MQTT) für lückenlose Statistiken.</li>
    <li><b>Manuelle Änderungen:</b> Erfordern zwingend das manuelle Umschalten auf <code>SaveData 1</code> und zurück auf <code>0</code>.</li>
    <li><b>Flash-Schutz:</b> Setzen Sie das Gerät <b>niemals</b> auf <code>SaveData 1</code>, solange eine dynamische Rule aktiv ist, die Werte häufig ändert!</li>
</ul>

<h2 id="8-workflow">8. 📝 Workflow und Traceability</h2>
<p>Der gesamte Vorgang wird revisionssicher am Ende des ursprünglichen <code>Protokoll.txt</code> angehängt.</p>

<hr>
<p class="info">Dokumentation erstellt am 03. März 2026 für das Projekt AutoCal.</p>
<p><a href="#top">Top ⬆️</a></p>

</body>
</html>
"""
