# Migration script for InvoiceFlowBot (Windows)
# Wrapper around Python migrate.py script

$ErrorActionPreference = "Stop"

# Get project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Run Python migrate script
python "$ProjectRoot\scripts\python\migrate.py" $args
