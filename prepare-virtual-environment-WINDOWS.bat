@echo off
REM =======================================
REM Batch script to set up Python environment for urbs
REM =======================================

REM Check if the virtual environment exists
if exist "urbs-env\Scripts\activate" (
    echo Virtual environment already exists.
) else (
    REM Create the virtual environment
    echo Creating virtual environment...
    py -3.12 -m venv urbs-env

    REM Check if creation was successful
    if not exist "urbs-env\Scripts\activate" (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
)

REM Activate the virtual environment (Windows)
call urbs-env\Scripts\activate
echo Virtual environment has been activated.

REM Check if packages are already installed
REM Using a dummy file to detect if packages are installed, you can also use pip freeze or similar checks
if exist "urbs-env\installed.flag" (
    echo Required packages already installed.
) else (
    echo Installing required packages from urbs-env.txt...
    python -m pip install -r urbs-env.txt

    REM Check if the installation succeeded
    if %errorlevel% neq 0 (
        echo Error: Failed to install packages.
        exit /b 1
    )

    REM Create a flag to indicate that packages have been installed
    echo Packages installed successfully > urbs-env\installed.flag
    echo Packages installed successfully.
)

REM Notify the user that the process is complete
echo Your urbs environment is ready to use.

REM Prevent the script from closing immediately
pause