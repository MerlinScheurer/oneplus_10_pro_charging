# Logs `adb shell dumpsys battery` every 30 seconds to a file.
# Usage: .\battery_log.ps1 [-IntervalSec 30] [-LogFile battery_log.txt]
# Stop with Ctrl+C.

param(
    [int]$IntervalSec = 30,
    [string]$LogFile = (Join-Path $PSScriptRoot 'battery_log.txt')
)

if (-not (Get-Command adb -ErrorAction SilentlyContinue)) {
    Write-Error 'adb not found in PATH.'
    exit 1
}

$devices = adb devices | Select-String -Pattern '\tdevice$'
if (-not $devices) {
    Write-Error 'No authorized device found. Check adb devices.'
    exit 1
}

Add-Content -Path $LogFile -Value ("=== session start {0} interval {1}s ===" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $IntervalSec)
Write-Host "Logging to $LogFile every $IntervalSec s. Ctrl+C to stop."

while ($true) {
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $dump = adb shell dumpsys battery 2>&1
    $bcc = adb logcat -d -s BatteryChargeControl:I 2>$null | Select-String -Pattern 'output data|voocphy' | Select-Object -Last 4

    Add-Content -Path $LogFile -Value ("--- {0} ---" -f $stamp)
    Add-Content -Path $LogFile -Value 'bcc logcat (latest):'
    Add-Content -Path $LogFile -Value ($bcc | ForEach-Object { $_.Line })
    Add-Content -Path $LogFile -Value $dump
    Add-Content -Path $LogFile -Value ''

    Start-Sleep -Seconds $IntervalSec
}
