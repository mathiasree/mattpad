#!/bin/sh
# Baut Matt|Pad als Flatpak und packt es in EINE Datei (MattPad-Linux.flatpak),
# die Autorinnen/Autoren per Doppelklick (GNOME Software/KDE Discover) oder mit
#   flatpak install --user MattPad-Linux.flatpak
# installieren. Fehlende Laufzeitumgebungen kommen dabei automatisch von Flathub.
# Voraussetzung: flatpak-builder, org.kde.Sdk//6.11, com.riverbankcomputing.PyQt.BaseApp//6.11
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$(cd "$HERE/../.." && pwd)"
OUT="${OUT:-$SRC/dist}"
WORK="${WORK:-$HOME/.cache/mattpad-flatpak}"
VERSION="$(sed -n 's/^APP_VERSION = "\(.*\)"/\1/p' "$SRC/mattpad.py")"
mkdir -p "$OUT" "$WORK"
flatpak-builder --user --force-clean --disable-rofiles-fuse \
    --state-dir="$WORK/state" --repo="$WORK/repo" \
    "$WORK/build" "$HERE/com.mathiasree.MattPad.yml"
flatpak build-bundle --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo \
    "$WORK/repo" "$OUT/MattPad-Linux.flatpak" com.mathiasree.MattPad
ls -la "$OUT/MattPad-Linux.flatpak"
