# -*- coding: utf-8 -*-
"""
# English: Contains the instructional text for the manual calibration info dialog as a secure asset.
# Deutsch: Enthält den Anleitungstext für den Info-Dialog der manuellen Kalibrierung als sicheres Asset.
"""

MANUAL_INFO_HTML = """
<h3>🎛️ Anleitung: Manuelle Messwerterfassung</h3>
<p>
Um eine exakte Kalibrierung zu gewährleisten, müssen die Werte der Dose und des Referenz-Messgeräts zeitgleich erfasst werden. Da sich Werte im Bruchteil einer Sekunde ändern, nutzen wir für Präzision die <b>Foto-Methode</b>.
</p>

<h4>Schritt-für-Schritt Durchführung:</h4>
<ol>
    <li><b>Das erste Messwert-Foto erstellen:</b><br>
        Da ein manuelles Ablesen nie 100% synchron ist, erstelle ein Foto, auf dem das Tasmota-Webinterface und das Display des Referenz-Messgeräts gleichzeitig scharf zu sehen sind.
        <br><em>Tipp: Das Foto "friert" den Moment ein und garantiert synchrone Messdaten.</em>
    </li>
    <li><b>Fünf Sekunden warten:</b><br>
        Warte nach dem ersten Foto exakt 5 Sekunden. Dies erlaubt dem System, natürliche Schwankungen für eine präzisere Durchschnittsberechnung abzubilden.
    </li>
    <li><b>Messreihe vervollständigen:</b><br>
        Wiederhole den Vorgang, bis du insgesamt <b>drei Fotos</b> im Abstand von je 5 Sekunden gemacht hast. Drei unabhängige Messpunkte sind für eine verlässliche Genauigkeit notwendig.
    </li>
    <li><b>Werte in die Applikation eintragen:</b><br>
        Übertrage die "eingefrorenen" Werte aus den Fotos in die Applikation.
        <ul>
            <li><b>Pflichtfelder:</b> Die drei <b>Leistungswerte (Watt)</b> der Dose und der Referenz sind zwingend erforderlich. Spannung (V) und Strom (A) sind optional, erhöhen aber die Genauigkeit.</li>
            <li><b>Format:</b> Gib alle Werte mit einem Punkt als Trennzeichen ein. Beachte die Formatvorgabe (2 oder 3 Nachkommastellen), die im Tooltip des jeweiligen Feldes angezeigt wird.</li>
        </ul>
    </li>
    <li><b>Kalibrierung berechnen und senden:</b><br>
        <b>Wichtig:</b> Die Ermittlung der Kalibrierdaten für eine Mess-Art (z.B. Spannung) erfolgt nur dann, wenn eine komplette Messreihe eingegeben wurde. Das bedeutet, dass beispielsweise für die Spannung alle drei Referenzwerte sowie alle drei dazugehörigen Werte des Prüflings lückenlos erfasst sein müssen.<br><br>
        Sobald eine Messreihe vollständig ist, berechnet die Applikation automatisch den optimalen CAL-Wert. Im Anschluss kannst du diese korrigierten Kalibrierungswerte mit einem Klick direkt an die Tasmota-Dose senden.
    </li>
</ol>
"""
