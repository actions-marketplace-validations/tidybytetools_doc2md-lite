"""Free MCP server for doc2md-lite (stdio).

Run:  uvx --from git+https://github.com/tidybytetools/doc2md-lite doc2md-lite-mcp
"""
import os
from mcp.server.fastmcp import FastMCP
import doc2md_lite as lite

mcp = FastMCP("doc2md-lite")


@mcp.tool()
def convert_to_markdown(path: str, tables: str = "lines", output_path: str = "") -> str:
    """Turn a local text PDF or saved HTML file into clean Markdown.

    path: full path to a .pdf or .html file on this computer.
    tables: PDF tables. "lines" (default) finds tables with border lines, "text" also tries
    tables lined up by spaces, "off" gives plain text.
    output_path: optional. If set, the Markdown is saved there and that path is returned.
    If empty, the Markdown text is returned.

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
