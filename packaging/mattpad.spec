# PyInstaller-Rezept für Matt|Pad (Windows und macOS).
# Aufruf aus dem Repo-Hauptordner:  pyinstaller --noconfirm packaging/mattpad.spec
# Ergebnis: dist/MattPad/ (Ordner, Grundlage für den MSI-Installer)
#           bzw. dist/MattPad.app (macOS)
# Copyright (C) 2026 Mathias Ree – GPL-3.0-or-later
import re
import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent
PKG = ROOT / "packaging"
VERSION = re.search(r'APP_VERSION = "([^"]+)"', (ROOT / "mattpad.py").read_text(encoding="utf-8")).group(1)

datas = [(str(ROOT / f), ".") for f in
         ("editor.html", "editor.js", "editor.css", "mattpad.png", "mattpad.svg", "LICENSE")]
datas += [
    (str(ROOT / "vendor/vditor/dist"), "vendor/vditor/dist"),
    (str(ROOT / "vendor/vditor/LICENSE"), "vendor/vditor"),
    (str(ROOT / "plugins"), "plugins"),
    (str(ROOT / "help"), "help"),
    (str(PKG / "icons"), "icons"),
]
# only the shipped dictionaries, not the personal x-personal-*.bdic
datas += [(str(p), "dictionaries") for p in sorted((ROOT / "dictionaries").glob("??-??.bdic"))]
datas += [(str(ROOT / "dictionaries/licenses"), "dictionaries/licenses")]

a = Analysis(
    [str(ROOT / "mattpad.py")],
    datas=datas,
    excludes=["tkinter", "PyQt6.QtQml", "PyQt6.QtQuick", "PyQt6.QtMultimedia", "PyQt6.QtBluetooth"],
    noarchive=False,
)
pyz = PYZ(a.pure)

icon = str(PKG / ("macos/mattpad.icns" if sys.platform == "darwin" else "windows/mattpad.ico"))
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="MattPad",
    console=False,
    icon=icon,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="MattPad", upx=False)

if sys.platform == "darwin":
    md_types = ["md", "markdown", "mdown", "mkd"]
    app = BUNDLE(
        coll,
        name="MattPad.app",
        icon=icon,
        bundle_identifier="com.mathiasree.MattPad",
        version=VERSION,
        info_plist={
            "CFBundleName": "MattPad",
            "CFBundleDisplayName": "Matt|Pad",
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
            "NSHumanReadableCopyright": "© 2026 Mathias Ree – GNU GPL v3 or later",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "12.0",
            "LSApplicationCategoryType": "public.app-category.productivity",
            "CFBundleDevelopmentRegion": "en",
            "CFBundleLocalizations": ["en", "de", "es", "pt"],
            "CFBundleAllowMixedLocalizations": True,
            "CFBundleDocumentTypes": [{
                "CFBundleTypeName": "Markdown document",
                "CFBundleTypeRole": "Editor",
                "LSHandlerRank": "Alternate",
                "CFBundleTypeExtensions": md_types,
                "LSItemContentTypes": ["net.daringfireball.markdown", "public.plain-text"],
            }],
        },
    )
