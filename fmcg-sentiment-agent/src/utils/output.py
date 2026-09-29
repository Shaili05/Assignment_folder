"""
output.py

Single place for real command-line output (reports, JSON, tables).
Logging goes to stderr, results go to stdout through this helper.
"""

import sys


def write_line(text=""):
    sys.stdout.write(f"{text}\n")


