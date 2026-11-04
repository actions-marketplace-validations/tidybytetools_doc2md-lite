<p>
  <a href="https://github.com/tidybytetools">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tidybytetools/doc2md-lite/main/assets/tidybytetools-lockup-dark.png">
      <img alt="Tidy Byte Tools" src="https://raw.githubusercontent.com/tidybytetools/doc2md-lite/main/assets/tidybytetools-lockup-light.png" height="44">
    </picture>
  </a>
</p>

# doc2md-lite

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/tidybytetools/doc2md-lite/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![MCP server](https://img.shields.io/badge/MCP-stdio-purple.svg)](#use-it-with-your-ai-app-mcp)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-listed-green.svg)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.tidybytetools/doc2md-lite)
[![PyPI downloads](https://img.shields.io/pypi/dm/doc2md-lite.svg)](https://pypistats.org/packages/doc2md-lite)
[![Glama score](https://glama.ai/mcp/servers/tidybytetools/doc2md-lite/badges/score.svg)](https://glama.ai/mcp/servers/tidybytetools/doc2md-lite)

**Free. No API key. Runs on your own computer, so your files stay with you.**

A tool that turns a text PDF or a saved web page (.html) into clean Markdown. Tables stay real Markdown tables.
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

## Use it with your AI app (MCP)

There is a small free MCP server built in. It gives your AI app one tool, `convert_to_markdown`. No API key or account is needed. It needs [uv](https://docs.astral.sh/uv/), which gives you the `uvx` command.

Run it by hand to check it starts (it waits quietly for an app to talk to it):

```
uvx --from doc2md-lite doc2md-lite-mcp
```

Pick your app below and copy the block. Restart the app after you save.

### Claude Desktop

Open **Settings > Developer > Edit Config**. That opens `claude_desktop_config.json`. Add this:

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

If Claude says it can't find `uvx`, run `which uvx` (Mac/Linux) or `where uvx` (Windows) and put that full path in `"command"`.

### Cursor

Put the same block in `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project):

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

### VS Code

VS Code uses `servers`, not `mcpServers`. Put this in `.vscode/mcp.json` in your project, or run **MCP: Open User Configuration** to use it everywhere:

```json
{
  "servers": {
    "doc2md-lite": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "doc2md-lite", "doc2md-lite-mcp"]
    }
  }
}
```

Or add it with one command:

```
code --add-mcp '{"name":"doc2md-lite","type":"stdio","command":"uvx","args":["--from","doc2md-lite","doc2md-lite-mcp"]}'
```

### Cline

In the Cline panel, click the **MCP Servers** icon, open **Configure**, then click **Configure MCP Servers**. Add this inside `mcpServers`:

```json
{
  "mcpServers": {
    "doc2md-lite": {
      "command": "uvx",
      "args": ["--from", "doc2md-lite", "doc2md-lite-mcp"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Codex

One command:

```
codex mcp add doc2md-lite -- uvx --from doc2md-lite doc2md-lite-mcp
```

Or add this to `~/.codex/config.toml`:

```toml
[mcp_servers.doc2md-lite]
command = "uvx"
args = ["--from", "doc2md-lite", "doc2md-lite-mcp"]
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
