# Referencia rápida de Markdown

Simplemente empiece a escribir: Matt|Pad da formato **en vivo**, como Typora. Con `Ctrl+2` verá el código fuente.

## Títulos

Empiece la línea con `# ` (hasta `###### `) o use `Ctrl+Alt+1` … `Ctrl+Alt+6`.

## Texto

| Escriba | Resultado | Atajo |
| --- | --- | --- |
| `**negrita**` | **negrita** | Ctrl+B |
| `*cursiva*` | *cursiva* | Ctrl+I |
| `~~tachado~~` | ~~tachado~~ | Ctrl+D |
| `` `código` `` | `código` | Ctrl+G |
| `==resaltado==` | ==resaltado== | |
| `[Texto](https://…)` | Enlace | Ctrl+K |

## Listas

- Viñetas con `- ` (Ctrl+L)

1. Numerada con `1. ` (Ctrl+Shift+L)

- [ ] Tarea con `- [ ] ` (Ctrl+J)

## Bloques

> Cita con `> ` (Ctrl+;)

```python
print("Bloque de código con ``` y el lenguaje")
```

Línea separadora con `---` (Ctrl+Shift+H), tabla con Ctrl+M.

Fórmulas: $E = mc^2$ en línea o en bloque con `$$`.

## Imágenes

`![Descripción](imagen.png)`: las rutas relativas se refieren a la carpeta del archivo.

## Programa

| Atajo | Función |
| --- | --- |
| Ctrl+N / O / S | Nuevo / Abrir / Guardar |
| Ctrl+Shift+N | Nuevo desde plantilla |
| Ctrl+Shift+S | Guardar todo |
| Ctrl+W | Cerrar pestaña (también clic central) |
| Ctrl+Tab | Pestaña siguiente |
| Ctrl+F, F3 | Buscar, buscar siguiente |
| Ctrl+H | Reemplazar |
| Ctrl+P | Imprimir |
| Ctrl+1 / 2 / 3 | En vivo / Código fuente / WYSIWYG |
| F7 | Ortografía activar/desactivar |
| F8 | Esquema |
| F11 | Pantalla completa |
| Ctrl + / – / 0 | Zoom |

## Plantillas y temas

**Archivo → Nuevo desde plantilla** (Ctrl+Shift+N) crea un documento a partir de una plantilla, p. ej. un capítulo de libro. El título y el nombre del autor se completan automáticamente.

**Ver → Tema** define el aspecto al escribir, al imprimir y al exportar a PDF/HTML.

Un documento también puede definir su propio tema, en el encabezado al principio:

```yaml
---
title: "Mi capítulo"
author: "Ana Pérez"
lang: es
theme: libro
---
```

`lang` controla la división de palabras en el texto justificado (`es`, `pt`, `en`, `de`, …).

Más plantillas y temas vienen como **plugin** (archivo ZIP): *Herramientas → Administrar plugins → Instalar plugin*.

El idioma de la interfaz se cambia en *Herramientas → Idioma de la interfaz*.
