# System Architecture Documentation

## Overview

The Employee Monitoring and Workspace Management System is built with a modular architecture designed for reliability, maintainability, and scalability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser (Client)                     │
│                     http://localhost:5000                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask API Server                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Routes: /api/status, /api/cameras, /api/employees   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  System Controller                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Coordinates all system components                     │  │
│  │ Main processing loop                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────┬──────────┬──────────┬──────────┬──────────┬───────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌─────────┐ ┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
│ Video   │ │Detection│ │Tracking│ │ Alert   │ │ Database │
│ Capture │ │ Module  │ │ Module │ │ Manager │ │ Manager  │
└─────────┘ └────────┘ └────────┘ └─────────┘ └──────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌─────────┐ ┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
│Cameras  │ │OpenCV/ │ │Employee│ │Desktop  │ │SQLite DB │
│USB/IP   │ │Face Rec│ │States  │ │Notif.   │ │          │
└─────────┘ └────────┘ └────────┘ └─────────┘ └──────────┘
```

## Components

### 1. Web Interface (Frontend)
**Files:** `ui/index.html`, `ui/style.css`, `ui/app.js`

**Responsibilities:**
- Display live camera feeds
- Show employee status dashboard
- Present alerts and logs
- Provide system controls

**Technologies:**
- HTML5 for structure
- CSS3 for styling
- Vanilla JavaScript for interactivity
- AJAX for API communication

### 2. API Server (Backend)
**File:** `src/api_server.py`

**Responsibilities:**
- Expose REST API endpoints
- Serve static frontend files
- Handle HTTP requests
- Stream video feeds (MJPEG)

**Technologies:**
- Flask web framework
- Flask-CORS for cross-origin requests

**Key Endpoints:**
- `GET /api/status` - System status
- `GET /api/cameras` - Camera list
- `GET /api/cameras/{id}/stream` - Video stream
- `GET /api/employees` - Employee list
- `POST /api/employees` - Register employee
- `GET /api/logs` - Presence logs
- `GET /api/alerts` - Alerts

### 3. System Controller
**File:** `src/controller.py`

**Responsibilities:**
- Initialize all components
- Coordinate system operation
- Main processing loop
- Manage system lifecycle

**Key Methods:**
- `start()` - Start monitoring
- `stop()` - Stop monitoring
- `_processing_loop()` - Main detection loop
- `get_system_status()` - Status aggregation

### 4. Video Capture Manager
**File:** `src/video_capture.py`

**Responsibilities:**
- Manage multiple camera streams
- Handle camera connections/disconnections
- Provide frame buffering
- Auto-reconnection

**Classes:**
- `CameraStream` - Single camera handler
- `VideoCaptureManager` - Multi-camera coordinator

**Features:**
- Multi-threaded capture
- Automatic reconnection
- Frame queue management
- USB and IP camera support

### 5. Detection Module
**File:** `src/detection.py`

**Responsibilities:**
- Detect persons in frames
- Detect and recognize faces
- Provide detection overlays

**Classes:**
- `PersonDetector` - HOG-based person detection
- `FaceDetector` - Face detection and recognition
- `DetectionManager` - Unified detection interface

**Technologies:**
- OpenCV HOG detector for persons
- dlib + face_recognition for faces
- Haar Cascades for fast face detection

### 6. Employee Tracker
**File:** `src/tracking.py`

**Responsibilities:**
- Track employee presence states
- Manage entry/exit events
- Monitor absence timeouts
- Trigger alerts

**Key Features:**
- State machine per employee
- Configurable timeouts
- Cooldown periods
- Automatic absence detection

**State Flow:**
```
Not Detected → Present → Last Seen → Absence Timer → Alert
                 ↑                                      │
                 └──────── Return Detected ────────────┘
```

### 7. Alert Manager
**File:** `src/alerts.py`

**Responsibilities:**
- Send desktop notifications
- Play alert sounds
- Manage alert throttling
- Track alert history

**Technologies:**
- plyer for cross-platform notifications
- winsound for Windows alert sounds

### 8. Database Manager
**File:** `src/database.py`

**Responsibilities:**
- Store employee data
- Log presence events
- Record alerts
- Provide querying capabilities

**Schema:**
- `employees` - Employee records with face encodings
- `presence_logs` - Entry/exit timestamps
- `absence_alerts` - Alert records
- `system_events` - System event log

### 9. Configuration Manager
**File:** `src/config_manager.py`

**Responsibilities:**
- Load YAML configuration
- Provide configuration access
- Support runtime updates
- Validate settings

## Data Flow

### Detection Flow
1. Camera captures frame
2. Frame queued in CameraStream
3. VideoCaptureManager provides frame to Controller
4. Controller passes frame to DetectionManager
5. DetectionManager performs person/face detection
6. Detection results returned with employee IDs
7. Controller updates EmployeeTracker
8. Tracker updates presence states

### Alert Flow
1. EmployeeTracker monitors presence states
2. Absence timeout exceeded
3. Tracker calls AlertManager
4. AlertManager creates database alert record
5. AlertManager sends desktop notification
6. AlertManager plays alert sound
7. Alert appears in web UI
8. User acknowledges via UI
9. Database updated

### API Request Flow
1. Browser sends HTTP request
2. Flask routes to appropriate handler
3. Handler calls Controller method
4. Controller queries relevant component
5. Data retrieved and formatted
6. JSON response sent to browser
7. JavaScript updates UI

## Threading Model

### Main Thread
- Flask web server
- API request handling
- UI serving

### Processing Thread
- Main detection loop
- Frame processing
- Detection coordination

### Camera Threads
- One thread per camera
- Continuous frame capture
- Frame queue management

### Tracking Thread
- Absence monitoring
- Timeout checking
- Alert triggering

## Database Schema

### employees
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    face_encoding BLOB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    active INTEGER DEFAULT 1
);
```

### presence_logs
```sql
CREATE TABLE presence_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL,
    camera_id INTEGER,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP,
    duration_seconds INTEGER,
    status TEXT DEFAULT 'present',
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
```

### absence_alerts
```sql
CREATE TABLE absence_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL,
    alert_time TIMESTAMP NOT NULL,
    absence_duration_seconds INTEGER,
    acknowledged INTEGER DEFAULT 0,
    acknowledged_at TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
```

## Configuration

All system configuration is in `config.yaml`:
- Camera definitions
- Detection parameters
- Tracking timeouts
- Alert settings
- Database options
- UI settings

See `CONFIGURATION.md` for detailed documentation.

## Error Handling

### Camera Failures
- Automatic reconnection attempts
- Fallback to last known frame
- Error status reporting

### Detection Failures
- Graceful degradation
- Logged warnings
- Continue operation

### Database Errors
- Transaction rollback
- Error logging
- System continues

### Alert Failures
- Logged warnings
- Database record still created
- System continues

## Performance Considerations

### Optimization Points
1. **Detection Interval** - Skip frames for performance
2. **Camera Resolution** - Lower resolution = faster processing
3. **Detection Method** - Person detection faster than face
4. **Thread Count** - Balance performance vs. CPU usage
5. **Database Indexing** - Indexed queries for speed

### Bottlenecks
- Face recognition (most CPU intensive)
- Multiple high-res cameras
- Network bandwidth for IP cameras
- Disk I/O for database writes

## Security Considerations

### Local Only
- No internet connectivity required
- All data stored locally
- Network access optional

### Data Protection
- Face encodings (not images) stored
- Database file permissions
- API host restriction (127.0.0.1)

### Privacy Compliance
- Local data processing
- No cloud storage
- User control over retention

## Extensibility

### Adding Features
1. **New Detection Methods** - Extend DetectionManager
2. **Custom Alerts** - Modify AlertManager
3. **Additional Logging** - Extend DatabaseManager
4. **API Endpoints** - Add routes in api_server.py

### Integration Points
- REST API for external systems
- Database for reporting tools
- Webhook support (can be added)
- Export capabilities (can be added)

## Deployment

### Requirements
- Python 3.8+
- Windows 10+ (primary platform)
- 4GB+ RAM
- Multi-core CPU recommended

### Installation
See `README.md` and `QUICKSTART.md`

### Maintenance
- Regular database cleanup
- Configuration backups
- Log rotation
- Performance monitoring

---

**Architecture Version:** 1.0  
**Last Updated:** November 2025
