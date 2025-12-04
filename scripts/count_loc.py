import os
import sys

def count_loc(root: str, exclude_docstrings: bool = False) -> int:
    total = 0
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if not f.endswith('.py'):
                continue
            p = os.path.join(dirpath, f)
            try:
                with open(p, 'r', encoding='utf-8') as fh:
                    in_doc = False
                    doc_delim = None
                    for line in fh:
                        s = line.rstrip()
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
                pass
    return total

def main():
    root_bp = os.path.join(os.path.dirname(__file__), '..', 'blueprint')
    root_ctrl = os.path.join(os.path.dirname(__file__), '..', 'control')
    root_bp = os.path.abspath(root_bp)
    root_ctrl = os.path.abspath(root_ctrl)
    excl = '--no-doc' in sys.argv
    print('Blueprint LOC:', count_loc(root_bp, exclude_docstrings=excl))
    print('Control LOC:', count_loc(root_ctrl, exclude_docstrings=excl))

if __name__ == '__main__':
    main()
