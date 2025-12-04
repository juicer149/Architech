"""Module docstring: should be excluded in logical LOC."""

# Leading comment-only line (excluded in logical)

x = 1  # inline comment should still count

y = 2

# if x:
# comment-only block should be excluded in logical

if x:
    y = y + 1  # inline comment

"""
Trailing docstring-like in code should not occur normally, but if present,
this is part of triple quotes and should be excluded in logical until closed.
"""

z = x + y
