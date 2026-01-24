# Format script for InvoiceFlowBot (Windows)
# Wrapper around Python format.py script

$ErrorActionPreference = "Stop"

# Get project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Run Python format script
python "$ProjectRoot\scripts\python\format.py" $args
