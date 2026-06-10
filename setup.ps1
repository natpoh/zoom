$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host "   Zoom Automation Environment Setup"
Write-Host "=========================================="

# 1. Check for Python
$pythonCmd = "python"
$pythonFound = $false

try {
    $ver = & $pythonCmd --version 2>&1
    if ($ver -match "Python") {
        Write-Host "Found Python: $ver"
        $pythonFound = $true
    }
} catch {
    # Python not found
}

if (-not $pythonFound) {
    Write-Host "Python not found in PATH."
    Write-Host "Attempting to install Python 3.11 via winget..."
    try {
        winget install --id Python.Python.3.11 --exact --accept-package-agreements --accept-source-agreements --force
        Write-Host "Python 3.11 installed successfully."
        
        # Refresh environment variables in current session to pick up new PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Check again
        try {
            $ver = & $pythonCmd --version 2>&1
            Write-Host "Verified Python is now in PATH: $ver"
            $pythonFound = $true
        } catch {
            Write-Host "WARNING: Python was installed but is still not in PATH."
            Write-Host "Please restart your terminal (or computer) and run this script again."
            exit
        }
    } catch {
        Write-Host "Failed to install Python. Please install it manually from https://www.python.org/downloads/"
        Write-Host "IMPORTANT: Make sure to check 'Add Python to PATH' during installation!"
        exit
    }
}

# 2. Check/Create Virtual Environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating a new virtual environment (venv)..."
    & $pythonCmd -m venv venv
} else {
    Write-Host "Virtual environment 'venv' already exists. Re-using it."
}

$pythonVenv = ".\venv\Scripts\python.exe"

if (-not (Test-Path $pythonVenv)) {
    Write-Host "Error: Could not find Python executable in venv."
    exit
}

# 3. Create requirements.txt
$reqFile = "requirements.txt"
$dependencies = @(
    "pyautogui",
    "schedule",
    "pyaudio"
)
$dependencies | Out-File -FilePath $reqFile -Encoding UTF8
Write-Host "Created $reqFile with required dependencies."

# 4. Install dependencies
Write-Host "Upgrading pip..."
& $pythonVenv -m pip install --upgrade pip

Write-Host "Installing dependencies..."
& $pythonVenv -m pip install -r $reqFile

Write-Host "=========================================="
Write-Host "Setup Complete!"
Write-Host "To run the script, use the following commands:"
Write-Host ".\venv\Scripts\Activate.ps1"
Write-Host "python zoom.py"
Write-Host "=========================================="
