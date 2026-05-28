#!/bin/bash
set -euo pipefail

cd /home/vvd/prakash/xorz/llm

# Senior requested specific 7 organs
ORGANS=("code-organ" "reason-organ" "data-organ" "debug-organ" "synthesis-organ" "gate-organ" "coordinator-organ")

for ORGAN in "${ORGANS[@]}"; do
    mkdir -p "organs/$ORGAN"
    cd "organs/$ORGAN"
    
    if [ ! -d ".git" ]; then
        git init
    fi
    
    cat <<EOF > SOUL.md
# Organ Identity: $ORGAN
## Role
This organ's identity and constraints.
EOF
    
    echo "[]" > tools.json
    echo "{}" > rewards.json
    
    git add . || true
    git commit -m "Initial gapman alternative setup for $ORGAN" || true
    
    cd ../..
done

echo "Successfully created and initialized all 7 organ directories."
