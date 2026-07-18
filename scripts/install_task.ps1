param([switch]$Test)

$TaskName = "DailyNewsDigest"
$BatchPath = Join-Path $PSScriptRoot "run_digest.bat"
$WorkDir = (Join-Path $PSScriptRoot "..") | Resolve-Path

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task '$TaskName'..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$trigger = New-ScheduledTaskTrigger -Daily -At 09:00
$action = New-ScheduledTaskAction -Execute $BatchPath -WorkingDirectory $WorkDir
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName -Trigger $trigger -Action $action -Principal $principal -Settings $settings -Force

Write-Host "[OK] Task '$TaskName' installed. Runs daily at 09:00." -ForegroundColor Green
Write-Host "     Project: $WorkDir"

if ($Test) {
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "[OK] Test run triggered. Check archives/ for output." -ForegroundColor Yellow
}
