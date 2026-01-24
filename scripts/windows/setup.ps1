# Setup script for InvoiceFlowBot (Windows)
# Wrapper around Python setup.py script

$ErrorActionPreference = "Stop"

# Get project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Run Python setup script
python "$ProjectRoot\scripts\python\setup.py" $args
