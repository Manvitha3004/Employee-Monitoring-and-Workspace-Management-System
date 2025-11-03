# Camera Diagnostics Script
# Run this to check camera availability and permissions

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🎥 CAMERA DIAGNOSTICS" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

# Check for cameras in Device Manager
Write-Host "1️⃣ Checking for connected cameras..." -ForegroundColor Yellow
try {
    $cameras = Get-PnpDevice -Class Camera -Status OK -ErrorAction SilentlyContinue
    if ($cameras) {
        Write-Host "   ✅ Found $($cameras.Count) camera(s):" -ForegroundColor Green
        $cameras | ForEach-Object {
            Write-Host "      • $($_.FriendlyName)" -ForegroundColor White
        }
    } else {
        Write-Host "   ❌ No cameras detected" -ForegroundColor Red
        Write-Host "      Check Device Manager or connect a USB camera" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not check camera devices" -ForegroundColor Yellow
}

# Check Windows Camera Service
Write-Host "`n2️⃣ Checking Windows Camera Service..." -ForegroundColor Yellow
try {
    $service = Get-Service -Name "FrameServer" -ErrorAction SilentlyContinue
    if ($service) {
        if ($service.Status -eq "Running") {
            Write-Host "   ✅ Camera service is running" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Camera service is $($service.Status)" -ForegroundColor Yellow
            Write-Host "      Starting service..." -ForegroundColor White
            Start-Service -Name "FrameServer" -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            $service = Get-Service -Name "FrameServer"
            if ($service.Status -eq "Running") {
                Write-Host "   ✅ Service started successfully" -ForegroundColor Green
            }
        }
    }
} catch {
    Write-Host "   ⚠️  Could not check camera service" -ForegroundColor Yellow
}

# Check if camera app is installed
Write-Host "`n3️⃣ Checking Windows Camera app..." -ForegroundColor Yellow
$cameraApp = Get-AppxPackage -Name "Microsoft.WindowsCamera" -ErrorAction SilentlyContinue
if ($cameraApp) {
    Write-Host "   ✅ Camera app installed" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Camera app not found" -ForegroundColor Yellow
}

# Check for processes using camera
Write-Host "`n4️⃣ Checking for apps that might be using camera..." -ForegroundColor Yellow
$cameraApps = @("Zoom", "Teams", "Skype", "Discord", "obs64", "obs32")
$foundApps = @()
foreach ($app in $cameraApps) {
    $process = Get-Process -Name $app -ErrorAction SilentlyContinue
    if ($process) {
        $foundApps += $app
    }
}
if ($foundApps.Count -gt 0) {
    Write-Host "   ⚠️  Found apps that might be using camera:" -ForegroundColor Yellow
    $foundApps | ForEach-Object {
        Write-Host "      • $_" -ForegroundColor White
    }
    Write-Host "      Consider closing these apps" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ No known camera apps running" -ForegroundColor Green
}

# Check registry for camera privacy settings
Write-Host "`n5️⃣ Checking camera privacy settings..." -ForegroundColor Yellow
try {
    $capabilityAccess = "HKCU:\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam"
    if (Test-Path $capabilityAccess) {
        $value = Get-ItemProperty -Path $capabilityAccess -Name "Value" -ErrorAction SilentlyContinue
        if ($value.Value -eq "Allow") {
            Write-Host "   ✅ Camera access is allowed" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Camera access: $($value.Value)" -ForegroundColor Yellow
            Write-Host "      Enable in: Settings → Privacy → Camera" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ⚠️  Could not check privacy settings" -ForegroundColor Yellow
}

# Server check
Write-Host "`n6️⃣ Checking server status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/status" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Server is running on http://127.0.0.1:5000" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Server is not running" -ForegroundColor Red
    Write-Host "      Start with: python main.py" -ForegroundColor Yellow
}

# Summary and recommendations
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📋 RECOMMENDATIONS" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

if ($cameras) {
    Write-Host "✅ Camera hardware: OK" -ForegroundColor Green
} else {
    Write-Host "❌ Camera hardware: NOT DETECTED" -ForegroundColor Red
    Write-Host "   → Connect a USB camera or check Device Manager" -ForegroundColor White
}

Write-Host "`n🌐 Access registration page at:" -ForegroundColor Yellow
Write-Host "   http://127.0.0.1:5000/register.html" -ForegroundColor Cyan
Write-Host "`n⚠️  IMPORTANT: Use 127.0.0.1, NOT localhost!" -ForegroundColor Yellow

Write-Host "`n📖 Troubleshooting steps:" -ForegroundColor Yellow
Write-Host "   1. Open http://127.0.0.1:5000/register.html in Chrome/Edge" -ForegroundColor White
Write-Host "   2. Click 'Start Camera'" -ForegroundColor White
Write-Host "   3. Click 'Allow' when browser asks for permission" -ForegroundColor White
Write-Host "   4. If still fails, check CAMERA_TROUBLESHOOTING.md" -ForegroundColor White

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
