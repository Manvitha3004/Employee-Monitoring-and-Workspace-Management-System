# 🎥 Live Camera Feed Setup Guide

## Current System Status

Your system is designed to work with **TWO separate functions**:

### 1. 📸 **Registration Camera** (Browser-based)
- Uses your webcam through the browser
- For capturing employee photos during registration
- Access: http://127.0.0.1:5000/register.html

### 2. 📹 **Monitoring Camera** (Python backend)
- Uses webcam through OpenCV (Python)
- For live employee detection and monitoring
- Shows on dashboard: http://127.0.0.1:5000

## ⚠️ The Problem

**You have ONE camera**, but the system needs it for TWO purposes:
1. Browser needs it for registration
2. Python needs it for monitoring/detection

**These CANNOT run at the same time** - only one application can access the camera at once.

## ✅ Solutions

### Option 1: **Sequential Use** (Recommended for 1 camera)

**How it works:**
1. **Registration Phase:** Use browser camera to register employees
2. **Monitoring Phase:** Stop registration, start monitoring system

**Steps:**
```
REGISTRATION (Browser):
1. Go to http://127.0.0.1:5000/register.html
2. Click "Start Camera" → Register employees
3. When done, close registration page

MONITORING (Python):
4. Go to http://127.0.0.1:5000 (dashboard)
5. Click "Start System" → Python takes camera
6. Live feed shows on dashboard
7. System detects registered employees
```

**Current Status:** ✅ Already set up this way!

### Option 2: **Two Cameras** (Best solution)

**Why?**
- Registration and monitoring can run simultaneously
- No need to switch between modes
- Professional setup

**What you need:**
- Keep your built-in webcam for **registration** (browser)
- Add external USB camera for **monitoring** (Python backend)

**Setup:**
1. Connect USB webcam to computer
2. Edit `config.yaml`:
   ```yaml
   cameras:
     - id: 1
       name: "Monitoring Camera"
       source: 1  # Use second camera (USB webcam)
       enabled: true
   ```
3. Now both work simultaneously!

**Recommended USB Camera:**
- Logitech C920 or C922
- Microsoft LifeCam
- Any USB webcam with 720p or higher

### Option 3: **IP Camera** (Professional)

**For larger deployments:**
- Use browser camera for registration (employee-facing)
- Use fixed IP camera for monitoring (office-facing)

**Setup:**
```yaml
cameras:
  - id: 1
    name: "Office Monitor"
    source: "rtsp://192.168.1.100:554/stream"
    enabled: true
```

## 🎯 Current Workflow (1 Camera)

### Phase 1: Registration
```
1. Dashboard OFF (don't start system)
2. Go to Registration page
3. Use browser camera to register employees
4. Complete all registrations
5. Close registration page
```

### Phase 2: Monitoring
```
1. Go to Dashboard
2. Click "Start System"
3. Python takes camera
4. Live feed appears in "Live Camera Feeds" section
5. System detects people
6. Matches against registered employees
7. Logs presence automatically
```

## 📊 What You'll See

### Dashboard (Monitoring Active):
```
┌─────────────────────────────────────┐
│  📹 Live Camera Feeds               │
├─────────────────────────────────────┤
│  Main Entrance (ID: 1) 🟢 Active   │
│  ┌───────────────────────────────┐ │
│  │                               │ │
│  │   [LIVE VIDEO FEED]           │ │
│  │   Shows office/workspace      │ │
│  │   Detects people in frame     │ │
│  │                               │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Present Employees                  │
├─────────────────────────────────────┤
│  B Manvitha (302004)                │
│  Entry: 10:30 AM                    │
│  Last Seen: 10:45 AM                │
└─────────────────────────────────────┘
```

## 🔧 Troubleshooting

### "No cameras configured" message?

**Solution:**
```powershell
# Stop the system
# Click "Stop System" on dashboard

# Edit config.yaml
# Make sure source is correct (0 for built-in, 1 for USB)

# Restart system
# Click "Start System" on dashboard
```

### Camera shows black screen?

**Causes:**
1. Browser is still using camera
2. Another app has camera (Zoom, Teams)
3. Wrong camera source in config

**Fix:**
```powershell
# Close all browser tabs with camera access
# Close Zoom, Teams, Skype
# Run:
Get-Process | Where {$_.ProcessName -match 'Camera|Zoom|Teams'} | Stop-Process -Force
```

### Want to see detection in action?

**Test it:**
1. Start system (dashboard → "Start System")
2. Stand in front of camera
3. System detects person
4. Checks if face matches registered employee
5. If match: Logs presence, shows in "Present" tab
6. If no match: Just shows detection

## 📝 Detection Methods

Current system uses **person detection** (not face recognition):

### Person Detection:
- ✅ Works without face recognition library
- ✅ Faster processing
- ✅ Detects anyone in frame
- ❌ Can't identify WHO specifically

### To Enable Face Recognition:
```
1. Install CMake and Visual Studio Build Tools
2. Install face_recognition library
3. Edit config.yaml:
   detection:
     method: "face"
     face_recognition_enabled: true
4. System will match faces to registered employees
```

## 🎬 Complete Demo Flow

### Scenario: Monitor employee "B Manvitha"

**Step 1 - Register** (Already done! ✅)
- Used browser camera
- Captured photo
- Saved as employee 302004

**Step 2 - Start Monitoring**
```
1. Close registration page
2. Go to dashboard
3. Click "Start System"
4. Camera feed appears
```

**Step 3 - Employee Arrives**
```
- B Manvitha walks into camera view
- System detects person
- Compares to registered employees
- Logs entry time
- Shows in "Present Employees" table
```

**Step 4 - Employee Leaves**
```
- B Manvitha leaves camera view
- Absence timer starts (20 min default)
- Moves to "Absent (On Timer)" tab
- After 20 min: Alert triggered
```

## 💡 Best Practices

### For Single Camera Setup:
1. Register all employees FIRST
2. Then start monitoring system
3. Don't switch back to registration while monitoring
4. To add new employee: Stop system → Register → Restart

### For Dual Camera Setup:
1. Camera 0 (built-in): Browser registration
2. Camera 1 (USB): Python monitoring
3. Both can run simultaneously
4. Register anytime without stopping monitoring

## 🚀 Next Steps

**Current Setup (1 camera):**
- ✅ Registration working
- ✅ 5 employees registered
- ⏳ Monitoring ready to start

**To Start Monitoring NOW:**
1. Close all browser tabs using camera
2. Go to dashboard: http://127.0.0.1:5000
3. Click green "Start System" button
4. Live camera feed will appear!
5. Stand in front of camera to test

**To Upgrade (2 cameras):**
1. Buy USB webcam (~$30-50)
2. Plug into computer
3. Edit config.yaml to use camera 1
4. Enjoy simultaneous registration + monitoring!

---

## ✅ Quick Commands

**Check available cameras:**
```powershell
# Run this to see all cameras
D:/Personal-Projects/Muki/venv/Scripts/python.exe -c "import cv2; i=0; while True: cap=cv2.VideoCapture(i); ret=cap.read()[0]; cap.release(); if not ret: break; print(f'Camera {i}: Available'); i+=1"
```

**Release camera:**
```powershell
Get-Process | Where {$_.ProcessName -match 'Camera|Zoom|Teams'} | Stop-Process -Force
```

**View registered employees:**
```powershell
D:/Personal-Projects/Muki/venv/Scripts/python.exe check_db.py
```

---

**Your system is ready! Start monitoring to see the live camera feed!** 🎥✨
