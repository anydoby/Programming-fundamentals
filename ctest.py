#!/usr/bin/env python3
# Python port of ctest.sh (original author: David De Potter).
# Works on Linux and macOS: needs only Python 3.8+, gcc (or the gcc
# alias for clang on macOS), and optionally valgrind.

"""
ctest.py

Compiles a user's C program and runs it on all test cases
found in a test folder (default: ./tests).

Each test case consists of:
  - <name>.in   input
  - <name>.out  expected output

If the user's program includes a clib header, the script will:
  - infer the library root
  - build libclib.a if missing
  - compile and link against build/lib/libclib.a

Output is compared like `diff -Z` after normalizing the final newline:
trailing whitespace on each line and a missing final newline are ignored.
"""

import os
import re
import shutil
import signal
import subprocess
import sys
from pathlib import Path


#-------------------------------------------------------------------#
#    Colors (disabled when stdout is not a terminal)                #
#-------------------------------------------------------------------#

if sys.stdout.isatty():
    CYAN, BBLUE, BLUE = "\033[1;36m", "\033[1;34m", "\033[0;34m"
    GREEN, RED, MAGENTA = "\033[32m", "\033[31m", "\033[35m"
    NC = "\033[0m"
else:
    CYAN = BBLUE = BLUE = GREEN = RED = MAGENTA = NC = ""


#-------------------------------------------------------------------#
#    Helper functions                                               #
#-------------------------------------------------------------------#

def die(msg):
    print(f"\n{RED}Error:{NC} {msg}")
    sys.exit(1)


def print_help():
    prog = sys.argv[0]
    print(f"""
Usage:
  {prog} <program.c> [options]

Description:
  Compiles <program.c> and runs it against all test cases in ./tests
  (or a folder you provide if ./tests is not found).

Options:
  --show-diff, -d
      Show the first 5 lines of expected vs actual output for each
      failed correctness test.

  --show-vg, -e
      Show valgrind error details for each failed valgrind check.

  --valgrind, -v
      Run valgrind on all test cases. Output remains a clean summary
      unless --show-vg or -e is enabled.

  --timeout SECONDS, -t SECONDS
      Fail a test if the program runs longer than this (default: 10,
      0 disables the limit).

  --help, -h
      Show this message and exit.

Examples:
  {prog} prog.c
  {prog} prog.c --show-diff
  {prog} prog.c --valgrind
  {prog} prog.c --valgrind --show-vg
  {prog} prog.c --show-diff --valgrind --show-vg
""")


#-------------------------------------------------------------------#
#    Parse arguments                                                #
#-------------------------------------------------------------------#

def parse_args(argv):
    if not argv:
        print_help()
        sys.exit(1)
    if argv[0] in ("--help", "-h"):
        print_help()
        sys.exit(0)

    opts = {"prog": argv[0], "show_diff": False, "show_vg": False,
            "valgrind": False, "timeout": 10.0}
    args = iter(argv[1:])
    for arg in args:
        if arg in ("--show-diff", "-d"):
            opts["show_diff"] = True
        elif arg in ("--show-vg", "-e"):
            opts["show_vg"] = True
        elif arg in ("--valgrind", "-v"):
            opts["valgrind"] = True
        elif arg in ("--timeout", "-t"):
            try:
                opts["timeout"] = float(next(args))
            except (StopIteration, ValueError):
                die("--timeout needs a number of seconds")
        elif arg in ("--help", "-h"):
            print_help()
            sys.exit(0)
        else:
            print(f"\nUnknown option: {arg}")
            print_help()
            sys.exit(1)
    return opts


#-------------------------------------------------------------------#
#    Compile program (with optional clib linking)                   #
#-------------------------------------------------------------------#

# Any non-commented include containing ".../C-library/include/<...>.h"
CLIB_RE = re.compile(
    r'^[ \t]*#include[ \t]*["<]([^">]*C-library/include/[^">]+\.h)[">]',
    re.MULTILINE)


def find_compiler():
    for cc in ("gcc", "cc", "clang"):
        if shutil.which(cc):
            return cc
    die("gcc not found. Please install gcc.")


def built_for_other_os(liba):
    """True if the archive holds object files of the wrong format, e.g.
    a Linux (ELF) libclib.a checked into git, used on macOS (Mach-O)."""
    data = liba.read_bytes()
    elf = b"\x7fELF" in data
    macho = b"\xcf\xfa\xed\xfe" in data or b"\xce\xfa\xed\xfe" in data
    if sys.platform == "darwin":
        return elf and not macho
    return macho and not elf


def compile_program(prog, cc):
    source = Path(prog).read_text(errors="replace")
    cmd = [cc, "-O2", "-std=c99", "-pedantic", "-Wall", "-o", "a.out"]

    match = CLIB_RE.search(source)
    if match:
        # Quoted includes are resolved relative to the source file.
        header = Path(match.group(1))
        if not header.is_absolute():
            header = Path(prog).resolve().parent / header
        libroot = header.parent.parent.resolve()   # .../C-library

        if not (libroot / "src").is_dir():
            die(f"clib src/ not found in: {libroot}")
        if not (libroot / "Makefile").is_file():
            die(f"Makefile not found in: {libroot}")

        liba = libroot / "build" / "lib" / "libclib.a"
        if not liba.is_file() or built_for_other_os(liba):
            print("\nBuilding clib static library...")
            target = ["clean", "lib"] if liba.is_file() else ["lib"]
            build = subprocess.run(["make", "-C", str(libroot), *target],
                                   stdout=subprocess.DEVNULL)
            if build.returncode != 0:
                die("Building clib failed.")
        if not liba.is_file():
            die(f"Static library not found: {liba}")

        print("\nCompiling the program with library clib...")
        cmd += [f"-I{libroot / 'include'}", prog, str(liba), "-lm"]
    else:
        print("\nCompiling the program...")
        cmd += [prog, "-lm"]

    sys.stdout.flush()
    if subprocess.run(cmd).returncode != 0:
        die("Compilation failed.")
    print("\nProgram successfully compiled as a.out")


#-------------------------------------------------------------------#
#    Locate and load test cases                                     #
#-------------------------------------------------------------------#

def locate_tests():
    test_dir = "./tests"
    while not os.path.isdir(test_dir):
        print(f"\nCould not find {test_dir}")
        print("Please provide a test folder (Enter to quit):")
        try:
            test_dir = input().strip()
        except EOFError:
            test_dir = ""
        if not test_dir:
            print("Compiled program not tested.")
            sys.exit(0)
    return Path(test_dir)


def natural_key(path):
    """Sort like `sort -V`: 2.in before 10.in."""
    return [int(part) if part.isdigit() else part
            for part in re.split(r"(\d+)", path.name)]


def display_name(name):
    """Pad the test number to two digits: 1.in -> 01.in."""
    m = re.match(r"^(.*[^0-9])?([0-9]+)(\.in)$", name)
    if not m:
        return name
    return f"{m.group(1) or ''}{int(m.group(2)):02d}{m.group(3)}"


#-------------------------------------------------------------------#
#    Output comparison                                              #
#-------------------------------------------------------------------#

def normalized_lines(data):
    """Lines without trailing whitespace; a missing final newline is
    not a difference (same as the final-newline fix + diff -Z)."""
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return [line.rstrip() for line in lines]


def show_diff_summary(expected, actual):
    for label, color, data in (("Expected:", GREEN, expected),
                               ("Actual:", RED, actual)):
        print(f"         {color}{label}{NC}")
        if data:
            text = data.decode(errors="replace").split("\n")
            if text[-1] == "":
                text.pop()
            for line in text[:5]:
                print(f"         {color}{line}{NC}")
        else:
            print("         (empty)")
        print()


#-------------------------------------------------------------------#
#    Valgrind reporting                                             #
#-------------------------------------------------------------------#

def valgrind_passed(out):
    return ("in use at exit: 0 bytes in 0 blocks" in out
            and "0 errors from 0 contexts" in out)


def show_valgrind_details(out):
    summary = re.compile(r"==.*(HEAP SUMMARY|LEAK SUMMARY|ERROR SUMMARY|"
                         r"in use at exit:|definitely lost:|indirectly lost:|"
                         r"possibly lost:|still reachable:)")
    invalid = re.compile(r"==.*(Invalid read|Invalid write|"
                         r"Use of uninitialised value|Conditional jump|"
                         r"Invalid free)")
    lines = out.splitlines()
    for line in [l for l in lines if summary.search(l)][:40]:
        print(f" {line}")
    inv = [l for l in lines if invalid.search(l)][:12]
    if inv:
        print("\n         Details:")
        for line in inv:
            print(f" {line}")


#-------------------------------------------------------------------#
#    Run tests                                                      #
#-------------------------------------------------------------------#

def describe_exit(rc):
    if rc < 0:
        try:
            return f"killed by signal {signal.Signals(-rc).name}"
        except ValueError:
            return f"killed by signal {-rc}"
    return f"exited with code {rc}"


def run_test(infile, outfile, opts):
    """Run one correctness test; returns True on PASS."""
    name = display_name(infile.name)
    timeout = opts["timeout"] or None
    sys.stdout.flush()
    try:
        with open(infile, "rb") as fin:
            result = subprocess.run(["./a.out"], stdin=fin,
                                    stdout=subprocess.PIPE, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"   Test {name}:    {RED}FAIL{NC} ")
        print(f"   (program did not finish within {opts['timeout']:g} s)")
        return False

    if result.returncode != 0:
        print(f"   Test {name}:    {RED}FAIL{NC} ")
        print(f"   (program {describe_exit(result.returncode)})")
        if opts["show_diff"]:
            print("   (no diff shown: program did not produce ")
            print("   normal output)")
        return False

    expected = outfile.read_bytes()
    if normalized_lines(expected) == normalized_lines(result.stdout):
        print(f"   Test {name}:    {GREEN}PASS{NC}")
        return True

    print(f"   Test {name}:    {RED}FAIL{NC}")
    if opts["show_diff"]:
        print("\n     Output details:")
        show_diff_summary(expected, result.stdout)
    return False


def run_valgrind(infile, opts):
    """Run one valgrind check; returns True on PASS."""
    sys.stdout.flush()
    with open(infile, "rb") as fin:
        result = subprocess.run(
            ["valgrind", "--leak-check=full", "--show-leak-kinds=all",
             "--track-origins=yes", "./a.out"],
            stdin=fin, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    out = result.stderr.decode(errors="replace")
    if valgrind_passed(out):
        print(f"     Valgrind:    {BLUE}PASS{NC}")
        return True
    print(f"     Valgrind:    {RED}FAIL{NC}")
    if opts["show_vg"]:
        print("\n     Valgrind details:")
        show_valgrind_details(out)
    return False


def main():
    opts = parse_args(sys.argv[1:])

    if not os.path.isfile(opts["prog"]):
        die(f"File not found: {opts['prog']}")
    cc = find_compiler()
    if opts["valgrind"] and not shutil.which("valgrind"):
        die("valgrind not found. Install it or run without --valgrind.")

    compile_program(opts["prog"], cc)

    test_dir = locate_tests()
    infiles = sorted(test_dir.glob("*.in"), key=natural_key)
    if not infiles:
        die(f"No test cases found in {test_dir}")

    print(f"{CYAN}\n┌────────────────────────┐{NC}")
    print(f"{CYAN}│     {BBLUE} TEST RESULTS      {CYAN}│{NC}")
    print(f"{CYAN}└────────────────────────┘\n{NC}")

    pass_ok = pass_vg = 0
    for infile in infiles:
        outfile = infile.with_suffix(".out")
        if not outfile.is_file():
            print(f"   Test {display_name(infile.name)}:    {RED}NA{NC} ")
            print(f"     output file {outfile.name} not found\n")
            continue

        if run_test(infile, outfile, opts):
            pass_ok += 1
        if opts["valgrind"] and run_valgrind(infile, opts):
            pass_vg += 1
        print()

    total = len(infiles)
    print("──────────────────────────\n")
    print(f"{MAGENTA}{'   Correctness: ':<16} {pass_ok:2d}/{total}{NC}")
    if opts["valgrind"]:
        print(f"{MAGENTA}{'   Valgrind:    ':<16} {pass_vg:2d}/{total}{NC}")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:            # e.g. ./ctest.py prog.c | head
        sys.stdout = None
    except KeyboardInterrupt:
        print()
        sys.exit(130)
