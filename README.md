# Employee Monitoring and Workspace Management System

A comprehensive, locally deployable solution for real-time employee monitoring and workspace management designed specifically for MSMEs (Micro, Small, and Medium Enterprises).

## Features

### Core Capabilities
- **Multi-Camera Support**: Connect USB and IP cameras simultaneously
- **Real-time Detection**: Detect and track employees using computer vision
- **Face Recognition**: Optional face recognition for automatic employee identification
- **Presence Tracking**: Automatic logging of entry/exit times and duration
- **Absence Monitoring**: Configurable timeout alerts when employees don't return
- **Local Alerts**: Desktop notifications and sound alerts for absence events
- **Web Dashboard**: Responsive web interface for monitoring and management
- **Historical Logs**: Detailed logs of all employee activity
- **No Cloud Dependency**: Everything runs locally on your hardware

### Technical Highlights
- Python-based backend with Flask REST API
- OpenCV for video processing
- Face recognition using dlib and face_recognition library
- SQLite database for local data storage
- Modern web UI with real-time updates
- Modular architecture for easy customization

##  Requirements

### Hardware
- Windows PC (Windows 10 or later recommended)
- Minimum 4GB RAM (8GB recommended)
- USB webcam or IP camera(s)
- Intel Core i5 or equivalent processor

### Software
- Python 3.8 or later
- Web browser (Chrome, Firefox, Edge)

## Installation

### Step 1: Install Python
1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation: `python --version`

### Step 2: Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd Muki

# Or download and extract the ZIP file
```

### Step 3: Install Dependencies
```powershell
# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

**Note**: Installing `dlib` and `face_recognition` may require additional tools:
- Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
- Or use pre-built wheels from https://github.com/jloh02/dlib

### Step 4: Configure the System
Edit `config.yaml` to set up your cameras and preferences:

```yaml
cameras:
  - id: 1
    name: "Main Entrance"
    source: 0  # 0 for default USB camera
    enabled: true
  - id: 2
    name: "Workspace"
    source: "rtsp://192.168.1.100:554/stream"  # IP camera RTSP URL
    enabled: true

tracking:
  absence_timeout: 1200  # 20 minutes in seconds
  presence_buffer: 30    # 30 seconds before marking absent
```

### Step 5: Run the System
```powershell
python main.py
```

The system will:
1. Initialize all cameras
2. Start monitoring
3. Launch the web interface at http://localhost:5000

## User Guide

### First-Time Setup

1. **Start the System**
   ```powershell
   python main.py
   ```

2. **Access the Web Interface**
   - Open your browser to http://localhost:5000
   - You'll see the main dashboard

3. **Register Employees** (Optional, for face recognition)
   - Use the API to register employees with photos:
   ```bash
   curl -X POST http://localhost:5000/api/employees \
     -H "Content-Type: application/json" \
     -d '{
       "employee_id": "EMP001",
       "name": "John Doe",
       "image_path": "path/to/photo.jpg"
     }'
   ```

### Daily Operations

#### Monitoring Dashboard
- **Current Occupancy**: See how many employees are present
- **Live Feeds**: View all camera streams with detection overlays
- **Employee Status**: Track who is present and who is absent
- **Alerts**: View and acknowledge absence alerts

#### Understanding Alerts
When an employee is not detected for the configured timeout period (default 20 minutes):
1. A desktop notification appears
2. An alert sound plays (if enabled)
3. The alert appears in the web interface
4. The alert is logged in the database

To acknowledge an alert, click the "Acknowledge" button in the UI.

### Configuration Options

#### Camera Settings
```yaml
cameras:
  - id: 1              # Unique camera ID
    name: "Camera 1"   # Display name
    source: 0          # 0, 1, 2... for USB or RTSP URL for IP camera
    enabled: true      # Enable/disable camera
```

#### Detection Settings
```yaml
detection:
  method: "face"                    # "face", "person", or "both"
  confidence_threshold: 0.5         # Detection confidence (0-1)
  face_recognition_enabled: true    # Enable face recognition
  face_recognition_tolerance: 0.6   # Face match strictness (lower = stricter)
```

#### Tracking Settings
```yaml
tracking:
  absence_timeout: 1200       # Seconds before alert (20 min)
  presence_buffer: 30         # Seconds before marking absent
  entry_exit_cooldown: 10     # Min seconds between events
```

#### Alert Settings
```yaml
alerts:
  enabled: true
  sound_enabled: true
  notification_enabled: true
  alert_repeat_interval: 300  # Don't repeat alerts within 5 min
```

## API Reference

### System Endpoints

#### Get System Status
```
GET /api/status
```
Returns current system status including running state, camera status, and occupancy.

#### Start System
```
POST /api/start
```

#### Stop System
```
POST /api/stop
```

### Camera Endpoints

#### List Cameras
```
GET /api/cameras
```

#### Get Camera Stream
```
GET /api/cameras/{camera_id}/stream
```
Returns MJPEG stream with detection overlays.

#### Get Camera Snapshot
```
GET /api/cameras/{camera_id}/snapshot
```
Returns single JPEG frame.

### Employee Endpoints

#### List Employees
```
GET /api/employees
```

#### Register Employee
```
POST /api/employees
Content-Type: application/json

{
  "employee_id": "EMP001",
  "name": "John Doe",
  "image_path": "optional/path/to/photo.jpg"
}
```

#### Get Employee Status
```
GET /api/employees/{employee_id}/status
GET /api/employees/status  # All employees
```

### Logs Endpoints

#### Get Presence Logs
```
GET /api/logs?employee_id=EMP001&limit=100
```

### Alerts Endpoints

#### Get Alerts
```
GET /api/alerts?unacknowledged=true
```

#### Acknowledge Alert
```
POST /api/alerts/{alert_id}/acknowledge
```

## Testing

Run the automated test suite:

```powershell
# Install pytest if not already installed
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Camera Not Detected
- **USB Camera**: Try different source IDs (0, 1, 2...)
- **IP Camera**: Verify RTSP URL format and network connectivity
- Check camera permissions in Windows settings

### Face Recognition Not Working
- Ensure employee photos are clear and well-lit
- Adjust `face_recognition_tolerance` in config.yaml
- Check that faces are properly registered in the database

### High CPU Usage
- Reduce detection interval in config: `detection.detection_interval: 2`
- Lower camera resolution
- Disable face recognition if not needed

### Alerts Not Showing
- Check Windows notification settings
- Verify `alerts.enabled: true` in config
- Check system logs in `logs/system.log`

### Database Errors
- Delete `data/employees.db` to reset (loses all data)
- Check file permissions in data directory

## Project Structure

```
Muki/
├── main.py                 # Application entry point
├── config.yaml            # System configuration
├── requirements.txt       # Python dependencies
├── src/
│   ├── __init__.py
│   ├── config_manager.py  # Configuration management
│   ├── database.py        # Database operations
│   ├── video_capture.py   # Camera handling
│   ├── detection.py       # Person/face detection
│   ├── tracking.py        # Employee tracking
│   ├── alerts.py          # Alert management
│   ├── controller.py      # Main system controller
│   └── api_server.py      # Flask API server
├── ui/
│   ├── index.html         # Web interface
│   ├── style.css          # Styles
│   └── app.js             # Frontend logic
├── tests/
│   └── test_system.py     # Automated tests
├── data/                  # Database files (created at runtime)
└── logs/                  # Log files (created at runtime)
```

## Privacy & Security

- **All Data Local**: No cloud services, all data stays on your machine
- **Database Encryption**: Consider encrypting the database file for sensitive deployments
- **Network Security**: Use firewall rules to restrict API access to local network only
- **Face Data**: Face encodings are stored as binary data, not actual images
- **GDPR Compliance**: Ensure proper consent and data handling per local regulations

## Advanced Configuration

### Running as Windows Service
Use NSSM (Non-Sucking Service Manager) to run as a background service:

```powershell
# Download NSSM from https://nssm.cc/
nssm install EmployeeMonitor "C:\path\to\python.exe" "C:\path\to\main.py"
nssm start EmployeeMonitor
```

### Database Backup
Regularly backup the database:

```powershell
# Copy database file
copy data\employees.db backups\employees_backup_$(Get-Date -Format 'yyyyMMdd').db
```

### Custom Alert Actions
Edit `src/alerts.py` to add custom alert actions like email, SMS, or webhook notifications.

## Performance Optimization

1. **Adjust Detection Interval**: Increase to process fewer frames
2. **Reduce Camera Resolution**: Lower resolution = faster processing
3. **Use Person Detection Only**: Faster than face recognition
4. **Limit Camera Count**: More cameras = more CPU usage
5. **Database Maintenance**: Run cleanup regularly to remove old logs

## Contributing

This is a complete, working system. Enhancements welcome:
- Additional detection algorithms
- Mobile app interface
- Export features (PDF reports, Excel)
- Multi-language support
- Enhanced analytics

## License

This project is provided as-is for use by MSMEs. Modify and adapt as needed for your specific requirements.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `logs/system.log`
3. Test individual components using the test suite
4. Verify configuration in `config.yaml`

## Learning Resources

- **OpenCV**: https://opencv.org/
- **Face Recognition**: https://face-recognition.readthedocs.io/
- **Flask**: https://flask.palletsprojects.com/
- **SQLite**: https://www.sqlite.org/

---

**Built with ❤️ for Small Businesses**
