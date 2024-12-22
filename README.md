# makehuman-pyside6  
*Das Programm befindet sich noch in der Entwicklung und ist weit davon entfernt, einsatzbereit zu sein. Trotzdem habe ich mich nach einem Jahr entschieden, das Repository auf öffentlich zu stellen.*  

Seien Sie vorsichtig – wir übernehmen keine Verantwortung, wenn die neue Version von MakeHuman nicht wie erwartet funktioniert. Es wird weiterhin empfohlen, eine virtuelle Umgebung zu nutzen, insbesondere unter Linux mit bereits installiertem Python.

**MAC wird derzeit nicht unterstützt**, und es ist möglich, dass dies auch in Zukunft so bleibt (falls OpenGL nicht weiterverwendet wird, wird Vulkan eingesetzt, nicht proprietäre Technologien wie Metal).

Die Einstellungen in der Datei `requirements.txt` gelten als minimale Versionen. Neuere Versionen sollten (!) funktionieren.

- **PyOpenGL** (für den OpenGL-Teil)  
- **PySide6** (für die Benutzeroberfläche)  
- **numpy** (für schnellere Berechnungen)  
- **psutil** (für Speicher-Debugging, möglicherweise nicht in der finalen Version enthalten)  

Wenn diese z. B. mit `pip install` installiert werden, werden auch andere Bibliotheken wie `shiboken6` hinzugefügt.  

Diese Installation wird sich sicherlich ändern, da sich alles noch in der Entwicklung befindet.

---

**Derzeit kann `makehuman.py` nur über die Kommandozeile gestartet werden.**  
Wechseln Sie dazu zunächst in das Verzeichnis:  
**`cd` in den Ordner**  
Führen Sie das Skript mit dem Interpreter aus:

```
python3 makehuman.py
```

Aktuell ist die Syntax wie folgt:

```
usage: makehuman.py [-h] [-V] [--nomultisampling] [-l] [-b BASE] [-A] [-v VERBOSE] [model]

positional arguments:
  model                 Name einer mhm-Modell-Datei (verwendet mit Basis-Mesh)

optionale Argumente:
  -h, --help            zeigt diese Hilfe und beendet das Programm
  -V, --version         zeigt die Version und Lizenzinformationen
  --nomultisampling     deaktiviert Multisampling (zur Anzeige von mehreren transparenten Ebenen)
                        Ohne Multisampling wird die normale Blend-Funktion genutzt
  -l                    erzwingt das Schreiben in eine Log-Datei
  -b BASE, --base BASE  wählt ein Basis-Mesh vor ('none' für keine Vorauswahl)
  -A, --admin           Unterstützt administrative Aufgaben ('Admin'). Der Befehl schreibt in den Programmordner, in dem MakeHuman installiert ist.
  -v VERBOSE, --verbose VERBOSE
                        Bitweise Option für ausführliche Protokolle:
                        1 niedriges Protokollierungslevel (Standard)
                        2 mittleres Protokollierungslevel
                        4 Speicherverwaltung
                        8 Dateizugriff
                        16 Aktivierung von numpy-Laufzeitfehlermeldungen
```

**Hinweis:** Es gibt noch Debug-Ausgaben, die nicht den verbose-Einstellungen folgen.

---

**Assets hinzufügen:**  
Da MakeHuman fast keine Assets enthält, um Speicherplatz auf GitHub zu sparen, müssen Assets hinzugefügt werden.

MakeHuman kann mit zwei Asset-Ordnern arbeiten:
1. Ein **Systemordner**, in dem MakeHuman selbst installiert ist.  
2. Ein **Benutzerordner**.

Starten Sie MakeHuman zunächst, um Ihren Arbeitsbereich (Benutzerordner) festzulegen. So können Sie Assets in Ihrer eigenen Umgebung herunterladen, anstatt sie mit dem Programmcode zu vermischen. Dies verhindert, dass Assets mehrfach heruntergeladen werden. Dies kann in den Einstellungen erfolgen:

1. **Gehen Sie zu den Einstellungen:**  
   Ändern Sie z. B. den Benutzerordner zu `d:\shared\mhuser` und die Log-Datei zu `d:\shared\mhuser\log` (Windows-Syntax, unter Linux entsprechend).  
2. **Speichern Sie die Änderungen.**

**Während der Entwicklung wird nicht empfohlen, Ausgaben umzuleiten.**

---

**Zusätzliche CLI-Tools:**  
Nach dem Festlegen der Pfade können auch die folgenden CLI-Tools mit dem Benutzerordner arbeiten:

- `compile_meshes.py`  
- `compile_targets.py`  
- `getpackages.py`

Diese Tools haben Optionen und können später ohne Interaktion ausgeführt werden (außer `getpackages.py`). Es wird jedoch empfohlen, sie ohne Optionen zu starten, um die Möglichkeit zu haben, den Befehl abzubrechen.

1. **`python3 getpackages.py`**: Lädt die Assets für die hm08-Basis herunter (wir empfehlen Benutzerspeicher).  
2. **`python3 compile_targets.py`**: Kompiliert die System-Targets.  
3. **`python3 compile_meshes.py`**: Kompiliert Meshes sowohl im System- als auch im Benutzerordner (mhclo + obj werden in mhbin kompiliert). Im Systemordner wird das Basis-Mesh selbst kompiliert.

Diese Funktionen können auch über die MakeHuman-GUI ausgeführt werden. Der Download kann ebenfalls dort erfolgen. Da der Systembereich normalerweise geschützt ist (insbesondere unter Linux), muss dazu die Option **`-A`** verwendet werden. Außerdem müssen die entsprechenden Benutzerrechte vorhanden sein.

**Hinweis:** In Zukunft könnte ein Paket die Standard-Assets bereits enthalten, wodurch die Installation einfacher wird.

---

**Konfigurationsdatei:**  
Die Datei mit dem Pfad zum Benutzerordner kann auch mit einem Editor geändert werden. Diese Datei bleibt bestehen, auch wenn die Software gelöscht wird.

Um diese Datei zu finden, zeigen Sie einfach die Version an. Sie wird in der letzten Zeile angezeigt:

```
python3 makehuman -V
```


