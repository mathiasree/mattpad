# Matt|Pad

Minimalistischer Markdown-Editor: schreibt sich wie Typora (Live-Vorschau), sieht aus wie Notepad++.
Vorlagen und Themes kommen als **Plugins** – gedacht für die Autorinnen und Autoren unserer Buchprojekte.

Python + PyQt6 (Qt WebEngine), Editor-Kern [Vditor](https://github.com/Vanessa219/vditor) (MIT, in `vendor/`).

© 2026 Mathias Ree – freie Software unter der **GNU General Public License v3 oder später** (siehe `LICENSE`).

## Starten (aus dem Quelltext, Linux)
```sh
python3 mattpad.py [datei.md …]
```
Benötigt PyQt6 mit QtWebEngine (Arch: `python-pyqt6-webengine`, Debian: `python3-pyqt6.qtwebengine`).

## Downloads bauen

| System | Ergebnis | Wie |
| --- | --- | --- |
| Windows 10/11 | `MattPad-<v>-Windows.msi` (ohne Adminrechte) | GitHub Actions, `.github/workflows/release.yml` |
| macOS 12+ | `MattPad-<v>-macOS-AppleSilicon.dmg`, `…-Intel.dmg` | GitHub Actions, dito |
| Linux | `MattPad-<v>-Linux.flatpak` | lokal: `packaging/flatpak/build.sh` |
| Windows portabel | `MattPad.exe` (eine Datei) | lokal mit Wine: `packaging/windows/build.sh` |

Neue Version: `APP_VERSION` in `mattpad.py` (und `<release>` in der metainfo.xml) erhöhen, dann
`git tag v1.0.1 && git push --tags` – GitHub baut MSI und DMGs und hängt sie an ein Release.

## Plugins (Vorlagen + Themes)
Siehe [`PLUGINS.md`](PLUGINS.md). Mitgeliefert: `plugins/buchprojekt` (spanische Kapitel-Vorlagen,
Theme „Libro“) und `plugins/themes-basis` (Sepia, Manuskript, Modern).

## Tastenkürzel
Siehe `Kurzreferenz.md` (F1 im Programm). Drucken: Strg+P, neu aus Vorlage: Strg+Shift+N.
