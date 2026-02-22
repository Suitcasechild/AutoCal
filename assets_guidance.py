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
    .index a {{ text-decoration: none; color: #4a9eff; font-weight: bold; }}
    .warning {{ background-color: #3d1a1d; border-left: 5px solid #dc3545; padding: 12px; margin: 15px 0; }}
    .tip {{ background-color: #1b3a22; border-left: 5px solid #28a745; padding: 12px; margin: 15px 0; }}
    .footer {{ margin-top: 60px; text-align: center; color: #777; border-top: 1px solid #444; padding-top: 25px; }}
</style>
</head>
<body>
<h1>📘 {_("Bedienungsanleitung: Tasmota Precision Calibrator")}</h1>
<p>{_("Willkommen beim Tasmota Precision Calibrator. Dieses Werkzeug wurde entwickelt, um die Kalibrierung von Tasmota-Energiemessgeräten auf ein professionelles Niveau zu heben.")}</p>

<div class="index">
    <h2>📌 {_("Inhaltsverzeichnis")}</h2>
    <ul>
        <li><a href="#ch1">🔬 {_("1. Technischer Hintergrund")}</a></li>
        <li><a href="#ch2">🔌 {_("2. Hardware & Messaufbau")}</a></li>
        <li><a href="#ch5">🚀 {_("5. Der Kalibrierungsprozess")}</a></li>
    </ul>
</div>

<h2 id="ch1">🔬 {_("1. Technischer Hintergrund: Warum \"Cal\"-Befehle?")}</h2>
<p>{_("Dieses Programm nutzt ausschließlich die Cal-Befehle, um Messunsicherheiten durch zeitlichen Verzug zu minimieren.")}</p>

<h2 id="ch2">🔌 {_("2. Hardware-Vorbereitung & Messaufbau")}</h2>
<div class="warning">⚠️ <b>{_("Wichtig:")}</b> {_("Achte auf kurze Leitungen zwischen Prüfling und Messgerät.")}</div>

<h2 id="ch5">🚀 {_("5. Der Kalibrierungsprozess (Schritt für Schritt)")}</h2>
<p>{_("Geben Sie die IP ein, führen Sie den Online-Check durch und folgen Sie den Anweisungen im Log-Fenster.")}</p>

<div class="footer">
    <a href="#top" style="color: #4a9eff;">🏠 {_("Zurück zum Index")}</a>
</div>
</body>
</html>
"""
