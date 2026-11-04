#!/usr/bin/env python3
"""Runner for the Doc2MD Lite GitHub Action (Tidy Byte Tools, MIT).

Reads its settings from INPUT_* environment variables set by action.yml,
turns the matching PDF and HTML files into Markdown with doc2md_lite.py
from this same tag, and reports to the job summary.
"""
import glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import doc2md_lite as d2m  # noqa: E402

TITLE = "Doc2MD Lite"


def env(name, default=""):
    return os.environ.get("INPUT_" + name, default).strip()


def flag(name, default="false"):
    v = env(name, default).lower()
    if v not in ("true", "false"):
        raise ValueError(f"{name.lower().replace('_', '-')} must be true or false (got '{v}')")
    return v == "true"


def number(name, default, low):
    raw = env(name, str(default))
    try:
        n = int(raw)
    except ValueError:
        raise ValueError(f"{name.lower().replace('_', '-')} must be a whole number (got '{raw}')")
    if n < low:
        raise ValueError(f"{name.lower().replace('_', '-')} must be {low} or more (got {n})")
    return n


def patterns(raw):
    out = []
    for line in raw.replace(",", "\n").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def find_files(include, exclude):
    skip = set()
    for p in exclude:
        skip.update(os.path.normpath(x) for x in glob.glob(p, recursive=True))
    found = []
    for p in include:
        for x in sorted(glob.glob(p, recursive=True)):
            n = os.path.normpath(x)
            if os.path.isfile(n) and n not in skip and not any(n.startswith(s + os.sep) for s in skip) and n not in found:
                found.append(n)
    return found


def esc_prop(s):
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(":", "%3A").replace(",", "%2C")


def esc_msg(s):
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def annotate(kind, msg, file=None, line=None, title=None):
    props = []
    if file:
        props.append(f"file={esc_prop(file.replace(os.sep, '/'))}")
    if line:
        props.append(f"line={line}")
    if title:
        props.append(f"title={esc_prop(title)}")
    print(f"::{kind} {','.join(props)}::{esc_msg(msg)}" if props else f"::{kind}::{esc_msg(msg)}")


def write_outputs(values):
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        for k, v in values.items():
            fh.write(f"{k}={v}\n")


def write_summary(text):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(text)


def cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def target_for(path, out_dir):
    md = os.path.splitext(path)[0] + ".md"
    return os.path.normpath(os.path.join(out_dir, md)) if out_dir else md


def read_md(path):
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read().replace("\r\n", "\n")
    except FileNotFoundError:
        return None


def main():
    try:
        include = patterns(env("FILES", "**/*.pdf"))
        exclude = patterns(env("EXCLUDE", ""))
        out_dir = env("OUTPUT_DIR", "")
        tables = env("TABLES", "lines")
        if tables not in ("lines", "text", "off"):
            raise ValueError(f"tables must be lines, text or off (got '{tables}')")
        check = flag("CHECK")
        fail_on_scanned = flag("FAIL_ON_SCANNED")
        fail_if_none = flag("FAIL_IF_NO_FILES", "true")
        if not include:
            raise ValueError("files is empty. Give at least one pattern, like docs/**/*.pdf")
        if out_dir and os.path.isabs(out_dir):
            raise ValueError("output-dir must be a folder inside the repo, not a full path")
    except ValueError as e:
        annotate("error", str(e), title=TITLE)
        return 1

    files = [f for f in find_files(include, exclude)
             if os.path.splitext(f)[1].lower() in (".pdf", ".html", ".htm")]
    empty = {"files": 0, "converted": 0, "changed": 0, "scanned-files": 0, "output-dir": out_dir}
    if not files:
        msg = f"No PDF or HTML files matched: {', '.join(include)}"
        write_outputs(empty)
        write_summary(f"### {TITLE}\n\n{msg}\n")
        if fail_if_none:
            annotate("error", msg + ". Check the files input, or set fail-if-no-files to false.", title=TITLE)
            return 1
        annotate("warning", msg, title=TITLE)
        return 0

    rows, errors, changed, scanned_files = [], 0, [], []
    for f in files:
        dest = target_for(f, out_dir)
        try:
            md, info = d2m.convert(f, tables)
        except Exception as e:  # a broken file should not stop the others
            errors += 1
            annotate("error", f"Could not convert this file: {e}", file=f, title=TITLE)
            rows.append((f, dest, "error", "", "", ""))
            continue
        old = read_md(dest)
        if old is None:
            state = "missing" if check else "new"
        elif old == md:
            state = "same"
        else:
            state = "out of date" if check else "updated"
        if state != "same":
            changed.append((f, dest, state))
        if not check and state != "same":
            os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
            with open(dest, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(md)
        if check and state != "same":
            annotate("error", f"{dest} is {state}. Run doc2md-lite on this file and commit the Markdown.",
                     file=f, title="Markdown copy " + state)
        pages = info.get("scanned_pages") or []
        if pages:
            scanned_files.append(f)
            annotate("error" if fail_on_scanned else "warning",
                     f"Page(s) {', '.join(map(str, pages))} have no text layer (scanned image) and were skipped.",
                     file=f, title="Scanned pages")
        rows.append((f, dest, state, info.get("headings", 0), info.get("tables", 0),
                     ", ".join(map(str, pages)) or "-"))

    converted = sum(1 for r in rows if r[2] != "error")
    write_outputs({"files": len(rows), "converted": converted, "changed": len(changed),
                   "scanned-files": len(scanned_files), "output-dir": out_dir})

    verb = "checked" if check else "converted"
    lines = [f"### {TITLE}", "",
             f"**{converted}** of **{len(rows)}** file(s) {verb}. "
             + (f"**{len(changed)}** Markdown file(s) missing or out of date." if check
                else f"**{len(changed)}** Markdown file(s) new or updated."), "",
             "| File | Markdown | Result | Headings | Tables | Scanned pages |", "|---|---|---|---:|---:|---|"]
    for f, dest, state, h, t, sp in rows[:200]:
        lines.append(f"| `{cell(f)}` | `{cell(dest)}` | {state} | {h} | {t} | {sp} |")
    if len(rows) > 200:
        lines.append(f"| ...and {len(rows) - 200} more | | | | | |")
    write_summary("\n".join(lines) + "\n\n")

    for f, dest, state, *_ in rows:
        print(f"{state:12} {f} -> {dest}")
    if errors:
        return 1
    if check and changed:
        annotate("error", f"{len(changed)} Markdown file(s) are missing or out of date.", title=TITLE)
        return 1
    if fail_on_scanned and scanned_files:
        annotate("error", f"{len(scanned_files)} file(s) have scanned pages with no text.", title=TITLE)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
