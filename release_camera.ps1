# Quick script to release camera from other applications

Write-Host "`n🎥 Releasing Camera Resources...`n" -ForegroundColor Cyan

# Kill Windows Camera app
Write-Host "1. Closing Windows Camera app..." -ForegroundColor Yellow
$camera = Get-Process -Name 'WindowsCamera' -ErrorAction SilentlyContinue
if ($camera) {
    $camera | Stop-Process -Force
    Write-Host "   ✅ Windows Camera closed" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Windows Camera not running" -ForegroundColor Gray
}

# Kill common video apps
$videoApps = @('Zoom', 'Teams', 'Skype', 'Discord')
Write-Host "`n2. Checking for video call apps..." -ForegroundColor Yellow
foreach ($app in $videoApps) {
    $process = Get-Process -Name $app -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "   ⚠️  Found $app running - Close it manually for best results" -ForegroundColor Yellow
    }
}

# Restart camera service (requires admin)
Write-Host "`n3. Restarting camera service..." -ForegroundColor Yellow
try {
    Restart-Service -Name 'FrameServer' -Force -ErrorAction Stop
    Write-Host "   ✅ Camera service restarted" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Could not restart service (run as Administrator for this)" -ForegroundColor Yellow
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Camera release attempted!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Refresh your browser (F5)" -ForegroundColor White
Write-Host "2. Click 'Start Camera' on http://127.0.0.1:5000/register.html" -ForegroundColor Cyan
Write-Host "3. Click 'Allow' when prompted" -ForegroundColor White
Write-Host "4. Camera should work!`n" -ForegroundColor Green

# Check if any process still has camera handles
Write-Host "Checking for processes with camera handles..." -ForegroundColor Yellow
$camProcesses = Get-Process | Where-Object {$_.Modules.ModuleName -like "*camera*" -or $_.Modules.ModuleName -like "*video*"} -ErrorAction SilentlyContinue
if ($camProcesses) {
    Write-Host "Processes that might be using camera:" -ForegroundColor Yellow
    $camProcesses | Select-Object -First 5 ProcessName -Unique | ForEach-Object {
        Write-Host "  • $($_.ProcessName)" -ForegroundColor White
    }
    Write-Host "`nConsider closing these apps if camera still doesn't work.`n" -ForegroundColor Yellow
}

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
