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
    - 4.1 [Beispiel-Tabelle (Programmansicht)](#41-beispiel-tabelle-programmansicht)
    - 4.2 [Der generierte Rule-String](#42-der-generierte-rule-string)
    - 4.3 [Rule-Modus 5 (Once Mode)](#43-rule-modus-5-once-mode)
5. [WICHTIG: Dauerbetrieb mit SaveData 0](#5-wichtig-dauerbetrieb-mit-savedata-0)
    - 5.1 [Warum SaveData 0? (Flash-Schutz)](#51-warum-savedata-0-flash-schutz)
    - 5.2 [Manuelle Änderungen am Gerät](#52-manuelle-änderungen-am-gerät)
6. [Workflow und Traceability](#6-workflow-und-traceability)

---

## 1. Einführung & Zielsetzung
Die dynamische **Power-Kalibrierung** ist ein Experten-Feature, das die Messgenauigkeit der Wirkleistung (`Power`) von Tasmota-basierten Energiemessgeräten über den gesamten Lastbereich hinweg drastisch erhöht. Anstatt einen einzigen, festen Kalibrierwert (`PowerCal`) zu verwenden, nutzt dieses System die internen Rules von Tasmota, um den **PowerCal-Wert** in Echtzeit an die aktuelle Last anzupassen.

## 2. Die Problematik der statischen Power-Kalibrierung
Die meisten Sensoren zur Leistungsmessung arbeiten nicht über den gesamten Messbereich (0A bis 10A) linear. Ein Gerät, das bei hoher Last (z. B. 2000W) perfekt **Power-kalibriert** ist, weist bei geringen Lasten (z. B. 10W) oft signifikante Abweichungen auf.
*   **Problem:** Ein statischer **PowerCal-Wert** ist immer nur ein Kompromiss für einen schmalen Lastbereich.
*   **Folge:** Ungenauigkeiten bei extrem hohen oder extrem niedrigen Lasten.

## 3. Funktionsweise der dynamischen Regelung
Das AutoCal-System nutzt die Ergebnisse aus einem vorangegangenen Multi-Stufen-Kalibrierlauf, um für jeden Bereich den optimalen **PowerCal-Korrekturfaktor** zu ermitteln.

### 3.1 Berechnung der Umschaltpunkte (Strom-Schwellen)
Um fließende Übergänge zwischen den Messstufen zu schaffen, berechnet das System die Mitte zwischen zwei benachbarten Messpunkten basierend auf dem gemessenen Strom.
*   **Beispiel:** 
    - Stufe 1 gemessen bei **1.0A**
    - Stufe 2 gemessen bei **4.0A**
    - **Umschaltpunkt:** (1.0 + 4.0) / 2 = **2.5A**

### 3.2 Warum Strom (A) als Triggerquelle?
Die Umschaltung der **Power-Kalibrierung** erfolgt ausschließlich auf Basis der **Strommesswerte (Energy#Current)**.
*   **Der Grund:** Die Strommessung arbeitet bei den meisten Sensoren über den gesamten Bereich hinweg sehr linear. 
*   **Die Logik:** Da der **PowerCal-Wert** (Leistung) durch die Rule ständig geändert wird, wäre die Leistung selbst als Trigger ungeeignet (Springen der Werte). Der Stromwert hingegen liefert eine stabile Basis zur Auswahl des passenden **PowerCal-Wertes**.

### 3.3 Hysterese-Logik (Anti-Flackern)
Damit das System bei einer Last, die genau auf dem Umschaltpunkt liegt, nicht ständig zwischen den **PowerCal-Werten** hin- und her-springt, wird eine **Hysterese** (Standard: 0.15A) angewendet.
*   **Hochschalten:** Erfolgt exakt am Strom-Umschaltpunkt (z. B. 2.50A).
*   **Runterschalten:** Erfolgt erst, wenn der Strom den Umschaltpunkt minus der Hysterese unterschreitet (z. B. 2.50A - 0.15A = 2.35A).

## 4. Anatomie der Tasmota-Rule (Praxisbeispiel)

### 4.1 Beispiel-Tabelle (Programmansicht)
Angenommen, es wurden drei Messstufen durchgeführt (Hysterese 0.15A):

| Strom (A) [Referenz] | PowerCal [Vorschlag] | Bereich (A) [Gültigkeit] |
| :--- | :--- | :--- |
| 0.894 A | **9576** | 0.000 - 2.587 A |
| 4.280 A | **9413** | 2.437 - 6.623 A |
| 8.966 A | **9361** | 6.473 - 10.000 A |

*   **Schwelle 1 (2.587A):** Mitte zwischen 0.894A und 4.280A.
*   **Schwelle 2 (6.623A):** Mitte zwischen 4.280A und 8.966A.
*   **Hysterese-Abzug:** Die Bereiche überlappen sich (z.B. 2.437A ist 2.587A - 0.15A).

### 4.2 Der generierte Rule-String
Der aus dieser Tabelle resultierende Befehl für Tasmota lautet:

`Rule1 ON Energy#Current>0 DO PowerCal 9576 ENDON ON Energy#Current>2.587 DO PowerCal 9413 ENDON ON Energy#Current>6.623 DO PowerCal 9361 ENDON ON Energy#Current<6.473 DO PowerCal 9413 ENDON ON Energy#Current<2.437 DO PowerCal 9576 ENDON`

*   **Teil 1:** `Energy#Current>0` -> Setzt den Basis-PowerCal für kleine Lasten.
*   **Teil 2:** `Energy#Current>2.587` -> Schaltet bei steigender Last hoch.
*   **Teil 3:** `Energy#Current<2.437` -> Schaltet bei sinkender Last (Hysterese) wieder runter.

### 4.3 Rule-Modus 5 (Once Mode)
Durch den Befehl `Rule1 5` wird die Rule im "Once Mode" aktiviert. Ein Trigger wird nur ausgeführt, wenn sich der Zustand von "Falsch" auf "Wahr" ändert. Dies schont die CPU der Dose und verhindert Log-Spam.

## 5. WICHTIG: Dauerbetrieb mit SaveData 0

### 5.1 Warum SaveData 0? (Flash-Schutz)
Tasmota-Geräte speichern Konfigurationsänderungen normalerweise sofort im Flash-Speicher. Dieser verträgt nur eine begrenzte Anzahl an Schreibzyklen. Da die Rule den **PowerCal-Wert** bei jedem Lastwechsel ändert, würde der Speicher ohne Schutz schnell zerstört werden.
*   **AutoCal setzt das Gerät daher auf `SaveData 0`**.
*   In diesem Modus werden Änderungen nur im **RAM (Arbeitsspeicher)** vorgenommen. Der Flash-Speicher bleibt geschützt.

### 5.2 Manuelle Änderungen am Gerät
**ACHTUNG:** Wenn das Gerät im Modus `SaveData 0` läuft, werden alle manuellen Änderungen (z. B. WLAN-Einstellungen, Friendly Name, Timer), die über das Webinterface oder die Konsole gemacht werden, **nach einem Neustart verloren gehen!**

**Vorgehensweise für manuelle Änderungen:**
1.  Konsole öffnen.
2.  Befehl: `SaveData 1` eingeben.
3.  Gewünschte Änderungen durchführen (Web-UI oder Konsole).
4.  **WICHTIG:** Danach wieder `SaveData 0` eingeben, um den Flash-Schutz für die dynamische Power-Kalibrierung wiederherzustellen.

## 6. Workflow und Traceability
1.  **Online-Check:** Prüfung auf bestehende Rules und Sicherung der MAC.
2.  **Report-Matching:** Automatisches Laden der **PowerCal-Werte** aus dem neuesten Report.
3.  **Berechnung:** Generierung der Rule basierend auf echten Strom-Messwerten.
4.  **Übertragung:** Aktivierung (Modus 5) und Setzen des Flash-Schutzes (`SaveData 0`).
5.  **Dokumentation:** Vermerk der Anpassung am Ende des ursprünglichen Protokolls.

---
*Dokumentation erstellt am 03. März 2026 für das Projekt AutoCal.*
