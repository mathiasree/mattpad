# Matt|Pad – Übersetzungen der Oberfläche
# Copyright (C) 2026 Mathias Ree – GPL-3.0-or-later
#
# Schlüssel = deutscher Originaltext aus mattpad.py. Fehlt eine Übersetzung,
# erscheint der deutsche Text. "&" markiert die Alt-Taste im Menü.
# Neue Sprache: Kürzel in LANGUAGES eintragen und ein Wörterbuch in TR anlegen.

LANGUAGES = {"de": "Deutsch", "en": "English", "es": "Español", "pt": "Português"}
VDITOR_LANG = {"de": "de_DE", "en": "en_US", "es": "es_ES", "pt": "pt_BR"}
QT_TRANSLATION = {"de": "de", "en": "en", "es": "es", "pt": "pt_BR"}

_lang = "de"


def set_language(lang):
    global _lang
    _lang = lang if lang in LANGUAGES else "en"


def language():
    return _lang


def T(text, **kw):
    s = TR.get(_lang, {}).get(text, text)
    return s.format(**kw) if kw else s


def pick_language(ui_languages):
    """First supported language from the system's list (e.g. ['es-CL', 'es'])."""
    for name in ui_languages:
        code = name.replace("_", "-").split("-")[0].lower()
        if code in LANGUAGES:
            return code
    return "en"


def localized(value):
    """Plugin texts may be a string or {"de": …, "es": …}."""
    if isinstance(value, dict):
        return value.get(_lang) or value.get("en") or next(iter(value.values()), "")
    return value or ""


TR = {
    # ------------------------------------------------------------------ English
    "en": {
        "&Datei": "&File", "&Neu": "&New", "Neu aus &Vorlage…": "New from &template…",
        "&Plugins verwalten…": "Manage &plugins…", "Ö&ffnen…": "&Open…", "&Speichern": "&Save",
        "Speichern &unter…": "Save &as…", "A&lle speichern": "Save a&ll", "S&chließen": "&Close",
        "Alle schli&eßen": "Clos&e all", "Neu &laden": "&Reload",
        "Als &HTML exportieren…": "Export as &HTML…", "Als &PDF exportieren…": "Export as &PDF…",
        "&Drucken…": "&Print…", "Ordner im Dateimanager öffnen": "Open folder in file manager",
        "&Beenden": "&Quit", "&Zuletzt geöffnet": "Recent &files", "Liste leeren": "Clear list",
        "(leer)": "(empty)",
        "&Bearbeiten": "&Edit", "&Rückgängig": "&Undo", "&Wiederholen": "&Redo",
        "&Ausschneiden": "Cu&t", "&Kopieren": "&Copy", "&Einfügen": "&Paste",
        "Als reinen Text einfügen": "Paste as plain text", "Alles &markieren": "Select &all",
        "&Suchen": "&Search", "&Suchen…": "&Find…", "&Weitersuchen": "Find &next",
        "&Rückwärts suchen": "Find &previous", "&Ersetzen…": "&Replace…",
        "&Format": "F&ormat", "Ü&berschrift": "&Heading", "Überschrift": "Heading",
        "Überschrift &{n}": "Heading &{n}", "&Fett": "&Bold", "&Kursiv": "&Italic",
        "&Durchgestrichen": "&Strikethrough", "Inline-&Code": "Inline &code", "&Link": "&Link",
        "&Zitat": "&Quote", "&Aufzählung": "&Bulleted list", "&Nummerierte Liste": "&Numbered list",
        "Auf&gabenliste": "&Task list", "Code&block": "Code bloc&k", "&Tabelle": "T&able",
        "&Trennlinie": "Horizontal &rule",
        "&Ansicht": "&View", "Editor-&Modus": "Editor &mode", "&Gliederung anzeigen": "Show &outline",
        "&Theme": "&Theme", "&Dunkles Design": "&Dark mode", "&Schreibmaschinenmodus": "&Typewriter mode",
        "&Vollbild": "&Full screen", "Ver&größern": "Zoom &in", "Ver&kleinern": "Zoom &out",
        "&Originalgröße": "&Reset zoom",
        "E&xtras": "&Tools", "&Rechtschreibprüfung": "&Spell checking",
        "Rechtschreibprüfung &aktiv": "Spell checking &on",
        "&Benutzerwörterbuch bearbeiten…": "Edit personal &dictionary…",
        "&Sprache der Oberfläche": "Interface &language",
        "Systemsprache ({lang})": "System language ({lang})",
        "Die neue Sprache gilt nach einem Neustart von Matt|Pad.": "The new language takes effect after restarting Matt|Pad.",
        "Sprache": "Language",
        "Markdown-&Kurzreferenz": "Markdown &quick reference", "&Lizenz (GNU GPL)": "&License (GNU GPL)",
        "Über Matt|&Pad": "&About Matt|Pad", "Werkzeugleiste": "Toolbar",
        "Live (Typora)": "Live (Typora)", "Quelltext + Vorschau": "Source + preview", "WYSIWYG": "WYSIWYG",
        "Markdown (*.md *.markdown *.mdown *.mkd *.txt);;Alle Dateien (*)":
            "Markdown (*.md *.markdown *.mdown *.mkd *.txt);;All files (*)",
        "Markdown-Datei": "Markdown file",
        "Länge: {chars}    Zeilen: {lines}    Wörter: {words}": "Length: {chars}    Lines: {lines}    Words: {words}",
        "Rechtschreibprüfung (F7 ein/aus, Sprachen unter Extras)": "Spell checking (F7 on/off, languages under Tools)",
        "ABC: aus": "ABC: off", "neu {n}": "new {n}", "Zoom: {z} %": "Zoom: {z} %",
        "Suchen:": "Find:", "◀ Zurück": "◀ Previous", "Weiter ▶": "Next ▶",
        "Groß-/Kleinschreibung": "Match case", "Nicht gefunden": "Not found", "{a} von {b}": "{a} of {b}",
        "Ersetzen": "Replace", "Suchen nach:": "Find what:", "Ersetzen durch:": "Replace with:",
        "Groß-/Kleinschreibung beachten": "Match case", "Regulärer Ausdruck": "Regular expression",
        "Alle ersetzen": "Replace all", "Schließen": "Close", "Fehler im Ausdruck: {e}": "Error in expression: {e}",
        "{count} Vorkommen ersetzt.": "{count} occurrences replaced.",
        "(keine Vorschläge)": "(no suggestions)",
        "„{word}“ zum Wörterbuch hinzufügen": "Add “{word}” to dictionary",
        "„{word}“ ins Wörterbuch aufgenommen": "“{word}” added to dictionary",
        "Speichern?": "Save?", "„{name}“ wurde geändert.\nÄnderungen speichern?": "“{name}” has been modified.\nSave changes?",
        "Öffnen": "Open", "Fehler": "Error", "Datei konnte nicht geöffnet werden:\n{e}": "Could not open file:\n{e}",
        "Speichern unter": "Save as", "Speichern fehlgeschlagen:\n{e}": "Saving failed:\n{e}",
        "Gespeichert: {path}": "Saved: {path}", "Neu laden": "Reload",
        "Ungespeicherte Änderungen gehen verloren. Trotzdem neu laden?": "Unsaved changes will be lost. Reload anyway?",
        "Datei wurde gelöscht oder verschoben: {path}": "File was deleted or moved: {path}",
        "„{path}“\n\nwurde von einem anderen Programm geändert.\nNeu laden?": "“{path}”\n\nwas changed by another program.\nReload?",
        "\n\nACHTUNG: Deine ungespeicherten Änderungen gehen dabei verloren.": "\n\nWARNING: your unsaved changes will be lost.",
        "Datei geändert": "File changed",
        "Als HTML exportieren": "Export as HTML", "Exportiert: {path}": "Exported: {path}",
        "Als PDF exportieren": "Export as PDF", "PDF gespeichert: {path}": "PDF saved: {path}",
        "PDF-Export fehlgeschlagen": "PDF export failed", "Drucken": "Print", "Drucke…": "Printing…",
        "An den Drucker gesendet": "Sent to printer", "Drucken fehlgeschlagen": "Printing failed",
        "Standard (ohne Theme)": "Default (no theme)",
        "{tip} – Theme-ID für die Kopfdaten: theme: {tid}": "{tip} – theme ID for the front matter: theme: {tid}",
        "Plugins verwalten…": "Manage plugins…",
        "Hinweis: Dieses Dokument legt sein Theme selbst in den Kopfdaten fest (theme: …).":
            "Note: this document sets its own theme in the front matter (theme: …).",
        "Neu aus Vorlage": "New from template",
        "Keine Vorlagen vorhanden. Vorlagen kommen über Plugins (Extras → Plugins verwalten).":
            "No templates available. Templates come with plugins (Tools → Manage plugins).",
        "Vorlage konnte nicht gelesen werden:\n{e}": "Could not read template:\n{e}",
        "Titel:": "Title:", "Autor/in:": "Author:", "Dokument anlegen": "Create document",
        "Plugins": "Plugins", "Plugin installieren (.zip)…": "Install plugin (.zip)…", "Entfernen": "Remove",
        "Plugin-Ordner öffnen": "Open plugin folder", "Keine Plugins installiert.": "No plugins installed.",
        "Version": "Version", "Autor": "Author", "Lizenz": "License", "Themes": "Themes", "Vorlagen": "Templates",
        "Mitgeliefert": "Built-in", "Selbst installiert": "Installed by you", "Plugin installieren": "Install plugin",
        "Matt|Pad-Plugin (*.zip)": "Matt|Pad plugin (*.zip)",
        "Installation fehlgeschlagen:\n{e}": "Installation failed:\n{e}",
        "„{name}“ wurde installiert.": "“{name}” has been installed.", "Plugin entfernen": "Remove plugin",
        "„{name}“ wirklich entfernen?": "Really remove “{name}”?",
        "Die ZIP-Datei enthält keine plugin.json.": "The ZIP file contains no plugin.json.",
        "Ungültiger Pfad in der ZIP-Datei: {name}": "Invalid path in ZIP file: {name}",
        "Über {app}": "About {app}", "{app} – Lizenz": "{app} – License",
        "Lizenz: GNU GPL, Version 3 oder später": "License: GNU GPL, version 3 or later",
        "Minimalistischer Markdown-Editor<br>Live-Darstellung wie Typora, Oberfläche wie Notepad++.<br>Vorlagen und Themes über Plugins.":
            "Minimalist Markdown editor<br>Live rendering like Typora, interface like Notepad++.<br>Templates and themes via plugins.",
        "Freie Software unter der GNU General Public License, Version 3 oder später (GPL-3.0-or-later). Ohne jede Gewährleistung.":
            "Free software under the GNU General Public License, version 3 or later (GPL-3.0-or-later). Without any warranty.",
        "Verwendet: Vditor (MIT), Qt / PyQt6 (GPL), Python, Hunspell-Wörterbücher, Breeze-Symbole (LGPL).":
            "Uses: Vditor (MIT), Qt / PyQt6 (GPL), Python, Hunspell dictionaries, Breeze icons (LGPL).",
    },
    # ------------------------------------------------------------------ Español
    "es": {
        "&Datei": "&Archivo", "&Neu": "&Nuevo", "Neu aus &Vorlage…": "Nuevo desde &plantilla…",
        "&Plugins verwalten…": "Administrar &plugins…", "Ö&ffnen…": "&Abrir…", "&Speichern": "&Guardar",
        "Speichern &unter…": "Guardar &como…", "A&lle speichern": "Guardar &todo", "S&chließen": "&Cerrar",
        "Alle schli&eßen": "Cerrar t&odo", "Neu &laden": "&Recargar",
        "Als &HTML exportieren…": "Exportar como &HTML…", "Als &PDF exportieren…": "Exportar como &PDF…",
        "&Drucken…": "&Imprimir…", "Ordner im Dateimanager öffnen": "Abrir carpeta en el explorador de archivos",
        "&Beenden": "&Salir", "&Zuletzt geöffnet": "Archivos &recientes", "Liste leeren": "Vaciar lista",
        "(leer)": "(vacío)",
        "&Bearbeiten": "&Editar", "&Rückgängig": "&Deshacer", "&Wiederholen": "&Rehacer",
        "&Ausschneiden": "Cor&tar", "&Kopieren": "&Copiar", "&Einfügen": "&Pegar",
        "Als reinen Text einfügen": "Pegar como texto sin formato", "Alles &markieren": "Seleccionar &todo",
        "&Suchen": "&Buscar", "&Suchen…": "&Buscar…", "&Weitersuchen": "Buscar &siguiente",
        "&Rückwärts suchen": "Buscar &anterior", "&Ersetzen…": "&Reemplazar…",
        "&Format": "&Formato", "Ü&berschrift": "&Título", "Überschrift": "Título",
        "Überschrift &{n}": "Título &{n}", "&Fett": "&Negrita", "&Kursiv": "&Cursiva",
        "&Durchgestrichen": "&Tachado", "Inline-&Code": "&Código en línea", "&Link": "&Enlace",
        "&Zitat": "Ci&ta", "&Aufzählung": "&Viñetas", "&Nummerierte Liste": "Lista &numerada",
        "Auf&gabenliste": "Lista de &tareas", "Code&block": "&Bloque de código", "&Tabelle": "T&abla",
        "&Trennlinie": "&Línea separadora",
        "&Ansicht": "&Ver", "Editor-&Modus": "&Modo del editor", "&Gliederung anzeigen": "Mostrar &esquema",
        "&Theme": "&Tema", "&Dunkles Design": "Modo &oscuro", "&Schreibmaschinenmodus": "Modo má&quina de escribir",
        "&Vollbild": "&Pantalla completa", "Ver&größern": "&Ampliar", "Ver&kleinern": "&Reducir",
        "&Originalgröße": "Tamaño &original",
        "E&xtras": "&Herramientas", "&Rechtschreibprüfung": "&Ortografía",
        "Rechtschreibprüfung &aktiv": "Revisión ortográfica &activa",
        "&Benutzerwörterbuch bearbeiten…": "Editar &diccionario personal…",
        "&Sprache der Oberfläche": "&Idioma de la interfaz",
        "Systemsprache ({lang})": "Idioma del sistema ({lang})",
        "Die neue Sprache gilt nach einem Neustart von Matt|Pad.": "El nuevo idioma se aplicará al reiniciar Matt|Pad.",
        "Sprache": "Idioma",
        "Markdown-&Kurzreferenz": "&Referencia rápida de Markdown", "&Lizenz (GNU GPL)": "&Licencia (GNU GPL)",
        "Über Matt|&Pad": "&Acerca de Matt|Pad", "Werkzeugleiste": "Barra de herramientas",
        "Live (Typora)": "En vivo (Typora)", "Quelltext + Vorschau": "Código fuente + vista previa", "WYSIWYG": "WYSIWYG",
        "Markdown (*.md *.markdown *.mdown *.mkd *.txt);;Alle Dateien (*)":
            "Markdown (*.md *.markdown *.mdown *.mkd *.txt);;Todos los archivos (*)",
        "Markdown-Datei": "Archivo Markdown",
        "Länge: {chars}    Zeilen: {lines}    Wörter: {words}": "Caracteres: {chars}    Líneas: {lines}    Palabras: {words}",
        "Rechtschreibprüfung (F7 ein/aus, Sprachen unter Extras)": "Ortografía (F7 activar/desactivar, idiomas en Herramientas)",
        "ABC: aus": "ABC: desact.", "neu {n}": "nuevo {n}", "Zoom: {z} %": "Zoom: {z} %",
        "Suchen:": "Buscar:", "◀ Zurück": "◀ Anterior", "Weiter ▶": "Siguiente ▶",
        "Groß-/Kleinschreibung": "Mayúsculas/minúsculas", "Nicht gefunden": "No encontrado", "{a} von {b}": "{a} de {b}",
        "Ersetzen": "Reemplazar", "Suchen nach:": "Buscar:", "Ersetzen durch:": "Reemplazar con:",
        "Groß-/Kleinschreibung beachten": "Distinguir mayúsculas y minúsculas", "Regulärer Ausdruck": "Expresión regular",
        "Alle ersetzen": "Reemplazar todo", "Schließen": "Cerrar", "Fehler im Ausdruck: {e}": "Error en la expresión: {e}",
        "{count} Vorkommen ersetzt.": "{count} coincidencias reemplazadas.",
        "(keine Vorschläge)": "(sin sugerencias)",
        "„{word}“ zum Wörterbuch hinzufügen": "Añadir «{word}» al diccionario",
        "„{word}“ ins Wörterbuch aufgenommen": "«{word}» añadido al diccionario",
        "Speichern?": "¿Guardar?", "„{name}“ wurde geändert.\nÄnderungen speichern?": "«{name}» ha sido modificado.\n¿Guardar los cambios?",
        "Öffnen": "Abrir", "Fehler": "Error", "Datei konnte nicht geöffnet werden:\n{e}": "No se pudo abrir el archivo:\n{e}",
        "Speichern unter": "Guardar como", "Speichern fehlgeschlagen:\n{e}": "Error al guardar:\n{e}",
        "Gespeichert: {path}": "Guardado: {path}", "Neu laden": "Recargar",
        "Ungespeicherte Änderungen gehen verloren. Trotzdem neu laden?": "Se perderán los cambios no guardados. ¿Recargar de todos modos?",
        "Datei wurde gelöscht oder verschoben: {path}": "El archivo fue eliminado o movido: {path}",
        "„{path}“\n\nwurde von einem anderen Programm geändert.\nNeu laden?": "«{path}»\n\nfue modificado por otro programa.\n¿Recargar?",
        "\n\nACHTUNG: Deine ungespeicherten Änderungen gehen dabei verloren.": "\n\nATENCIÓN: se perderán tus cambios no guardados.",
        "Datei geändert": "Archivo modificado",
        "Als HTML exportieren": "Exportar como HTML", "Exportiert: {path}": "Exportado: {path}",
        "Als PDF exportieren": "Exportar como PDF", "PDF gespeichert: {path}": "PDF guardado: {path}",
        "PDF-Export fehlgeschlagen": "Error al exportar PDF", "Drucken": "Imprimir", "Drucke…": "Imprimiendo…",
        "An den Drucker gesendet": "Enviado a la impresora", "Drucken fehlgeschlagen": "Error al imprimir",
        "Standard (ohne Theme)": "Predeterminado (sin tema)",
        "{tip} – Theme-ID für die Kopfdaten: theme: {tid}": "{tip} – ID del tema para el encabezado: theme: {tid}",
        "Plugins verwalten…": "Administrar plugins…",
        "Hinweis: Dieses Dokument legt sein Theme selbst in den Kopfdaten fest (theme: …).":
            "Nota: este documento define su propio tema en el encabezado (theme: …).",
        "Neu aus Vorlage": "Nuevo desde plantilla",
        "Keine Vorlagen vorhanden. Vorlagen kommen über Plugins (Extras → Plugins verwalten).":
            "No hay plantillas. Las plantillas vienen con los plugins (Herramientas → Administrar plugins).",
        "Vorlage konnte nicht gelesen werden:\n{e}": "No se pudo leer la plantilla:\n{e}",
        "Titel:": "Título:", "Autor/in:": "Autor/a:", "Dokument anlegen": "Crear documento",
        "Plugins": "Plugins", "Plugin installieren (.zip)…": "Instalar plugin (.zip)…", "Entfernen": "Eliminar",
        "Plugin-Ordner öffnen": "Abrir carpeta de plugins", "Keine Plugins installiert.": "No hay plugins instalados.",
        "Version": "Versión", "Autor": "Autor", "Lizenz": "Licencia", "Themes": "Temas", "Vorlagen": "Plantillas",
        "Mitgeliefert": "Incluido", "Selbst installiert": "Instalado por ti", "Plugin installieren": "Instalar plugin",
        "Matt|Pad-Plugin (*.zip)": "Plugin de Matt|Pad (*.zip)",
        "Installation fehlgeschlagen:\n{e}": "Error en la instalación:\n{e}",
        "„{name}“ wurde installiert.": "«{name}» se ha instalado.", "Plugin entfernen": "Eliminar plugin",
        "„{name}“ wirklich entfernen?": "¿Eliminar «{name}»?",
        "Die ZIP-Datei enthält keine plugin.json.": "El archivo ZIP no contiene plugin.json.",
        "Ungültiger Pfad in der ZIP-Datei: {name}": "Ruta no válida en el archivo ZIP: {name}",
        "Über {app}": "Acerca de {app}", "{app} – Lizenz": "{app} – Licencia",
        "Lizenz: GNU GPL, Version 3 oder später": "Licencia: GNU GPL, versión 3 o posterior",
        "Minimalistischer Markdown-Editor<br>Live-Darstellung wie Typora, Oberfläche wie Notepad++.<br>Vorlagen und Themes über Plugins.":
            "Editor Markdown minimalista<br>Vista en vivo como Typora, interfaz como Notepad++.<br>Plantillas y temas mediante plugins.",
        "Freie Software unter der GNU General Public License, Version 3 oder später (GPL-3.0-or-later). Ohne jede Gewährleistung.":
            "Software libre bajo la Licencia Pública General de GNU, versión 3 o posterior (GPL-3.0-or-later). Sin ninguna garantía.",
        "Verwendet: Vditor (MIT), Qt / PyQt6 (GPL), Python, Hunspell-Wörterbücher, Breeze-Symbole (LGPL).":
            "Utiliza: Vditor (MIT), Qt / PyQt6 (GPL), Python, diccionarios Hunspell, iconos Breeze (LGPL).",
    },
    # ------------------------------------------------------------------ Português (Brasil)
    "pt": {
        "&Datei": "&Arquivo", "&Neu": "&Novo", "Neu aus &Vorlage…": "Novo a partir de &modelo…",
        "&Plugins verwalten…": "Gerenciar &plugins…", "Ö&ffnen…": "&Abrir…", "&Speichern": "&Salvar",
        "Speichern &unter…": "Salvar &como…", "A&lle speichern": "Salvar &tudo", "S&chließen": "&Fechar",
        "Alle schli&eßen": "Fechar t&udo", "Neu &laden": "&Recarregar",
        "Als &HTML exportieren…": "Exportar como &HTML…", "Als &PDF exportieren…": "Exportar como &PDF…",
        "&Drucken…": "&Imprimir…", "Ordner im Dateimanager öffnen": "Abrir pasta no gerenciador de arquivos",
        "&Beenden": "Sa&ir", "&Zuletzt geöffnet": "Arquivos &recentes", "Liste leeren": "Limpar lista",
        "(leer)": "(vazio)",
        "&Bearbeiten": "&Editar", "&Rückgängig": "&Desfazer", "&Wiederholen": "&Refazer",
        "&Ausschneiden": "Recor&tar", "&Kopieren": "&Copiar", "&Einfügen": "C&olar",
        "Als reinen Text einfügen": "Colar como texto simples", "Alles &markieren": "Selecionar &tudo",
        "&Suchen": "&Localizar", "&Suchen…": "&Localizar…", "&Weitersuchen": "Localizar &próximo",
        "&Rückwärts suchen": "Localizar &anterior", "&Ersetzen…": "&Substituir…",
        "&Format": "&Formatar", "Ü&berschrift": "&Título", "Überschrift": "Título",
        "Überschrift &{n}": "Título &{n}", "&Fett": "&Negrito", "&Kursiv": "&Itálico",
        "&Durchgestrichen": "&Tachado", "Inline-&Code": "&Código embutido", "&Link": "&Link",
        "&Zitat": "Ci&tação", "&Aufzählung": "&Marcadores", "&Nummerierte Liste": "Lista &numerada",
        "Auf&gabenliste": "Lista de &tarefas", "Code&block": "&Bloco de código", "&Tabelle": "T&abela",
        "&Trennlinie": "&Linha divisória",
        "&Ansicht": "E&xibir", "Editor-&Modus": "&Modo do editor", "&Gliederung anzeigen": "Mostrar &estrutura",
        "&Theme": "&Tema", "&Dunkles Design": "Modo &escuro", "&Schreibmaschinenmodus": "Modo má&quina de escrever",
        "&Vollbild": "&Tela cheia", "Ver&größern": "&Ampliar", "Ver&kleinern": "&Reduzir",
        "&Originalgröße": "Tamanho &original",
        "E&xtras": "&Ferramentas", "&Rechtschreibprüfung": "&Ortografia",
        "Rechtschreibprüfung &aktiv": "Verificação ortográfica &ativa",
        "&Benutzerwörterbuch bearbeiten…": "Editar &dicionário pessoal…",
        "&Sprache der Oberfläche": "&Idioma da interface",
        "Systemsprache ({lang})": "Idioma do sistema ({lang})",
        "Die neue Sprache gilt nach einem Neustart von Matt|Pad.": "O novo idioma será aplicado ao reiniciar o Matt|Pad.",
        "Sprache": "Idioma",
        "Markdown-&Kurzreferenz": "&Referência rápida de Markdown", "&Lizenz (GNU GPL)": "&Licença (GNU GPL)",
        "Über Matt|&Pad": "&Sobre o Matt|Pad", "Werkzeugleiste": "Barra de ferramentas",
        "Live (Typora)": "Ao vivo (Typora)", "Quelltext + Vorschau": "Código-fonte + pré-visualização", "WYSIWYG": "WYSIWYG",
        "Markdown (*.md *.markdown *.mdown *.mkd *.txt);;Alle Dateien (*)":
            "Markdown (*.md *.markdown *.mdown *.mkd *.txt);;Todos os arquivos (*)",
        "Markdown-Datei": "Arquivo Markdown",
        "Länge: {chars}    Zeilen: {lines}    Wörter: {words}": "Caracteres: {chars}    Linhas: {lines}    Palavras: {words}",
        "Rechtschreibprüfung (F7 ein/aus, Sprachen unter Extras)": "Ortografia (F7 liga/desliga, idiomas em Ferramentas)",
        "ABC: aus": "ABC: desl.", "neu {n}": "novo {n}", "Zoom: {z} %": "Zoom: {z} %",
        "Suchen:": "Localizar:", "◀ Zurück": "◀ Anterior", "Weiter ▶": "Próximo ▶",
        "Groß-/Kleinschreibung": "Maiúsculas/minúsculas", "Nicht gefunden": "Não encontrado", "{a} von {b}": "{a} de {b}",
        "Ersetzen": "Substituir", "Suchen nach:": "Localizar:", "Ersetzen durch:": "Substituir por:",
        "Groß-/Kleinschreibung beachten": "Diferenciar maiúsculas e minúsculas", "Regulärer Ausdruck": "Expressão regular",
        "Alle ersetzen": "Substituir tudo", "Schließen": "Fechar", "Fehler im Ausdruck: {e}": "Erro na expressão: {e}",
        "{count} Vorkommen ersetzt.": "{count} ocorrências substituídas.",
        "(keine Vorschläge)": "(sem sugestões)",
        "„{word}“ zum Wörterbuch hinzufügen": "Adicionar “{word}” ao dicionário",
        "„{word}“ ins Wörterbuch aufgenommen": "“{word}” adicionado ao dicionário",
        "Speichern?": "Salvar?", "„{name}“ wurde geändert.\nÄnderungen speichern?": "“{name}” foi modificado.\nSalvar as alterações?",
        "Öffnen": "Abrir", "Fehler": "Erro", "Datei konnte nicht geöffnet werden:\n{e}": "Não foi possível abrir o arquivo:\n{e}",
        "Speichern unter": "Salvar como", "Speichern fehlgeschlagen:\n{e}": "Falha ao salvar:\n{e}",
        "Gespeichert: {path}": "Salvo: {path}", "Neu laden": "Recarregar",
        "Ungespeicherte Änderungen gehen verloren. Trotzdem neu laden?": "As alterações não salvas serão perdidas. Recarregar mesmo assim?",
        "Datei wurde gelöscht oder verschoben: {path}": "O arquivo foi excluído ou movido: {path}",
        "„{path}“\n\nwurde von einem anderen Programm geändert.\nNeu laden?": "“{path}”\n\nfoi modificado por outro programa.\nRecarregar?",
        "\n\nACHTUNG: Deine ungespeicherten Änderungen gehen dabei verloren.": "\n\nATENÇÃO: suas alterações não salvas serão perdidas.",
        "Datei geändert": "Arquivo modificado",
        "Als HTML exportieren": "Exportar como HTML", "Exportiert: {path}": "Exportado: {path}",
        "Als PDF exportieren": "Exportar como PDF", "PDF gespeichert: {path}": "PDF salvo: {path}",
        "PDF-Export fehlgeschlagen": "Falha ao exportar PDF", "Drucken": "Imprimir", "Drucke…": "Imprimindo…",
        "An den Drucker gesendet": "Enviado para a impressora", "Drucken fehlgeschlagen": "Falha ao imprimir",
        "Standard (ohne Theme)": "Padrão (sem tema)",
        "{tip} – Theme-ID für die Kopfdaten: theme: {tid}": "{tip} – ID do tema para o cabeçalho: theme: {tid}",
        "Plugins verwalten…": "Gerenciar plugins…",
        "Hinweis: Dieses Dokument legt sein Theme selbst in den Kopfdaten fest (theme: …).":
            "Observação: este documento define o próprio tema no cabeçalho (theme: …).",
        "Neu aus Vorlage": "Novo a partir de modelo",
        "Keine Vorlagen vorhanden. Vorlagen kommen über Plugins (Extras → Plugins verwalten).":
            "Nenhum modelo disponível. Os modelos vêm com os plugins (Ferramentas → Gerenciar plugins).",
        "Vorlage konnte nicht gelesen werden:\n{e}": "Não foi possível ler o modelo:\n{e}",
        "Titel:": "Título:", "Autor/in:": "Autor(a):", "Dokument anlegen": "Criar documento",
        "Plugins": "Plugins", "Plugin installieren (.zip)…": "Instalar plugin (.zip)…", "Entfernen": "Remover",
        "Plugin-Ordner öffnen": "Abrir pasta de plugins", "Keine Plugins installiert.": "Nenhum plugin instalado.",
        "Version": "Versão", "Autor": "Autor", "Lizenz": "Licença", "Themes": "Temas", "Vorlagen": "Modelos",
        "Mitgeliefert": "Incluído", "Selbst installiert": "Instalado por você", "Plugin installieren": "Instalar plugin",
        "Matt|Pad-Plugin (*.zip)": "Plugin do Matt|Pad (*.zip)",
        "Installation fehlgeschlagen:\n{e}": "Falha na instalação:\n{e}",
        "„{name}“ wurde installiert.": "“{name}” foi instalado.", "Plugin entfernen": "Remover plugin",
        "„{name}“ wirklich entfernen?": "Remover “{name}”?",
        "Die ZIP-Datei enthält keine plugin.json.": "O arquivo ZIP não contém plugin.json.",
        "Ungültiger Pfad in der ZIP-Datei: {name}": "Caminho inválido no arquivo ZIP: {name}",
        "Über {app}": "Sobre o {app}", "{app} – Lizenz": "{app} – Licença",
        "Lizenz: GNU GPL, Version 3 oder später": "Licença: GNU GPL, versão 3 ou posterior",
        "Minimalistischer Markdown-Editor<br>Live-Darstellung wie Typora, Oberfläche wie Notepad++.<br>Vorlagen und Themes über Plugins.":
            "Editor Markdown minimalista<br>Visualização ao vivo como no Typora, interface como no Notepad++.<br>Modelos e temas por meio de plugins.",
        "Freie Software unter der GNU General Public License, Version 3 oder später (GPL-3.0-or-later). Ohne jede Gewährleistung.":
            "Software livre sob a Licença Pública Geral GNU, versão 3 ou posterior (GPL-3.0-or-later). Sem qualquer garantia.",
        "Verwendet: Vditor (MIT), Qt / PyQt6 (GPL), Python, Hunspell-Wörterbücher, Breeze-Symbole (LGPL).":
            "Utiliza: Vditor (MIT), Qt / PyQt6 (GPL), Python, dicionários Hunspell, ícones Breeze (LGPL).",
    },
}
