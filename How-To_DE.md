# 📖 How-To: Tasmota-Kalibrierung für Einsteiger
## *Vom Nullpunkt zur eigenen Master-Referenzdose*

Dieses Dokument beschreibt den Weg zur hochpräzisen Kalibrierung deiner Tasmota-Geräte, auch wenn du **kein** Profi-Multimeter (Fluke 45) und **keine** bereits kalibrierte Referenzdose besitzt.

---

## 📋 Inhaltsverzeichnis
1. [Das Konzept: Die "Bootstrapping"-Strategie](#1-das-konzept)
2. [Voraussetzungen & Hardware](#2-voraussetzungen)
3. [Schritt 1: Vorbereitung der ersten Dose (DUT)](#3-schritt-1)
4. [Schritt 2: Die Manuelle Kalibrierung (Der Grundstein)](#4-schritt-2)
    - 4.1 [Die Foto-Methode zur Synchronisation](#41-foto-methode)
    - 4.2 [Eingabe der Messwerte](#42-eingabe)
5. [Schritt 3: Verifizierung & Erhebung zur Master-Dose](#5-schritt-3)
6. [Schritt 4: Skalierung (Weitere Dosen kalibrieren)](#6-schritt-4)
7. [Wichtige Tipps für maximale Präzision](#7-tipps)

---

<a name="1-das-konzept"></a>
## 1. 💡 Das Konzept: Die "Bootstrapping"-Strategie
Da du keine Referenz hast, erschaffen wir uns eine. 
*   **Phase 1:** Du nimmst eine Tasmota-Dose und kalibrierst sie extrem sorgfältig mit einem einfachen Steckdosen-Messgerät (manuelle Methode).
*   **Phase 2:** Diese Dose ist nun dein "Gold-Standard" (Master-Dose).
*   **Phase 3:** Alle weiteren Dosen steckst du einfach hinter diese Master-Dose. Die Software vergleicht beide Dosen automatisch und kalibriert die neue Dose in Sekunden (HOME-Modus).

---

<a name="2-voraussetzungen"></a>
## 2. 🔌 Voraussetzungen & Hardware
Du benötigst:
1.  **Den Prüfling (DUT):** Die Tasmota-Dose, die kalibriert werden soll.
2.  **Ein einfaches Messgerät:** Ein handelsübliches Energiekosten-Messgerät für die Steckdose.
3.  **Lasten für Kalibrierung & Test:** Da die manuelle Kalibrierung in der App auf eine Laststufe optimiert ist, solltest du folgende Verbraucher bereithalten:
    *   **Kalibrier-Last (Ideal):** Ein Heizlüfter oder Wasserkocher mit ca. **1200W**. Dies ist der optimale Arbeitspunkt für die Basis-Kalibrierung.
    *   **Test-Lasten (Verifizierung):** Eine Glühbirne (ca. **200W**) und eine starke Last (ca. **2500W**), um nach der Kalibrierung zu prüfen, wie groß die Abweichungen in den Randbereichen sind.
    *   **Vermeide** LED-Lampen, PCs oder Fernseher (instabile Schaltnetzteile).
4.  **Smartphone:** Für die Foto-Methode.

---

<a name="3-schritt-1"></a>
## 3. 🛠️ Schritt 1: Vorbereitung der ersten Dose (DUT)
1.  Stecke das einfache Messgerät in die Wandsteckdose.
2.  Stecke die Tasmota-Dose (DUT) in das Messgerät.
3.  Schließe die Last an die Tasmota-Dose an.
4.  **WICHTIG:** Schalte die Last ein und lass alles **5 Minuten warmgelaufen** (Bauteile-Drift stabilisieren).
5.  Öffne den Tasmota Calibrator, gib die IP der Dose ein und klicke auf **"Online Check"**.

---

<a name="4-schritt-2"></a>
## 4. 📉 Schritt 2: Die Manuelle Kalibrierung (Der Grundstein)
Wähle im Hauptmenü unter Referenz den Punkt **"Manuell (Eingabe)"**.

💡 **Tipp:** Nutze den integrierten **Hilfe-Button** direkt im Fenster der manuellen Messwerterfassung für eine Kurzanleitung. Detaillierte Hintergrundinfos findest du zudem in der Datei `manual_info.md`.

<a name="41-foto-methode"></a>
### 4.1 Die Foto-Methode zur Synchronisation
Tasmota und dein Messgerät zeigen Werte nicht exakt zur gleichen Millisekunde an. Um diesen Versatz auszugleichen:
1.  Klicke in der App auf **"Kalibrierung Starten"**. Die App beginnt, die internen Werte der Dose zu loggen.
2.  Nimm dein Smartphone und mache ein **Foto**, auf dem sowohl das Display deines externen Messgeräts als auch der Monitor deines PCs (mit der laufenden App) zu sehen ist.
3.  Wiederhole dies für drei verschiedene Lastzustände (falls möglich, z.B. 40W Birne, 100W Birne, oder einfach drei Fotos in zeitlichem Abstand bei gleicher Last).

<a name="42-eingabe"></a>
### 4.2 Eingabe der Messwerte
1.  Nachdem die App die Messung beendet hat, öffnet sich die Eingabemaske.
2.  Schau dir deine Fotos an. Suche in der Liste der App den Zeitpunkt, der auf dem Foto zu sehen war.
3.  Trage die Werte vom Display deines Messgeräts (V, A, W) in die entsprechenden Felder der App ein.
4.  Die App berechnet nun mittels **linearer Regression** die optimalen Kalibrierfaktoren.
5.  Klicke auf **"Auswahl Kalibrieren"**, um die Werte an die Dose zu senden.

---

<a name="5-schritt-3"></a>
## 5. ✅ Schritt 3: Verifizierung & Erhebung zur Master-Dose
Nachdem die Dose kalibriert wurde:
1.  Prüfe die Werte im Webinterface der Dose gegen dein Messgerät. Stimmen sie überein?
2.  **Glückwunsch!** Diese Dose ist nun deine **Referenz-Dose**. Markiere sie (z.B. mit einem Aufkleber "MASTER").

---

<a name="6-schritt-4"></a>
## 6. 🚀 Schritt 4: Skalierung (Weitere Dosen kalibrieren)
Ab jetzt wird es einfach:
1.  Stecke deine **Master-Dose** in die Wand.
2.  Stecke die **neue Dose (DUT)** in die Master-Dose.
3.  Schließe die Last an die neue Dose an.
4.  Wähle in der App als Referenz **"Tasmota (HOME-Modus)"** und gib die IP der Master-Dose ein.
5.  Klicke auf Start. Die App erledigt den Rest (Eigenverbrauch-Abzug, Abgleich, Senden) vollautomatisch in ca. 60 Sekunden.

---

<a name="7-tipps"></a>
## 7. 💡 Wichtige Tipps für maximale Präzision
*   **Kurze Kette:** Benutze keine unnötigen Verlängerungskabel zwischen Master und DUT. Jeder Übergangswiderstand verfälscht das Ergebnis.
*   **SaveData 0:** Wenn du später die **Dynamische Kalibrierung** (Experten-Feature) nutzt, klicke auf den dortigen **Hilfe-Button** im Dialog für tiefere Einblicke. Detaillierte technische Informationen findest du in der Datei `anleitung_dynamic_cal.md`. Denke daran, dass manuelle Änderungen an der Dose (Name, WLAN) nur gespeichert werden, wenn du vorher kurz `SaveData 1` in der Konsole eingibst.
*   **Stabile Spannung:** Kalibriere nicht unbedingt dann, wenn gerade die Waschmaschine oder der Backofen im Haus läuft, da dies die Netzspannung instabil machen kann.

---
*Dokumentation erstellt am 09. März 2026 für das Projekt AutoCal.*
