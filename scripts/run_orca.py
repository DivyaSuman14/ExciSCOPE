from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

ROOT = Path("geometries").resolve()

MAX_CONCURRENT_JOBS = 1

ORCA = "/home/dsuman/orca_6_1_1/orca"


def completed_successfully(outfile):
    if not outfile.exists():
        return False

    try:
        text = outfile.read_text(errors="ignore")
        return "ORCA TERMINATED NORMALLY" in text
    except Exception:
        return False


def run_job(inp):
    workdir = inp.parent
    outfile = workdir / f"{inp.stem}.out"

    if completed_successfully(outfile):
        return inp.stem, "SKIPPED (already complete)"

    print(f"Starting {inp.stem}")

    with outfile.open("w") as out:
        result = subprocess.run(
            [ORCA, inp.name],
            cwd=workdir,
            stdout=out,
            stderr=subprocess.STDOUT,
        )

    if result.returncode == 0 and completed_successfully(outfile):
        return inp.stem, "DONE"

    return inp.stem, f"FAILED (return code {result.returncode})"


inputs = sorted(ROOT.glob("*/*.inp"))

print(f"Found {len(inputs)} ORCA calculations")
print(f"Running at most {MAX_CONCURRENT_JOBS} simultaneously\n")

with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS) as executor:
    futures = {executor.submit(run_job, inp): inp for inp in inputs}

    for future in as_completed(futures):
        molecule, status = future.result()
        print(f"{molecule:30s} {status}")

print("\nAll submitted calculations processed.")
