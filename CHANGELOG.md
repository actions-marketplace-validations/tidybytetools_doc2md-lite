# Changelog

What changed in doc2md-lite, newest first.

## 1.2.2 - 2026-11-09

- Shorten the GitHub Action description to under 125 characters so the Action can be listed on the GitHub Marketplace.

## 1.2.1 - 2026-11-09

- Point Homepage, Documentation, and the MCP Registry websiteUrl at the official product page on [tidybytetools.github.io](https://tidybytetools.github.io/tools/doc2md/).
- README: add a clear Links section (Website, Apify cloud version where it exists, Pro on Gumroad) and a short FAQ.

## 1.2.0 - 2026-11-09

- Fix: if the Markdown was saved under a hidden folder like `.github/`, the artifact upload said no files were found. The upload now includes those folders.
- New: a GitHub Action (`action.yml`). Add `uses: tidybytetools/doc2md-lite@v1` to a workflow to turn the PDF and HTML files in your repo into Markdown.
- Check mode (`check: "true"`) fails the step when a committed Markdown copy is missing or out of date.
- The action warns about scanned PDF pages, can upload the Markdown as an artifact, and writes a report to the run page.
- The command-line tool and MCP server did not change.

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
