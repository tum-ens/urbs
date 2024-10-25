#!/bin/bash
# =======================================
# Bash script to set up Python environment for urbs
# =======================================

# Check if the virtual environment exists
if [ -d "urbs-env/bin" ]; then
    echo "Virtual environment already exists."
else
    # Create the virtual environment
    echo "Creating virtual environment..."
    python3 -m venv urbs-env

    # Check if creation was successful
    if [ ! -d "urbs-env/bin" ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Activate the virtual environment (Linux/Mac)
source urbs-env/bin/activate
echo "Virtual environment has been activated."

# Check if packages are already installed
# Using a dummy file to detect if packages are installed
if [ -f "urbs-env/installed.flag" ]; then
    echo "Required packages already installed."
else
    echo "Installing required packages from urbs-env.txt..."
    python -m pip install -r urbs-env.txt

    # Check if the installation succeeded
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install packages."
        exit 1
    fi

    # Create a flag to indicate that packages have been installed
    echo "Packages installed successfully" > urbs-env/installed.flag
    echo "Packages installed successfully."
fi

# Notify the user that the process is complete
echo "Your urbs environment is ready to use."