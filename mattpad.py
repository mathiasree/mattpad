#!/usr/bin/env python3
# Matt|Pad – minimalistischer Markdown-Editor
# Copyright (C) 2026 Mathias Ree
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Matt|Pad – a minimal Typora-like Markdown editor with a Notepad++-style window."""

import datetime
import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from PyQt6.QtCore import (QEvent, QFileSystemWatcher, QLibraryInfo, QLocale, QObject,
                          QSettings, QSize, QStandardPaths, Qt, QTimer, QTranslator,
                          QUrl, pyqtSignal, pyqtSlot)
from PyQt6.QtGui import (QAction, QActionGroup, QColor, QDesktopServices, QIcon,
                         QKeySequence, QPainter, QPixmap)
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (QApplication, QCheckBox, QDialog, QDialogButtonBox,
                             QFileDialog, QFormLayout, QGridLayout, QHBoxLayout,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMainWindow, QMenu, QMessageBox, QPlainTextEdit,
                             QPushButton, QSplitter, QTabWidget, QToolButton,
                             QVBoxLayout, QWidget)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n  # noqa: E402
from i18n import T  # noqa: E402

APP_NAME = "Matt|Pad"          # shown to the user
APP_ID = "MattPad"             # file names, settings, folders ("|" is not allowed there)
APP_VERSION = "1.0.1"
APP_COPYRIGHT = "© 2026 Mathias Ree"
APP_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
EDITOR_URL = QUrl.fromLocalFile(str(APP_DIR / "editor.html"))
SERVER_NAME = f"mattpad-{getpass.getuser()}"

MODE_NAMES = {"ir": "Live (Typora)", "sv": "Quelltext + Vorschau", "wysiwyg": "WYSIWYG"}  # translated with T()
MAX_RECENT = 12
SPELL_LANGS = {"de-DE": "Deutsch", "es-ES": "Español", "pt-BR": "Português (Brasil)",
               "pt-PT": "Português (Portugal)", "en-US": "English"}
DICT_DIR = APP_DIR / "dictionaries"
CONVERT_DICT = next((p for p in ("/usr/lib/qt6/qwebengine_convert_dict",               # Arch
                                  "/usr/lib/qt6/libexec/qwebengine_convert_dict",       # Debian
                                  "/usr/lib/x86_64-linux-gnu/qt6/libexec/qwebengine_convert_dict",
                                  str(APP_DIR / "qwebengine_convert_dict.exe"))              # Windows build
                     if Path(p).exists()), "qwebengine_convert_dict")


def tidy_markdown(text, original):
    """Undo cosmetic changes Vditor makes, so that files (e.g. Obsidian notes)
    don't get reformatted just by editing them."""
    # task lists: "- [X]  done" -> "- [x] done"
    def task(m):
        mark = m.group(2) if m.group(2) == " " or "[X]" in original else "x"
        return f"{m.group(1)}{mark}] "
    text = re.sub(r"^(\s*(?:[-*+]|\d+[.)]) \[)([ xX])\] {1,2}", task, text, flags=re.M)
    # Obsidian callouts: Vditor inserts an empty ">" line after the title
    if not re.search(r"^> \[!.*\n>\s*\n", original, flags=re.M):
        text = re.sub(r"^(> \[!.*)\n>\s*\n", r"\1\n", text, flags=re.M)
    # tables: Vditor pads cells to equal width; keep them compact unless the
    # file already used padded tables
    if not re.search(r"^\|?\s*:?-{4,}", original, flags=re.M):
        text = re.sub(r"^\|.*\|[ \t]*$", _compact_table_row, text, flags=re.M)
    # Vditor puts an extra blank line before tables; collapse runs of blank
    # lines (outside fenced code) unless the file already had them
    if "\n\n\n" not in original:
        parts = re.split(r"(^(?:```|~~~)[^\n]*\n.*?^(?:```|~~~)[ \t]*$)", text, flags=re.M | re.S)
        text = "".join(p if i % 2 else re.sub(r"\n{3,}", "\n\n", p) for i, p in enumerate(parts))
    # keep a blank line after YAML front matter if the file had one
    if re.match(r"---\n.*?\n---\n\n", original, flags=re.S):
        text = re.sub(r"\A(---\n.*?\n---\n)(?!\n)", r"\1\n", text, flags=re.S)
    return text


def _compact_table_row(m):
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", m.group(0).strip())[1:-1]]
    if all(re.fullmatch(r":?-+:?", c) for c in cells):
        cells = [(":" if c.startswith(":") else "") + "---" + (":" if c.endswith(":") and len(c) > 1 else "")
                 for c in cells]
    return "|" + "|".join(f" {c} " if c else " " for c in cells) + "|"


def default_spell_langs():
    """Dictionaries switched on at first start: the interface language, plus
    the regional variant for Portuguese."""
    lang = i18n.language()
    if lang == "pt":
        return ["pt-PT"] if QLocale.system().name() == "pt_PT" else ["pt-BR"]
    return [c for c in SPELL_LANGS if c.startswith(lang + "-")] or ["en-US"]


def settings_format():
    # Windows: an .ini in %APPDATA% instead of the registry, so the word list
    # (woerterbuch.txt) can live next to it.
    return QSettings.Format.IniFormat if sys.platform == "win32" else QSettings.Format.NativeFormat


def data_dir() -> Path:
    """Writable per-user folder (plugins, dictionaries):
    Linux ~/.local/share/MattPad, Windows %APPDATA%\\MattPad,
    macOS ~/Library/Application Support/MattPad."""
    d = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    d.mkdir(parents=True, exist_ok=True)
    return d


def setup_dict_dir():
    """Spell-check dictionaries must live in one folder that also holds the
    user's word list. If the program folder is read-only (MSI, .app, Flatpak),
    copy the bundled dictionaries to the user's data folder."""
    global DICT_DIR
    bundled = APP_DIR / "dictionaries"
    if os.access(bundled, os.W_OK):
        DICT_DIR = bundled
        return
    DICT_DIR = data_dir() / "dictionaries"
    DICT_DIR.mkdir(parents=True, exist_ok=True)
    for f in bundled.glob("*.bdic"):
        dst = DICT_DIR / f.name
        if not dst.exists() or dst.stat().st_size != f.stat().st_size:
            shutil.copyfile(f, dst)


# --- plugins: themes + templates --------------------------------------------------
# A plugin is a folder with a plugin.json, CSS themes and Markdown templates.
# Plugins contain no program code, so installing one is harmless.

def _plugin_files(pdir, declared, subdir, pattern, key):
    """Entries declared in plugin.json, or else all files in the subfolder."""
    if declared is None:
        declared = [{key: str(f.relative_to(pdir))} for f in sorted((pdir / subdir).glob(pattern))]
    out = []
    for entry in declared:
        if not isinstance(entry, dict) or not entry.get(key):
            continue
        f = (pdir / entry[key]).resolve()
        if f.is_file() and f.is_relative_to(pdir.resolve()):
            out.append(dict(entry, path=f))
    return out


def load_plugins(roots):
    """roots: [(folder, builtin)]. A user plugin with the same id replaces a
    bundled one."""
    by_id = {}
    for root, builtin in roots:
        if not root.is_dir():
            continue
        for pdir in sorted(root.iterdir()):
            manifest = pdir / "plugin.json"
            if pdir.name.startswith(".") or not manifest.is_file():
                continue
            try:
                meta = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                print(f"{APP_ID}: Plugin {pdir.name} ignoriert: {e}", file=sys.stderr)
                continue
            p = {
                "id": str(meta.get("id") or pdir.name),
                "name": i18n.localized(meta.get("name")) or pdir.name,
                "version": str(meta.get("version", "")),
                "author": meta.get("author", ""),
                "description": i18n.localized(meta.get("description")),
                "license": i18n.localized(meta.get("license")),
                "dir": pdir,
                "builtin": builtin,
            }
            p["themes"] = [{"id": str(t.get("id") or t["path"].stem),
                            "name": i18n.localized(t.get("name")) or t["path"].stem,
                            "description": i18n.localized(t.get("description")),
                            "css": t["path"], "plugin": p}
                           for t in _plugin_files(pdir, meta.get("themes"), "themes", "*.css", "css")]
            p["templates"] = [{"name": i18n.localized(t.get("name")) or t["path"].stem,
                               "description": i18n.localized(t.get("description")),
                               "file": t["path"], "plugin": p}
                              for t in _plugin_files(pdir, meta.get("templates"), "templates", "*.md", "file")]
            by_id[p["id"]] = p
    return sorted(by_id.values(), key=lambda p: p["name"].lower())


def install_plugin_zip(zip_path, target_root):
    """Unpack a plugin .zip (plugin.json at the top or in one top folder)."""
    with zipfile.ZipFile(zip_path) as z:
        manifests = sorted((n for n in z.namelist()
                            if n.rsplit("/", 1)[-1] == "plugin.json" and n.count("/") <= 1), key=len)
        if not manifests:
            raise ValueError(T("Die ZIP-Datei enthält keine plugin.json."))
        prefix = manifests[0][:-len("plugin.json")]
        meta = json.loads(z.read(manifests[0]).decode("utf-8"))
        pid = re.sub(r"[^\w.-]", "_", str(meta.get("id") or Path(zip_path).stem))
        target_root.mkdir(parents=True, exist_ok=True)
        dest, tmp = target_root / pid, target_root / f".{pid}.tmp"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir()
        for info in z.infolist():
            if info.is_dir() or not info.filename.startswith(prefix):
                continue
            out = (tmp / info.filename[len(prefix):]).resolve()
            if not out.is_relative_to(tmp.resolve()):
                shutil.rmtree(tmp, ignore_errors=True)
                raise ValueError(T("Ungültiger Pfad in der ZIP-Datei: {name}", name=info.filename))
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(z.read(info))
        shutil.rmtree(dest, ignore_errors=True)
        tmp.rename(dest)
    return meta.get("name") or pid


def front_matter(text):
    """Simple 'key: value' pairs from a YAML front matter block."""
    m = re.match(r"---\n(.*?)\n---[ \t]*(?:\n|$)", text or "", flags=re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        kv = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
        if kv:
            out[kv.group(1).lower()] = kv.group(2).strip("\"'")
    return out


TEMPLATE_VARS = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def fill_template(text, values):
    return TEMPLATE_VARS.sub(lambda m: values.get(m.group(1).lower(), m.group(0)), text)


class TemplateDialog(QDialog):
    """Datei → Neu aus Vorlage: pick a template, enter title/author."""

    def __init__(self, window, templates, author):
        super().__init__(window)
        self.setWindowTitle(T("Neu aus Vorlage"))
        self.templates = templates
        self.list = QListWidget()
        for t in templates:
            it = QListWidgetItem(f"{t['name']}   ({t['plugin']['name']})")
            it.setToolTip(t["description"] or str(t["file"]))
            self.list.addItem(it)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        split = QSplitter()
        split.addWidget(self.list)
        split.addWidget(self.preview)
        split.setSizes([260, 460])
        self.desc = QLabel()
        self.desc.setWordWrap(True)
        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit(author)
        form = QFormLayout()
        form.addRow(T("Titel:"), self.title_edit)
        form.addRow(T("Autor/in:"), self.author_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(T("Dokument anlegen"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        lay.addWidget(split, 1)
        lay.addWidget(self.desc)
        lay.addLayout(form)
        lay.addWidget(buttons)
        self.list.currentRowChanged.connect(self.show_template)
        self.list.itemDoubleClicked.connect(lambda _: self.accept())
        self.list.setCurrentRow(0)
        self.resize(780, 520)

    def show_template(self, row):
        if 0 <= row < len(self.templates):
            t = self.templates[row]
            try:
                self.preview.setPlainText(t["file"].read_text(encoding="utf-8"))
            except OSError as e:
                self.preview.setPlainText(str(e))
            self.desc.setText(t["description"])

    def selected(self):
        row = self.list.currentRow()
        return self.templates[row] if 0 <= row < len(self.templates) else None


class PluginDialog(QDialog):
    """Extras → Plugins verwalten."""

    def __init__(self, window):
        super().__init__(window)
        self.window_ = window
        self.setWindowTitle(T("Plugins"))
        self.list = QListWidget()
        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setTextFormat(Qt.TextFormat.RichText)
        self.info.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info.setMinimumWidth(320)
        split = QSplitter()
        split.addWidget(self.list)
        split.addWidget(self.info)
        split.setSizes([240, 400])
        btn_install = QPushButton(QIcon.fromTheme("list-add"), T("Plugin installieren (.zip)…"))
        btn_install.clicked.connect(self.install)
        self.btn_remove = QPushButton(QIcon.fromTheme("list-remove"), T("Entfernen"))
        self.btn_remove.clicked.connect(self.remove)
        btn_folder = QPushButton(QIcon.fromTheme("folder-open"), T("Plugin-Ordner öffnen"))
        btn_folder.clicked.connect(window.open_plugin_folder)
        btn_reload = QPushButton(QIcon.fromTheme("view-refresh"), T("Neu laden"))
        btn_reload.clicked.connect(self.reload)
        close = QPushButton(T("Schließen"))
        close.clicked.connect(self.accept)
        row = QHBoxLayout()
        for b in (btn_install, self.btn_remove, btn_folder, btn_reload):
            row.addWidget(b)
        row.addStretch()
        row.addWidget(close)
        lay = QVBoxLayout(self)
        lay.addWidget(split, 1)
        lay.addLayout(row)
        self.list.currentRowChanged.connect(self.show_plugin)
        self.fill()
        self.resize(760, 440)

    def fill(self):
        self.list.clear()
        for p in self.window_.plugins:
            self.list.addItem(f"{p['name']} {p['version']}".strip())
        if self.window_.plugins:
            self.list.setCurrentRow(0)
        else:
            self.show_plugin(-1)

    def current_plugin(self):
        row = self.list.currentRow()
        plugins = self.window_.plugins
        return plugins[row] if 0 <= row < len(plugins) else None

    def show_plugin(self, _row):
        p = self.current_plugin()
        self.btn_remove.setEnabled(bool(p and not p["builtin"]))
        if not p:
            self.info.setText(T("Keine Plugins installiert."))
            return
        esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;")
        themes = ", ".join(esc(t["name"]) for t in p["themes"]) or "–"
        templates = ", ".join(esc(t["name"]) for t in p["templates"]) or "–"
        self.info.setText(
            f"<h3>{esc(p['name'])}</h3>"
            f"<p>{esc(p['description'])}</p>"
            f"<p><b>{T('Version')}:</b> {esc(p['version'] or '–')}<br>"
            f"<b>{T('Autor')}:</b> {esc(p['author'] or '–')}<br>"
            f"<b>{T('Lizenz')}:</b> {esc(p['license'] or '–')}<br>"
            f"<b>{T('Themes')}:</b> {themes}<br><b>{T('Vorlagen')}:</b> {templates}</p>"
            f"<p style='color:gray'>{T('Mitgeliefert') if p['builtin'] else T('Selbst installiert')}: "
            f"{esc(p['dir'])}</p>")

    def install(self):
        path, _ = QFileDialog.getOpenFileName(self, T("Plugin installieren"), str(Path.home()),
                                              T("Matt|Pad-Plugin (*.zip)"))
        if not path:
            return
        try:
            name = install_plugin_zip(path, self.window_.user_plugin_dir())
        except (OSError, ValueError, zipfile.BadZipFile) as e:
            QMessageBox.warning(self, T("Plugin installieren"), T("Installation fehlgeschlagen:\n{e}", e=e))
            return
        self.reload()
        QMessageBox.information(self, T("Plugin installieren"), T("„{name}“ wurde installiert.", name=name))

    def remove(self):
        p = self.current_plugin()
        if not p or p["builtin"]:
            return
        if QMessageBox.question(self, T("Plugin entfernen"), T("„{name}“ wirklich entfernen?", name=p['name'])) \
                != QMessageBox.StandardButton.Yes:
            return
        shutil.rmtree(p["dir"], ignore_errors=True)
        self.reload()

    def reload(self):
        self.window_.reload_plugins()
        self.fill()


def disk_icon(body: str) -> QIcon:
    """Small floppy-disk icon like Notepad++ uses for tab states."""
    pm = QPixmap(16, 16)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QColor(body).darker(150))
    p.setBrush(QColor(body))
    p.drawRoundedRect(1, 1, 14, 14, 2, 2)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#ffffff"))
    p.drawRect(4, 2, 8, 5)
    p.setBrush(QColor(body).darker(160))
    p.drawRect(4, 10, 8, 5)
    p.end()
    return QIcon(pm)


class Bridge(QObject):
    """Object exposed to editor.js via QWebChannel."""
    loaded = pyqtSignal()
    initialized = pyqtSignal(str)
    edited = pyqtSignal(str)

    @pyqtSlot()
    def pageReady(self):
        self.loaded.emit()

    @pyqtSlot(str)
    def ready(self, text):
        self.initialized.emit(text)

    @pyqtSlot(str)
    def changed(self, text):
        self.edited.emit(text)


class EditorPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        # Links clicked in the document open in the system browser.
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class EditorTab(QWebEngineView):
    modifiedChanged = pyqtSignal()
    textChanged = pyqtSignal()

    def __init__(self, window, path=None, text="", newline="\n", opts=None):
        super().__init__()
        self.window_ = window
        self.path = path
        self.text = text
        self.saved_text = text
        self.disk_text = text
        self.newline = newline
        self.encoding = "UTF-8"
        self.is_ready = False
        self.mode = opts.get("mode", "ir")
        self._opts = opts
        self.theme_href = None   # CSS of the plugin theme currently shown
        self.doc_lang = None

        page = EditorPage(self)
        self.setPage(page)
        s = page.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        self.bridge = Bridge(self)
        self.channel = QWebChannel(self)
        self.channel.registerObject("bridge", self.bridge)
        page.setWebChannel(self.channel)
        self.bridge.loaded.connect(self._on_page_loaded)
        self.bridge.initialized.connect(self._on_initialized)
        self.bridge.edited.connect(self._on_edited)

        self.setAcceptDrops(True)
        self.load(EDITOR_URL)

    # --- state -------------------------------------------------------------
    @property
    def modified(self):
        return self.text != self.saved_text

    def title(self):
        return Path(self.path).name if self.path else self.window_.untitled_name(self)

    def link_base(self):
        return QUrl.fromLocalFile(str(Path(self.path).parent) + "/").toString() if self.path else ""

    def js(self, code, callback=None):
        if callback:
            self.page().runJavaScript(code, callback)
        else:
            self.page().runJavaScript(code)

    def call(self, func, *args):
        self.js(f"{func}({', '.join(json.dumps(a) for a in args)})")

    # --- bridge callbacks --------------------------------------------------
    def _on_page_loaded(self):
        self.theme_href, self.doc_lang = self.window_.theme_href(self), self.window_.doc_lang(self)
        opts = dict(self._opts, linkBase=self.link_base(), themeHref=self.theme_href, lang=self.doc_lang)
        self.js(f"init({json.dumps(self.text)}, {json.dumps(opts)})")

    def _on_initialized(self, normalized):
        # Vditor normalizes the Markdown slightly; use that as the clean state
        # so a freshly opened file doesn't show up as modified.
        was_modified = self.modified
        self.text = normalized
        if not was_modified:
            self.saved_text = normalized
        self.is_ready = True
        self.modifiedChanged.emit()
        self.textChanged.emit()
        self.refresh_theme()

    def _on_edited(self, text):
        was = self.modified
        self.text = text
        if was != self.modified:
            self.modifiedChanged.emit()
        self.textChanged.emit()
        self.refresh_theme()

    def refresh_theme(self):
        """Apply the theme/language named in the front matter, or the default."""
        if not self.is_ready:
            return
        href, lang = self.window_.theme_href(self), self.window_.doc_lang(self)
        if href != self.theme_href:
            self.theme_href = href
            self.call("setThemeCSS", href)
        if lang != self.doc_lang:
            self.doc_lang = lang
            self.call("setDocLang", lang)

    def mark_saved(self):
        self.saved_text = self.text
        self.modifiedChanged.emit()

    def set_text(self, text):
        self.text = text
        self.call("setMarkdown", text)

    # --- Qt events ---------------------------------------------------------
    def contextMenuEvent(self, event):
        w = self.window_
        menu = QMenu(self)
        req = self.lastContextMenuRequest()
        if req and req.misspelledWord():
            suggestions = req.spellCheckerSuggestions()
            for word in suggestions[:8]:
                a = menu.addAction(word)
                f = a.font()
                f.setBold(True)
                a.setFont(f)
                a.triggered.connect(lambda _=False, word=word: self.page().replaceMisspelledWord(word))
            if not suggestions:
                menu.addAction(T("(keine Vorschläge)")).setEnabled(False)
            menu.addSeparator()
            word = req.misspelledWord()
            menu.addAction(QIcon.fromTheme("list-add"), T("„{word}“ zum Wörterbuch hinzufügen", word=word),
                           lambda: w.add_word(word))
            menu.addSeparator()
        menu.addAction(w.act_undo)
        menu.addAction(w.act_redo)
        menu.addSeparator()
        menu.addAction(w.act_cut)
        menu.addAction(w.act_copy)
        menu.addAction(w.act_paste)
        menu.addSeparator()
        menu.addAction(w.act_select_all)
        menu.addSeparator()
        menu.addMenu(w.menu_format)
        menu.exec(event.globalPos())

    def dragEnterEvent(self, event):
        if self._local_files(event):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        files = self._local_files(event)
        if files:
            event.acceptProposedAction()
            for f in files:
                self.window_.open_file(f)
        else:
            super().dropEvent(event)

    @staticmethod
    def _local_files(event):
        md = event.mimeData()
        if not md.hasUrls():
            return []
        files = [u.toLocalFile() for u in md.urls() if u.isLocalFile()]
        return [f for f in files if Path(f).suffix.lower() in
                (".md", ".markdown", ".mdown", ".mkd", ".txt")]


class FindBar(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window_ = window
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 3, 6, 3)
        lay.addWidget(QLabel(T("Suchen:")))
        self.edit = QLineEdit()
        self.edit.setClearButtonEnabled(True)
        self.edit.setMinimumWidth(260)
        self.edit.textChanged.connect(lambda: self.find())
        self.edit.returnPressed.connect(lambda: self.find())
        lay.addWidget(self.edit)
        prev_btn = QPushButton(T("◀ Zurück"))
        prev_btn.clicked.connect(lambda: self.find(backward=True))
        next_btn = QPushButton(T("Weiter ▶"))
        next_btn.clicked.connect(lambda: self.find())
        lay.addWidget(prev_btn)
        lay.addWidget(next_btn)
        self.case = QCheckBox(T("Groß-/Kleinschreibung"))
        self.case.toggled.connect(lambda: self.find())
        lay.addWidget(self.case)
        self.info = QLabel()
        lay.addWidget(self.info)
        lay.addStretch()
        close = QToolButton()
        close.setText("✕")
        close.setAutoRaise(True)
        close.clicked.connect(self.close_bar)
        lay.addWidget(close)
        self.hide()

    def open_bar(self):
        self.show()
        self.edit.setFocus()
        self.edit.selectAll()

    def close_bar(self):
        tab = self.window_.current()
        if tab:
            tab.page().findText("")
            tab.setFocus()
            tab.call("focusEditor")
        self.hide()

    def find(self, backward=False):
        tab = self.window_.current()
        if not tab:
            return
        flags = QWebEnginePage.FindFlag(0)
        if backward:
            flags |= QWebEnginePage.FindFlag.FindBackward
        if self.case.isChecked():
            flags |= QWebEnginePage.FindFlag.FindCaseSensitively
        tab.page().findText(self.edit.text(), flags, self._on_result)

    def _on_result(self, result):
        if not self.edit.text():
            self.info.setText("")
        elif result.numberOfMatches() == 0:
            self.info.setText(f"<span style='color:#c00'>{T('Nicht gefunden')}</span>")
        else:
            self.info.setText(T("{a} von {b}", a=result.activeMatch(), b=result.numberOfMatches()))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close_bar()
        else:
            super().keyPressEvent(event)


class ReplaceDialog(QDialog):
    def __init__(self, window):
        super().__init__(window)
        self.window_ = window
        self.setWindowTitle(T("Ersetzen"))
        g = QGridLayout(self)
        g.addWidget(QLabel(T("Suchen nach:")), 0, 0)
        self.find_edit = QLineEdit()
        g.addWidget(self.find_edit, 0, 1)
        g.addWidget(QLabel(T("Ersetzen durch:")), 1, 0)
        self.repl_edit = QLineEdit()
        g.addWidget(self.repl_edit, 1, 1)
        self.case = QCheckBox(T("Groß-/Kleinschreibung beachten"))
        g.addWidget(self.case, 2, 1)
        self.regex = QCheckBox(T("Regulärer Ausdruck"))
        g.addWidget(self.regex, 3, 1)
        self.info = QLabel()
        g.addWidget(self.info, 4, 0, 1, 2)
        btn = QPushButton(T("Alle ersetzen"))
        btn.setDefault(True)
        btn.clicked.connect(self.replace_all)
        g.addWidget(btn, 0, 2)
        close = QPushButton(T("Schließen"))
        close.clicked.connect(self.close)
        g.addWidget(close, 1, 2)
        self.resize(480, 0)

    def replace_all(self):
        tab = self.window_.current()
        needle = self.find_edit.text()
        if not tab or not needle:
            return
        pattern = needle if self.regex.isChecked() else re.escape(needle)
        flags = 0 if self.case.isChecked() else re.IGNORECASE
        try:
            repl = self.repl_edit.text()
            if not self.regex.isChecked():
                repl = repl.replace("\\", "\\\\")
            new, count = re.subn(pattern, repl, tab.text, flags=flags)
        except re.error as e:
            self.info.setText(T("Fehler im Ausdruck: {e}", e=e))
            return
        if count:
            tab.set_text(new)
        self.info.setText(T("{count} Vorkommen ersetzt.", count=count))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        fmt = settings_format()
        self.settings = QSettings(fmt, QSettings.Scope.UserScope, APP_ID, APP_ID)
        self.migrate_settings(fmt)
        self.plugins, self.themes, self.templates = [], {}, []
        self.load_plugin_data()
        self.icon_saved = disk_icon("#3b7dd8")
        self.icon_modified = disk_icon("#d83b3b")
        self.untitled_counter = 0
        self.untitled_names = {}
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.on_file_changed_on_disk)

        self.setWindowIcon(QIcon(str(APP_DIR / "mattpad.svg")))
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_current_changed)
        self.tabs.tabBarDoubleClicked.connect(lambda i: self.new_file() if i < 0 else None)
        self.tabs.tabBar().installEventFilter(self)

        self.find_bar = FindBar(self)
        central = QWidget()
        v = QVBoxLayout(central)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self.tabs)
        v.addWidget(self.find_bar)
        self.setCentralWidget(central)

        self.build_actions()
        self.build_menus()
        self.build_toolbar()
        self.build_statusbar()

        self.replace_dialog = None
        self.user_dict = self.build_user_dict()
        self.words_watcher = QFileSystemWatcher(self)
        self.words_watcher.fileChanged.connect(
            lambda p: QTimer.singleShot(300, lambda: self.on_user_words_changed(p)))
        geo = self.settings.value("geometry")
        if geo:
            self.restoreGeometry(geo)
        else:
            # first start: fit small screens (laptops, 1366×768)
            avail = QApplication.primaryScreen().availableGeometry()
            self.resize(min(1100, int(avail.width() * 0.9)), min(780, int(avail.height() * 0.9)))

    def migrate_settings(self, fmt):
        """Take over settings and word list from the old name 'MathiasPad'."""
        if self.settings.allKeys():
            return
        old = QSettings(fmt, QSettings.Scope.UserScope, "MathiasPad", "MathiasPad")
        if not old.allKeys():
            return
        for k in old.allKeys():
            self.settings.setValue(k, old.value(k))
        self.settings.sync()
        words = Path(old.fileName()).parent / "woerterbuch.txt"
        if words.exists() and not self.user_words_file().exists():
            self.user_words_file().parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(words, self.user_words_file())

    # --- plugins -----------------------------------------------------------
    def user_plugin_dir(self):
        return data_dir() / "plugins"

    def load_plugin_data(self):
        self.plugins = load_plugins([(APP_DIR / "plugins", True), (self.user_plugin_dir(), False)])
        self.themes = {t["id"]: t for p in self.plugins for t in p["themes"]}
        self.templates = [t for p in self.plugins for t in p["templates"]]

    def reload_plugins(self):
        self.load_plugin_data()
        self.fill_theme_menu()
        for t in self.all_tabs():
            t.theme_href = None   # force reloading the CSS (it may have changed)
            t.refresh_theme()

    def open_plugin_folder(self):
        d = self.user_plugin_dir()
        d.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(d)))

    def show_plugins(self):
        PluginDialog(self).exec()

    def theme_for(self, tab):
        """Theme named in the document's front matter ('theme: id'), else the default."""
        tid = front_matter(tab.text).get("theme") if tab else None
        if tid not in self.themes:
            tid = self.settings.value("theme", "")
        return self.themes.get(tid)

    def theme_href(self, tab):
        t = self.theme_for(tab)
        if not t:
            return None
        try:
            stamp = int(t["css"].stat().st_mtime)
        except OSError:
            return None
        return QUrl.fromLocalFile(str(t["css"])).toString() + f"?v={stamp}"

    @staticmethod
    def doc_lang(tab):
        lang = front_matter(tab.text).get("lang", "") if tab else ""
        return lang if re.fullmatch(r"[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*", lang) else None

    def fill_theme_menu(self):
        m = self.menu_theme
        m.clear()
        group = QActionGroup(m)
        current = self.settings.value("theme", "")
        if current not in self.themes:
            current = ""
        entries = [("", T("Standard (ohne Theme)"), "")] + \
                  [(t["id"], t["name"], t["description"] or t["plugin"]["name"]) for t in self.themes.values()]
        for i, (tid, name, tip) in enumerate(entries):
            a = m.addAction(name)
            a.setCheckable(True)
            a.setChecked(tid == current)
            a.setToolTip(tip)
            a.setStatusTip(T("{tip} – Theme-ID für die Kopfdaten: theme: {tid}", tip=tip, tid=tid) if tid else "")
            group.addAction(a)
            a.triggered.connect(lambda _=False, tid=tid: self.set_theme(tid))
            if i == 0 and len(entries) > 1:
                m.addSeparator()
        m.addSeparator()
        m.addAction(QIcon.fromTheme("preferences-plugin"), T("Plugins verwalten…"), self.show_plugins)

    def set_ui_language(self, code):
        self.settings.setValue("ui_lang", code)
        new = code or i18n.pick_language(QLocale.system().uiLanguages())
        if new != i18n.language():
            i18n.set_language(new)   # only for this message; the menus follow after a restart
            QMessageBox.information(self, T("Sprache"),
                                    T("Die neue Sprache gilt nach einem Neustart von Matt|Pad."))

    def set_theme(self, tid):
        self.settings.setValue("theme", tid)
        for t in self.all_tabs():
            t.refresh_theme()
        tab = self.current()
        if tab and front_matter(tab.text).get("theme") in self.themes and tid != front_matter(tab.text)["theme"]:
            self.statusBar().showMessage(
                T("Hinweis: Dieses Dokument legt sein Theme selbst in den Kopfdaten fest (theme: …)."), 6000)

    def new_from_template(self):
        if not self.templates:
            QMessageBox.information(self, T("Neu aus Vorlage"),
                                    T("Keine Vorlagen vorhanden. Vorlagen kommen über Plugins (Extras → Plugins verwalten)."))
            return
        dlg = TemplateDialog(self, self.templates, self.settings.value("author", ""))
        if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.selected():
            return
        t = dlg.selected()
        author = dlg.author_edit.text().strip()
        if author:
            self.settings.setValue("author", author)
        try:
            raw = t["file"].read_text(encoding="utf-8").replace("\r\n", "\n")
        except OSError as e:
            QMessageBox.warning(self, T("Fehler"), T("Vorlage konnte nicht gelesen werden:\n{e}", e=e))
            return
        today = datetime.date.today()
        title = dlg.title_edit.text().strip()
        text = fill_template(raw, {"title": title, "titel": title, "titulo": title,
                                   "author": author, "autor": author,
                                   "date": today.isoformat(), "datum": today.isoformat(), "fecha": today.isoformat(),
                                   "year": str(today.year), "jahr": str(today.year),
                                   "lang": i18n.language()})
        cur = self.current()
        if self.tabs.count() == 1 and cur and not cur.path and not cur.modified and not cur.text:
            self.tabs.removeTab(0)
            self.untitled_names.pop(cur, None)
            cur.deleteLater()
        tab = EditorTab(self, text=text, opts=self.editor_opts())
        tab.saved_text = None   # a new document from a template counts as unsaved
        self.add_tab(tab)
        if title:
            self.untitled_names[tab] = re.sub(r'[\\/:*?"<>|]', "", title)[:60] or self.untitled_name(tab)
            self.update_tab(tab)

    # --- options -----------------------------------------------------------
    def editor_opts(self):
        return {
            "mode": self.settings.value("mode", "ir"),
            "dark": self.settings.value("dark", False, type=bool),
            "outline": self.settings.value("outline", False, type=bool),
            "typewriter": self.settings.value("typewriter", False, type=bool),
            "uiLang": i18n.VDITOR_LANG.get(i18n.language(), "en_US"),
        }

    # --- UI construction ---------------------------------------------------
    def action(self, text, slot, shortcut=None, icon=None, hint=None, checkable=False):
        a = QAction(text, self)
        if icon:
            a.setIcon(QIcon.fromTheme(icon))
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        if hint:
            # Shown in the menu only; the editor itself handles the key.
            a.setText(f"{text}\t{hint}")
        a.setCheckable(checkable)
        a.triggered.connect(slot)
        return a

    def build_actions(self):
        A = self.action
        self.act_new = A(T("&Neu"), self.new_file, "Ctrl+N", "document-new")
        self.act_new_template = A(T("Neu aus &Vorlage…"), self.new_from_template, "Ctrl+Shift+N", "document-new-from-template")
        self.act_plugins = A(T("&Plugins verwalten…"), self.show_plugins, None, "preferences-plugin")
        self.act_open = A(T("Ö&ffnen…"), self.open_dialog, "Ctrl+O", "document-open")
        self.act_save = A(T("&Speichern"), self.save, "Ctrl+S", "document-save")
        self.act_save_as = A(T("Speichern &unter…"), self.save_as, "Ctrl+Alt+S", "document-save-as")
        self.act_save_all = A(T("A&lle speichern"), self.save_all, "Ctrl+Shift+S", "document-save-all")
        self.act_close = A(T("S&chließen"), lambda: self.close_tab(self.tabs.currentIndex()), "Ctrl+W", "document-close")
        self.act_close_all = A(T("Alle schli&eßen"), self.close_all, "Ctrl+Shift+W", "window-close")
        self.act_reload = A(T("Neu &laden"), self.reload_current, None, "view-refresh")
        self.act_export_html = A(T("Als &HTML exportieren…"), self.export_html, None, "text-html")
        self.act_export_pdf = A(T("Als &PDF exportieren…"), self.export_pdf, None, "application-pdf")
        self.act_print = A(T("&Drucken…"), self.print_doc, "Ctrl+P", "document-print")
        self.act_open_folder = A(T("Ordner im Dateimanager öffnen"), self.open_folder, None, "folder-open")
        self.act_quit = A(T("&Beenden"), self.close, "Ctrl+Q", "application-exit")

        self.act_undo = A(T("&Rückgängig"), lambda: self.cmd("undo"), None, "edit-undo", hint="Ctrl+Z")
        self.act_redo = A(T("&Wiederholen"), lambda: self.cmd("redo"), None, "edit-redo", hint="Ctrl+Y")
        WA = QWebEnginePage.WebAction
        self.act_cut = A(T("&Ausschneiden"), lambda: self.page_action(WA.Cut), None, "edit-cut", hint="Ctrl+X")
        self.act_copy = A(T("&Kopieren"), lambda: self.page_action(WA.Copy), None, "edit-copy", hint="Ctrl+C")
        self.act_paste = A(T("&Einfügen"), lambda: self.page_action(WA.Paste), None, "edit-paste", hint="Ctrl+V")
        self.act_paste_plain = A(T("Als reinen Text einfügen"), lambda: self.page_action(WA.PasteAndMatchStyle), None, None, hint="Ctrl+Shift+V")
        self.act_select_all = A(T("Alles &markieren"), lambda: self.page_action(WA.SelectAll), None, "edit-select-all", hint="Ctrl+A")

        self.act_find = A(T("&Suchen…"), self.find_bar.open_bar, "Ctrl+F", "edit-find")
        self.act_find_next = A(T("&Weitersuchen"), lambda: self.find_bar.find(), "F3", "go-down-search")
        self.act_find_prev = A(T("&Rückwärts suchen"), lambda: self.find_bar.find(backward=True), "Shift+F3", "go-up-search")
        self.act_replace = A(T("&Ersetzen…"), self.show_replace, "Ctrl+H", "edit-find-replace")

        self.act_bold = A(T("&Fett"), lambda: self.cmd("bold"), None, "format-text-bold", hint="Ctrl+B")
        self.act_italic = A(T("&Kursiv"), lambda: self.cmd("italic"), None, "format-text-italic", hint="Ctrl+I")
        self.act_strike = A(T("&Durchgestrichen"), lambda: self.cmd("strike"), None, "format-text-strikethrough", hint="Ctrl+D")
        self.act_inline_code = A(T("Inline-&Code"), lambda: self.cmd("inline-code"), None, "format-text-code", hint="Ctrl+G")
        self.act_link = A(T("&Link"), lambda: self.cmd("link"), None, "insert-link", hint="Ctrl+K")
        self.act_quote = A(T("&Zitat"), lambda: self.cmd("quote"), None, "format-text-blockquote", hint="Ctrl+;")
        self.act_list = A(T("&Aufzählung"), lambda: self.cmd("list"), None, "format-list-unordered", hint="Ctrl+L")
        self.act_olist = A(T("&Nummerierte Liste"), lambda: self.cmd("ordered-list"), None, "format-list-ordered", hint="Ctrl+Shift+L")
        self.act_check = A(T("Auf&gabenliste"), lambda: self.cmd("check"), None, "checkbox", hint="Ctrl+J")
        self.act_code = A(T("Code&block"), lambda: self.cmd("code"), None, "code-context", hint="Ctrl+U")
        self.act_table = A(T("&Tabelle"), lambda: self.cmd("table"), None, "insert-table", hint="Ctrl+M")
        self.act_hr = A(T("&Trennlinie"), lambda: self.cmd("line"), None, "newline", hint="Ctrl+Shift+H")
        self.act_headings = [A(T("Überschrift &{n}", n=n), lambda _=False, n=n: self.cmd("headings", n),
                               None, None, hint=f"Ctrl+Alt+{n}") for n in range(1, 7)]

        self.act_mode = {}
        for key, name in MODE_NAMES.items():
            a = A(T(name), lambda _=False, k=key: self.set_mode(k), None, None, checkable=True)
            self.act_mode[key] = a
        self.act_mode["ir"].setShortcut("Ctrl+1")
        self.act_mode["sv"].setShortcut("Ctrl+2")
        self.act_mode["wysiwyg"].setShortcut("Ctrl+3")
        self.act_outline = A(T("&Gliederung anzeigen"), self.toggle_outline, "F8", "view-list-tree", checkable=True)
        self.act_dark = A(T("&Dunkles Design"), self.toggle_dark, None, "weather-clear-night", checkable=True)
        self.act_typewriter = A(T("&Schreibmaschinenmodus"), self.toggle_typewriter, None, None, checkable=True)
        self.act_fullscreen = A(T("&Vollbild"), self.toggle_fullscreen, "F11", "view-fullscreen", checkable=True)
        self.act_zoom_in = A(T("Ver&größern"), lambda: self.zoom(0.1), "Ctrl++", "zoom-in")
        self.act_zoom_out = A(T("Ver&kleinern"), lambda: self.zoom(-0.1), "Ctrl+-", "zoom-out")
        self.act_zoom_reset = A(T("&Originalgröße"), lambda: self.zoom(None), "Ctrl+0", "zoom-original")
        self.act_about = A(T("Über Matt|&Pad"), self.about, None, "help-about")
        self.act_license = A(T("&Lizenz (GNU GPL)"), self.show_license, None, "license")
        self.act_spell = A(T("Rechtschreibprüfung &aktiv"), self.apply_spellcheck, "F7", "tools-check-spelling", checkable=True)
        self.act_spell.setChecked(self.settings.value("spell_on", True, type=bool))
        active = self.settings.value("spell_langs", default_spell_langs(), type=list)
        self.act_spell_langs = {}
        for code, name in SPELL_LANGS.items():
            a = A(name, self.apply_spellcheck, None, None, checkable=True)
            a.setChecked(code in active)
            self.act_spell_langs[code] = a
        self.act_edit_words = A(T("&Benutzerwörterbuch bearbeiten…"), self.edit_user_words, None, "accessories-dictionary")
        self.act_md_help = A(T("Markdown-&Kurzreferenz"), self.md_help, "F1", "help-contents")

        self.act_mode[self.settings.value("mode", "ir")].setChecked(True)
        self.act_outline.setChecked(self.settings.value("outline", False, type=bool))
        self.act_dark.setChecked(self.settings.value("dark", False, type=bool))
        self.act_typewriter.setChecked(self.settings.value("typewriter", False, type=bool))

        # Extra shortcuts known from Notepad++ / browsers
        for seq, slot in (("Ctrl+Tab", lambda: self.cycle_tab(1)),
                          ("Ctrl+Shift+Tab", lambda: self.cycle_tab(-1)),
                          ("Ctrl+=", lambda: self.zoom(0.1))):
            a = QAction(self)
            a.setShortcut(QKeySequence(seq))
            a.triggered.connect(slot)
            self.addAction(a)

    def build_menus(self):
        mb = self.menuBar()
        m = mb.addMenu(T("&Datei"))
        m.addActions([self.act_new, self.act_new_template, self.act_open])
        self.menu_recent = m.addMenu(QIcon.fromTheme("document-open-recent"), T("&Zuletzt geöffnet"))
        self.menu_recent.aboutToShow.connect(self.fill_recent_menu)
        m.addAction(self.act_reload)
        m.addSeparator()
        m.addActions([self.act_save, self.act_save_as, self.act_save_all])
        m.addSeparator()
        m.addActions([self.act_close, self.act_close_all])
        m.addSeparator()
        m.addActions([self.act_export_html, self.act_export_pdf, self.act_open_folder])
        m.addSeparator()
        m.addAction(self.act_print)
        m.addSeparator()
        m.addAction(self.act_quit)

        m = mb.addMenu(T("&Bearbeiten"))
        m.addActions([self.act_undo, self.act_redo])
        m.addSeparator()
        m.addActions([self.act_cut, self.act_copy, self.act_paste, self.act_paste_plain])
        m.addSeparator()
        m.addAction(self.act_select_all)

        m = mb.addMenu(T("&Suchen"))
        m.addActions([self.act_find, self.act_find_next, self.act_find_prev])
        m.addSeparator()
        m.addAction(self.act_replace)

        m = self.menu_format = mb.addMenu(T("&Format"))
        hm = m.addMenu(QIcon.fromTheme("format-text-heading"), T("Ü&berschrift"))
        hm.addActions(self.act_headings)
        m.addSeparator()
        m.addActions([self.act_bold, self.act_italic, self.act_strike, self.act_inline_code, self.act_link])
        m.addSeparator()
        m.addActions([self.act_list, self.act_olist, self.act_check, self.act_quote])
        m.addSeparator()
        m.addActions([self.act_code, self.act_table, self.act_hr])

        m = mb.addMenu(T("&Ansicht"))
        mm = m.addMenu(T("Editor-&Modus"))
        mm.addActions(list(self.act_mode.values()))
        m.addAction(self.act_outline)
        m.addSeparator()
        self.menu_theme = m.addMenu(QIcon.fromTheme("preferences-desktop-theme-global"), T("&Theme"))
        self.fill_theme_menu()
        m.addActions([self.act_dark, self.act_typewriter, self.act_fullscreen])
        m.addSeparator()
        m.addActions([self.act_zoom_in, self.act_zoom_out, self.act_zoom_reset])

        m = mb.addMenu(T("E&xtras"))
        sm = m.addMenu(QIcon.fromTheme("tools-check-spelling"), T("&Rechtschreibprüfung"))
        sm.addAction(self.act_spell)
        sm.addSeparator()
        sm.addActions(list(self.act_spell_langs.values()))
        sm.addSeparator()
        sm.addAction(self.act_edit_words)
        m.addSeparator()
        m.addAction(self.act_plugins)
        lm = m.addMenu(QIcon.fromTheme("preferences-desktop-locale"), T("&Sprache der Oberfläche"))
        group = QActionGroup(lm)
        current = self.settings.value("ui_lang", "")
        system = i18n.LANGUAGES[i18n.pick_language(QLocale.system().uiLanguages())]
        for code, name in [("", T("Systemsprache ({lang})", lang=system))] + list(i18n.LANGUAGES.items()):
            a = lm.addAction(name)
            a.setCheckable(True)
            a.setChecked(code == current)
            group.addAction(a)
            a.triggered.connect(lambda _=False, code=code: self.set_ui_language(code))
            if not code:
                lm.addSeparator()

        m = mb.addMenu(T("&?"))
        m.addActions([self.act_md_help, self.act_license, self.act_about])

    def build_toolbar(self):
        tb = self.addToolBar(T("Werkzeugleiste"))
        tb.setObjectName("main_toolbar")
        tb.setIconSize(QSize(16, 16))
        tb.setMovable(False)
        groups = [
            [self.act_new, self.act_open, self.act_save, self.act_save_all, self.act_close, self.act_print],
            [self.act_cut, self.act_copy, self.act_paste],
            [self.act_undo, self.act_redo],
            [self.act_find, self.act_replace],
            [self.act_zoom_in, self.act_zoom_out],
            [self.act_bold, self.act_italic, self.act_strike, self.act_inline_code],
            [self.act_list, self.act_olist, self.act_check, self.act_quote,
             self.act_code, self.act_table, self.act_link],
            [self.act_outline, self.act_dark],
        ]
        for i, g in enumerate(groups):
            if i:
                tb.addSeparator()
            tb.addActions(g)
        # Heading dropdown
        btn = QToolButton()
        btn.setText("H")
        btn.setToolTip(T("Überschrift"))
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(btn)
        menu.addActions(self.act_headings)
        btn.setMenu(menu)
        tb.insertWidget(self.act_bold, btn)
        # Tooltips with shortcut
        for a in tb.actions():
            parts = a.text().replace("&", "").split("\t")
            sc = a.shortcut().toString() or (parts[1] if len(parts) > 1 else "")
            a.setToolTip(parts[0].rstrip("…") + (f" ({sc})" if sc else ""))

    def build_statusbar(self):
        sb = self.statusBar()
        self.st_type = QLabel(T("Markdown-Datei"))
        self.st_counts = QLabel()
        self.st_mode = QLabel()
        self.st_eol = QLabel()
        self.st_enc = QLabel()
        self.st_spell = QLabel()
        self.st_spell.setToolTip(T("Rechtschreibprüfung (F7 ein/aus, Sprachen unter Extras)"))
        sb.addWidget(self.st_type, 1)
        for w in (self.st_counts, self.st_mode, self.st_spell, self.st_eol, self.st_enc):
            w.setContentsMargins(8, 0, 8, 0)
            sb.addPermanentWidget(w)

    # --- tabs ----------------------------------------------------------------
    def current(self) -> EditorTab:
        return self.tabs.currentWidget()

    def all_tabs(self):
        return [self.tabs.widget(i) for i in range(self.tabs.count())]

    def untitled_name(self, tab):
        if tab not in self.untitled_names:
            self.untitled_counter += 1
            self.untitled_names[tab] = T("neu {n}", n=self.untitled_counter)
        return self.untitled_names[tab]

    def add_tab(self, tab):
        tab.modifiedChanged.connect(lambda t=tab: self.update_tab(t))
        tab.textChanged.connect(lambda t=tab: self.update_status() if t is self.current() else None)
        tab.setZoomFactor(self.settings.value("zoom", 1.0, type=float))
        i = self.tabs.addTab(tab, self.icon_saved, tab.title())
        self.tabs.setCurrentIndex(i)
        self.update_tab(tab)
        tab.setFocus()
        return tab

    def new_file(self):
        return self.add_tab(EditorTab(self, opts=self.editor_opts()))

    def update_tab(self, tab):
        i = self.tabs.indexOf(tab)
        if i < 0:
            return
        self.tabs.setTabIcon(i, self.icon_modified if tab.modified else self.icon_saved)
        self.tabs.setTabText(i, tab.title())
        self.tabs.setTabToolTip(i, tab.path or tab.title())
        if tab is self.current():
            self.update_title()

    def update_title(self):
        tab = self.current()
        if not tab:
            self.setWindowTitle(APP_NAME)
            return
        name = tab.path or tab.title()
        self.setWindowTitle(f"{'*' if tab.modified else ''}{name} - {APP_NAME}")

    def update_status(self):
        tab = self.current()
        if not tab:
            return
        t = tab.text
        words = len(re.findall(r"\w+", t))
        lines = t.count("\n") + 1 if t else 1
        sep = lambda n: f"{n:,}".replace(",", "." if i18n.language() in ("de", "es", "pt") else ",")
        self.st_counts.setText(T("Länge: {chars}    Zeilen: {lines}    Wörter: {words}",
                                 chars=sep(len(t)), lines=sep(lines), words=sep(words)))
        self.st_mode.setText(T(MODE_NAMES.get(tab.mode, tab.mode)))
        self.st_eol.setText("Windows (CR LF)" if tab.newline == "\r\n" else "Unix (LF)")
        self.st_enc.setText(tab.encoding)

    def on_current_changed(self, _):
        self.update_title()
        self.update_status()
        tab = self.current()
        if tab:
            for k, a in self.act_mode.items():
                a.setChecked(k == tab.mode)
            if self.find_bar.isVisible():
                self.find_bar.find()

    def cycle_tab(self, step):
        n = self.tabs.count()
        if n:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + step) % n)

    def eventFilter(self, obj, event):
        # middle click on a tab closes it, like in Notepad++
        if obj is self.tabs.tabBar() and event.type() == event.Type.MouseButtonRelease \
                and event.button() == Qt.MouseButton.MiddleButton:
            i = obj.tabAt(event.position().toPoint())
            if i >= 0:
                self.close_tab(i)
                return True
        return super().eventFilter(obj, event)

    def close_tab(self, index, keep_one=True):
        tab = self.tabs.widget(index)
        if tab is None:
            return True
        if tab.modified:
            self.tabs.setCurrentIndex(index)
            r = QMessageBox.question(
                self, T("Speichern?"), T("„{name}“ wurde geändert.\nÄnderungen speichern?", name=tab.title()),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Save)
            if r == QMessageBox.StandardButton.Cancel:
                return False
            if r == QMessageBox.StandardButton.Save and not self.save(tab):
                return False
        if tab.path and tab.path in self.watcher.files():
            if not any(t.path == tab.path for t in self.all_tabs() if t is not tab):
                self.watcher.removePath(tab.path)
        self.tabs.removeTab(index)
        self.untitled_names.pop(tab, None)
        tab.deleteLater()
        if keep_one and self.tabs.count() == 0:
            self.new_file()
        return True

    def close_all(self):
        for i in reversed(range(self.tabs.count())):
            if not self.close_tab(i, keep_one=False):
                break
        if self.tabs.count() == 0:
            self.new_file()

    # --- files ---------------------------------------------------------------
    @staticmethod
    def read_file(path):
        raw = Path(path).read_bytes()
        try:
            text, enc = raw.decode("utf-8-sig"), "UTF-8"
        except UnicodeDecodeError:
            text, enc = raw.decode("cp1252", errors="replace"), "ANSI (Windows-1252)"
        newline = "\r\n" if "\r\n" in text else "\n"
        return text.replace("\r\n", "\n"), newline, enc

    def open_dialog(self):
        start = self.settings.value("last_dir", str(Path.home()))
        files, _ = QFileDialog.getOpenFileNames(self, T("Öffnen"), start, T("Markdown (*.md *.markdown *.mdown *.mkd *.txt);;Alle Dateien (*)"))
        for f in files:
            self.open_file(f)

    def open_file(self, path):
        path = str(Path(path).resolve())
        for i, t in enumerate(self.all_tabs()):
            if t.path == path:
                self.tabs.setCurrentIndex(i)
                return t
        if not Path(path).exists():
            # Notepad++ behaviour: a missing file opens as a new, empty document
            text, newline, enc = "", "\n", "UTF-8"
        else:
            try:
                text, newline, enc = self.read_file(path)
            except OSError as e:
                QMessageBox.warning(self, T("Fehler"), T("Datei konnte nicht geöffnet werden:\n{e}", e=e))
                return None
        # replace a single empty, untouched "neu 1" tab
        cur = self.current()
        if self.tabs.count() == 1 and cur and not cur.path and not cur.modified and not cur.text:
            self.tabs.removeTab(0)
            self.untitled_names.pop(cur, None)
            cur.deleteLater()
        tab = EditorTab(self, path, text, newline, self.editor_opts())
        tab.encoding = enc
        self.add_tab(tab)
        if Path(path).exists():
            self.watcher.addPath(path)
        self.add_recent(path)
        self.settings.setValue("last_dir", str(Path(path).parent))
        return tab

    def save(self, tab=None):
        tab = tab or self.current()
        if not tab:
            return False
        if not tab.path:
            return self.save_as(tab)
        return self.write(tab, tab.path)

    def save_as(self, tab=None):
        tab = tab if isinstance(tab, EditorTab) else self.current()
        if not tab:
            return False
        start = tab.path or str(Path(self.settings.value("last_dir", str(Path.home()))) / f"{tab.title()}.md")
        path, _ = QFileDialog.getSaveFileName(self, T("Speichern unter"), start, T("Markdown (*.md *.markdown *.mdown *.mkd *.txt);;Alle Dateien (*)"))
        if not path:
            return False
        if not Path(path).suffix:
            path += ".md"
        if tab.path and tab.path in self.watcher.files():
            self.watcher.removePath(tab.path)
        tab.path = str(Path(path).resolve())
        tab.call("setLinkBase", tab.link_base())
        self.settings.setValue("last_dir", str(Path(path).parent))
        self.add_recent(tab.path)
        return self.write(tab, tab.path)

    def write(self, tab, path):
        data = tidy_markdown(tab.text, tab.disk_text)
        if data and not data.endswith("\n"):
            data += "\n"
        tidied = data
        data = data.replace("\n", tab.newline)
        enc = "utf-8" if tab.encoding.startswith("UTF") else "cp1252"
        try:
            if path in self.watcher.files():
                self.watcher.removePath(path)
            with open(path, "w", encoding=enc, errors="replace", newline="") as f:
                f.write(data)
            self.watcher.addPath(path)
        except OSError as e:
            QMessageBox.warning(self, T("Fehler"), T("Speichern fehlgeschlagen:\n{e}", e=e))
            return False
        tab.disk_text = tidied
        tab.mark_saved()
        self.statusBar().showMessage(T("Gespeichert: {path}", path=path), 3000)
        return True

    def save_all(self):
        for t in self.all_tabs():
            if t.modified:
                self.tabs.setCurrentWidget(t)
                if not self.save(t):
                    return

    def reload_current(self):
        tab = self.current()
        if not tab or not tab.path or not Path(tab.path).exists():
            return
        if tab.modified and QMessageBox.question(
                self, T("Neu laden"), T("Ungespeicherte Änderungen gehen verloren. Trotzdem neu laden?")) \
                != QMessageBox.StandardButton.Yes:
            return
        self.reload_tab(tab)

    def reload_tab(self, tab):
        text, newline, enc = self.read_file(tab.path)
        tab.newline, tab.encoding = newline, enc
        tab.disk_text = text
        tab.saved_text = None  # make the next normalized text the clean state
        tab.set_text(text)
        QTimer.singleShot(300, lambda: tab.js("getMarkdown()", lambda v: self._after_reload(tab, v)))

    def _after_reload(self, tab, value):
        if value is not None:
            tab.text = value
        tab.mark_saved()
        self.update_status()

    def on_file_changed_on_disk(self, path):
        # Some programs (and Syncthing) replace files; re-add the watch.
        QTimer.singleShot(200, lambda: self._check_disk(path))

    def _check_disk(self, path):
        if Path(path).exists() and path not in self.watcher.files():
            self.watcher.addPath(path)
        for tab in self.all_tabs():
            if tab.path != path:
                continue
            if not Path(path).exists():
                self.statusBar().showMessage(T("Datei wurde gelöscht oder verschoben: {path}", path=path), 6000)
                continue
            try:
                disk_text = self.read_file(path)[0]
            except OSError:
                continue
            if disk_text.rstrip("\n") in ((tab.saved_text or "").rstrip("\n"), tab.disk_text.rstrip("\n")):
                continue
            self.tabs.setCurrentWidget(tab)
            msg = T("„{path}“\n\nwurde von einem anderen Programm geändert.\nNeu laden?", path=path)
            if tab.modified:
                msg += T("\n\nACHTUNG: Deine ungespeicherten Änderungen gehen dabei verloren.")
            if QMessageBox.question(self, T("Datei geändert"), msg) == QMessageBox.StandardButton.Yes:
                self.reload_tab(tab)
            else:
                tab.saved_text = None
                tab.modifiedChanged.emit()

    def add_recent(self, path):
        recent = [p for p in self.settings.value("recent", [], type=list) if p != path]
        recent.insert(0, path)
        self.settings.setValue("recent", recent[:MAX_RECENT])

    def fill_recent_menu(self):
        self.menu_recent.clear()
        recent = self.settings.value("recent", [], type=list)
        for i, p in enumerate(recent, 1):
            a = self.menu_recent.addAction(f"&{i % 10}: {p}" if i <= 10 else p)
            a.triggered.connect(lambda _=False, p=p: self.open_file(p))
        if recent:
            self.menu_recent.addSeparator()
            self.menu_recent.addAction(T("Liste leeren"), lambda: self.settings.setValue("recent", []))
        else:
            self.menu_recent.addAction(T("(leer)")).setEnabled(False)

    def open_folder(self):
        tab = self.current()
        if tab and tab.path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(tab.path).parent)))

    # --- export ----------------------------------------------------------------
    def theme_css(self, tab):
        """Theme CSS for export/print; relative url(...) made absolute so fonts
        and images of the plugin are found."""
        t = self.theme_for(tab)
        if not t:
            return ""
        try:
            css = t["css"].read_text(encoding="utf-8")
        except OSError:
            return ""
        base = t["css"].parent

        def absolute(m):
            url = m.group(2)
            if re.match(r"[a-z][\w+.-]*:|/|#", url, flags=re.I):
                return m.group(0)
            return f'url("{QUrl.fromLocalFile(str((base / url).resolve())).toString()}")'
        return re.sub(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""", absolute, css)

    def html_document(self, tab, body):
        css_path = APP_DIR / "vendor/vditor/dist/index.css"
        fm = front_matter(tab.text)
        esc = lambda v: v.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
        title = esc(fm.get("title") or (Path(tab.path).stem if tab.path else tab.title()))
        lang = self.doc_lang(tab) or i18n.language()
        meta = f'<meta name="author" content="{esc(fm["author"])}">' if fm.get("author") else ""
        base = f'<base href="{tab.link_base()}">' if tab.path else ""
        # the front matter is metadata, not part of the printed text
        body = re.sub(r'\A\s*<pre class="vditor-yml-front-matter"[^>]*>.*?</pre>\s*', "", body, flags=re.S)
        return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title>{meta}
<meta name="generator" content="{APP_NAME} {APP_VERSION}">{base}
<style>{css_path.read_text(encoding='utf-8')}</style>
<style>body{{max-width:820px;margin:40px auto;padding:0 24px;background:var(--mp-page-bg,#fff);}}
.vditor-reset{{font-size:16px;line-height:1.7;font-family:"Noto Sans","Segoe UI",sans-serif;}}
@media print{{body{{margin:0;max-width:none;}}}}</style>
<style>{self.theme_css(tab)}</style>
</head><body><div class="vditor-reset">{body}</div></body></html>"""

    def export_html(self):
        tab = self.current()
        if not tab:
            return
        start = str(Path(tab.path).with_suffix(".html")) if tab.path else f"{tab.title()}.html"
        path, _ = QFileDialog.getSaveFileName(self, T("Als HTML exportieren"), start, "HTML (*.html)")
        if path:
            tab.js("getHTML()", lambda body: self._write_html(tab, path, body))

    def _write_html(self, tab, path, body):
        Path(path).write_text(self.html_document(tab, body), encoding="utf-8")
        self.statusBar().showMessage(T("Exportiert: {path}", path=path), 4000)

    def export_pdf(self):
        tab = self.current()
        if not tab:
            return
        start = str(Path(tab.path).with_suffix(".pdf")) if tab.path else f"{tab.title()}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, T("Als PDF exportieren"), start, "PDF (*.pdf)")
        if path:
            tab.js("getHTML()", lambda body: self._print_pdf(tab, path, body))

    def _print_pdf(self, tab, path, body):
        page = QWebEnginePage(self)
        page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self._pdf_page = page

        def done(_path, ok):
            self.statusBar().showMessage(
                T("PDF gespeichert: {path}", path=path) if ok else T("PDF-Export fehlgeschlagen"), 4000)
            page.deleteLater()

        page.pdfPrintingFinished.connect(done)
        page.loadFinished.connect(lambda ok: page.printToPdf(path))
        base = QUrl.fromLocalFile(str(Path(tab.path).parent) + "/") if tab.path else QUrl.fromLocalFile(str(APP_DIR) + "/")
        page.setHtml(self.html_document(tab, body), base)

    def print_doc(self):
        tab = self.current()
        if not tab:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setDocName(Path(tab.path).stem if tab.path else tab.title())
        dlg = QPrintDialog(printer, self)
        dlg.setWindowTitle(T("Drucken"))
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._printer = printer
            tab.js("getHTML()", lambda body: self._print_doc(tab, printer, body))

    def _print_doc(self, tab, printer, body):
        # Render the exported HTML in an offscreen view, then hand it to the printer.
        view = QWebEngineView()
        view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        view.show()
        self._print_view = view
        self.statusBar().showMessage(T("Drucke…"))

        def done(ok):
            self.statusBar().showMessage(
                T("An den Drucker gesendet") if ok else T("Drucken fehlgeschlagen"), 4000)
            view.deleteLater()
            self._print_view = self._printer = None

        view.printFinished.connect(done)
        view.loadFinished.connect(lambda ok: view.print(printer))
        base = QUrl.fromLocalFile(str(Path(tab.path).parent) + "/") if tab.path else QUrl.fromLocalFile(str(APP_DIR) + "/")
        view.setHtml(self.html_document(tab, body), base)

    # --- editing commands --------------------------------------------------------
    def cmd(self, name, arg=None):
        tab = self.current()
        if tab:
            tab.setFocus()
            tab.call("cmd", name, arg)

    def page_action(self, action):
        tab = self.current()
        if tab:
            tab.setFocus()
            tab.page().triggerAction(action)

    def show_replace(self):
        if not self.replace_dialog:
            self.replace_dialog = ReplaceDialog(self)
        if self.find_bar.edit.text():
            self.replace_dialog.find_edit.setText(self.find_bar.edit.text())
        self.replace_dialog.show()
        self.replace_dialog.raise_()
        self.replace_dialog.find_edit.setFocus()

    # --- spell checking ----------------------------------------------------------
    def user_words_file(self):
        if sys.platform == "darwin":   # settings are a .plist in ~/Library/Preferences there
            return data_dir() / "woerterbuch.txt"
        return Path(self.settings.fileName()).parent / "woerterbuch.txt"

    def build_user_dict(self):
        """Compile the user's word list into a .bdic that Chromium loads as an
        extra "language". Chromium caches dictionaries by name, so every
        rebuild gets a new name."""
        if not shutil.which(CONVERT_DICT):   # e.g. Windows: no converter shipped
            return None
        words_file = self.user_words_file()
        words = []
        if words_file.exists():
            words = [w.strip() for w in words_file.read_text(encoding="utf-8").splitlines()]
        # the converter fails on lists with fewer than two words
        words = sorted({w for w in words if w and "/" not in w} | {"MattPad", "Matt", "Vditor"})
        for old in DICT_DIR.glob("x-personal-*.bdic"):
            old.unlink(missing_ok=True)
        name = f"x-personal-{int(time.time() * 1000)}"
        tmp = DICT_DIR / "user"
        tmp.with_suffix(".aff").write_text("SET UTF-8\n", encoding="utf-8")
        tmp.with_suffix(".dic").write_text(f"{len(words)}\n" + "\n".join(words) + "\n", encoding="utf-8")
        try:
            subprocess.run([CONVERT_DICT, str(tmp.with_suffix(".dic")), str(DICT_DIR / f"{name}.bdic")],
                           capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            return None
        finally:
            tmp.with_suffix(".aff").unlink(missing_ok=True)
            tmp.with_suffix(".dic").unlink(missing_ok=True)
        return name if (DICT_DIR / f"{name}.bdic").exists() else None

    def add_word(self, word):
        f = self.user_words_file()
        f.parent.mkdir(parents=True, exist_ok=True)
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(word + "\n")
        self.user_dict = self.build_user_dict()
        self.apply_spellcheck()
        self.statusBar().showMessage(T("„{word}“ ins Wörterbuch aufgenommen", word=word), 3000)

    def edit_user_words(self):
        f = self.user_words_file()
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("", encoding="utf-8")
        if str(f) not in self.words_watcher.files():
            self.words_watcher.addPath(str(f))
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(f)))

    def on_user_words_changed(self, path):
        if Path(path).exists() and path not in self.words_watcher.files():
            self.words_watcher.addPath(path)
        self.user_dict = self.build_user_dict()
        self.apply_spellcheck()

    def apply_spellcheck(self):
        langs = [c for c, a in self.act_spell_langs.items() if a.isChecked()]
        on = self.act_spell.isChecked() and bool(langs)
        self.settings.setValue("spell_on", self.act_spell.isChecked())
        self.settings.setValue("spell_langs", langs)
        profile = QWebEngineProfile.defaultProfile()
        profile.setSpellCheckLanguages(langs + ([self.user_dict] if self.user_dict else []))
        profile.setSpellCheckEnabled(on)
        self.st_spell.setText("ABC: " + " ".join(dict.fromkeys(c[:2].upper() for c in langs)) if on else T("ABC: aus"))

    # --- view ------------------------------------------------------------------
    def set_mode(self, mode):
        self.settings.setValue("mode", mode)
        for k, a in self.act_mode.items():
            a.setChecked(k == mode)
        tab = self.current()
        if tab:
            tab.mode = mode
            tab.call("cmd", "edit-mode", mode)
            self.update_status()

    def toggle_outline(self, on):
        self.settings.setValue("outline", on)
        for t in self.all_tabs():
            t.js(f"if (vditor && vditor.vditor.outline.element.style.display {'===' if on else '!=='} 'none') cmd('outline')")

    def toggle_dark(self, on):
        self.settings.setValue("dark", on)
        for t in self.all_tabs():
            t.call("setDark", on)

    def toggle_typewriter(self, on):
        self.settings.setValue("typewriter", on)
        for t in self.all_tabs():
            t.js(f"vditor && (vditor.vditor.options.typewriterMode = {'true' if on else 'false'})")

    def toggle_fullscreen(self, on):
        self.showFullScreen() if on else self.showNormal()

    def zoom(self, delta):
        z = 1.0 if delta is None else self.settings.value("zoom", 1.0, type=float) + delta
        z = max(0.5, min(3.0, round(z, 2)))
        self.settings.setValue("zoom", z)
        for t in self.all_tabs():
            t.setZoomFactor(z)
        self.statusBar().showMessage(T("Zoom: {z} %", z=int(z * 100)), 1500)

    def md_help(self):
        names = {"de": "Kurzreferenz.md", "en": "Quick reference.md",
                 "es": "Referencia rápida.md", "pt": "Referência rápida.md"}
        p = APP_DIR / "help" / names.get(i18n.language(), names["en"])
        if p.exists():
            self.open_file(p)

    def about(self):
        QMessageBox.about(self, T("Über {app}", app=APP_NAME),
                          f"<h3>{APP_NAME} {APP_VERSION}</h3>"
                          + T("Minimalistischer Markdown-Editor<br>Live-Darstellung wie Typora, Oberfläche wie Notepad++.<br>Vorlagen und Themes über Plugins.")
                          + f"<br><br>{APP_COPYRIGHT}<br>"
                          + T("Freie Software unter der GNU General Public License, Version 3 oder später (GPL-3.0-or-later). Ohne jede Gewährleistung.")
                          + "<br><br>"
                          + T("Verwendet: Vditor (MIT), Qt / PyQt6 (GPL), Python, Hunspell-Wörterbücher, Breeze-Symbole (LGPL)."))

    def show_license(self):
        p = APP_DIR / "LICENSE"
        dlg = QDialog(self)
        dlg.setWindowTitle(T("{app} – Lizenz", app=APP_NAME))
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(p.read_text(encoding="utf-8") if p.exists()
                          else "GNU General Public License v3: https://www.gnu.org/licenses/gpl-3.0.html")
        f = text.font()
        f.setFamily("monospace")
        text.setFont(f)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dlg.reject)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel(f"{APP_NAME} {APP_VERSION} – {APP_COPYRIGHT}<br>"
                             + T("Lizenz: GNU GPL, Version 3 oder später")))
        lay.addWidget(text)
        lay.addWidget(buttons)
        dlg.resize(680, 600)
        dlg.exec()

    # --- session -------------------------------------------------------------------
    def restore_session(self):
        files = [p for p in self.settings.value("session", [], type=list) if Path(p).exists()]
        for p in files:
            self.open_file(p)
        idx = self.settings.value("session_index", 0, type=int)
        if files and 0 <= idx < self.tabs.count():
            self.tabs.setCurrentIndex(idx)
        return bool(files)

    def closeEvent(self, event):
        session = [t.path for t in self.all_tabs() if t.path]
        cur = self.current()
        for i in reversed(range(self.tabs.count())):
            if self.tabs.widget(i).modified and not self.close_tab(i, keep_one=False):
                event.ignore()
                return
        self.settings.setValue("session", session)
        self.settings.setValue("session_index", session.index(cur.path) if cur and cur.path in session else 0)
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


class App(QApplication):
    """Collects macOS 'open document' events (Finder double-click, dock drop),
    which arrive as events instead of command line arguments."""
    fileOpenRequested = pyqtSignal(str)

    def __init__(self, argv):
        super().__init__(argv)
        self.pending_files = []

    def event(self, e):
        if e.type() == QEvent.Type.FileOpen and e.file():
            self.pending_files.append(e.file())
            self.fileOpenRequested.emit(e.file())
            return True
        return super().event(e)


def main():
    if sys.platform == "win32":
        # GPU rendering leaves the editor blank on some drivers/VMs/RDP; a text
        # editor doesn't need it.
        os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")
    QApplication.setApplicationName(APP_ID)
    QApplication.setApplicationVersion(APP_VERSION)
    setup_dict_dir()   # before Qt WebEngine starts
    os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = str(DICT_DIR)
    app = App(sys.argv)
    app.setDesktopFileName(os.environ.get("FLATPAK_ID") or "mattpad")
    # interface language: chosen in the menu, else the computer's language
    ui_lang = QSettings(settings_format(), QSettings.Scope.UserScope, APP_ID, APP_ID).value("ui_lang", "")
    i18n.set_language(ui_lang or i18n.pick_language(QLocale.system().uiLanguages()))
    qt_tr = QTranslator(app)
    qt_name = f"qtbase_{i18n.QT_TRANSLATION[i18n.language()]}"
    for d in (QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath),
              str(APP_DIR / "PyQt6" / "Qt6" / "translations"), "/app/translations"):
        if qt_tr.load(qt_name, d):
            app.installTranslator(qt_tr)
            break
    if (APP_DIR / "icons").is_dir():
        # Windows/macOS have no icon theme; the build bundles the needed Breeze icons.
        QIcon.setThemeSearchPaths([str(APP_DIR / "icons")] + QIcon.themeSearchPaths())
        QIcon.setThemeName("breeze")
    files = [a for a in sys.argv[1:] if not a.startswith("-")]

    # Single instance: hand files to an already running window (like Notepad++).
    sock = QLocalSocket()
    sock.connectToServer(SERVER_NAME)
    if sock.waitForConnected(300):
        sock.write(json.dumps([str(Path(f).resolve()) for f in files]).encode())
        sock.waitForBytesWritten(1000)
        sock.disconnectFromServer()
        return 0

    win = MainWindow()
    win.apply_spellcheck()
    server = QLocalServer()
    QLocalServer.removeServer(SERVER_NAME)
    server.listen(SERVER_NAME)

    def on_connection():
        conn = server.nextPendingConnection()

        def read():
            try:
                paths = json.loads(bytes(conn.readAll()).decode() or "[]")
            except ValueError:
                paths = []
            for p in paths:
                win.open_file(p)
            win.setWindowState(win.windowState() & ~Qt.WindowState.WindowMinimized)
            win.raise_()
            win.activateWindow()

        conn.readyRead.connect(read)
        conn.disconnected.connect(conn.deleteLater)

    server.newConnection.connect(on_connection)

    files += app.pending_files
    app.pending_files.clear()
    app.fileOpenRequested.connect(lambda f: (app.pending_files.clear(), win.open_file(f)))
    if files:
        for f in files:
            win.open_file(f)
    elif not win.restore_session():
        win.new_file()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
