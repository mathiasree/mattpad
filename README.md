# Matt|Pad

A minimalist Markdown editor for authors: it writes like Typora (formatting appears as you type) and looks like a classic text editor (tabs, menus, toolbar).
**Templates and themes come as plugins** – e.g. book chapters with a print-ready book layout.

*Editor Markdown para autoras y autores · Editor Markdown para autoras e autores · Markdown-Editor für Autorinnen und Autoren*

**Download:** [Releases](https://github.com/mathiasree/mattpad/releases) – Windows (.msi, no admin rights needed), macOS (.dmg, Apple Silicon and Intel), Linux (.flatpak).

## Features
- Live Markdown editing, source view, WYSIWYG mode ([Vditor](https://github.com/Vanessa219/vditor))
- Templates (*File → New from template*) and themes (*View → Theme*) as plugins – see [PLUGINS.md](PLUGINS.md)
- Theme applies while writing, when printing and in PDF/HTML export; per document via front matter (`theme: libro`, `lang: es`)
- Interface in English, Spanish, Portuguese and German – follows the system language
- Spell checking: Spanish, Portuguese (BR/PT), English, German
- Bundled plugins: *Book project* (Spanish/Portuguese chapter templates, “Libro” theme with Lora) and *Basic themes* (Sepia, Manuscript, Modern)

## Run from source
```sh
python3 mattpad.py [file.md …]
```
Requires Python 3 with PyQt6 and PyQt6-WebEngine.

## Build
| System | Output | How |
| --- | --- | --- |
| Windows 10/11 | `MattPad-Windows.msi` (multilingual, per-user) | GitHub Actions (`.github/workflows/release.yml`) |
| macOS 12+ | `MattPad-macOS-AppleSilicon.dmg`, `MattPad-macOS-Intel.dmg` | GitHub Actions |
| Linux | `MattPad-Linux.flatpak` | `packaging/flatpak/build.sh` |

New version: raise `APP_VERSION` in `mattpad.py` (and `<release>` in the metainfo), then `git tag vX.Y.Z && git push --tags`.

## Translations
UI strings live in [`i18n.py`](i18n.py) (keys are the German source strings). Corrections welcome.

## License
© 2026 Mathias Ree – free software under the **GNU General Public License v3 or later** ([LICENSE](LICENSE)).
Third-party: Vditor (MIT), Qt/PyQt6 (GPL v3), Hunspell dictionaries (GPL/LGPL/MPL), Breeze icons (LGPL), Lora font (SIL OFL 1.1).
