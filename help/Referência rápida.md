# Referência rápida de Markdown

É só começar a digitar: o Matt|Pad formata **ao vivo**, como o Typora. Com `Ctrl+2` você vê o código-fonte.

## Títulos

Comece a linha com `# ` (até `###### `) ou use `Ctrl+Alt+1` … `Ctrl+Alt+6`.

## Texto

| Digite | Resultado | Atalho |
| --- | --- | --- |
| `**negrito**` | **negrito** | Ctrl+B |
| `*itálico*` | *itálico* | Ctrl+I |
| `~~tachado~~` | ~~tachado~~ | Ctrl+D |
| `` `código` `` | `código` | Ctrl+G |
| `==destaque==` | ==destaque== | |
| `[Texto](https://…)` | Link | Ctrl+K |

## Listas

- Marcadores com `- ` (Ctrl+L)

1. Numerada com `1. ` (Ctrl+Shift+L)

- [ ] Tarefa com `- [ ] ` (Ctrl+J)

## Blocos

> Citação com `> ` (Ctrl+;)

```python
print("Bloco de código com ``` e a linguagem")
```

Linha divisória com `---` (Ctrl+Shift+H), tabela com Ctrl+M.

Fórmulas: $E = mc^2$ no texto ou em bloco com `$$`.

## Imagens

`![Descrição](imagem.png)`: caminhos relativos referem-se à pasta do arquivo.

## Programa

| Atalho | Função |
| --- | --- |
| Ctrl+N / O / S | Novo / Abrir / Salvar |
| Ctrl+Shift+N | Novo a partir de modelo |
| Ctrl+Shift+S | Salvar tudo |
| Ctrl+W | Fechar aba (também clique do meio) |
| Ctrl+Tab | Próxima aba |
| Ctrl+F, F3 | Localizar, localizar próximo |
| Ctrl+H | Substituir |
| Ctrl+P | Imprimir |
| Ctrl+1 / 2 / 3 | Ao vivo / Código-fonte / WYSIWYG |
| F7 | Ortografia liga/desliga |
| F8 | Estrutura |
| F11 | Tela cheia |
| Ctrl + / – / 0 | Zoom |

## Modelos e temas

**Arquivo → Novo a partir de modelo** (Ctrl+Shift+N) cria um documento a partir de um modelo, por exemplo um capítulo de livro. Título e autor são preenchidos automaticamente.

**Exibir → Tema** define a aparência ao escrever, ao imprimir e ao exportar para PDF/HTML.

Um documento também pode definir o próprio tema, no cabeçalho bem no início:

```yaml
---
title: "Meu capítulo"
author: "Ana Pérez"
lang: pt
theme: libro
---
```

`lang` controla a hifenização no texto justificado (`pt`, `es`, `en`, `de`, …).

Mais modelos e temas vêm como **plugin** (arquivo ZIP): *Ferramentas → Gerenciar plugins → Instalar plugin*.

O idioma da interface é alterado em *Ferramentas → Idioma da interface*.
