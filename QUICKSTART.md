# Quick Start Guide

## First Time Setup (5 minutes)

### 1. Install Python
- Download from https://www.python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation
- Verify: Open PowerShell and run `python --version`

### 2. Install the System
```powershell
# Open PowerShell in the project directory
cd D:\Personal-Projects\Muki

# Run installation script
.\install.ps1
```

### 3. Configure Cameras
Edit `config.yaml`:
```yaml
cameras:
  - id: 1
    name: "Main Camera"
    source: 0        # 0 for USB camera, or RTSP URL for IP camera
    enabled: true
```

### 4. Start the System
```powershell
.\start.ps1
```

### 5. Open Web Interface
Open your browser to: **http://localhost:5000**

## Quick Commands

### Start System
```powershell
.\start.ps1
```

### Register Employee (with photo)
```powershell
.\venv\Scripts\Activate.ps1
python utils/employee_manager.py register EMP001 "John Doe" --photo path/to/photo.jpg
```

### Register Employee (without photo)
```powershell
.\venv\Scripts\Activate.ps1
python utils/employee_manager.py register EMP001 "John Doe"
```

### List All Employees
```powershell
.\venv\Scripts\Activate.ps1
python utils/employee_manager.py list
```

### View Recent Logs
```powershell
.\venv\Scripts\Activate.ps1
python utils/employee_manager.py logs --limit 50
```

### View Alerts
```powershell
.\venv\Scripts\Activate.ps1
python utils/employee_manager.py alerts --unacknowledged
```

## Common Issues

### Camera Not Working
- Try different source numbers: 0, 1, 2...
- For IP cameras, verify RTSP URL format
- Check Windows camera permissions

### Face Recognition Errors
If you see errors about dlib or face_recognition:
1. You can still use the system without face recognition
2. Set in config.yaml: `detection.face_recognition_enabled: false`
3. Use person detection instead: `detection.method: "person"`

### Port Already in Use
If port 5000 is busy, change in config.yaml:
```yaml
ui:
  port: 8080  # Use different port
```

## Daily Use

1. **Start System**: Double-click `start.ps1` or run in PowerShell
2. **Monitor**: Open http://localhost:5000 in your browser
3. **View Status**: Check dashboard for current occupancy and alerts
4. **Acknowledge Alerts**: Click "Acknowledge" button when employees return
5. **Stop System**: Press Ctrl+C in PowerShell window

## Tips

- Keep the system running in the background
- Regularly backup `data/employees.db`
- Check `logs/system.log` for troubleshooting
- Adjust `absence_timeout` in config for your needs
- Use person detection if face recognition is too slow

## Need Help?

1. Check `README.md` for detailed documentation
2. Review `logs/system.log` for errors
3. Run tests: `pytest tests/ -v`
4. Verify config: Review `config.yaml`

---

**System Ready!** You can now monitor your workspace effectively.
