# Setup Environment for Django + Linting Tools
# Execute this script with: powershell -ExecutionPolicy Bypass -File setup_env.ps1

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Django Project Setup - Environment Configuration" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# Step 1: Find Python
Write-Host "`nStep 1: Searching for Python installation..." -ForegroundColor Yellow

$pythonPaths = @(
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe",
    "C:\Program Files\Python39\python.exe",
    "C:\Program Files (x86)\Python311\python.exe",
    "C:\Program Files (x86)\Python310\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
)

$pythonExe = $null
foreach ($path in $pythonPaths) {
    if (Test-Path $path) {
        $pythonExe = $path
        Write-Host "✓ Found Python at: $pythonExe" -ForegroundColor Green
        break
    }
}

if (-not $pythonExe) {
    Write-Host "✗ Python not found in common locations" -ForegroundColor Red
    Write-Host "`nPlease install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Step 2: Create Virtual Environment
Write-Host "`nStep 2: Creating virtual environment..." -ForegroundColor Yellow

$venvPath = ".\venv"
if (Test-Path $venvPath) {
    Write-Host "Virtual environment already exists" -ForegroundColor Cyan
} else {
    & $pythonExe -m venv $venvPath
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Activate Virtual Environment
Write-Host "`nStep 3: Activating virtual environment..." -ForegroundColor Yellow
$activateScript = ".\venv\Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Could not find activate script" -ForegroundColor Red
    exit 1
}

# Step 4: Upgrade pip
Write-Host "`nStep 4: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ pip upgraded" -ForegroundColor Green
} else {
    Write-Host "⚠ pip upgrade had issues, continuing..." -ForegroundColor Yellow
}

# Step 5: Install Requirements
Write-Host "`nStep 5: Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Requirements installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install requirements" -ForegroundColor Red
    exit 1
}

# Step 6: Install pre-commit hooks
Write-Host "`nStep 6: Installing pre-commit hooks..." -ForegroundColor Yellow
pre-commit install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pre-commit hooks installed" -ForegroundColor Green
} else {
    Write-Host "⚠ Pre-commit installation had issues" -ForegroundColor Yellow
}

# Step 7: Format existing code
Write-Host "`nStep 7: Formatting existing code..." -ForegroundColor Yellow
black api core --quiet
isort api core --quiet
Write-Host "✓ Code formatted with black and isort" -ForegroundColor Green

# Step 8: Run validation
Write-Host "`nStep 8: Running code quality checks..." -ForegroundColor Yellow
python scripts/validate.py

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Use 'make format' to format code" -ForegroundColor White
Write-Host "  2. Use 'make validate' to check code quality" -ForegroundColor White
Write-Host "  3. Use 'make help' to see all available commands" -ForegroundColor White
Write-Host "`nVirtual environment is now active. Happy coding!" -ForegroundColor Green
