# Changelog

What changed in doc2md-lite, newest first.

## 1.1.0 - 2026-11-04

- MCP tool now has safety labels (tool annotations) so AI apps know what it does:
  readOnlyHint false, destructiveHint true, idempotentHint true, openWorldHint false.
- The tool description now says when to use it and when not to.
- Needs mcp 1.10 or newer.

## 1.0.0 - 2026-11-04

- First release.
- Turns a text PDF or a saved HTML page into clean Markdown. Tables stay Markdown tables.
- Free MCP server, `doc2md-lite-mcp`, with one tool, `convert_to_markdown`.
- You can install it from PyPI with `pip install doc2md-lite`.
