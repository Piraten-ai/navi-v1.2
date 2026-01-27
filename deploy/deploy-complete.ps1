# Deploy NAVI to Jetson - Single Command
# Runs complete installation with one command
# Usage: .\deploy-complete.ps1 -JetsonIP 192.168.39.196

param(
    [string]$JetsonIP = "192.168.39.196",
    [string]$JetsonUser = "navi",
    [string]$JetsonPassword = "1122"
)

Write-Host "=== NAVI Standalone Deployment ===" -ForegroundColor Green
Write-Host "Target: $JetsonUser@$JetsonIP"
Write-Host ""

# Convert password to secure string
$SecurePassword = ConvertTo-SecureString $JetsonPassword -AsPlainText -Force
$Credential = New-Object System.Management.Automation.PSCredential($JetsonUser, $SecurePassword)

# SSH and run installation
Write-Host "Connecting to Jetson and running complete installation..." -ForegroundColor Yellow
$InstallCommand = @"
bash -c 'curl -sSL https://raw.githubusercontent.com/Piraten-ai/navi-main/main/deploy/install_complete.sh | sudo bash'
"@

try {
    # Use plink (part of PuTTY) or ssh if available
    if (Get-Command ssh -ErrorAction SilentlyContinue) {
        # Using OpenSSH
        $SecurePassword = $Credential.GetNetworkCredential().Password
        $Command = "echo '$SecurePassword' | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $JetsonUser@$JetsonIP $InstallCommand"
        Invoke-Expression $Command
    }
    else {
        Write-Host "SSH not found. Please install OpenSSH or PuTTY." -ForegroundColor Red
        Write-Host ""
        Write-Host "Manual deployment:" -ForegroundColor Yellow
        Write-Host "1. SSH to Jetson: ssh $JetsonUser@$JetsonIP"
        Write-Host "2. Run: curl -sSL https://raw.githubusercontent.com/Piraten-ai/navi-main/main/deploy/install_complete.sh | sudo bash"
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual deployment:" -ForegroundColor Yellow
    Write-Host "1. SSH to Jetson: ssh $JetsonUser@$JetsonIP"
    Write-Host "2. Run: curl -sSL https://raw.githubusercontent.com/Piraten-ai/navi-main/main/deploy/install_complete.sh | sudo bash"
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Wait for installation to complete (10-15 minutes)"
Write-Host "2. Open http://$JetsonIP:3000 in your browser"
Write-Host "3. System is ready when you see the dashboard"
Write-Host ""
