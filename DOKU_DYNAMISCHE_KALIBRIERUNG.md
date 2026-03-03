# Dokumentation: Dynamische Power-Kalibrierung (Tasmota Rules)

Dieses Dokument beschreibt die Funktionsweise, die mathematische Logik und die Sicherheitsmechanismen der dynamischen **Power-Kalibrierung** für Tasmota-Geräte.

---

## Inhaltsverzeichnis
1. [Einführung & Zielsetzung](#1-einführung--zielsetzung)
2. [Die Problematik der statischen Power-Kalibrierung](#2-die-problematik-der-statischen-power-kalibrierung)
3. [Funktionsweise der dynamischen Regelung](#3-funktionsweise-der-dynamischen-regelung)
    - 3.1 [Berechnung der Umschaltpunkte (Strom-Schwellen)](#31-berechnung-der-umschaltpunkte-strom-schwellen)
    - 3.2 [Warum Strom (A) als Triggerquelle?](#32-warum-strom-a-als-triggerquelle)
    - 3.3 [Hysterese-Logik (Anti-Flackern)](#33-hysterese-logik-anti-flackern)
4. [Anatomie der Tasmota-Rule (Praxisbeispiel)](#4-anatomie-der-tasmota-rule-praxisbeispiel)
5. [Dauerbetrieb mit SaveData 0](#5-dauerbetrieb-mit-savedata-0)
6. [Auswirkungen auf die Energiemessung (Zählerstände)](#6-auswirkungen-auf-die-energiemessung-zählerstände)
7. [<span style="color:red">WICHTIG: Zusammenfassung & Sicherheit</span>](#7-wichtig-zusammenfassung--sicherheit)
8. [Workflow und Traceability](#8-workflow-und-traceability)

---

## 1. Einführung & Zielsetzung
Die dynamische **Power-Kalibrierung** ist ein Experten-Feature, das die Messgenauigkeit der Wirkleistung (`Power`) über den gesamten Lastbereich hinweg drastisch erhöht, indem der **PowerCal-Wert** in Echtzeit angepasst wird.

## 2. Die Problematik der statischen Power-Kalibrierung
Ein statischer **PowerCal-Wert** ist immer nur ein Kompromiss. Sensoren arbeiten oft nicht linear, was bei sehr kleinen oder sehr hohen Lasten zu Fehlmessungen führt.

## 3. Funktionsweise der dynamischen Regelung
### 3.1 Berechnung der Umschaltpunkte (Strom-Schwellen)
Das System berechnet die Mitte zwischen zwei benachbarten Messpunkten basierend auf dem gemessenen Strom.

### 3.2 Warum Strom (A) als Triggerquelle?
Die Strommessung ist linear und stabil. Da die Leistung (`Power`) durch die Rule ständig korrigiert wird, würde sie als Trigger zu instabilen Zuständen ("Springen") führen.

### 3.3 Hysterese-Logik (Anti-Flackern)
Durch eine Überlappung der Bereiche (Standard 0.15A) wird verhindert, dass das System an den Schwellenwerten zwischen zwei **PowerCal-Faktoren** flackert.

## 4. Anatomie der Tasmota-Rule (Praxisbeispiel)
Ein typischer Befehl im "Once-Mode" (`Rule1 5`) sieht so aus:
`Rule1 ON Energy#Current>0 DO PowerCal 9576 ENDON ON Energy#Current>2.587 DO PowerCal 9413 ENDON ...`

---

## 5. Dauerbetrieb mit SaveData 0
Um den Flash-Speicher der Hardware zu schützen, setzt AutoCal das Gerät permanent auf **`SaveData 0`**. In diesem Modus werden Änderungen nur im **RAM (Arbeitsspeicher)** vorgenommen.

---

## 6. Auswirkungen auf die Energiemessung (Zählerstände)
Eine oft unterschätzte Folge des Modus `SaveData 0` betrifft die internen Energiezähler der Dose (`Total`, `Today`, `Yesterday`).

1.  **Speicherort:** Tasmota verwaltet die kumulierten Verbrauchswerte im selben Speicherbereich wie die Systemeinstellungen.
2.  **Verhalten im Betrieb:** Solange die Dose läuft, werden die Wattstunden (Wh) im RAM ganz normal weitergezählt. Die Anzeige in der Weboberfläche ist korrekt.
3.  **Verhalten bei Neustart/Stromausfall:** Da `SaveData 0` das automatische "Einbrennen" der Werte in den Flash-Speicher verhindert, gehen alle seit dem letzten Speichervorgang aufgelaufenen Energiedaten bei einem Reboot verloren. Das Gerät springt auf den Stand zurück, der zuletzt bei `SaveData 1` gesichert wurde.
4.  **Notwendigkeit für Rules:** Ohne diesen Modus würde jede durch die Rule ausgelöste Änderung am **PowerCal-Wert** einen Schreibzyklus im Flash verursachen. Bei häufigen Lastwechseln wäre der Speicher (ca. 100.000 Zyklen) innerhalb kürzester Zeit physisch zerstört.

---

## 7. <span style="color:red">WICHTIG: Zusammenfassung & Sicherheit</span>

*   **Der Kompromiss:** Die dynamische **Power-Kalibrierung** bietet höchste Präzision, erfordert aber den Verzicht auf die automatische Dauer-Speicherung von Zählerständen im Gerät.
*   **Datensicherung:** Für eine lückenlose Verbrauchsstatistik sollten die Daten über externe Systeme (z.B. Home Assistant, MQTT-Broker) geloggt werden.
*   **Manuelle Änderungen:** Jede manuelle Änderung (WLAN, Timer, Name) erfordert ein temporäres `SaveData 1`, gefolgt von einem anschließenden `SaveData 0`, um den RAM-Inhalt fest in den Flash zu übernehmen.
*   **Flash-Schutz:** Setzen Sie das Gerät **niemals** auf `SaveData 1`, während eine dynamische Rule aktiv ist, die den **PowerCal-Wert** häufig ändert!

---

## 8. Workflow und Traceability
Der Prozess wird lückenlos dokumentiert und am Ende jedes Messprotokolls vermerkt, um eine vollständige Revisionssicherheit der **Power-Kalibrierung** zu gewährleisten.

---
*Dokumentation erstellt am 03. März 2026 für das Projekt AutoCal.*
