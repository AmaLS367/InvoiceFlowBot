# Lint script for InvoiceFlowBot (Windows)
# Wrapper around Python lint.py script

$ErrorActionPreference = "Stop"

# Get project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Run Python lint script
python "$ProjectRoot\scripts\python\lint.py" $args
