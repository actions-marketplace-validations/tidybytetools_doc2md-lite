# doc2md-lite

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/tidybytetools/doc2md-lite/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![MCP server](https://img.shields.io/badge/MCP-stdio-purple.svg)](#use-it-from-claude-desktop-or-cursor-mcp)

Free tool that turns a text PDF or a saved web page (.html) into clean Markdown. Tables stay real Markdown tables.
Need Word files, chunks for AI search (RAG), whole folders or page ranges? The paid version does that: **[doc2md on Gumroad](https://tidybyte.gumroad.com/l/frlkv)**

Runs on your own computer, so your files are never uploaded anywhere. MIT license. Python 3.10 or newer, on Windows, Mac and Linux.

<!-- mcp-name: io.github.tidybytetools/doc2md-lite -->

## Install

```
pip install doc2md-lite
```

Or use pipx, which keeps it in its own space:

```
pipx install doc2md-lite
```

Want the newest code from GitHub instead?

```
pip install git+https://github.com/tidybytetools/doc2md-lite
```

## Use it

```
doc2md-lite report.pdf                 # writes report.md
doc2md-lite page.html -o page.md
doc2md-lite report.pdf -o -            # print the Markdown on screen
doc2md-lite report.pdf --tables text   # also find tables with no border lines
```

Example run:

```
Saved: report.md  (4 headings, 1 tables)
```

What you get from a PDF:

```
# Spring Store Report

Our team checked every store in March. Most stores met the new goal...

## Sales by region

| Region | Stores | Sales |
| --- | --- | --- |
| North | 12 | $48,200 |
| South | 9 | $39,950 |
```

What it keeps: headings (found by font size and bold in PDFs), paragraphs, bullet and numbered lists, tables, and in HTML also bold, italic, links and code blocks. From web pages it drops scripts, styles, menus and footers.

When you run it in a terminal it ends with one short line about the paid version. `--quiet` turns it off, and it never shows when output is piped or redirected.

## Known limits

- **Scanned PDFs.** Pages that are just an image (no text layer) are skipped, and the tool tells you which ones.
- **Headings in PDFs are a best guess** from font size and bold. Odd layouts may need a quick fix.
- **Two-column PDFs** (like science papers) may mix the columns.
- **One file at a time.** No folders, no page ranges, no Word files, no RAG chunks. The paid version has those.
- **Files only.** It does not download web pages. Save the page first.

## Lite vs paid

| | lite (free) | [doc2md](https://tidybyte.gumroad.com/l/frlkv) |
|---|---|---|
| Text PDF and HTML to Markdown | yes | yes |
| Tables kept as Markdown tables | yes | yes |
| Word (.docx), with bold, italic, links and lists | no | yes |
| RAG chunks (JSONL with page, heading path, size and overlap) | no | yes |
| Whole folders, sub-folders too | no | yes |
| Page ranges and password-protected PDFs | no | yes |

## Other good free tools

Pick what fits you. [MarkItDown](https://github.com/microsoft/markitdown) reads many more file types. [pandoc](https://pandoc.org/) is great for Word and HTML but does not read PDFs. [pymupdf4llm](https://github.com/pymupdf/RAG) is fast on PDFs but uses the AGPL license. doc2md-lite is small, MIT, keeps PDF tables as tables, and has an MCP server built in.

## Use it from Claude Desktop or Cursor (MCP)

There is a small free MCP server built in. It gives your AI app one tool, `convert_to_markdown`. It needs [uv](https://docs.astral.sh/uv/).

Run it by hand to check it starts (it waits quietly for an app to talk to it):

```
uvx --from doc2md-lite doc2md-lite-mcp
```

Claude Desktop (`claude_desktop_config.json`) or Cursor (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "doc2md-lite": {
      "command": "uvx",
      "args": ["--from", "doc2md-lite", "doc2md-lite-mcp"]
    }
  }
}
```

Tool: `convert_to_markdown(path, tables="lines", output_path="")`. It returns the Markdown text. If you set `output_path`, it saves the file there and returns the path instead.

## For AI agents

- **Use when:** you have a local PDF with real text (you can select the words) or a saved HTML file, and you want Markdown to read or store.
- **Don't use when:** the PDF is a scan, the file is .docx, or you need many files or chunks with page numbers. Use the paid version for those.
- **Input:** a file path, plus optional `tables` (`lines`, `text`, `off`).
- **Output:** Markdown text. Tables are Markdown tables with the first row as the header.
- CLI exit code is 0 on success and 1 on error (message on stderr, or `{"ok": false, "error": ...}` with `--json`). See also [`llms.txt`](https://github.com/tidybytetools/doc2md-lite/blob/main/llms.txt).

## Python

```python
from doc2md_lite import convert
md, info = convert("report.pdf")   # info: type, tables, headings, scanned_pages
```

## Tests

```
pip install pdfplumber beautifulsoup4 reportlab "mcp<2"
python3 -m unittest discover tests
```

## License

MIT. See `LICENSE`.
