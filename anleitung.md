# 📘 Bedienungsanleitung: Tasmota Precision Calibrator

Willkommen beim **Tasmota Precision Calibrator**. Dieses Werkzeug wurde entwickelt, um die Kalibrierung von Tasmota-Energiemessgeräten auf ein professionelles Niveau zu heben.

---

<a name="index"></a>
## 📌 Inhaltsverzeichnis
*   [🔬 1. Technischer Hintergrund: Warum "Cal"-Befehle?](#ch1)
    *   [1.1 Der Vorteil gegenüber Set-Befehlen](#ch1_1)
    *   [1.2 Messunsicherheit und zeitlicher Ablauf](#ch1_2)
*   [🔌 2. Hardware-Vorbereitung & Messaufbau](#ch2)
    *   [2.1 Der physikalische Messaufbau (WICHTIG!)](#ch2_1)
    *   [2.2 Fluke 45 Einstellungen](#ch2_2)
*   [🖥️ 3. Menü-Referenz & Funktionen](#ch3)
    *   [3.1 Menü: Datei](#ch3_1)
    *   [3.2 Menü: Setup](#ch3_2)
    *   [3.3 Menü: Hilfe](#ch3_3)
*   [📂 4. Das Report-Verzeichnis & Messdaten](#ch4)
    *   [4.1 Ordnerstruktur (MAC-basiert)](#ch4_1)
    *   [4.2 Dateitypen und Inhalte](#ch4_2)
    *   [4.3 Verwendung vorhandener Messdaten](#ch4_3)
*   [🚀 5. Der Kalibrierungsprozess (Schritt für Schritt)](#ch5)
    *   [5.1 🛠️ Vorbereitung & Initialisierung](#ch5_1)
    *   [5.2 ▶️ Start der Messsequenz](#ch5_2)
    *   [5.3 🔄 Ermittlung des Eigenverbrauchs](#ch5_3)
    *   [5.4 📉 Messung unter Last](#ch5_4)
    *   [5.5 ✅ Analyse und Finalisierung](#ch5_5)
*   [🛠️ 6. Troubleshooting & Expertentipps](#ch6)

---

<a name="ch1"></a>
## 🔬 1. Technischer Hintergrund: Warum "Cal"-Befehle?

In Tasmota gibt es zwei Wege zur Kalibrierung: Die `Set`-Befehle (z.B. `VoltSet`) und die `Cal`-Befehle (z.B. `VoltageCal`). Dieses Programm nutzt ausschließlich die `Cal`-Befehle.

<a name="ch1_1"></a>
### 1.1 Der Vorteil gegenüber Set-Befehlen
Bei der herkömmlichen Methode mit `Set`-Befehlen muss der Benutzer einen Wert ablesen und manuell eingeben. In dieser Zeitspanne kann sich die Netzspannung oder die Last bereits leicht verändert haben, was zu einer ungenauen Kalibrierung führt.

<a name="ch1_2"></a>
### 1.2 Messunsicherheit und zeitlicher Ablauf
*   **⚖️ Statistische Sicherheit:** Die Software erfasst viele Datenpunkte (z.B. 30 Messungen) gleichzeitig von der Referenz und dem Prüfling. 
*   **📈 Regression:** Statt einer einfachen Punkt-Kalibrierung wird eine lineare Regression durchgeführt. Dies gleicht Schwankungen im Stromnetz mathematisch aus und minimiert die Messunsicherheit drastisch.
*   **⏱️ Zeitvorteil:** Da die Software die Werte automatisiert abfragt, entfällt das Fehlerrisiko durch menschliche Ablese- oder Tippfehler.

---

<a name="ch2"></a>
## 🔌 2. Hardware-Vorbereitung & Messaufbau

<a name="ch2_1"></a>
### 2.1 Der physikalische Messaufbau (WICHTIG!)
Der korrekte Aufbau unterscheidet sich je nachdem, welches Referenzgerät Sie verwenden.

#### **A) Aufbau mit Tasmota-Referenzdose (HOME-Modus)**
In diesem Modus misst die Referenzdose den Eigenverbrauch des Prüflings mit, der später automatisch abgezogen wird.
1.  **🏠 Wandsteckdose:** Stromquelle.
2.  **📏 Referenz-Dose:** Ihre bereits kalibrierte Tasmota-Dose.
3.  **🔌 Prüfling (DUT):** Die neu zu kalibrierende Tasmota-Dose.
4.  **💡 Last:** Ein stabiler Verbraucher (z.B. Glühbirne).

#### **B) Aufbau mit Fluke 45 (PRO-Modus)**
Hier wird das Fluke mit einem Messadapter direkt hinter den Prüfling geschaltet, um dessen Ausgangswerte präzise zu erfassen.
1.  **🏠 Wandsteckdose:** Stromquelle.
2.  **🔌 Prüfling (DUT):** Die zu kalibrierende Tasmota-Dose.
3.  **📏 Fluke 45:** Anschluss über Messadapter (zwischen Prüfling und Last).
4.  **💡 Last:** Ein stabiler Verbraucher (z.B. Glühbirne).

⚠️ **Wichtiger Hinweis:** Achte in beiden Fällen auf möglichst **kurze Verbindungsleitungen** zwischen dem Prüfling (DUT) und dem Messgerät/Adapter, um Messfehler durch Leitungsverluste zu minimieren.

💡 **Tipp:** Verwende keine Schaltnetzteile oder Motoren als Last, da diese instabile Werte liefern. Eine ohmsche Last (Glühfaden) ist ideal.

<a name="ch2_2"></a>
### 2.2 Fluke 45 Einstellungen
*   Verbinde das Gerät via RS232 mit dem PC.
*   Stelle sicher, dass die Baudrate im Gerät (Standard: 9600) mit der Software übereinstimmt.
*   Das Programm setzt das Gerät automatisch in den Dual-Display-Modus (`VAC` und `AAC`).

---

<a name="ch3"></a>
## 🖥️ 3. Menü-Referenz & Funktionen

<a name="ch3_1"></a>
### 3.1 📁 Menü: Datei
*   **💾 Log Speichern:** Sichert den kompletten Textverlauf des Log-Fensters in einer `.txt` Datei zur späteren Fehleranalyse.
*   **📂 Report-Ordner öffnen:** Öffnet den Windows-Explorer direkt im Stammverzeichnis Ihrer Messberichte.
*   **❌ Beenden:** Schließt das Programm. Laufende Messungen werden dabei abgebrochen.

<a name="ch3_2"></a>
### 3.2 ⚙️ Menü: Setup
*   **🌐 Allgemein:** Hier definieren Sie das Hauptverzeichnis für alle Berichte (`Reports`).
*   **📟 Fluke 45:** Öffnet das Setup für die serielle Schnittstelle. Nutzen Sie hier den Button **"Fluke finden"**, um automatisch den richtigen COM-Port und die Baudrate zu ermitteln.
*   **🔌 Tasmota-Referenz:** Falls Sie kein Fluke nutzen, geben Sie hier die IP-Adresse Ihrer bereits kalibrierten Referenzdose ein.

<a name="ch3_3"></a>
### 3.3 ❓ Menü: Hilfe
*   **📘 Anleitung:** Öffnet dieses Dokument. Das Fenster ist nicht-modal, Sie können also parallel in der GUI arbeiten.
*   **ℹ️ Lizenz & Info:** Zeigt die aktuelle Softwareversion (z.B. v5.3.0) und Informationen zum Entwickler.

---

<a name="ch4"></a>
## 📂 4. Das Report-Verzeichnis & Messdaten

<a name="ch4_1"></a>
### 4.1 Ordnerstruktur (MAC-basiert)
Um Verwechslungen auszuschließen, erstellt die Software für jede Tasmota-Dose einen eigenen Unterordner, der nach der eindeutigen **MAC-Adresse** benannt ist (z.B. `Reports/2C-BC-BB.../`).

<a name="ch4_2"></a>
### 4.2 Dateitypen und Inhalte
In jedem Geräteordner finden Sie:
*   **📊 CSV-Dateien (`..._Stufe_1.csv`):** Tabellarische Messwerte jeder einzelnen Sekunde. Ideal für eine eigene Auswertung in Excel.
*   **📄 Protokolle (`..._Protokoll.txt`):** Der zusammenfassende Bericht. Er enthält die berechneten Faktoren und dokumentiert den "As-Found" (Vorher) und "As-Left" (Nachher) Zustand.

<a name="ch4_3"></a>
### 4.3 Verwendung vorhandener Messdaten
Wenn Sie eine Kalibrierung für ein Gerät starten, für das bereits Daten existieren, fragt die Software, ob Sie diese nutzen möchten. Dies spart Zeit, wenn Sie nur einen neuen Report generieren oder die Werte erneut anwenden möchten, ohne die Hardware erneut aufzubauen.

---

<a name="ch5"></a>
## 🚀 5. Der Kalibrierungsprozess (Schritt für Schritt)

Dieser Abschnitt dient als exakte Handlungsanweisung für den Operator. Bitte folgen Sie den Schritten in der angegebenen Reihenfolge.

<a name="ch5_1"></a>
### 5.1 🛠️ Vorbereitung & Initialisierung
1.  **⌨️ Aktion:** Geben Sie die **IP-Adresse des Prüflings (DUT)** im Hauptfenster ein.
2.  **🌐 Aktion:** Klicken Sie auf **"Online Check"**.
    *   *Hintergrund:* Die Software prüft die Erreichbarkeit, liest die MAC-Adresse aus und erstellt automatisch das passende Unterverzeichnis im Reports-Ordner. Die Geräte-Infos (Version, Name, MAC) werden im rechten Panel eingeblendet.
    *   *Hinweis zu Zugangsdaten:* Falls das Gerät passwortgeschützt ist, erscheint hier die Abfrage. Die Daten werden für die gesamte Sitzung gespeichert und müssen beim Start der Kalibrierung nicht erneut eingegeben werden.
3.  **🖱️ Aktion:** Wählen Sie die **Referenz-Quelle** (Fluke 45 oder Tasmota-Referenz).
    *   *Hintergrund:* Hiermit wird festgelegt, über welchen Kommunikationsweg (RS232 oder HTTP) die Vergleichswerte bezogen werden.
4.  **⚙️ Aktion:** Stellen Sie die **Messparameter** ein (Stufen & Messungen pro Stufe).
    *   *Empfehlung:* 1 Stufe mit 30 Messungen bietet ein exzellentes Verhältnis zwischen Zeitaufwand und Präzision.

<a name="ch5_2"></a>
### 5.2 ▶️ Start der Messsequenz
1.  **🖱️ Aktion:** Klicken Sie auf den Button **"Kalibrierung Starten"**.
    *   *Hintergrund:* Die Software sperrt nun alle Eingabefelder im Hauptmenü, um Fehlkonfigurationen während der Messung zu verhindern. Falls das Gerät passwortgeschützt ist, erscheint jetzt automatisch die Passwortabfrage.

<a name="ch5_3"></a>
### 5.3 🔄 Ermittlung des Eigenverbrauchs (Offset-Messung) — [Nur Tasmota-Referenz]
*Hinweis: Dieser Schritt wird beim Fluke 45 automatisch übersprungen.*
1.  **🔌 Aktion:** Warten Sie auf die automatische Abschaltung des Prüflings.
    *   *Hintergrund:* Wenn Sie eine **Tasmota-Referenzdose** nutzen, schaltet das Programm das Relais des Prüflings (DUT) **automatisch AUS**. Da die Referenzdose vor dem Prüfling gesteckt ist, misst sie dessen Eigenverbrauch (Elektronik/WLAN) mit. Dieser "Offset" wird mathematisch von den späteren Referenzwerten abgezogen, um nur die reine Last am Ausgang zu bewerten.
2.  **⏳ Aktion:** Berühren Sie den Aufbau während der 5-sekündigen Stabilisierungsphase nicht.

<a name="ch5_4"></a>
### 5.4 📉 Messung unter Last
1.  **📢 Aktion:** Ein Popup-Fenster erscheint: **"Bitte Ziel-Dose jetzt EINSCHALTEN!"**. Schalten Sie den Prüfling nun über das Webinterface oder den Taster am Gerät ein.
2.  **📊 Aktion:** Beobachten Sie die **Live-Graphen**.
    *   *Hintergrund:* Die Software wartet nach dem Einschalten 7 Sekunden (Inrush-Filter), bis sich der Stromfluss stabilisiert hat. Erst dann beginnt die Aufzeichnung der Datenpunkte.
    *   *Hintergrund:* Jede Sekunde wird ein Datenpaar (Referenz & DUT) abgefragt. Ungültige Werte (0-Werte durch Netzwerkfehler) werden automatisch erkannt, verworfen und die Messung wird wiederholt, bis die geforderte Anzahl erreicht ist.

<a name="ch5_5"></a>
### 5.5 ✅ Analyse und Finalisierung
1.  **📋 Aktion:** Nach Abschluss der letzten Stufe öffnet sich automatisch das Fenster **"Kalibrierungs-Ergebnis"**.
2.  **🔍 Aktion:** Prüfen Sie die vorgeschlagenen Werte für VoltageCal, CurrentCal und PowerCal.
    *   *Hintergrund:* Die `PowerCal`-Werte werden auf zwei Arten berechnet (Mittelwert und lineare Regression). Die Regression (Standardwahl) ist über den gesamten Messbereich meist präziser.
3.  **📤 Aktion:** Klicken Sie auf den Button **"Werte an Dose senden"**.
    *   *Hintergrund:* Die Software sendet die Befehle via HTTP-Backlog an den Prüfling. Danach erfolgt eine sofortige Verifizierung ("As-Left" Prüfung), um sicherzustellen, dass die Werte korrekt gespeichert wurden. Das Ergebnis wird im Log dokumentiert.

---

<a name="ch6"></a>
## 🛠️ 6. Troubleshooting & Expertentipps

*   **❌ Problem:** "Keine serielle Antwort vom Fluke"
    *   **Lösung:** Kabel prüfen oder "Fluke finden" im Setup erneut ausführen. Oft liegt es an einem falschen COM-Port.
*   **⚠️ Problem:** "HTTP 401 Unauthorized"
    *   **Lösung:** Die Dose ist passwortgeschützt. Geben Sie die Daten im erscheinenden Popup ein. Als Standardbenutzer ist "admin" bereits voreingestellt.
*   **🔐 Tipp zu Zugangsdaten:** Die App speichert eingegebene Passwörter sicher im Arbeitsspeicher, bis das Programm geschlossen wird. Nutzen Sie den **"Online Check"** vor der Messung, um die Zugangsdaten einmalig zu hinterlegen. So läuft der eigentliche Kalibrierprozess ohne Unterbrechung durch Popups durch.
*   **🌡️ Tipp für Experten:** Lassen Sie die Messanordnung ca. 5 Minuten "warmlaufen". Elektronische Bauteile driften leicht, bis sie ihre Betriebstemperatur erreicht haben. Eine Kalibrierung im warmen Zustand ist präziser.

---
[🏠 Zurück zum Index](#index)
