#!/usr/bin/env bash
set -euo pipefail

# Move into the project root so every relative path below lands in the right place.
cd "$(dirname "$0")"

# Create a dedicated virtual environment for the backend dependencies.
python -m venv backend/venv

# Activate the virtual environment in the current shell session.
source backend/venv/bin/activate

# Upgrade pip first so package installation is more reliable.
python -m pip install --upgrade pip

# Install all backend dependencies from requirements.txt.
pip install -r backend/requirements.txt

# Create the directories the project expects at runtime.
mkdir -p backend/storage/chroma_db backend/tmp frontend/src/components frontend/src/api frontend/public

# Print a friendly completion message.
echo "Setup complete. Activate backend/venv before starting the backend."
