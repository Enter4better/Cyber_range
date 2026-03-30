# cleanup_vbox.ps1
Write-Host "=== VirtualBox Cleanup Script ===" -ForegroundColor Cyan

# Set correct VBoxManage path
$vboxmanage = "D:\VirtualBox\VBoxManage.exe"

# Check if file exists
if (-not (Test-Path $vboxmanage)) {
    Write-Host "ERROR: Cannot find VBoxManage.exe at $vboxmanage" -ForegroundColor Red
    Write-Host "Please check the path, current directory contents:" -ForegroundColor Yellow
    dir D:\VirtualBox\
    exit 1
}

Write-Host "Found VBoxManage: $vboxmanage" -ForegroundColor Green

# 1. Stop all running VMs
Write-Host "`n1. Stopping running VMs..." -ForegroundColor Yellow
$running = & $vboxmanage list runningvms
if ($running) {
    $running | ForEach-Object {
        $vmName = ($_ -split '"')[1]
        if ($vmName) {
            Write-Host "   Stopping: $vmName"
            & $vboxmanage controlvm $vmName poweroff
            Start-Sleep -Seconds 2
        }
    }
} else {
    Write-Host "   No running VMs" -ForegroundColor Green
}

# 2. Remove all host-only networks
Write-Host "`n2. Removing host-only networks..." -ForegroundColor Yellow
$hostonly = & $vboxmanage list hostonlyifs
if ($hostonly -match "Name:") {
    $hostonly | Select-String "Name:" | ForEach-Object {
        $name = $_ -replace "Name:\s+", ""
        Write-Host "   Removing: $name"
        & $vboxmanage hostonlyif remove $name
        Start-Sleep -Seconds 1
    }
} else {
    Write-Host "   No host-only networks" -ForegroundColor Green
}

# 3. Clean Vagrant residues
Write-Host "`n3. Cleaning Vagrant directories..." -ForegroundColor Yellow
$vagrantDir = "D:\AI_range\vms"
if (Test-Path $vagrantDir) {
    # Try to destroy each VM properly
    Get-ChildItem $vagrantDir -Directory | ForEach-Object {
        $vmPath = $_.FullName
        Write-Host "   Cleaning: $($_.Name)"
        try {
            Push-Location $vmPath
            vagrant destroy -f
            Pop-Location
        } catch {
            Write-Host "   Destroy failed, deleting directory directly" -ForegroundColor Yellow
        }
    }
    
    # Delete all vms directory contents
    Remove-Item -Path "$vagrantDir\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   Cleaned: $vagrantDir" -ForegroundColor Green
}

# 4. Remove residual VMs from VirtualBox
Write-Host "`n4. Cleaning residual VMs from VirtualBox..." -ForegroundColor Yellow
$vms = & $vboxmanage list vms
if ($vms) {
    $vms | ForEach-Object {
        $vmName = ($_ -split '"')[1]
        if ($vmName -like "*AI_range*" -or $vmName -like "*web-server*" -or $vmName -like "*database*" -or $vmName -like "*defense*") {
            Write-Host "   Deleting VM: $vmName"
            & $vboxmanage unregistervm $vmName --delete
        }
    }
} else {
    Write-Host "   No residual VMs" -ForegroundColor Green
}

# 5. Clean Vagrant global state
Write-Host "`n5. Cleaning Vagrant global state..." -ForegroundColor Yellow
vagrant global-status --prune

# 6. Verify cleanup results
Write-Host "`n6. Verifying cleanup results..." -ForegroundColor Yellow
$remaining = & $vboxmanage list vms
if ($remaining) {
    Write-Host "   Remaining VMs:" -ForegroundColor Yellow
    $remaining
} else {
    Write-Host "   No remaining VMs" -ForegroundColor Green
}

$remainingNetworks = & $vboxmanage list hostonlyifs
if ($remainingNetworks) {
    Write-Host "   Remaining host-only networks:" -ForegroundColor Yellow
    $remainingNetworks
} else {
    Write-Host "   No remaining host-only networks" -ForegroundColor Green
}

Write-Host "`n=== Cleanup Complete ===" -ForegroundColor Green
Write-Host "You can now run: streamlit run app.py" -ForegroundColor Cyan