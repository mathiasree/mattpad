# Matt|Pad-Plugins: Vorlagen und Themes

Ein Plugin ist ein **Ordner** (zum Weitergeben: als **ZIP-Datei**) mit Vorlagen (Markdown) und
Themes (CSS). Plugins enthalten **keinen Programmcode** – ein Plugin zu installieren ist also gefahrlos.

## Aufbau

```
mein-plugin/
├── plugin.json
├── themes/
│   └── mein-theme.css
├── templates/
│   └── kapitel.md
└── fonts/            (optional: Schriften, Bilder …)
```

### plugin.json

```json
{
  "id": "mein-plugin",
  "name": "Mein Plugin",
  "version": "1.0.0",
  "author": "Vorname Nachname",
  "license": "GPL-3.0-or-later",
  "description": "Wofür das Plugin gedacht ist.",
  "themes": [
    {"id": "mein-theme", "name": "Mein Theme", "css": "themes/mein-theme.css",
     "description": "Kurzbeschreibung"}
  ],
  "templates": [
    {"name": "Kapitel", "file": "templates/kapitel.md", "description": "Kurzbeschreibung"}
  ]
}
```

`name` und `description` dürfen ein Text oder mehrsprachig sein:
`{"de": "Kapitel", "en": "Chapter", "es": "Capítulo", "pt": "Capítulo"}`.

Lässt man `themes` bzw. `templates` weg, nimmt Matt|Pad automatisch alle `themes/*.css` und
`templates/*.md` (Name = Dateiname). Die Theme-`id` muss über alle Plugins eindeutig sein.

## Vorlagen

Normale Markdown-Dateien. Platzhalter werden beim Anlegen ersetzt:

| Platzhalter | wird zu |
| --- | --- |
| `{{title}}` (auch `{{titel}}`, `{{titulo}}`) | Titel aus dem Dialog |
| `{{author}}` (auch `{{autor}}`) | Autor/in (wird gemerkt) |
| `{{date}}` (auch `{{datum}}`, `{{fecha}}`) | heutiges Datum, z. B. 2026-11-07 |
| `{{year}}` (auch `{{jahr}}`) | aktuelles Jahr |
| `{{lang}}` | Sprache der Oberfläche (`de`, `en`, `es`, `pt`) |

Kopfdaten (YAML-Front-Matter) am Anfang legen Theme und Sprache für dieses Dokument fest:

```yaml
---
title: "{{title}}"
author: "{{author}}"
lang: es        # Sprache: Silbentrennung im Blocksatz, <html lang> beim Export
theme: libro    # Theme-id – gilt für dieses Dokument, egal was unter Ansicht → Theme gewählt ist
---
```

Die Kopfdaten erscheinen beim Drucken und im PDF/HTML-Export nicht; `title` und `author`
werden dort als Dokument-Metadaten verwendet.

## Themes

Ein Theme ist eine CSS-Datei. Sie gilt im Editor **und** beim Drucken/PDF/HTML-Export.

- Text: Selektor `.vditor-reset` (z. B. `.vditor-reset { font-family: …; }`, `.vditor-reset h1 { … }`)
- Seitenfarbe: `:root { --mp-page-bg: #fbf8f1; }`
- Dunkler Modus im Editor: `body.dark …`
- Nur für Druck/PDF: `@media print { … }`, Seitenränder mit `@page { margin: 2cm; }`
- Schriften/Bilder relativ zur CSS-Datei: `@font-face { src: url("../fonts/X.ttf"); }`
  (bitte nur frei weitergebbare Schriften, z. B. SIL OFL, und die Lizenz beilegen)

Beispiel: `plugins/buchprojekt/themes/libro.css`.

Beim Entwickeln: Plugin-Ordner direkt in den Benutzer-Plugin-Ordner legen
(*Extras → Plugins verwalten → Plugin-Ordner öffnen*) und nach Änderungen „Neu laden“ drücken.

| System | Benutzer-Plugin-Ordner |
| --- | --- |
| Linux | `~/.local/share/MattPad/plugins` (Flatpak: `~/.var/app/com.mathiasree.MattPad/data/MattPad/plugins`) |
| Windows | `%APPDATA%\MattPad\plugins` |
| macOS | `~/Library/Application Support/MattPad/plugins` |

## Weitergeben

Den Plugin-Ordner zippen (so dass `plugin.json` oben in der ZIP-Datei oder in genau einem
Unterordner liegt). Installieren: *Extras → Plugins verwalten → Plugin installieren (.zip)*.
Ein Plugin mit derselben `id` wie ein mitgeliefertes ersetzt dieses (so lassen sich
aktualisierte Vorlagen verteilen, ohne Matt|Pad neu zu installieren).
