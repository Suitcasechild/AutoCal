# 🧠 Tasmota-Wissen für Dummies: Warum "SaveData" dein Gerät rettet

> 💡 **WICHTIGER VORAB-HINWEIS:** Die folgenden Erklärungen zu `SaveData 0` und dem "Auto-Save" sind **NUR** dann wichtig, wenn du die **Dynamische Kalibrierung** (per Rule) nutzt. Wenn du eine ganz normale Standard-Kalibrierung (PRO- oder HOME-Modus) machst, ist dieses Thema für dich hinfällig und du musst nichts beachten!

Diese Anleitung erklärt dir ganz einfach, was hinter den Kulissen deiner Tasmota-Dose passiert, wenn du sie kalibrierst, und warum wir "Tricks" wie `SaveData 0` und "Auto-Save" anwenden müssen.

---

## 1. 💾 Das Gedächtnis deiner Dose (RAM vs. Flash)

Stell dir deine Tasmota-Dose wie einen Menschen mit einem Notizblock vor:

*   **Das Kurzzeitgedächtnis (RAM):** Hier merkt sich die Dose Dinge, die gerade passieren (wie viel Strom fließt gerade?). Das geht blitzschnell, aber wenn man den Stecker zieht, ist alles vergessen.
*   **Der Notizblock (Flash-Speicher):** Hier werden wichtige Dinge "festgeschrieben" (WLAN-Passwort, Name der Dose, Kalibrierwerte). Wenn der Strom weg ist, kann die Dose später einfach nachlesen.

### Das Problem: Der Notizblock nutzt sich ab!
Der Flash-Speicher (der Notizblock) ist aus einer Art elektronischem Papier. Man kann darauf schreiben, aber nach ca. 100.000 Mal Radieren und Neu-Schreiben ist das Papier durchgescheuert und die Dose ist **kaputt**.

---

## 2. ⚡ SaveData 1: Der "Vorsichtige" Modus (Standard)

Normalerweise steht Tasmota auf `SaveData 1`. 
*   **Was passiert?** Jedes Mal, wenn du eine Einstellung änderst (z. B. die Dose umbenennst), schreibt die Dose das sofort auf den Notizblock (Flash).
*   **Warum ist das gut?** Wenn der Strom ausfällt, weiß die Dose nach dem Neustart noch alles.
*   **Wann ist das schlecht?** Wenn wir sehr oft etwas ändern – zum Beispiel jede Sekunde.

---

## 3. 🛡️ SaveData 0: Der "Schutzschild" (Für Profis)

Wenn wir die **Dynamische Kalibrierung** nutzen, berechnet unser Programm ständig neue Werte, damit die Messung immer super genau ist. Das passiert bei jedem Lastwechsel (z. B. wenn der Kühlschrank anspringt).

*   **Das Risiko:** Würden wir dabei `SaveData 1` lassen, würde die Dose den Notizblock innerhalb weniger Wochen "durchscheuern" und wäre Elektroschrott.
*   **Die Lösung:** Wir schalten auf `SaveData 0`. Jetzt behält die Dose alle Änderungen **nur im Kopf (RAM)** und schreibt sie NICHT auf den Notizblock.
*   **Der Vorteil:** Der Notizblock wird geschont. Die Dose lebt ewig.

---

## 4. 📉 Die Schattenseite von SaveData 0

Wenn der Schutzschild (`SaveData 0`) an ist, gibt es ein Problem:
1.  **Zählerverlust:** Die Dose zählt fleißig deine verbrauchten Wattstunden (Wh). Aber sie behält diese Zahl nur im Kopf. Wenn jetzt jemand über das Kabel stolpert oder die Sicherung rausfliegt, ist die Zahl weg. Nach dem Neustart steht dein Zähler wieder auf dem Stand von vor dem Stromausfall.
2.  **Einstellungen gehen verloren:** Wenn du die Dose umbenennst oder einen Timer stellst, während `SaveData 0` aktiv ist, wird das nicht gespeichert. Nach einem Neustart heißt die Dose wieder wie vorher.

---

## 5. 🚀 Die Rettung: Das "Auto-Save" (Rule2)

Hier kommt unser neuer Trick ins Spiel. Wir wollen den Schutz von `SaveData 0`, aber nicht die Gefahr, alle Zählerstände zu verlieren. 

**Die Lösung ist ein kleiner Roboter (eine "Rule"), der folgendes tut:**
1.  Er wartet 5 Minuten.
2.  Er klappt kurz den Schutzschild weg (`SaveData 1`).
3.  Tasmota bemerkt das und schreibt sofort alle aktuellen Zählerstände schnell auf den Notizblock.
4.  Der Roboter wartet 1 Sekunde (`Delay 10`).
5.  Er klappt den Schutzschild sofort wieder hoch (`SaveData 0`).

**Warum ist das genial?**
*   Du verlierst im schlimmsten Fall nur die Daten der letzten 5 Minuten, nicht die von Wochen.
*   Die Dose wird nur alle 5 Minuten einmal kurz belastet, statt jede Sekunde. Das hält der Notizblock (Flash) problemlos 50 Jahre lang aus.

---

## 📋 Zusammenfassung: Was du dir merken musst

| Modus | Was passiert? | Vorteile | Nachteile |
| :--- | :--- | :--- | :--- |
| **SaveData 1** | Schreibt alles sofort auf den Chip. | Sicher gegen Stromausfall. | Chip geht bei ständigen Änderungen kaputt. |
| **SaveData 0** | Behält alles nur im RAM. | Chip wird geschützt (Lebensdauer!). | Datenverlust bei Stromausfall. |
| **Auto-Save** | Schaltet alle 5 Min. kurz um. | Beste Sicherheit + Langes Leben. | Erfordert eine kleine Rule auf der Dose. |

### Wie mache ich jetzt manuelle Änderungen?
Wenn du im Modus `SaveData 0` (durch die dynamische Kalibrierung) bist und den Namen der Dose permanent ändern willst:
1.  Gehe in die Tasmota-Konsole.
2.  Tippe `SaveData 1` und drücke Enter.
3.  Ändere deinen Namen/WLAN/Timer.
4.  Tippe `SaveData 0` und drücke Enter (um den Schutz wieder zu aktivieren).

---
*Erstellt am 09. März 2026 – Damit Technik für jeden verständlich bleibt.*
