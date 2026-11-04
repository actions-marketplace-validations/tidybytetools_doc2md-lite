# Changelog

What changed in doc2md-lite, newest first.

## 1.1.1 - 2026-11-04

- Fix: installing from the MCP Registry now starts the MCP server. Before, it started the plain command-line tool by mistake.
- New: `doc2md-lite mcp` starts the MCP server. `uvx doc2md-lite mcp` works too. The old `doc2md-lite-mcp` command still works.
- To read a file that is named `mcp`, use `./mcp`.

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
