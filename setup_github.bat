@echo off
echo ========================================
echo GitHub Setup for Florida Corp Processor
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if Git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

echo Python and Git are available!
echo.

REM Run the Python setup script
echo Running GitHub setup script...
python setup_github.py

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo Next steps:
echo 1. Create a repository on GitHub.com
echo 2. Follow the instructions shown above
echo 3. See GITHUB_SETUP_GUIDE.md for detailed steps
echo.
pause
