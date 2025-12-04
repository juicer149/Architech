#!/usr/bin/env python3
import argparse
import os
import sys
from typing import List, Tuple, Dict


def iter_paths(targets: List[str], include_exts: Tuple[str, ...], exclude: List[str]) -> List[str]:
    files: List[str] = []
    exclude_set = set(os.path.abspath(p) for p in exclude)

    def is_excluded(path: str) -> bool:
        ap = os.path.abspath(path)
        if ap in exclude_set:
            return True
        for ex in exclude_set:
            if ap.startswith(ex + os.sep):
                return True
        return False

    # If no explicit targets passed, default to current directory
    if not targets:
        targets = [os.getcwd()]

    for target in targets:
        if os.path.isfile(target):
            if is_excluded(target):
                continue
            if include_exts and not target.endswith(include_exts):
                return files
            files.append(target)
            continue

        root = target
        if not os.path.isdir(root):
            # allow glob-like folder/* expansion
            # if target ends with * or **, derive base
            base = target.rstrip("*/")
            if os.path.isdir(base):
                root = base
            else:
                # skip invalid target
                continue

        for dirpath, _, filenames in os.walk(root):
            if is_excluded(dirpath):
                continue
            for f in filenames:
                path = os.path.join(dirpath, f)
                if is_excluded(path):
                    continue
                if include_exts and not path.endswith(include_exts):
                    continue
                files.append(path)
    return files


def count_loc(paths: List[str], logical: bool, exclude_docstrings: bool) -> int:
    total = 0
    for p in paths:
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                in_doc = False
                doc_delim = None
                for line in fh:
                    s = line.rstrip()
                    if not logical:
                        total += 1
                        continue
                    if not in_doc:
                        if not s.strip():
                            continue
                        if s.lstrip().startswith('#'):
                            continue
                        if exclude_docstrings:
                            ls = s.lstrip()
                            if ls.startswith('"""') or ls.startswith("'''"):
                                # one-line docstring
                                if ls.count('"""') == 2 or ls.count("'''") == 2:
                                    continue
                                in_doc = True
                                doc_delim = '"""' if ls.startswith('"""') else "'''"
                                continue
                        total += 1
                    else:
                        if doc_delim and doc_delim in s:
                            in_doc = False
                            doc_delim = None
                        # skip docstring content
                        continue
        except Exception:
            # ignore unreadable files
            pass
    return total


def count_file(p: str, logical: bool, exclude_docstrings: bool) -> int:
    try:
        with open(p, 'r', encoding='utf-8') as fh:
            in_doc = False
            doc_delim = None
            total = 0
            for line in fh:
                s = line.rstrip()
                if not logical:
                    total += 1
                    continue
                if not in_doc:
                    if not s.strip():
                        continue
                    if s.lstrip().startswith('#'):
                        continue
                    if exclude_docstrings:
                        ls = s.lstrip()
                        if ls.startswith('"""') or ls.startswith("'''"):
                            # one-line docstring
                            if ls.count('"""') == 2 or ls.count("'''") == 2:
                                continue
                            in_doc = True
                            doc_delim = '"""' if ls.startswith('"""') else "'''"
                            continue
                    total += 1
                else:
                    if doc_delim and doc_delim in s:
                        in_doc = False
                        doc_delim = None
                    continue
            return total
    except Exception:
        return 0


def count_breakdown_file(p: str) -> Dict[str, int]:
    """Return breakdown: total, blanks, comments, docstrings, code (logical) and chars per category."""
    out = {
        "total": 0,
        "blanks": 0,
        "comments": 0,
        "docstrings": 0,
        "code": 0,
        # char counts
        "chars_blanks": 0,
        "chars_comments": 0,
        "chars_docstrings": 0,
        "chars_code": 0,
    }
    try:
        with open(p, 'r', encoding='utf-8') as fh:
            in_doc = False
            doc_delim = None
            for line in fh:
                out["total"] += 1
                s = line.rstrip()
                if not in_doc:
                    if not s.strip():
                        out["blanks"] += 1
                        out["chars_blanks"] += len(line)
                        continue
                    if s.lstrip().startswith('#'):
                        out["comments"] += 1
                        out["chars_comments"] += len(line)
                        continue
                    ls = s.lstrip()
                    if ls.startswith('"""') or ls.startswith("'''"):
                        # one-line docstring
                        if ls.count('"""') == 2 or ls.count("'''") == 2:
                            out["docstrings"] += 1
                            out["chars_docstrings"] += len(line)
                            continue
                        in_doc = True
                        doc_delim = '"""' if ls.startswith('"""') else "'''"
                        out["docstrings"] += 1
                        out["chars_docstrings"] += len(line)
                        continue
                    out["code"] += 1
                    out["chars_code"] += len(line)
                else:
                    out["docstrings"] += 1
                    out["chars_docstrings"] += len(line)
                    if doc_delim and doc_delim in s:
                        in_doc = False
                        doc_delim = None
                    continue
    except Exception:
        pass
    return out


# ---------- Aggregation & Rendering Helpers ----------

def summarize_folder(folder: str, fps: List[str]) -> Dict[str, object]:
    """Aggregate metrics for a folder and compute per-file rows.

    Returns dict with keys:
      total, docs, comments, blanks, logical,
      chars_total, chars_docs, chars_comments, chars_blanks, chars_logical,
      file_rows: List[Tuple[file_rel, total_lines, total_chars, logical_lines, logical_chars, docs_lines, docs_chars]]
    """
    f_total = f_docs = f_comments = f_blanks = f_logical = 0
    f_chars_total = f_chars_docs = f_chars_comments = f_chars_blanks = f_chars_logical = 0
    file_rows: List[Tuple[str, int, int, int, int, int, int]] = []
    for fp in sorted(fps):
        bd = count_breakdown_file(fp)
        f_total += bd["total"]
        f_docs += bd["docstrings"]
        f_comments += bd["comments"]
        f_blanks += bd["blanks"]
        f_logical += bd["code"]
        f_chars_total += bd.get("chars_blanks", 0) + bd.get("chars_comments", 0) + bd.get("chars_docstrings", 0) + bd.get("chars_code", 0)
        f_chars_docs += bd.get("chars_docstrings", 0)
        f_chars_comments += bd.get("chars_comments", 0)
        f_chars_blanks += bd.get("chars_blanks", 0)
        f_chars_logical += bd.get("chars_code", 0)
        rel = os.path.relpath(fp, folder if os.path.isdir(folder) else os.path.dirname(fp))
        file_total_chars = bd.get("chars_blanks", 0) + bd.get("chars_comments", 0) + bd.get("chars_docstrings", 0) + bd.get("chars_code", 0)
        file_rows.append((
            rel,
            bd["total"], file_total_chars,
            bd["code"], bd.get("chars_code", 0),
            bd["docstrings"], bd.get("chars_docstrings", 0),
        ))

    return {
        "total": f_total,
        "docs": f_docs,
        "comments": f_comments,
        "blanks": f_blanks,
        "logical": f_logical,
        "chars_total": f_chars_total,
        "chars_docs": f_chars_docs,
        "chars_comments": f_chars_comments,
        "chars_blanks": f_chars_blanks,
        "chars_logical": f_chars_logical,
        "file_rows": file_rows,
    }


def print_summary_table(title: str, total: int, docs: int, comments: int, logical: int,
                        chars_total: int, chars_docs: int, chars_comments: int, chars_logical: int) -> None:
    print(f"\n{title}:")
    sum_col1 = "Category"
    sum_col2 = "Lines"
    sum_col3 = "Chars"
    sum_rows = [
        ("Total", total, chars_total),
        ("Documentation", docs, chars_docs),
        ("Comments", comments, chars_comments),
        ("Logical", logical, chars_logical),
    ]
    sw1 = max(len(sum_col1), *(len(str(r[0])) for r in sum_rows))
    sw2 = max(len(sum_col2), *(len(str(r[1])) for r in sum_rows))
    sw3 = max(len(sum_col3), *(len(str(r[2])) for r in sum_rows))
    ssep = "+" + "-" * (sw1 + 2) + "+" + "-" * (sw2 + 2) + "+" + "-" * (sw3 + 2) + "+"
    print("    " + ssep)
    print(f"    | {sum_col1.ljust(sw1)} | {sum_col2.rjust(sw2)} | {sum_col3.rjust(sw3)} |")
    print("    " + ssep)
    for n, lns, chs in sum_rows:
        print(f"    | {str(n).ljust(sw1)} | {str(lns).rjust(sw2)} | {str(chs).rjust(sw3)} |")
    print("    " + ssep)


def print_file_table(file_rows: List[Tuple[str, int, int, int, int, int, int]], summary_only: bool) -> None:
    if summary_only:
        return
    col1 = "File"
    sub_l = "Lines"
    sub_c = "Chars"
    w1 = max(len(col1), *(len(str(r[0])) for r in file_rows)) if file_rows else len(col1)
    w2 = max(len(sub_l), *(len(str(r[1])) for r in file_rows)) if file_rows else len(sub_l)
    w3 = max(len(sub_c), *(len(str(r[2])) for r in file_rows)) if file_rows else len(sub_c)
    w4 = max(len(sub_l), *(len(str(r[3])) for r in file_rows)) if file_rows else len(sub_l)
    w5 = max(len(sub_c), *(len(str(r[4])) for r in file_rows)) if file_rows else len(sub_c)
    w6 = max(len(sub_l), *(len(str(r[5])) for r in file_rows)) if file_rows else len(sub_l)
    w7 = max(len(sub_c), *(len(str(r[6])) for r in file_rows)) if file_rows else len(sub_c)

    gw_total = (w2 + 2) + (w3 + 2)
    gw_logical = (w4 + 2) + (w5 + 2)
    gw_docs = (w6 + 2) + (w7 + 2)

    gsep = "+" + "-" * (w1 + 2) + "+" + "-" * gw_total + "+" + "-" * gw_logical + "+" + "-" * gw_docs + "+"
    print("\n    " + gsep)
    print(f"    | {col1.ljust(w1)} | {'Total'.center(gw_total)} | {'Logical'.center(gw_logical)} | {'Documentation'.center(gw_docs)} |")

    dsep = "+" + "-" * (w1 + 2) + "+" + "-" * (w2 + 2) + "+" + "-" * (w3 + 2) + "+" + "-" * (w4 + 2) + "+" + "-" * (w5 + 2) + "+" + "-" * (w6 + 2) + "+" + "-" * (w7 + 2) + "+"
    print("    " + dsep)
    print(f"    | {' '.ljust(w1)} | {sub_l.rjust(w2)} | {sub_c.rjust(w3)} | {sub_l.rjust(w4)} | {sub_c.rjust(w5)} | {sub_l.rjust(w6)} | {sub_c.rjust(w7)} |")
    print("    " + dsep)
    for r in file_rows:
        r1, r2, r3, r4, r5, r6, r7 = r
        print(f"    | {str(r1).ljust(w1)} | {str(r2).rjust(w2)} | {str(r3).rjust(w3)} | {str(r4).rjust(w4)} | {str(r5).rjust(w5)} | {str(r6).rjust(w6)} | {str(r7).rjust(w7)} |")
    print("    " + dsep)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Count LOC and logical LOC in Python code.")
    parser.add_argument('targets', nargs='*', help="Files or folders to include (default: current directory). Use folder/ to indicate a folder or a specific file path.")
    parser.add_argument('--ext', default='py', help="File extension to include (default: py). Currently only Python is supported.")
    parser.add_argument('--exclude', nargs='*', default=[], help="Paths (files or folders) to exclude.")
    parser.add_argument('--logical', action='store_true', help="Show only logical LOC (exclude blanks, comments, docstrings); otherwise print full breakdown.")
    parser.add_argument('--summary-only', '--sum', dest='summary_only', action='store_true', help="Only print per-folder and grand summary tables; hide per-file tables.")
    parser.add_argument('--no-doc', action='store_true', help="Deprecated: docstrings are excluded by default in logical counts.")

    args = parser.parse_args(argv)

    include_exts = (f".{args.ext}",)
    paths = iter_paths(args.targets, include_exts, args.exclude)
    if not paths:
        print("No files matched.")
        return 1

    # When logical is requested, exclude docstrings by default.
    exclude_doc = True

    # Group by top-level folder provided in targets for reporting
    by_folder: Dict[str, List[str]] = {}
    for p in paths:
        # determine which target folder this file belongs to
        folder = None
        for t in args.targets:
            tb = t.rstrip('*/')
            if os.path.isdir(tb) and os.path.abspath(p).startswith(os.path.abspath(tb) + os.sep):
                folder = tb
                break
        folder = folder or 'files'
        by_folder.setdefault(folder, []).append(p)

    banner = "#" * 43
    title = "Lines of Code (LOC)"
    print(banner)
    # center title within banner width
    print(f"# {title.center(39)} #")
    print(banner)
    grand_total = grand_logical = grand_docs = grand_comments = 0
    grand_chars_total = grand_chars_docs = grand_chars_comments = grand_chars_logical = 0

    for folder, fps in by_folder.items():
        summary = summarize_folder(folder, fps)

        grand_total += summary["total"]
        grand_logical += summary["logical"]
        grand_docs += summary["docs"]
        grand_comments += summary["comments"]
        grand_chars_total += summary["chars_total"]
        grand_chars_docs += summary["chars_docs"]
        grand_chars_comments += summary["chars_comments"]
        grand_chars_logical += summary["chars_logical"]

        print_summary_table(
            folder,
            summary["total"], summary["docs"], summary["comments"], summary["logical"],
            summary["chars_total"], summary["chars_docs"], summary["chars_comments"], summary["chars_logical"],
        )
        print_file_table(summary["file_rows"], args.summary_only)
        

    print_summary_table(
        "Total",
        grand_total, grand_docs, grand_comments, grand_logical,
        grand_chars_total, grand_chars_docs, grand_chars_comments, grand_chars_logical,
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
