# Stop the script immediately if any command fails.
$ErrorActionPreference = "Stop"

# Move into the project root so every relative path below lands in the right place.
Set-Location $PSScriptRoot

# Create a dedicated virtual environment for the backend dependencies.
python -m venv backend\venv

# Activate the virtual environment for the rest of this script.
. .\backend\venv\Scripts\Activate.ps1

# Upgrade pip first so package installation is more reliable.
python -m pip install --upgrade pip

# Install all backend dependencies from requirements.txt.
pip install -r backend\requirements.txt

# Create the directories the project expects at runtime.
New-Item -ItemType Directory -Force -Path backend\storage\chroma_db, frontend\src\components, frontend\src\api, frontend\public | Out-Null

# Print a friendly completion message.
Write-Host "Setup complete. Use .\backend\venv\Scripts\Activate.ps1 before starting the backend."
