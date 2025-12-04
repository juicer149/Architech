import os
from scripts import loc

FIXTURE = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'python_sample.py')
FIXTURE = os.path.abspath(FIXTURE)


def test_loc_physical_and_logical_counts():
    paths = [FIXTURE]
    # Count physical: all lines
    physical = loc.count_loc(paths, logical=False, exclude_docstrings=False)
    # Count logical: excludes blanks, comment-only, and docstrings
    logical = loc.count_loc(paths, logical=True, exclude_docstrings=True)

    # Derive expected counts by reading file and simulating rules
    with open(FIXTURE, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()

    # Physical LOC equals total lines in file
    assert physical == len(lines)

    # Logical LOC: compute expectation inline
    in_doc = False
    doc_delim = None
    expected_logical = 0
    for line in lines:
        s = line.rstrip()
        if not in_doc:
            if not s.strip():
                continue
            if s.lstrip().startswith('#'):
                continue
            ls = s.lstrip()
            if ls.startswith('"""') or ls.startswith("'''"):
                # one-line docstring
                if ls.count('"""') == 2 or ls.count("'''") == 2:
                    continue
                in_doc = True
                doc_delim = '"""' if ls.startswith('"""') else "'''"
                continue
            expected_logical += 1
        else:
            if doc_delim and doc_delim in s:
                in_doc = False
                doc_delim = None
            continue

    assert logical == expected_logical


def test_iter_paths_single_file():
    paths = loc.iter_paths([FIXTURE], include_exts=(".py",), exclude=[])
    assert len(paths) == 1 and paths[0] == FIXTURE
