"""Free MCP server for doc2md-lite (stdio).

Run:  uvx --from git+https://github.com/tidybytetools/doc2md-lite doc2md-lite-mcp
"""
import os
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
import doc2md_lite as lite

mcp = FastMCP("doc2md-lite")


@mcp.tool(
    title="Convert PDF or HTML to Markdown",
    annotations=ToolAnnotations(
        title="Convert PDF or HTML to Markdown",
        readOnlyHint=False,      # writes a file when output_path is set
        destructiveHint=True,    # replaces the file at output_path if it exists
        idempotentHint=True,     # same input gives the same output
        openWorldHint=False,     # local files only, no network
    ),
)
def convert_to_markdown(path: str, tables: str = "lines", output_path: str = "") -> str:
    """Turn a local text PDF or saved HTML file into clean Markdown.

    Use this when you want to read, quote, summarize or index a document as text,
    for example before RAG chunking or pasting into a prompt. Tables are kept as
    Markdown tables. Do not use it for scanned PDFs or photos (there is no OCR),
    for live web URLs (save the page as .html first), or when you only need the
    tables as CSV data (use a PDF table extractor instead).

    path: full path to a .pdf or .html file on this computer.
    tables: PDF tables. "lines" (default) finds tables with border lines, "text" also tries
    tables lined up by spaces, "off" gives plain text.
    output_path: optional. If set, the Markdown is saved there and that path is returned.
    An existing file at that path is replaced. If empty, nothing is written and the
    Markdown text is returned.

    Tables come back as Markdown tables. Scanned (image-only) PDF pages have no text and are skipped.
    """
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"file not found: {path}")
    if tables not in ("lines", "text", "off"):
        raise ValueError("tables must be lines, text or off")
    md, _info = lite.convert(path, tables)
    if output_path:
        output_path = os.path.expanduser(output_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
        return output_path
    return md


def main():
    mcp.run()


if __name__ == "__main__":
    main()
