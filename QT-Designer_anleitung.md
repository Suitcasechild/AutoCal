# 🎨 Anleitung: Umgang mit Qt Designer & Übersetzungen

Diese Anleitung beschreibt den korrekten Workflow, wenn neue GUI-Elemente im **Qt Designer** hinzugefügt und anschließend internationalisiert (übersetzt) werden sollen.

---

## ⚠️ Das Grundproblem
Dateien aus dem Qt Designer (`.ui`-Dateien) sind statische XML-Dateien. Sie enthalten keine Programm-Logik und können **keine Python-Funktionen** wie `_("Text")` ausführen.

Das bedeutet:
*   Ein Text, den du im Designer eintippst (z.B. "Speichern"), wird beim Programmstart **immer** genau so angezeigt.
*   Die automatische Übersetzung funktioniert **nur**, wenn wir dem Programm im Python-Code explizit sagen, dass es diesen Text übersetzen soll.

---

## ✅ Der Workflow (Schritt für Schritt)

### 1. Arbeit im Qt Designer (`.ui` Datei)
1.  **Element hinzufügen:** Ziehe dein Widget (Button, Label, etc.) an die gewünschte Stelle.
2.  **Text setzen:** Schreibe den deutschen Text hinein (z.B. "Verbindung testen"). Dieser dient als Default-Wert und Platzhalter.
3.  **WICHTIG: Objekt-Namen vergeben!**
    *   Gib dem Element im Eigenschafts-Editor (`Property Editor`) unter `objectName` einen sprechenden Namen.
    *   ❌ **Schlecht:** `pushButton_4`, `label_12`
    *   ✅ **Gut:** `btn_test_connection`, `lbl_status_message`

### 2. Arbeit im Python-Code (`gui_main.py`)
Damit die Übersetzung greift, müssen wir das Element im Code "anfassen". Das geschieht idealerweise in der Methode `setup_ui_logic` oder direkt in der `__init__`-Methode der `MainWindow`-Klasse.

**Code-Beispiel:**

```python
# In der Datei gui_main.py, innerhalb der Klasse MainWindow

def setup_ui_logic(self):
    # ... bestehender Code ...

    # NEU: Übersetzung für das Element aktivieren
    # Wir prüfen sicherheitshalber, ob das Element existiert (hasattr)
    if hasattr(self.ui, 'btn_test_connection'):
        self.ui.btn_test_connection.setText(_("Verbindung testen"))
```

### 3. Was passiert im Hintergrund?
1.  Python lädt die UI. Der Button zeigt kurzzeitig den statischen Text aus dem Designer ("Verbindung testen").
2.  Python führt die Zeile `setText(_("Verbindung testen"))` aus.
3.  Die Funktion `_()` schaut in der aktuellen Sprachdatei (z.B. Englisch) nach.
4.  Findet sie eine Übersetzung, wird der Text auf dem Button durch "Test Connection" ersetzt.

---

## 📝 Zusammenfassung für den Entwickler
*   **Im Designer:** Immer deutschen Text als Basis verwenden. Sauber benennen!
*   **Im Code:** Jedes Text-Element muss einmal mit `setText(_("..."))` initialisiert werden.
*   **Kommunikation:** Wenn du neue Elemente in der UI ergänzt hast, sag mir Bescheid (z.B. *"Habe Button 'Start' (btn_start) hinzugefügt"*), damit ich den Python-Code entsprechend aktualisieren kann.
