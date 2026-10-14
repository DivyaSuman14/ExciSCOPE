#!/bin/bash

ORCA_PLOT="/home/dsuman/orca_6_1_1/orca_plot"
ROOT="geometries"

# For TDDFT with TDA false:
STATES="1 3 5 7 9 11 13 15 17 19"

for dir in "$ROOT"/*/; do

    molecule=$(basename "$dir")

    # Expect <molecule>/<molecule>.gbw
    gbw="${molecule}.gbw"

    if compgen -G "${dir}/*.cube" > /dev/null; then
        echo "$molecule : cube files already exist, skipping"
        continue
    fi


    if [ ! -f "${dir}/${gbw}" ]; then
        echo "$molecule : no GBW file, skipping"
        continue
    fi

    echo "=================================================="
    echo "Processing $molecule"
    echo "=================================================="

    cd "$dir" || exit 1

    printf "6\ny\n%s\n12\n" "$STATES" | \
        "$ORCA_PLOT" "$gbw" -i \
        > orca_plot_diffdens.log 2>&1

    echo "$molecule : done"

    cd - > /dev/null

done
