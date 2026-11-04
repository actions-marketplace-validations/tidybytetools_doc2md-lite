#!/usr/bin/env python3
"""doc2md-lite: turn a text PDF or a saved HTML page into clean Markdown. Tables stay Markdown tables.
Free, MIT license. Runs offline.

Usage:
  doc2md-lite report.pdf             # writes report.md
  doc2md-lite page.html -o page.md
  doc2md-lite page.html -o -         # print to screen

Paid version (Word files, RAG chunks, whole folders, page picking): https://tidybyte.gumroad.com/l/frlkv
"""
import argparse, json, os, re, sys
from collections import Counter

__version__ = "1.0.0"
PAID_URL = "https://tidybyte.gumroad.com/l/frlkv"


# ---------- shared helpers ----------

def parse_pages(spec, total):
    """'1,3-5' -> [1,3,4,5] (1-based). None means every page."""
    if not spec:
        return list(range(1, total + 1))
    pages = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a) if a else 1, (int(b) if b else total) + 1))
        else:
            pages.append(int(part))
    bad = [p for p in pages if p < 1 or p > total]
    if bad:
        raise ValueError(f"page {bad[0]} is out of range (file has {total} pages)")
    return sorted(set(pages))


def _clean_cell(c):
    if c is None:
        return ""
    return re.sub(r"\s+", " ", str(c)).strip()


def clean_table(rows):
    rows = [[_clean_cell(c) for c in r] for r in rows]
    rows = [r for r in rows if any(r)]
    if not rows:
        return []
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    keep = [i for i in range(width) if any(r[i] for r in rows)]
    return [[r[i] for i in keep] for r in rows]


def md_table(rows):
    """Rows (first row = header) -> Markdown table text."""
    rows = clean_table(rows)
    if not rows:
        return ""
    esc = lambda c: c.replace("\\", "\\\\").replace("|", "\\|")
    head = rows[0]
    out = ["| " + " | ".join(esc(c) for c in head) + " |",
           "|" + "|".join(" --- " for _ in head) + "|"]
    out += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows[1:]]
    return "\n".join(out)


def block(kind, text, page=None, level=0):
    return {"kind": kind, "text": text, "page": page, "level": level}


def blocks_to_md(blocks):
    out = []
    for b in blocks:
        if b["kind"] == "heading":
            out.append("#" * b["level"] + " " + b["text"])
        else:
            out.append(b["text"])
    md = "\n\n".join(x.strip("\n") for x in out if x.strip())
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


# ---------- PDF ----------

BULLET_RE = re.compile(r"^\s*[\u2022\u25cf\u25aa\u2013\u00b7*\-]\s+")
NUM_RE = re.compile(r"^\s*(\d{1,3})[.)]\s+")


def _inside(obj, boxes):
    x = (obj["x0"] + obj["x1"]) / 2
    y = (obj["top"] + obj["bottom"]) / 2
    return any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in boxes)


def pdf_blocks(path, pages=None, tables="lines", password=None):
    """Read a text PDF into blocks. tables: 'lines' (ruled tables), 'text' (also space-aligned), 'off'."""
    import pdfplumber
    out = []
    with pdfplumber.open(path, password=password) as pdf:
        nums = parse_pages(pages, len(pdf.pages))
        sizes = Counter()
        for pno in nums:  # body size = the most common font size
            for ch in pdf.pages[pno - 1].chars:
                sizes[round(ch["size"], 1)] += 1
        body = sizes.most_common(1)[0][0] if sizes else 10
        bigger = sorted({s for s in sizes if s >= body * 1.15}, reverse=True)[:3]
        level_of = {s: i + 1 for i, s in enumerate(bigger)}
        scanned = []
        for pno in nums:
            page = pdf.pages[pno - 1]
            if not page.chars:
                scanned.append(pno)
                continue
            items = []
            boxes = []
            if tables != "off":
                st = {"vertical_strategy": "lines", "horizontal_strategy": "lines"}
                found = page.find_tables(st)
                if not found and tables == "text":
                    found = page.find_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})
                for t in found:
                    rows = clean_table(t.extract())
                    if len(rows) >= 2 or (rows and tables == "lines" and len(rows[0]) > 1):
                        boxes.append(t.bbox)
                        items.append((t.bbox[1], block("table", md_table(rows), pno)))
            text_page = page.filter(lambda o: o.get("object_type") != "char" or not _inside(o, boxes)) if boxes else page
            lines = text_page.extract_text_lines(return_chars=True)
            para, last = [], None
            def flush():
                if para:
                    items.append((para[0][0], block("para", " ".join(t for _, t in para), pno)))
                    para.clear()
            for ln in lines:
                txt = re.sub(r"\(cid:\d+\)", "", ln["text"].replace("(cid:127)", "\u2022")).strip()
                if not txt:
                    continue
                size = round(Counter(round(c["size"], 1) for c in ln["chars"]).most_common(1)[0][0], 1)
                bold = sum("Bold" in c.get("fontname", "") for c in ln["chars"]) > len(ln["chars"]) * 0.8
                lvl = level_of.get(size)
                if lvl is None and bold and len(txt) < 80 and not txt.endswith((".", ",", ":")):
                    lvl = min(len(bigger) + 1, 6)
                if lvl:
                    flush()
                    items.append((ln["top"], block("heading", txt, pno, lvl)))
                    last = None
                    continue
                m = BULLET_RE.match(txt) or NUM_RE.match(txt)
                if m:
                    flush()
                    mark = (m.group(1) + ".") if m.re is NUM_RE else "-"
                    items.append((ln["top"], block("list", f"{mark} {txt[m.end():].strip()}", pno)))
                    last = ln
                    continue
                gap = (ln["top"] - last["bottom"]) if last else 0
                if last and gap > size * 0.9:
                    flush()
                if para and para[-1][1].endswith("-") and not para[-1][1].endswith(" -"):
                    para[-1] = (para[-1][0], para[-1][1][:-1] + txt)  # re-join a split word
                else:
                    para.append((ln["top"], txt))
                last = ln
            flush()
            items.sort(key=lambda x: x[0])
            merged = []
            for _, b in items:  # glue list items into one list block
                if merged and b["kind"] == "list" and merged[-1]["kind"] == "list" and merged[-1]["page"] == b["page"]:
                    merged[-1]["text"] += "\n" + b["text"]
                else:
                    merged.append(b)
            out.extend(merged)
    return out, scanned


# ---------- HTML ----------

SKIP_TAGS = {"script", "style", "noscript", "head", "template", "svg", "iframe", "form", "button"}
CHROME_TAGS = {"nav", "footer", "aside"}


def _inline(node):
    return _inline_nodes(node.children)


def _inline_nodes(children):
    from bs4 import NavigableString, Comment
    out = []
    for c in children:
        if isinstance(c, Comment):
            continue
        if isinstance(c, NavigableString):
            out.append(re.sub(r"\s+", " ", str(c)))
            continue
        n = c.name
        if n in SKIP_TAGS:
            continue
        inner = _inline(c)
        core = inner.strip()
        if n == "br":
            out.append("  \n")
        elif n in ("strong", "b") and core:
            out.append(inner.replace(core, f"**{core}**", 1))
        elif n in ("em", "i") and core:
            out.append(inner.replace(core, f"*{core}*", 1))
        elif n == "code" and core:
            out.append(f"`{core}`")
        elif n == "a" and core and c.get("href") and not c["href"].startswith(("javascript:", "#")):
            out.append(f"[{core}]({c['href']})")
        elif n == "img":
            alt = c.get("alt", "").strip()
            if alt:
                out.append(f"![{alt}]({c.get('src', '')})")
        else:
            out.append(inner)
    return "".join(out)


def _html_list(node, depth=0):
    lines, i = [], 1
    for li in node.find_all("li", recursive=False):
        subs = [s.extract() for s in li.find_all(["ul", "ol"], recursive=False)]
        mark = f"{i}." if node.name == "ol" else "-"
        lines.append("    " * depth + f"{mark} " + re.sub(r"\s+", " ", _inline(li)).strip())
        for s in subs:
            lines.extend(_html_list(s, depth + 1))
        i += 1
    return lines


def _html_walk(node, out):
    from bs4 import NavigableString, Tag
    buf = []
    def flush():
        t = re.sub(r"[ \t]+", " ", "".join(buf)).strip()
        if t:
            out.append(block("para", t))
        buf.clear()
    for c in node.children:
        if not isinstance(c, Tag):
            if isinstance(c, NavigableString) and type(c).__name__ == "NavigableString":
                buf.append(str(c))
            continue
        n = c.name
        if n in SKIP_TAGS:
            continue
        if re.fullmatch(r"h[1-6]", n):
            flush()
            t = re.sub(r"\s+", " ", c.get_text(" ")).strip()
            if t:
                out.append(block("heading", t, level=int(n[1])))
        elif n == "p":
            flush()
            t = re.sub(r"[ \t]+", " ", _inline(c)).strip()
            if t:
                out.append(block("para", t))
        elif n in ("ul", "ol"):
            flush()
            lines = _html_list(c)
            if lines:
                out.append(block("list", "\n".join(lines)))
        elif n == "table":
            flush()
            rows = []
            for tr in c.find_all("tr"):
                if tr.find_parent("table") is not c:
                    continue
                rows.append([re.sub(r"\s+", " ", _inline(td)).strip() for td in tr.find_all(["th", "td"], recursive=False)])
            t = md_table(rows)
            if t:
                out.append(block("table", t))
        elif n == "pre":
            flush()
            code = c.get_text()
            lang = ""
            cd = c.find("code")
            if cd:
                for cls in cd.get("class", []):
                    if cls.startswith("language-"):
                        lang = cls[9:]
            out.append(block("code", f"```{lang}\n{code.strip(chr(10))}\n```"))
        elif n == "blockquote":
            flush()
            sub = []
            _html_walk(c, sub)
            txt = blocks_to_md(sub).strip()
            if txt:
                out.append(block("para", "\n".join("> " + l if l else ">" for l in txt.split("\n"))))
        elif n == "hr":
            flush()
            out.append(block("para", "---"))
        elif n in ("div", "section", "article", "main", "body", "html", "header", "figure", "nav", "footer", "aside", "dl", "details"):
            flush()
            _html_walk(c, out)
        else:
            buf.append(_inline_nodes([c]))
    flush()


def html_blocks(path_or_text, keep_chrome=False, is_text=False):
    from bs4 import BeautifulSoup
    if is_text:
        raw = path_or_text
    else:
        with open(path_or_text, "rb") as f:
            raw = f.read()
    soup = BeautifulSoup(raw, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    for t in soup.find_all(list(SKIP_TAGS)):
        t.decompose()
    if not keep_chrome:
        for t in soup.find_all(list(CHROME_TAGS)):
            t.decompose()
    root = soup.find("main") or soup.find("article") or soup.body or soup
    out = []
    _html_walk(root, out)
    if not any(b["kind"] == "heading" and b["level"] == 1 for b in out) and title:
        out.insert(0, block("heading", title, level=1))
    return out


# ---------- top level ----------

def convert(path, tables="lines"):
    """Return (markdown, info) for one .pdf or .html file."""
    ext = os.path.splitext(path)[1].lower()
    info = {"type": ext[1:], "scanned_pages": []}
    if ext == ".pdf":
        blocks, info["scanned_pages"] = pdf_blocks(path, None, tables)
    elif ext in (".html", ".htm"):
        blocks = html_blocks(path)
    else:
        raise ValueError(f"lite reads .pdf and .html only (got '{ext}'). Word files need the paid version: {PAID_URL}")
    info["tables"] = sum(1 for b in blocks if b["kind"] == "table")
    info["headings"] = sum(1 for b in blocks if b["kind"] == "heading")
    return blocks_to_md(blocks), info


def main(argv=None):
    ap = argparse.ArgumentParser(description="Turn a text PDF or HTML file into clean Markdown.")
    ap.add_argument("file", help="a .pdf or .html file")
    ap.add_argument("-o", "--output", help="output .md file, or - for the screen. Default: next to the input")
    ap.add_argument("--tables", choices=["lines", "text", "off"], default="lines",
                    help="PDF tables: lines (with borders, default), text (also lined up by spaces), off")
    ap.add_argument("--json", action="store_true", help="print a JSON summary (for scripts and agents)")
    ap.add_argument("-q", "--quiet", action="store_true", help="no tip about the paid version")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    try:
        if not os.path.isfile(a.file):
            raise FileNotFoundError(f"file not found: {a.file}")
        md, info = convert(a.file, a.tables)
        out = a.output or os.path.splitext(a.file)[0] + ".md"
        if out == "-":
            sys.stdout.write(md)
            return 0
        with open(out, "w", encoding="utf-8") as f:
            f.write(md)
        if a.json:
            print(json.dumps({"ok": True, "input": a.file, "output": out, "chars": len(md), **info}))
        else:
            print(f"Saved: {out}  ({info['headings']} headings, {info['tables']} tables)")
            if info["scanned_pages"]:
                print(f"Note: pages {info['scanned_pages']} have no text (scanned) and were skipped.")
            if not a.quiet and sys.stdout.isatty():
                print(f"Need Word files, RAG chunks or whole folders? {PAID_URL}")
        return 0
    except Exception as e:
        if a.json:
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
