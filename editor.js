// Matt|Pad – Copyright (C) 2026 Mathias Ree – GPL-3.0-or-later
// Bridge between the Qt window (mattpad.py) and the Vditor editor.
let vditor = null;
let bridge = null;

new QWebChannel(qt.webChannelTransport, (channel) => {
  bridge = channel.objects.bridge;
  bridge.pageReady();
});

function init(markdown, opts) {
  document.body.classList.toggle("dark", !!opts.dark);
  setThemeCSS(opts.themeHref);
  setDocLang(opts.lang);
  vditor = new Vditor("editor", {
    mode: opts.mode || "ir",
    lang: opts.uiLang || "en_US",
    cdn: "vendor/vditor",
    value: markdown,
    cache: { enable: false },
    // hidden via CSS, but the buttons are still used as command targets
    toolbar: [{ name: "headings", hotkey: "⇧⌘⌥H" }, "bold", "italic", "strike",
      "line", "quote", "list", { name: "ordered-list", hotkey: "⇧⌘L" }, "check", "code", "inline-code", "link", "table",
      "undo", "redo", "edit-mode", "outline"],
    theme: opts.dark ? "dark" : "classic",
    outline: { enable: !!opts.outline, position: "left" },
    typewriterMode: !!opts.typewriter,
    preview: {
      theme: { current: opts.dark ? "dark" : "light" },
      hljs: { style: opts.dark ? "native" : "github", lineNumber: false },
      math: { engine: "KaTeX" },
      markdown: {
        autoSpace: false,
        fixTermTypo: false,
        mark: true,
        toc: true,
        footnotes: true,
        linkBase: opts.linkBase || "",
      },
    },
    input: (value) => bridge.changed(value),
    after: () => {
      // Vditor disables spellcheck; the Qt side decides whether it's active
      for (const m of ["ir", "sv", "wysiwyg"]) {
        if (vditor.vditor[m]) vditor.vditor[m].element.spellcheck = true;
      }
      bridge.ready(vditor.getValue());
      vditor.focus();
    },
  });
}

function getMarkdown() {
  return vditor ? vditor.getValue() : null;
}

function setMarkdown(markdown) {
  vditor.setValue(markdown);
  bridge.changed(vditor.getValue());
}

function getHTML() {
  return vditor.getHTML();
}

function cmd(name, arg) {
  const el = vditor && vditor.vditor.toolbar.elements[name];
  if (!el) return;
  if (name === "headings") {
    el.querySelector(`button[data-tag="h${arg}"]`).click();
  } else if (name === "edit-mode") {
    el.querySelector(`button[data-mode="${arg}"]`).click();
  } else {
    el.children[0].click();
  }
}

function setDark(dark) {
  document.body.classList.toggle("dark", dark);
  vditor.setTheme(dark ? "dark" : "classic", dark ? "dark" : "light",
    dark ? "native" : "github");
}

function setLinkBase(base) {
  vditor.vditor.lute.SetLinkBase(base);
}

function focusEditor() {
  if (vditor) vditor.focus();
}

// Plugin theme: one extra stylesheet loaded after editor.css
function setThemeCSS(href) {
  let link = document.getElementById("mp-theme");
  if (!href) {
    if (link) link.remove();
    document.body.classList.remove("mp-themed");
    return;
  }
  if (!link) {
    link = document.createElement("link");
    link.id = "mp-theme";
    link.rel = "stylesheet";
    document.head.appendChild(link);
  }
  link.href = href;
  document.body.classList.add("mp-themed");
}

// Document language (front matter "lang: es") – used for hyphenation
function setDocLang(lang) {
  document.documentElement.lang = lang || "de";
}
