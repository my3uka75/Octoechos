import os
import re

# Character sets: name format is A.nhnh
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"   # A-Z
DIGITS = "123456789"                     # n: 1-9 (no zero)
HEX = "abcdef"                           # h: a-f

PER_LETTER = len(DIGITS) * len(HEX) * len(DIGITS) * len(HEX)   # 2916
TOTAL = len(LETTERS) * PER_LETTER                              # 75816

# Text written into every file
FILE_CONTENT = "Date:\t\n\n---\n"

# Directory for output files (same as script)
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()

START_PATTERN = re.compile(r"^([A-Za-z])\.([1-9])([a-fA-F])([1-9])([a-fA-F])$")


def name_to_index(name: str) -> int:
    """Convert a name like 'B.1a2c' to its position in the sequence."""
    match = START_PATTERN.match(name.strip())
    if not match:
        raise ValueError("Start must look like A.nhnh (e.g. B.1a2c): "
                         "n = 1-9, h = a-f.")
    l, n1, h1, n2, h2 = match.groups()
    i = LETTERS.index(l.upper())
    i = i * len(DIGITS) + DIGITS.index(n1)
    i = i * len(HEX) + HEX.index(h1.lower())
    i = i * len(DIGITS) + DIGITS.index(n2)
    i = i * len(HEX) + HEX.index(h2.lower())
    return i


def index_to_name(i: int) -> str:
    """Convert a position in the sequence back to a name like 'B.1a2c'."""
    i, h2 = divmod(i, len(HEX))
    i, n2 = divmod(i, len(DIGITS))
    i, h1 = divmod(i, len(HEX))
    l, n1 = divmod(i, len(DIGITS))
    return f"{LETTERS[l]}.{DIGITS[n1]}{HEX[h1]}{DIGITS[n2]}{HEX[h2]}"


def main():
    start_name = input("Start position (e.g. B.1a2c): ")
    try:
        start_idx = name_to_index(start_name)
    except ValueError as e:
        print(f"Error: {e}")
        return

    try:
        number_files = int(input("Number of files to create: "))
    except ValueError:
        print("Error: number of files must be an integer.")
        return
    if number_files < 1:
        print("Error: number of files must be at least 1.")
        return

    end_idx = start_idx + number_files - 1
    if end_idx >= TOTAL:
        print(
            f"Error: that would run past the last name ({index_to_name(TOTAL - 1)}). "
            f"Maximum from this start is {TOTAL - start_idx} files."
        )
        return

    created = skipped = 0
    for i in range(start_idx, end_idx + 1):
        filepath = os.path.join(script_dir, f"{index_to_name(i)}.md")
        if os.path.exists(filepath):   # never overwrite existing notes
            skipped += 1
            continue
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(FILE_CONTENT)
        created += 1

    print(
        f"Done: {created} created, {skipped} skipped (already existed). "
        f"Range: {index_to_name(start_idx)} to {index_to_name(end_idx)}."
    )


if __name__ == "__main__":
    main()