# 📸 Camera-Based Employee Registration Guide

## Overview

The Employee Monitoring System now features **live camera-based employee registration**! This allows you to register employees by capturing their photo directly through your webcam or any connected camera.

---

## ✨ Key Features

### 1. **Live Camera Preview**
- Real-time video feed from your camera
- Mirror mode for natural selfie-style capture
- High-quality image capture (up to 1280x720)

### 2. **Web-Based Registration**
- No software installation needed
- Works in any modern browser
- Simple, intuitive interface

### 3. **Instant Photo Capture**
- Click once to capture photo
- Preview before registering
- Retake option if needed

### 4. **Complete Employee Profile**
- Employee ID (unique identifier)
- Full Name (required)
- Department (optional)
- Photo (captured via camera)

---

## 🚀 How to Use

### Step 1: Access Registration Page

1. Open your browser to: **http://127.0.0.1:5000**
2. Click the **"📸 Register Employee"** button in the header
3. You'll be taken to the registration page

### Step 2: Start Camera

1. Click **"Start Camera"** button
2. **Allow camera permissions** when prompted by your browser
3. Your live video feed will appear
4. Position yourself (or the employee) in front of the camera

### Step 3: Capture Photo

1. When ready, click **"📸 Capture Photo"**
2. The photo will appear in the preview panel on the right
3. If not satisfied, click **"🔄 Retake"** to try again

### Step 4: Fill Employee Details

1. **Employee ID**: Enter a unique identifier (e.g., EMP004, EMP005)
   - Must be unique
   - Only letters and numbers allowed
   
2. **Full Name**: Enter employee's full name (e.g., Sarah Johnson)
   - Required field
   
3. **Department**: Enter department (optional, e.g., Engineering, Sales)
   - This is optional but helps with organization

### Step 5: Register

1. Click **"✅ Register Employee"** button
2. Wait for confirmation message
3. Choose to register another employee or return to dashboard

---

## 🎥 Camera Setup

### Supported Cameras

- **USB Webcams** (built-in or external)
- **Laptop cameras** (built-in)
- **External USB cameras**

### Browser Permissions

The first time you click "Start Camera", your browser will ask:

```
"http://127.0.0.1:5000 wants to use your camera"
```

**Click "Allow"** to grant permission.

### Troubleshooting Camera Issues

**Camera not detected?**
- Check if camera is connected
- Close other applications using the camera (Zoom, Skype, etc.)
- Try a different browser (Chrome, Edge recommended)
- Refresh the page and try again

**Permission denied?**
- Check browser camera settings
- In Chrome: Settings → Privacy and Security → Site Settings → Camera
- Make sure http://127.0.0.1:5000 is allowed

---

## 💡 Best Practices

### Photo Quality

✅ **DO:**
- Ensure good lighting (face the light source)
- Keep a neutral facial expression
- Look directly at the camera
- Remove glasses if possible (reduces glare)
- Keep face centered in frame

❌ **DON'T:**
- Use backlit conditions (window behind you)
- Tilt head too much
- Wear hats or face coverings
- Be too far from camera

### Registration Tips

1. **Unique IDs**: Use a consistent format (EMP001, EMP002, etc.)
2. **Full Names**: Use proper capitalization (John Doe, not john doe)
3. **Departments**: Be consistent (Engineering vs engineering)
4. **Batch Registration**: Register multiple employees in one session

---

## 🔧 Technical Details

### Image Processing

- **Format**: JPEG (90% quality)
- **Storage**: `data/employee_photos/` directory
- **Naming**: `{employee_id}.jpg` (e.g., EMP004.jpg)
- **Resolution**: Original camera resolution preserved

### Data Storage

Employee data is stored in SQLite database with:
- Employee ID (unique identifier)
- Full Name
- Department (optional)
- Photo path
- Registration timestamp

### API Endpoint

```http
POST /api/employees/register
Content-Type: application/json

{
  "employee_id": "EMP004",
  "name": "Sarah Johnson",
  "department": "Engineering",
  "photo_data": "data:image/jpeg;base64,/9j/4AAQ..." 
}
```

---

## 📊 After Registration

### What Happens Next?

1. **Photo Saved**: Image stored in `data/employee_photos/`
2. **Database Updated**: Employee record created
3. **System Ready**: Employee can now be detected by the system
4. **Dashboard Updated**: New employee appears in employee list

### Verify Registration

Go back to the main dashboard to see:
- New employee in the employee list
- Employee status (absent initially)
- Photo stored successfully

---

## 🎯 Monitoring After Registration

Once registered, the employee will be:

1. **Detected** when they enter camera view
2. **Tracked** with entry/exit times
3. **Monitored** for absence (20-minute default timeout)
4. **Logged** in presence history

---

## 🔐 Privacy & Security

### Data Protection

- All data stored **locally** on your machine
- No cloud upload or external sharing
- Photos accessible only on local server
- Database encrypted with permissions

### Access Control

- Registration page requires server access
- Only accessible on local network (127.0.0.1)
- Can be restricted with authentication (future feature)

---

## 📱 Mobile Support

The registration page is **mobile-friendly**:
- Works on smartphones and tablets
- Touch-optimized controls
- Responsive design
- Front/rear camera selection

---

## ⚙️ Configuration

### Camera Settings

Edit `config.yaml` for camera preferences:

```yaml
cameras:
  - id: "registration_cam"
    name: "Registration Camera"
    source: 0  # 0 = default camera, 1 = second camera
    enabled: true
```

### Photo Quality

For higher quality photos, modify in `register.js`:

```javascript
capturedImageData = canvas.toDataURL('image/jpeg', 0.95); // 95% quality
```

---

## 🆘 Common Issues

### Issue: "No camera detected"
**Solution**: 
- Check camera connection
- Ensure no other app is using camera
- Try different USB port

### Issue: "Failed to access camera"
**Solution**:
- Grant browser camera permissions
- Check camera drivers
- Try different browser

### Issue: "Registration failed"
**Solution**:
- Check if Employee ID already exists
- Ensure photo was captured
- Check server logs for errors

### Issue: "Photo quality poor"
**Solution**:
- Improve lighting
- Clean camera lens
- Use external webcam for better quality

---

## 🔄 Workflow Example

### Complete Registration Flow

1. **Manager**: Opens registration page
2. **Employee**: Stands in front of camera
3. **Manager**: Clicks "Start Camera"
4. **System**: Shows live preview
5. **Manager**: Positions employee, clicks "Capture"
6. **System**: Shows captured photo
7. **Manager**: Fills in details (ID, Name, Department)
8. **Manager**: Clicks "Register Employee"
9. **System**: Saves photo and creates record
10. **Confirmation**: Shows success message
11. **Repeat**: For next employee or return to dashboard

---

## 📈 Benefits

### For Administrators

✅ Quick registration (1-2 minutes per employee)
✅ No separate photo upload needed
✅ Immediate verification of photo quality
✅ Organized employee database

### For Employees

✅ Fast onboarding process
✅ Professional photo capture
✅ No external photo requirements
✅ Immediate system access

---

## 🎓 Training Tips

### For Registration Staff

1. **Prepare**: Have employee list ready with IDs
2. **Setup**: Test camera and lighting beforehand
3. **Communicate**: Explain process to employees
4. **Capture**: Take 2-3 photos, use best one
5. **Verify**: Check photo quality before confirming
6. **Document**: Keep record of registrations

---

## 🔮 Future Enhancements

Planned features:
- Bulk registration support
- Photo editing/cropping
- Multiple photo angles
- QR code ID scanning
- Badge printing integration

---

## 📞 Support

### Getting Help

- Check `README.md` for general system info
- Review `RUNNING.md` for operational guide
- See `CONFIGURATION.md` for settings
- Check logs in `logs/` directory

### Reporting Issues

If registration fails:
1. Check browser console (F12)
2. Review server logs
3. Verify camera permissions
4. Test with different browser

---

## ✅ Quick Checklist

Before starting registration:

- [ ] Server running (http://127.0.0.1:5000)
- [ ] Camera connected and working
- [ ] Browser camera permissions granted
- [ ] Good lighting setup
- [ ] Employee list prepared
- [ ] Unique IDs planned

---

**System Ready!** Start registering employees with live camera capture! 📸
