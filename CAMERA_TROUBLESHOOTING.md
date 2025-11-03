# 🎥 Camera Permission Troubleshooting Guide

## Quick Fix Steps

### ✅ Most Common Solution

**Problem:** "Failed to access camera. Please allow camera permissions."

**Solution:** Access via the correct URL

```
✅ USE THIS: http://127.0.0.1:5000/register.html
❌ NOT THIS: http://localhost:5000/register.html
```

**Why?** Browsers treat `127.0.0.1` and `localhost` differently for security. Use the IP address version!

---

## Step-by-Step Fixes

### 1️⃣ **Check Windows Camera Permissions**

1. Open **Windows Settings** (Win + I)
2. Go to **Privacy & Security** → **Camera**
3. Ensure these are ON:
   - "Camera access" toggle
   - "Let apps access your camera" toggle
   - "Let desktop apps access your camera" toggle

### 2️⃣ **Allow Browser Camera Access**

#### For Chrome/Edge:
1. Go to `chrome://settings/content/camera` (or `edge://settings/content/camera`)
2. Ensure camera is not blocked
3. Check "Sites allowed to access camera" list
4. Add `http://127.0.0.1:5000` if not present

#### For Firefox:
1. Go to `about:preferences#privacy`
2. Scroll to **Permissions** → **Camera**
3. Click "Settings" next to Camera
4. Ensure `http://127.0.0.1:5000` is allowed

### 3️⃣ **Close Other Applications**

Camera can only be used by one application at a time. Close:
- ✖ Zoom
- ✖ Microsoft Teams
- ✖ Skype
- ✖ Discord (if camera is on)
- ✖ OBS Studio
- ✖ Other camera apps

### 4️⃣ **Grant Permission When Prompted**

When you click "Start Camera", browser shows:

```
┌────────────────────────────────────────┐
│ http://127.0.0.1:5000 wants to         │
│ Use your camera                        │
│                                        │
│  [Block]          [Allow] ←── CLICK    │
└────────────────────────────────────────┘
```

**Always click "Allow"!**

### 5️⃣ **Check Camera Icon in Address Bar**

After first attempt, check your browser address bar:

```
http://127.0.0.1:5000  🎥  🔒
                       ↑
                  Click here
```

Click the camera icon and select "Always allow"

### 6️⃣ **Try Different Browser**

**Best to Worst for Camera Access:**
1. ✅ Google Chrome (Recommended)
2. ✅ Microsoft Edge (Recommended)
3. ⚠️ Firefox (Works but may need extra steps)
4. ❌ Internet Explorer (Not supported)
5. ❌ Safari (macOS only)

---

## Advanced Troubleshooting

### Check if Camera is Detected

**In PowerShell:**
```powershell
Get-PnpDevice -Class Camera -Status OK
```

Should show your camera. If not, check Device Manager.

### Test Camera in Windows

1. Open **Camera** app (built-in Windows app)
2. If it works there, the camera hardware is fine
3. If it doesn't work, update drivers:
   - Open Device Manager
   - Expand "Cameras" or "Imaging devices"
   - Right-click camera → Update driver

### Browser Console Errors

1. Open registration page
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Click "Start Camera"
5. Read the error message

**Common Error Messages:**

| Error | Meaning | Solution |
|-------|---------|----------|
| `NotAllowedError` | Permission denied | Click "Allow" when prompted |
| `NotFoundError` | No camera found | Connect camera or check drivers |
| `NotReadableError` | Camera in use | Close other apps using camera |
| `OverconstrainedError` | Settings not supported | Use simpler camera settings |
| `SecurityError` | Security blocked | Use http://127.0.0.1:5000 |

---

## Platform-Specific Issues

### Windows 10/11

**Camera Privacy Settings:**
```
Settings → Privacy → Camera
- Turn ON "Allow apps to access your camera"
- Turn ON "Allow desktop apps to access your camera"
```

**Check Camera Service:**
```powershell
# Run as Administrator
Get-Service -Name "FrameServer" | Start-Service
```

### Windows 11 Specific

Windows 11 has stricter camera permissions:

1. **Settings** → **Privacy & security** → **Camera**
2. Enable "Camera access"
3. Enable "Let apps access your camera"
4. Scroll down to **Desktop apps** section
5. Ensure your browser is listed and enabled

---

## Alternative: Use File Upload Instead

If camera access continues to fail, you can modify the system to upload photos instead:

### Quick Workaround

1. Take photo with phone/camera
2. Save to computer
3. Use employee manager CLI:
   ```powershell
   python utils/employee_manager.py
   # Choose option 1 (Add employee)
   # Provide path to photo file
   ```

---

## Testing Camera Access

### Simple Browser Test

Open this URL in your browser:
```
https://webcamtests.com/
```

If camera works there, it's a permission issue with our app.

### JavaScript Test

Open browser console (F12) and paste:

```javascript
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    console.log('✅ Camera access granted!');
    stream.getTracks().forEach(track => track.stop());
  })
  .catch(error => {
    console.error('❌ Camera error:', error.name, error.message);
  });
```

---

## Still Not Working?

### Last Resort Steps

1. **Restart Browser** completely (close all windows)
2. **Restart Computer** to reset camera drivers
3. **Update Windows** (Settings → Windows Update)
4. **Update Browser** to latest version
5. **Reinstall Camera Drivers**
6. **Try USB Camera** instead of built-in camera

### Get More Help

Check these logs:
- Browser Console (F12 → Console tab)
- Server logs (check terminal where Python is running)
- Windows Event Viewer → Windows Logs → Application

---

## Success Checklist

Before attempting again:

- [ ] Using `http://127.0.0.1:5000` (not localhost)
- [ ] Windows Camera privacy is enabled
- [ ] Browser camera permission granted
- [ ] No other apps using camera
- [ ] Camera appears in Device Manager
- [ ] Using Chrome or Edge browser
- [ ] Page refreshed after fixing permissions

---

## Prevention

### Set Permanent Permissions

**Chrome/Edge:**
1. Visit `chrome://settings/content/camera`
2. Add `http://127.0.0.1:5000` to "Allowed to use your camera"
3. Never get prompted again!

**Firefox:**
1. Visit `about:preferences#privacy`
2. Find Camera → Settings
3. Set `http://127.0.0.1:5000` to "Allow"

---

## Expected Behavior

### When Working Correctly:

1. Click "Start Camera"
2. Browser shows permission dialog
3. Click "Allow"
4. Live video appears instantly
5. Can capture photo
6. Registration succeeds

**Total time: 2-3 seconds** ⚡

---

**After following this guide, your camera should work!** 🎉

If you've tried everything and it still doesn't work, use the file upload workaround with `utils/employee_manager.py`.
