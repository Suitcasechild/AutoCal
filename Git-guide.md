# Anleitung zur Einrichtung von Git

Um dieses Projekt mit einem Git-Repository zu verbinden und die Änderungen zu speichern, sind die folgenden Schritte notwendig.

### 1. Git installieren (falls noch nicht geschehen)

Der vorherige Fehler deutet darauf hin, dass Git entweder nicht installiert oder nicht im Systempfad ist.
*   **Aktion:** Laden Sie Git von der offiziellen Webseite herunter und installieren Sie es: [https://git-scm.com/downloads](https://git-scm.com/downloads)
*   **Wichtig:** Während der Installation, stellen Sie sicher, dass die Option "Git from the command line and also from 3rd-party software" oder eine ähnliche Option, die Git zum Systempfad hinzufügt, ausgewählt ist. Nach der Installation müssen Sie eventuell das Terminal neu starten.

### 2. Lokales Git-Repository initialisieren

Ihr Projektordner muss als Git-Repository eingerichtet werden.
*   **Befehl:**
    ```shell
    git init
    ```
*   **Erklärung:** Dieser Befehl erstellt einen versteckten `.git`-Ordner in Ihrem Projektverzeichnis (`C:\Users\Arnulf\Documents\TASMOTA\AutoCal`), der alle Änderungen nachverfolgt.

### 3. Git-Benutzer konfigurieren (einmalig)

Git muss wissen, wer Sie sind, um Ihre Änderungen zu kennzeichnen.
*   **Befehle:**
    ```shell
    git config --global user.name "Ihr Name"
    git config --global user.email "ihre.email@example.com"
    ```
*   **Aktion:** Ersetzen Sie `"Ihr Name"` und `"ihre.email@example.com"` mit Ihren echten Daten.

### 4. Neues Repository auf GitHub (oder einem anderen Anbieter) erstellen

*   **Aktion:**
    1.  Gehen Sie auf die Webseite Ihres Git-Anbieters (z.B. [GitHub.com](https://github.com)).
    2.  Erstellen Sie ein **neues, leeres Repository**. Geben Sie ihm einen Namen (z.B. `Tasmota-AutoCal`).
    3.  **Wichtig:** Initialisieren Sie das Repository **NICHT** mit einer `README.md`, `.gitignore` oder Lizenzdatei, da Ihr Projekt diese Dateien bereits enthält.
    4.  Nach der Erstellung zeigt Ihnen die Seite die URL des Repositorys an. Sie sieht meist so aus: `https://github.com/IhrUsername/Tasmota-AutoCal.git`. Kopieren Sie diese URL.

### 5. Lokales Repository mit dem Online-Repository verbinden

*   **Befehl:**
    ```shell
    git remote add origin https://github.com/IhrUsername/Tasmota-AutoCal.git
    ```
*   **Aktion:** Ersetzen Sie die URL durch die, die Sie in Schritt 4 kopiert haben. `origin` ist der Standard-Kurzname für die Online-Verbindung.

### 6. Alle Projektdateien zum ersten "Commit" hinzufügen

Jetzt sagen Sie Git, dass alle aktuellen Dateien in der ersten Version des Repositorys enthalten sein sollen.
*   **Befehle:**
    ```shell
    git add .
    git commit -m "Initial commit: Tasmota Calibrator v5.0 mit Regressions-Logik"
    ```
*   **Erklärung:** `git add .` fügt alle Dateien zum "Staging"-Bereich hinzu. `git commit` speichert diesen Schnappschuss dauerhaft mit einer beschreibenden Nachricht.

### 7. Projektdateien hochladen

Der letzte Schritt ist das Hochladen Ihrer lokalen Commits zum Online-Repository.
*   **Befehl:**
    ```shell
    git push -u origin master
    ```
*   **Hinweis:** Je nach Git-Version kann Ihre Haupt-Branch `main` statt `master` heißen. Falls der Befehl fehlschlägt, versuchen Sie `git push -u origin main`.
