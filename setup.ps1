# PowerShell setup script for Zoom Automation
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Zoom Automation - Setup Environment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

function Get-PythonPath {
    try {
        $res = & python --version 2>&1
        if ($res -match "Python 3\.") { return "python" }
    } catch {}

    try {
        $res = & py -3 --version 2>&1
        if ($res -match "Python 3\.") { return "py -3" }
    } catch {}

    $possiblePaths = @(
        "$env:LocalAppData\Programs\Python\Python3*\python.exe",
        "$env:ProgramFiles\Python3*\python.exe",
        "C:\Python3*\python.exe"
    )
    foreach ($pathPattern in $possiblePaths) {
        $found = Get-Item $pathPattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found -and (Test-Path $found.FullName)) {
            return $found.FullName
        }
    }

    return $null
}

# 1. Check Python
$pythonCmd = Get-PythonPath

if (-not $pythonCmd) {
    Write-Host "[!] Python 3 not found in PATH." -ForegroundColor Yellow
    Write-Host "[+] Attempting to install Python via winget..." -ForegroundColor Green

    $installed = $false
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        try {
            winget install --id Python.Python.3.11 --exact --accept-package-agreements --accept-source-agreements --scope user
            $installed = $true
        } catch {
            Write-Host "[-] Failed to install Python via winget." -ForegroundColor Yellow
        }
    }

    if (-not $installed) {
        Write-Host "[+] Downloading official Python 3.11 installer..." -ForegroundColor Green
        $installerUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        $installerPath = "$env:TEMP\python-3.11.9-amd64.exe"
        
        try {
            Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
            Write-Host "[+] Running Python installer..." -ForegroundColor Green
            Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1" -Wait
            Remove-Item $installerPath -ErrorAction SilentlyContinue
            $installed = $true
        } catch {
            Write-Host "[-] Download or installation failed: $_" -ForegroundColor Red
        }
    }

    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    $pythonCmd = Get-PythonPath

    if (-not $pythonCmd) {
        Write-Host "[-] ERROR: Python not found after installation attempt." -ForegroundColor Red
        Write-Host "Please install Python 3 manually from https://www.python.org/downloads/" -ForegroundColor Red
        Write-Host "Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[v] Found Python: $pythonCmd" -ForegroundColor Green

# 2. Virtual Environment (venv) setup
$venvDir = Join-Path $PSScriptRoot "venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "[+] Creating virtual environment (venv)..." -ForegroundColor Green
    if ($pythonCmd -eq "py -3") {
        & py -3 -m venv "$venvDir"
    } else {
        & "$pythonCmd" -m venv "$venvDir"
    }
} else {
    Write-Host "[v] Virtual environment 'venv' already exists." -ForegroundColor Green
}

if (-not (Test-Path $venvPython)) {
    Write-Host "[-] ERROR: Could not find venv\Scripts\python.exe" -ForegroundColor Red
    exit 1
}

# 3. Install dependencies
$reqFile = Join-Path $PSScriptRoot "requirements.txt"
if (-not (Test-Path $reqFile)) {
    Write-Host "[+] Creating requirements.txt..." -ForegroundColor Green
    $dependencies = @("pyautogui", "schedule", "PyAudioWPatch", "pygetwindow")
    $dependencies | Out-File -FilePath $reqFile -Encoding ASCII
}

Write-Host "[+] Upgrading pip..." -ForegroundColor Green
& "$venvPython" -m pip install --upgrade pip

Write-Host "[+] Installing dependencies from requirements.txt..." -ForegroundColor Green
& "$venvPython" -m pip install -r "$reqFile"

# 4. Check config.py
$configFile = Join-Path $PSScriptRoot "config.py"
$configExample = Join-Path $PSScriptRoot "config.py.example"
if (-not (Test-Path $configFile)) {
    if (Test-Path $configExample) {
        Write-Host "[+] Creating config.py from template config.py.example..." -ForegroundColor Green
        Copy-Item $configExample $configFile
    } else {
        Write-Host "[+] Creating default config.py..." -ForegroundColor Green
        $configContent = @(
            "# Zoom Credentials",
            "conf_id = '85244706153'",
            "conf_pass = 'd3piUExIRlBaTkttZlRZM2xidGtlZz09'",
            "",
            "# Audio Folder Path",
            "kirtan_folder = 'C:/kirtans/'",
            "",
            "# Speaker that Zoom plays into (chosen by select_audio.py). Empty = system default.",
            "audio_output_device = ''"
        )
        $configContent | Out-File -FilePath $configFile -Encoding ASCII
    }
}

# 5. Speaker selection (which speaker Zoom plays into - the bot listens to it)
Write-Host ""
Write-Host "[+] Choosing the speaker to listen to..." -ForegroundColor Green
$selectAudioScript = Join-Path $PSScriptRoot "select_audio.py"
if (Test-Path $selectAudioScript) {
    $env:PYTHONIOENCODING = "utf-8"
    & "$venvPython" "$selectAudioScript"
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "   Setup completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "To run the application, execute start_zoom.bat" -ForegroundColor Yellow
Write-Host "To pick another speaker later, run setup.bat again (or: venv\Scripts\python.exe select_audio.py)" -ForegroundColor Yellow

