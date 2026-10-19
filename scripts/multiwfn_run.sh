MULTIWFN="/home/dsuman/Downloads/Multiwfn_2026.9.1_bin_Linux/Multiwfn"

PARENT_DIR="geometries"
export OMP_NUM_THREADS=1
PARENT_DIR=$(realpath "$PARENT_DIR")

shopt -s nullglob

for CUBE_DIR in "$PARENT_DIR"/*/; do

    [[ -d "$CUBE_DIR" ]] || continue

    cube_files=("$CUBE_DIR"/*cisdp*.cube)

    # Skip folders without cube files
    if (( ${#cube_files[@]} == 0 )); then
        continue
    fi
 
    echo "========================================"
    echo "Processing folder: $CUBE_DIR"
    echo "Found ${#cube_files[@]} cube files"
    echo "========================================"

    # Create results folder
    OUTDIR="${CUBE_DIR%/}/multiwfn_results"
    mkdir -p "$OUTDIR"

    # Loop through cube files
    for cube in "${cube_files[@]}"; do

        cube_name=$(basename "$cube")

        if [[ "$cube_name" =~ \.cisdp([0-9]+)\.cube$ ]]; then

            xx=$((10#${BASH_REMATCH[1]}))

            if (( xx < 1 || xx % 2 == 0 )); then
                echo "Invalid cisdp number: $cube_name"
                continue
            fi

            state=$(( (xx + 1) / 2 ))

        else
            echo "Cannot extract state number: $cube_name"
            continue
        fi

        logfile="$OUTDIR/state_${state}.txt"

        # Create temporary working directory
        workdir=$(mktemp -d "$OUTDIR/.state_${state}.XXXXXX")

        # Prepare Multiwfn commands
        cat > "$workdir/commands.txt" <<'EOF'
18
3
0
0
q
EOF

        echo
        echo "----------------------------------------"
        echo "Processing: $cube_name"
        echo "cisdp number: $xx"
        echo "State: $state"
        echo "----------------------------------------"

        # Run Multiwfn directly
        if (
            cd "$workdir"

            "$MULTIWFN" "$cube" -nt "$OMP_NUM_THREADS" \
                < commands.txt > multiwfn_full.log 2>&1

        ); then
            echo "Multiwfn finished."
        else
            echo "Multiwfn failed for $cube_name"
            echo "See: $workdir/multiwfn_full.log"
            continue
        fi

        # Extract relevant output
        if awk '
            /q_CT \(positive and negative parts\):/ {
                printing = 1
            }

            printing {
                print
            }

            printing && /Overlap integral between C[+] and C-/ {
                complete = 1
                exit
            }

            END {
                if (!complete) exit 1
            }
        ' "$workdir/multiwfn_full.log" > "$workdir/results.txt"
        then

            mv "$workdir/results.txt" "$logfile"

            echo "Saved: $logfile"

            # Clean temporary files
            rm -rf "$workdir"

        else
            echo "Results block missing for $cube_name"
            echo "Inspect: $workdir/multiwfn_full.log"
        fi

    done

    echo
    echo "Finished folder: $CUBE_DIR"
    echo

done

echo "========================================"
echo "All folders processed."
echo "========================================"
