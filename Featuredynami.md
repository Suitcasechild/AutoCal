# Feature-Erweiterung: Periodische Energiedatensicherung (Auto-Save)

Dieses Dokument beschreibt die geplante Erweiterung der dynamischen Power-Kalibrierung, um Zählerverluste bei Stromausfällen zu minimieren, während der Flash-Schutz für `PowerCal`-Änderungen aktiv bleibt.

---

## 1. Erkenntnis & Logik
Tasmota speichert bei jedem Wechsel von `SaveData` (z. B. von 0 auf 1) sofort den gesamten Konfigurationsblock (Settings) in den Flash-Speicher. Da die kumulierten Energiewerte (`Total`) Teil dieses Blocks sind, werden sie bei diesem Vorgang automatisch mit gesichert.

## 2. Technische Umsetzung (Rule-Konzept)
Da `Rule1` bereits für die dynamische Power-Kalibrierung belegt ist, wird für dieses Feature **`Rule2`** verwendet.

### Der geplante Rule-String:
```text
Rule2 
  ON System#Boot DO RuleTimer1 300 ENDON 
  ON Rules#Timer=1 DO Backlog SaveData 1; Delay 10; SaveData 0; RuleTimer1 300 ENDON
```

### Funktionsweise:
1.  **System#Boot:** Nach dem Start der Dose wird ein interner Timer auf 300 Sekunden (5 Minuten) gesetzt.
2.  **Rules#Timer=1:** Sobald der Timer abläuft, wird eine Befehlskette (`Backlog`) ausgeführt:
    - `SaveData 1`: Triggert das sofortige Speichern aller RAM-Daten (inkl. Wh-Zähler) in den Flash.
    - `Delay 10`: Wartet 1 Sekunde, um dem Flash-Schreibzyklus Zeit zu geben.
    - `SaveData 0`: Aktiviert sofort wieder den Schutz für die dynamische Kalibrierung.
    - `RuleTimer1 300`: Startet den 5-Minuten-Zyklus erneut.

## 3. Sicherheitsaspekt (Risiko-Minimierung)
Durch die Verwendung von `Delay 10` (1 Sekunde) wird das Zeitfenster, in dem `SaveData` auf `1` steht, auf ein Minimum reduziert. Die Wahrscheinlichkeit, dass genau in dieser einen Sekunde die `Rule1` einen Lastwechsel erkennt und einen `PowerCal`-Wert fest in den Flash schreibt, ist mathematisch extrem gering. Selbst wenn dies passiert, ist ein einzelner Schreibvorgang alle 5 Minuten für die Lebensdauer des Flash-Speichers absolut unbedenklich.

## 4. Integration in AutoCal
In einer zukünftigen Version soll der `DynamicCalDialog` eine Option erhalten:
- **[x] Energiedaten alle 5 Min. sichern (Auto-Save Rule2)**
Beim Senden der Kalibrierung wird dann zusätzlich die `Rule2` generiert und auf dem Gerät aktiviert (`Rule2 1`).

---
*Konzept erstellt am 03. März 2026.*
