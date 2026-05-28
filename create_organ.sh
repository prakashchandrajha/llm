#!/bin/bash
set -euo pipefail

ORGAN_NAME=$1
ORGANS_DIR="/home/vvd/prakash/xorz/llm/organs"
ORGAN_PATH="$ORGANS_DIR/$ORGAN_NAME"

echo "Creating organ: $ORGAN_NAME at $ORGAN_PATH"

mkdir -p "$ORGAN_PATH"
cd "$ORGAN_PATH"

# Initialize git repo
if [ ! -d ".git" ]; then
    git init
fi

# Create base SOUL.md if it doesn't exist
if [ ! -f "SOUL.md" ]; then
    cat <<EOF > SOUL.md
# Organ Identity: $ORGAN_NAME

## Role
(Define the specific role, constraints, and instructions for this organ here)

## Capabilities
- Can use tools? (Yes/No)
- Has access to AST graph? (Yes/No)

## Token Economy
- Strictness: High
- Max Tokens: 2000
EOF
fi

# Install mattpocock/skills
if [ ! -d ".skills" ]; then
    echo "Installing mattpocock/skills for $ORGAN_NAME..."
    npx -y skills@latest add mattpocock/skills
fi

echo "Successfully scaffolded organ: $ORGAN_NAME"
echo "----------------------------------------"
