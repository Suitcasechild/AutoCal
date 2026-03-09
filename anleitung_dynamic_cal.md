# 🚀 Dokumentation: Dynamische Power-Kalibrierung (Tasmota Rules)

Dieses Dokument beschreibt die Funktionsweise, die mathematische Logik und die Sicherheitsmechanismen der dynamischen **Power-Kalibrierung** für Tasmota-Geräte.

---

## 📋 Inhaltsverzeichnis
1. [Einführung & Zielsetzung](#1-einführung--zielsetzung)
2. [Die Problematik der statischen Power-Kalibrierung](#2-die-problematik-der-statischen-power-kalibrierung)
3. [Funktionsweise der dynamischen Regelung](#3-funktionsweise-der-dynamischen-regelung)
    - 3.1 [Berechnung der Umschaltpunkte (Strom-Schwellen)](#31-berechnung-der-umschaltpunkte-strom-schwellen)
    - 3.2 [Warum Strom (A) als Triggerquelle?](#32-warum-strom-a-als-triggerquelle)
    - 3.3 [Hysterese-Logik (Anti-Flackern)](#33-hysterese-logik-anti-flackern)
4. [Anatomie der Tasmota-Rule (Praxisbeispiel)](#4-anatomie-der-tasmota-rule-praxisbeispiel)
    - 4.1 [Beispiel-Tabelle (Programmansicht)](#41-beispiel-tabelle-programmansicht)
    - 4.2 [Der generierte Rule-String](#42-der-generierte-rule-string)
    - 4.3 [Rule-Modus 5 (Once Mode)](#43-rule-modus-5-once-mode)
5. [Dauerbetrieb mit SaveData 0](#5-dauerbetrieb-mit-savedata-0)
    - 5.1 [Warum SaveData 0? (Flash-Schutz)](#51-warum-savedata-0-flash-schutz)
    - 5.2 [Manuelle Änderungen am Gerät](#52-manuelle-änderungen-am-gerät)
6. [Auswirkungen auf die Energiemessung (Zählerstände)](#6-auswirkungen-auf-die-energiemessung-zählerstände)
7. [WICHTIG: Zusammenfassung & Sicherheit](#7-wichtig-zusammenfassung--sicherheit)
8. [Workflow und Traceability](#8-workflow-und-traceability)

---

## 1. 💡 Einführung & Zielsetzung
Die dynamische **Power-Kalibrierung** ist ein Experten-Feature, das die Messgenauigkeit der Wirkleistung (`Power`) über den gesamten Lastbereich hinweg drastisch erhöht. Anstatt einen einzigen, festen Kalibrierwert (`PowerCal`) zu verwenden, nutzt dieses System die internen Rules von Tasmota, um den **PowerCal-Wert** in Echtzeit an den fließenden Strom anzupassen.

## 2. ⚠️ Die Problematik der statischen Power-Kalibrierung
Sensoren zur Leistungsmessung arbeiten oft nicht linear. Ein Gerät, das bei hoher Last (z. B. 2000W) perfekt **Power-kalibriert** ist, weist bei geringen Lasten oft signifikante Abweichungen auf. Ein statischer Wert ist daher immer nur ein Kompromiss.

## 3. ⚙️ Funktionsweise der dynamischen Regelung

### 3.1 Berechnung der Umschaltpunkte (Strom-Schwellen)
Um fließende Übergänge zwischen den Messstufen zu schaffen, berechnet das System die Mitte zwischen zwei benachbarten Messpunkten.
*   **Beispiel:** 
    - Stufe 1 gemessen bei **1.0A**
    - Stufe 2 gemessen bei **4.0A**
    - **Umschaltpunkt:** (1.0 + 4.0) / 2 = **2.5A**

### 3.2 Warum Strom (A) als Triggerquelle?
Die Umschaltung der **Power-Kalibrierung** erfolgt ausschließlich auf Basis der **Strommesswerte (Energy#Current)**.
*   **Stabilität:** Der Stromwert ist bei den meisten Sensoren über den gesamten Bereich linear und unabhängig von der gerade durchgeführten Leistungskorrektur.
*   **Kein Zirkelbezug:** Da wir die Leistung (`Power`) gerade erst korrigieren, würde sie als Trigger zu instabilen Zuständen führen.

### 3.3 Hysterese-Logik (Anti-Flackern)
Damit das System an einem Umschaltpunkt nicht ständig zwischen den Werten springt, wird eine **Hysterese** (Standard: 0.15A) angewendet.
*   **Hochschalten:** Erfolgt exakt am Strom-Umschaltpunkt (z. B. 2.50A).
*   **Runterschalten:** Erfolgt erst, wenn der Strom den Umschaltpunkt minus der Hysterese unterschreitet (z. B. 2.50A - 0.15A = 2.35A).

## 4. 🔍 Anatomie der Tasmota-Rule (Praxisbeispiel)

### 4.1 Beispiel-Tabelle (Programmansicht)
Angenommen, es wurden drei Messstufen durchgeführt (Hysterese 0.15A):

| Strom (A) [Referenz] | PowerCal [Vorschlag] | Bereich (A) [Gültigkeit] |
| :--- | :--- | :--- |
| 0.894 A | **9576** | 0.000 - 2.587 A |
| 4.280 A | **9413** | 2.437 - 6.623 A |
| 8.966 A | **9361** | 6.473 - 10.000 A |

*   **Schwelle 1 (2.587A):** Mitte zwischen 0.894A und 4.280A.
*   **Schwelle 2 (6.623A):** Mitte zwischen 4.280A und 8.966A.

### 4.2 Der generierte Rule-String
Der resultierende Befehl für Tasmota lautet:

`Rule1 ON Energy#Current>0 DO PowerCal 9576 ENDON ON Energy#Current>2.587 DO PowerCal 9413 ENDON ON Energy#Current>6.623 DO PowerCal 9361 ENDON ON Energy#Current<6.473 DO PowerCal 9413 ENDON ON Energy#Current<2.437 DO PowerCal 9576 ENDON`

*   `Energy#Current>X.XXX`: Schaltet bei steigender Last hoch.
*   `Energy#Current<X.XXX`: Schaltet bei sinkender Last (Hysterese) wieder runter.

### 4.3 Rule-Modus 5 (Once Mode)
Durch den Befehl `Rule1 5` wird der "Once Mode" aktiviert. Ein Trigger wird nur ausgeführt, wenn sich der Zustand von "Falsch" auf "Wahr" ändert. Dies verhindert redundante Befehle bei jeder sekündlichen Messung.

## 5. 🛡️ Dauerbetrieb mit SaveData 0

### 5.1 Warum SaveData 0? (Flash-Schutz)
Hardware-Speicher (Flash) hat begrenzte Schreibzyklen. Da die Rule den **PowerCal-Wert** bei jedem Lastwechsel ändert, würde der Speicher ohne Schutz schnell zerstört werden.
*   **AutoCal setzt das Gerät permanent auf `SaveData 0`**.
*   Änderungen erfolgen nur im **RAM (Arbeitsspeicher)**. Der Flash bleibt geschützt.

### 5.2 Manuelle Änderungen am Gerät
**ACHTUNG:** Im Modus `SaveData 0` gehen manuelle Änderungen (WLAN, Timer, Name) nach einem Neustart verloren!
1.  Befehl: `SaveData 1` in Konsole eingeben.
2.  Änderungen durchführen.
3.  **WICHTIG:** Danach wieder `SaveData 0` eingeben.

## 6. <span style="color:red">⚡ Auswirkungen auf die Energiemessung (Zählerstände)</span>
Eine Folge des Modus `SaveData 0` betrifft die Energiezähler der Dose (`Total`, `Today`, `Yesterday`).

1.  **Speicherort:** Tasmota verwaltet Zählerstände im selben Bereich wie Systemeinstellungen.
2.  **Verhalten im Betrieb:** Wh werden im RAM korrekt weitergezählt und angezeigt.
3.  **Verhalten bei Neustart:** Ohne das "Einbrennen" in den Flash gehen die seit dem letzten Speichervorgang aufgelaufenen Daten verloren.
4.  **Notwendigkeit:** Ohne `SaveData 0` würde jede Rule-Aktion den Flash-Speicher physisch zerstören.

## 7. <span style="color:red">🛑 WICHTIG: Zusammenfassung & Sicherheit</span>

*   **Der Kompromiss:** Höchste Präzision der **Power-Kalibrierung** erfordert den Verzicht auf automatische Dauer-Speicherung von Zählerständen im Gerät.
*   **Datensicherung:** Nutzen Sie externe Systeme (Home Assistant, MQTT) für lückenlose Statistiken.
*   **Manuelle Änderungen:** Erfordern zwingend das manuelle Umschalten auf `SaveData 1` und zurück auf `0`.
*   **Flash-Schutz:** Setzen Sie das Gerät **niemals** auf `SaveData 1`, solange eine dynamische Rule aktiv ist, die Werte häufig ändert!

## 8. 📝 Workflow und Traceability
Der gesamte Vorgang wird revisionssicher am Ende des ursprünglichen `Protokoll.txt` angehängt.

---
*Dokumentation erstellt am 03. März 2026 für das Projekt AutoCal.*
