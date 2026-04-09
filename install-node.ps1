Write-Host "Checking Node.js installation..."
$nodePath = "C:\Program Files\nodejs\node.exe"
if (Test-Path $nodePath) {
    Write-Host "Node.js already installed at $nodePath"
    exit 0
}

$installerPath = Join-Path $PSScriptRoot "node-installer.msi"
if (-not (Test-Path $installerPath)) {
    Write-Host "Installer not found at $installerPath"
    exit 1
}

Write-Host "Starting elevated Node.js installation..."
$process = Start-Process msiexec -ArgumentList "/i `"$installerPath`" /quiet /norestart" -Verb RunAs -PassThru -Wait
if ($process.ExitCode -eq 0) {
    Write-Host "Installation completed successfully."
} else {
    Write-Host "Installation failed with exit code $($process.ExitCode)."
    exit $process.ExitCode
}

# Verify installation
if (Test-Path $nodePath) {
    Write-Host "Node.js verified at $nodePath"
    $nodeVersion = & $nodePath --version
    Write-Host "Node version: $nodeVersion"
} else {
    Write-Host "Node.js not found after installation."
    exit 1
}