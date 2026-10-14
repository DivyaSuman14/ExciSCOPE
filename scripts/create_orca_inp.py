from pathlib import Path

ROOT = Path("geometries").resolve()

NPROCS = 8
MAXCORE_MB = 3000


CHARGE_MULT = {
    "pyridinium": (1, 1),
    "streptocyanine-c1": (1, 1),
    "streptocyanine-c3": (1, 1),
    "streptocyanine-c5": (1, 1),
}
i = 0
for xyz in sorted(ROOT.glob("*/*.xyz")):
    folder = xyz.parent
    molecule = folder.name

    if molecule in CHARGE_MULT:
        print(f"Using charge/multiplicity for {molecule}: {CHARGE_MULT[molecule]}")
        charge, multiplicity = CHARGE_MULT.get(molecule, (0, 1))
    else:
        charge, multiplicity = (0, 1)

    inp = folder / f"{molecule}.inp"

    content = f"""\
! CAM-B3LYP aug-cc-pVTZ TightSCF RIJCOSX UseSym

%pal
    nprocs {NPROCS}
end

%maxcore {MAXCORE_MB}

%tddft
    nroots 10
    triplets false
    tda false
end

* xyzfile {charge} {multiplicity} {xyz.name}
"""

    inp.write_text(content)
    i += 1
    # print(f"Created: {inp}")
print(f"Created {i} ORCA input files in {ROOT}.")
print("Done.")
