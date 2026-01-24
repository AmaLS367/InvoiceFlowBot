# Run script for InvoiceFlowBot (Windows)
# Wrapper around Python run.py script

$ErrorActionPreference = "Stop"

# Get project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Run Python run script
python "$ProjectRoot\scripts\python\run.py" $args
