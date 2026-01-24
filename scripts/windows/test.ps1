# Test script for InvoiceFlowBot (Windows)
# Wrapper around Python test.py script

$ErrorActionPreference = "Stop"

# Get project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Run Python test script
python "$ProjectRoot\scripts\python\test.py" $args
