#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path

runs = Path(sys.argv[1] if len(sys.argv) > 1 else "geometries")
output = Path(sys.argv[2] if len(sys.argv) > 2 else "ct_results.csv")

# Supports negative numbers and scientific notation, including Fortran D.
number = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?)"

patterns = {
    "D_index_Angstrom": rf"\bD index:\s*{number}",
    "Dipole_norm_Debye": (
        rf"Dipole moment variation\s*\(Debye\)"
        rf"[^\r\n]*?\bNorm:\s*{number}"
    ),
    "Sigma_Angstrom": rf"\bdelta_sigma index:\s*{number}",
    "t_index_Angstrom": rf"\bt index:\s*{number}",
    "S_plus_minus_index": rf"S\+- index\)\s*:\s*{number}",
}

files = [
    path
    for path in runs.glob("*/multiwfn_results/state_*.txt")
    if re.fullmatch(r"state_\d+\.txt", path.name)
]

files.sort(key=lambda p: (
    p.parent.parent.name,
    int(p.stem.split("_")[1]),
))

if not files:
    sys.exit(f"No state_*.txt files found under {runs.resolve()}")

rows = []
incomplete = 0

for path in files:
    text = path.read_text(encoding="utf-8")
    row = {
        "molecule": path.parent.parent.name,
        "state": int(path.stem.split("_")[1]),
    }

    missing = []
    for column, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            row[column] = float(
                match.group(1).replace("D", "E").replace("d", "e")
            )
        else:
            row[column] = ""
            missing.append(column)

    if missing:
        incomplete += 1
        print(
            f"WARNING: {path}: missing {', '.join(missing)}",
            file=sys.stderr,
        )

    rows.append(row)

with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=["molecule", "state", *patterns],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} rows to {output.resolve()}")
print(f"Rows with missing values: {incomplete}")
