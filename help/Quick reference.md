# Markdown quick reference

Just start typing – Matt|Pad formats **live**, like Typora. Press `Ctrl+2` to see the source.

## Headings

Start a line with `# ` (up to `###### `) or press `Ctrl+Alt+1` … `Ctrl+Alt+6`.

## Text

| Type | Result | Shortcut |
| --- | --- | --- |
| `**bold**` | **bold** | Ctrl+B |
| `*italic*` | *italic* | Ctrl+I |
| `~~struck~~` | ~~struck~~ | Ctrl+D |
| `` `code` `` | `code` | Ctrl+G |
| `==highlight==` | ==highlight== | |
| `[Text](https://…)` | Link | Ctrl+K |

## Lists

- Bulleted with `- ` (Ctrl+L)

1. Numbered with `1. ` (Ctrl+Shift+L)

- [ ] Task with `- [ ] ` (Ctrl+J)

## Blocks

> Quote with `> ` (Ctrl+;)

```python
print("Code block with ``` and a language")
```

Horizontal rule with `---` (Ctrl+Shift+H), table with Ctrl+M.

Formulas: $E = mc^2$ inline or as a block with `$$`.

## Images

`![Description](picture.png)` – relative paths refer to the folder of the file.

## Program

| Shortcut | Function |
| --- | --- |
| Ctrl+N / O / S | New / Open / Save |
| Ctrl+Shift+N | New from template |
| Ctrl+Shift+S | Save all |
| Ctrl+W | Close tab (also middle click) |
| Ctrl+Tab | Next tab |
| Ctrl+F, F3 | Find, find next |
| Ctrl+H | Replace |
| Ctrl+P | Print |
| Ctrl+1 / 2 / 3 | Live / Source / WYSIWYG |
| F7 | Spell checking on/off |
| F8 | Outline |
| F11 | Full screen |
| Ctrl + / – / 0 | Zoom |

## Templates and themes

**File → New from template** (Ctrl+Shift+N) creates a document from a template – e.g. a book chapter. Title and author are filled in automatically.

**View → Theme** sets the look while writing, when printing and in PDF/HTML export.

A document can also set its own theme – in the front matter at the very top:

```yaml
---
title: "My chapter"
author: "Ana Pérez"
lang: en
theme: libro
---
```

`lang` controls hyphenation in justified text (`en`, `es`, `pt`, `de`, …).

More templates and themes come as a **plugin** (ZIP file): *Tools → Manage plugins → Install plugin*.

The interface language can be changed under *Tools → Interface language*.
