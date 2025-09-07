param(
    [Parameter(Mandatory=$true)]
    [string]$DestinationPath,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [switch]$NonInteractive
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopFile = Join-Path $ScriptDir "r_vertical_text.desktop"
$PluginFolder = Join-Path $ScriptDir "r_vertical_text"
$DestDesktopFile = Join-Path $DestinationPath "r_vertical_text.desktop"
$DestPluginFolder = Join-Path $DestinationPath "r_vertical_text"

Write-Host "Krita Vertical Text Plugin Copy Started..." -ForegroundColor Green
Write-Host "Destination: $DestinationPath" -ForegroundColor Yellow

if (-not (Test-Path $DestinationPath)) {
    Write-Host "Destination directory does not exist: $DestinationPath" -ForegroundColor Red
    if ($NonInteractive) {
        Write-Host "Non-interactive mode: Creating directory automatically" -ForegroundColor Yellow
        try {
            New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
            Write-Host "Directory created: $DestinationPath" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to create directory: $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "Create directory? (y/N): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        if ($response -eq "y" -or $response -eq "Y") {
            try {
                New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
                Write-Host "Directory created: $DestinationPath" -ForegroundColor Green
            }
            catch {
                Write-Host "Failed to create directory: $($_.Exception.Message)" -ForegroundColor Red
                exit 1
            }
        }
        else {
            Write-Host "Copy cancelled." -ForegroundColor Red
            exit 1
        }
    }
}

if (Test-Path $DesktopFile) {
    try {
        if ($Force -or -not (Test-Path $DestDesktopFile)) {
            Copy-Item -Path $DesktopFile -Destination $DestDesktopFile -Force
            Write-Host "✓ .desktop file copied: $DestDesktopFile" -ForegroundColor Green
        }
        else {
            Write-Host "! .desktop file already exists: $DestDesktopFile" -ForegroundColor Yellow
            if ($NonInteractive) {
                Write-Host "Non-interactive mode: Overwriting automatically" -ForegroundColor Yellow
                Copy-Item -Path $DesktopFile -Destination $DestDesktopFile -Force
                Write-Host "✓ .desktop file overwritten: $DestDesktopFile" -ForegroundColor Green
            }
            else {
                Write-Host "Overwrite? (y/N): " -NoNewline -ForegroundColor Yellow
                $response = Read-Host
                if ($response -eq "y" -or $response -eq "Y") {
                    Copy-Item -Path $DesktopFile -Destination $DestDesktopFile -Force
                    Write-Host "✓ .desktop file overwritten: $DestDesktopFile" -ForegroundColor Green
                }
                else {
                    Write-Host "- .desktop file copy skipped" -ForegroundColor Yellow
                }
            }
        }
    }
    catch {
        Write-Host "✗ Failed to copy .desktop file: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "✗ .desktop file not found: $DesktopFile" -ForegroundColor Red
}

if (Test-Path $PluginFolder) {
    try {
        if ($Force -or -not (Test-Path $DestPluginFolder)) {
            Copy-Item -Path $PluginFolder -Destination $DestPluginFolder -Recurse -Force
            Write-Host "✓ r_vertical_text folder copied: $DestPluginFolder" -ForegroundColor Green
        }
        else {
            Write-Host "! r_vertical_text folder already exists: $DestPluginFolder" -ForegroundColor Yellow
            if ($NonInteractive) {
                Write-Host "Non-interactive mode: Overwriting automatically" -ForegroundColor Yellow
                Copy-Item -Path $PluginFolder -Destination $DestPluginFolder -Recurse -Force
                Write-Host "✓ r_vertical_text folder overwritten: $DestPluginFolder" -ForegroundColor Green
            }
            else {
                Write-Host "Overwrite? (y/N): " -NoNewline -ForegroundColor Yellow
                $response = Read-Host
                if ($response -eq "y" -or $response -eq "Y") {
                    Copy-Item -Path $PluginFolder -Destination $DestPluginFolder -Recurse -Force
                    Write-Host "✓ r_vertical_text folder overwritten: $DestPluginFolder" -ForegroundColor Green
                }
                else {
                    Write-Host "- r_vertical_text folder copy skipped" -ForegroundColor Yellow
                }
            }
        }
    }
    catch {
        Write-Host "✗ Failed to copy r_vertical_text folder: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "✗ r_vertical_text folder not found: $PluginFolder" -ForegroundColor Red
}

Write-Host ""
Write-Host "Copy process completed." -ForegroundColor Green
