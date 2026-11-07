# Markdown-Kurzreferenz

Einfach lostippen – Matt|Pad formatiert **live**, wie Typora. Mit `Ctrl+2` siehst du den Quelltext.

## Überschriften

Zeile mit `# ` beginnen (bis `###### `) oder `Ctrl+Alt+1` … `Ctrl+Alt+6`.

## Text

| Eingabe | Ergebnis | Kürzel |
| --- | --- | --- |
| `**fett**` | **fett** | Ctrl+B |
| `*kursiv*` | *kursiv* | Ctrl+I |
| `~~durch~~` | ~~durch~~ | Ctrl+D |
| `` `code` `` | `code` | Ctrl+G |
| `==markiert==` | ==markiert== | |
| `[Text](https://…)` | Link | Ctrl+K |

## Listen

- Aufzählung mit `- ` (Ctrl+L)

1. Nummeriert mit `1. ` (Ctrl+Shift+L)

- [ ] Aufgabe mit `- [ ] ` (Ctrl+J)

## Blöcke

> Zitat mit `> ` (Ctrl+;)

```python
print("Codeblock mit ``` und Sprache")
```

Trennlinie mit `---` (Ctrl+Shift+H), Tabelle mit Ctrl+M.

Formeln: $E = mc^2$ inline oder als Block mit `$$`.

## Bilder

`![Beschreibung](bild.png)` – relative Pfade beziehen sich auf den Ordner der Datei.

## Programm

| Kürzel | Funktion |
| --- | --- |
| Ctrl+N / O / S | Neu / Öffnen / Speichern |
| Ctrl+Shift+S | Alle speichern |
| Ctrl+W | Tab schließen (auch Mittelklick) |
| Ctrl+Tab | Nächster Tab |
| Ctrl+F, F3 | Suchen, weitersuchen |
| Ctrl+H | Ersetzen |
| Ctrl+1 / 2 / 3 | Live / Quelltext / WYSIWYG |
| F8 | Gliederung |
| F11 | Vollbild |
| Ctrl + / – / 0 | Zoom |
| Ctrl+Shift+N | Neu aus Vorlage |
| Ctrl+P | Drucken |
| F7 | Rechtschreibprüfung ein/aus |

## Vorlagen und Themes

**Datei → Neu aus Vorlage** (Ctrl+Shift+N) legt ein Dokument aus einer Vorlage an – z. B. ein Buchkapitel. Titel und Autor/in werden automatisch eingesetzt.

**Ansicht → Theme** bestimmt das Aussehen beim Schreiben, beim Drucken und beim PDF-/HTML-Export.

Ein Dokument kann sein Theme auch selbst festlegen – in den Kopfdaten ganz oben:

```yaml
---
title: "Mein Kapitel"
author: "Ana Pérez"
lang: es
theme: libro
---
```

`lang` steuert die Silbentrennung im Blocksatz (`de`, `es`, `en`, …).

Weitere Vorlagen und Themes kommen als **Plugin** (ZIP-Datei): *Extras → Plugins verwalten → Plugin installieren*.

Die Sprache der Oberfläche lässt sich unter *Extras → Sprache der Oberfläche* ändern.
