#!/bin/bash

# ==============================================================================
# ForgeX4 COSMOS-Ω: Final Project Cleanup Script (v3 - Foolproof)
# This script uses a robust "scorched earth" method to ensure a perfectly
# clean repository, regardless of its current state.
# ==============================================================================

set -e

echo "🚀 Starting final, foolproof project cleanup..."

# --- 1. Un-track ALL files from Git ---
# This gives us a clean slate. Your local files are safe.
echo "🧹 Clearing the Git index..."
git rm -r --cached . > /dev/null 2>&1 || true

# --- 2. Add back ONLY the essential files and folders ---
echo "✅ Re-staging the final, essential project files..."
git add LICENSE README.md requirements.txt .gitignore
git add cosmos/
git add data/genomes/
git add data/telemetry_v3/snapshot_dataset_v_final.parquet
git add artifacts/phase2/digital_twin_v7.1_The_Fusion_Model.joblib
git add artifacts/logs/ledger_20251001_122006.json
git add scripts/run_cosmic_debugger.py
git add cleanup_project.sh # Add this script itself to the repo

# --- 3. Overwrite the .gitignore with the final, correct version ---
echo "✍️  Writing the final .gitignore..."
cat <<EOF > .gitignore
# Python
__pycache__/
*.pyc

# IDE files
.vscode/

# Data, Temp Files, and Artifacts - Ignore all by default
data/telemetry_v*/*
data/temp/
artifacts/phase2/*
artifacts/logs/*

# Keep specific final artifacts for the published project (the ! rule)
!data/telemetry_v3/snapshot_dataset_v_final.parquet
!artifacts/phase2/digital_twin_v7.1_The_Fusion_Model.joblib
!artifacts/logs/ledger_20251001_122006.json

# Ignore our cleanup script from future commits
cleanup_project.sh
EOF

# --- 4. Commit and Push the Final Clean State ---
echo "📦 Staging all cleanup changes..."
git add .gitignore

echo "✉️  Creating the final cleanup commit..."
git commit -m "chore: final cleanup of all development and experimental artifacts"

echo "🌍 Pushing the final, clean state to GitHub..."
git push origin main

echo "✅ SUCCESS! Project cleanup is complete. Your repository is now in its perfect, final state."