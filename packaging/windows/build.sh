#!/bin/sh
# Baut lokal eine PORTABLE MattPad.exe (eine einzelne Datei, ohne Installation).
# Der MSI-Installer entsteht dagegen auf GitHub (.github/workflows/release.yml).
# Wine dient nur als Bauwerkzeug; die .exe läuft auf Windows 10/11 ohne Wine/Python.
# Bau-Umgebung (Wine-Prefix mit Windows-Python 3.12, PyQt6, PyInstaller; ~3,5 GB)
# liegt außerhalb des Repos in $WORK.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$(cd "$HERE/../.." && pwd)"
WORK="${WORK:-$HOME/projekte/mdpad-windows}"
export WINEPREFIX="$WORK/wineprefix" WINEDEBUG=-all WINEDLLOVERRIDES="mscoree,mshtml="
PY='C:\Python312\python.exe'
winpath() { echo 'Z:'"$(echo "$1" | tr / '\\')"; }

rm -rf "$WORK/stage" "$WORK/build" "$WORK/dist"
mkdir -p "$WORK/stage/dictionaries" "$WORK/stage/vendor/vditor"
cp "$SRC"/mattpad.py "$SRC"/i18n.py "$SRC"/editor.html "$SRC"/editor.js "$SRC"/editor.css "$SRC"/LICENSE \
   "$SRC"/mattpad.png "$SRC"/mattpad.svg "$HERE"/mattpad.ico "$WORK/stage/"
cp -r "$SRC/vendor/vditor/dist" "$SRC/vendor/vditor/LICENSE" "$WORK/stage/vendor/vditor/"
cp -r "$SRC/plugins" "$SRC/help" "$WORK/stage/"
cp "$SRC"/dictionaries/??-??.bdic "$WORK/stage/dictionaries/"
cp -r "$SRC/packaging/icons" "$WORK/stage/"

cd "$WORK/stage"
wine "$PY" -m PyInstaller --noconfirm --clean --onefile --windowed \
    --name MattPad --icon mattpad.ico \
    --distpath "$(winpath "$WORK/dist")" --workpath "$(winpath "$WORK/build")" \
    --add-data 'editor.html;.' --add-data 'editor.js;.' --add-data 'editor.css;.' --add-data 'LICENSE;.' \
    --add-data 'help;help' --add-data 'mattpad.png;.' --add-data 'mattpad.svg;.' \
    --add-data 'vendor;vendor' --add-data 'dictionaries;dictionaries' --add-data 'icons;icons' \
    --add-data 'plugins;plugins' \
    --exclude-module tkinter \
    mattpad.py
rm -rf "$WORK/stage" "$WORK/build"
ls -la "$WORK/dist"
