# Configuration Guide

This document explains all configuration options available in `config.yaml`.

## Camera Configuration

```yaml
cameras:
  - id: 1                    # Unique camera identifier (integer)
    name: "Main Entrance"    # Display name for the camera
    source: 0                # Camera source (see below)
    enabled: true            # Whether camera is active
```

### Camera Sources

**USB Cameras:**
- Use integer values: `0`, `1`, `2`, etc.
- Try different values to find your camera

**IP Cameras:**
- Use RTSP URL format: `rtsp://username:password@ip:port/path`
- Examples:
  - `rtsp://admin:password@192.168.1.100:554/stream`
  - `rtsp://192.168.1.100/live/main`

**Multiple Cameras:**
```yaml
cameras:
  - id: 1
    name: "Entrance"
    source: 0
    enabled: true
  - id: 2
    name: "Workspace"
    source: "rtsp://192.168.1.100:554/stream"
    enabled: true
  - id: 3
    name: "Exit"
    source: 1
    enabled: false  # Temporarily disabled
```

## Detection Settings

```yaml
detection:
  method: "face"                      # Detection method
  confidence_threshold: 0.5           # Detection confidence (0-1)
  detection_interval: 1               # Process every N frames
  face_recognition_enabled: true      # Enable face recognition
  face_recognition_tolerance: 0.6     # Face match tolerance
```

### Detection Methods

- **`face`**: Detect and recognize faces (most accurate for identification)
- **`person`**: Detect people using body detection (faster, no recognition)
- **`both`**: Use both methods (most comprehensive)

### Confidence Threshold
- Range: 0.0 to 1.0
- Lower = more detections, but more false positives
- Higher = fewer detections, but more accurate
- Recommended: 0.5 for faces, 0.6 for persons

### Detection Interval
- Process every N frames
- Higher = better performance, less responsive
- Lower = worse performance, more responsive
- Recommended: 1 for real-time, 2-3 for performance

### Face Recognition Tolerance
- Range: 0.0 to 1.0
- Lower = stricter matching, fewer false matches
- Higher = looser matching, more false matches
- Recommended: 0.6 (default)

## Tracking Settings

```yaml
tracking:
  absence_timeout: 1200          # Seconds until alert (20 minutes)
  presence_buffer: 30            # Seconds before marking absent
  entry_exit_cooldown: 10        # Cooldown between events
```

### Absence Timeout
- Time in seconds before triggering absence alert
- Default: 1200 (20 minutes)
- Examples:
  - 5 minutes: `300`
  - 10 minutes: `600`
  - 30 minutes: `1800`
  - 1 hour: `3600`

### Presence Buffer
- Grace period before marking employee as absent
- Prevents false absences from brief obstructions
- Default: 30 seconds
- Recommended: 20-60 seconds

### Entry/Exit Cooldown
- Minimum time between entry/exit events
- Prevents duplicate logging from flickering detection
- Default: 10 seconds
- Recommended: 5-15 seconds

## Alert Settings

```yaml
alerts:
  enabled: true                  # Master alert switch
  sound_enabled: true            # Play alert sounds
  notification_enabled: true     # Show desktop notifications
  alert_repeat_interval: 300     # Min seconds between repeat alerts
```

### Alert Types

**Desktop Notifications:**
- System tray notifications
- Requires Windows 10+
- Configure in Windows notification settings

**Sound Alerts:**
- System beep sound
- Frequency: 1000 Hz
- Duration: 500ms

### Alert Repeat Interval
- Prevents spam from same employee
- Time in seconds
- Default: 300 (5 minutes)

## Database Settings

```yaml
database:
  path: "data/employees.db"      # Database file location
  log_retention_days: 90         # Keep logs for N days
```

### Database Path
- Relative or absolute path
- Directory will be created if it doesn't exist
- Default: `data/employees.db`

### Log Retention
- Number of days to keep logs
- Older logs are deleted during cleanup
- Default: 90 days
- Set to 0 to keep forever (not recommended)

## UI Settings

```yaml
ui:
  port: 5000                     # Web server port
  host: "127.0.0.1"             # Web server host
  debug: false                   # Debug mode
  video_stream_fps: 15          # Video stream frame rate
```

### Port and Host
- Port: 1024-65535 (use 5000-9999 for safety)
- Host: 
  - `127.0.0.1` = localhost only (secure)
  - `0.0.0.0` = all interfaces (allows network access)

### Debug Mode
- `true`: Enable Flask debug mode (development only)
- `false`: Production mode (recommended)

### Video Stream FPS
- Frame rate for web video streams
- Lower = better network performance
- Higher = smoother video
- Recommended: 10-20 FPS

## System Settings

```yaml
system:
  max_threads: 4                 # Maximum processing threads
  log_level: "INFO"              # Logging verbosity
  log_file: "logs/system.log"    # Log file path
```

### Log Levels
- `DEBUG`: Verbose, all details
- `INFO`: Normal operation messages
- `WARNING`: Warnings only
- `ERROR`: Errors only

### Max Threads
- Number of concurrent processing threads
- Higher = better performance, more CPU usage
- Recommended: Number of CPU cores

## Example Configurations

### Simple USB Camera Setup
```yaml
cameras:
  - id: 1
    name: "Office Camera"
    source: 0
    enabled: true

detection:
  method: "person"  # Faster than face
  confidence_threshold: 0.6

tracking:
  absence_timeout: 600  # 10 minutes
```

### Multiple IP Cameras with Face Recognition
```yaml
cameras:
  - id: 1
    name: "Main Entrance"
    source: "rtsp://admin:pass@192.168.1.100:554/stream"
    enabled: true
  - id: 2
    name: "Back Entrance"
    source: "rtsp://admin:pass@192.168.1.101:554/stream"
    enabled: true

detection:
  method: "face"
  face_recognition_enabled: true
  face_recognition_tolerance: 0.5  # Stricter matching

tracking:
  absence_timeout: 1800  # 30 minutes
```

### Performance-Optimized Setup
```yaml
detection:
  method: "person"           # Faster than face
  detection_interval: 2      # Skip every other frame
  
ui:
  video_stream_fps: 10       # Lower FPS for bandwidth

system:
  max_threads: 2             # Limit CPU usage
```

## Configuration Best Practices

1. **Start Simple**: Begin with one camera and basic settings
2. **Test Detection**: Verify detection works before enabling recognition
3. **Tune Timeouts**: Adjust `absence_timeout` based on your workflow
4. **Monitor Performance**: Check CPU usage and adjust intervals
5. **Backup Config**: Keep a backup of working configurations
6. **Regular Updates**: Review and optimize settings periodically

## Troubleshooting

**High CPU Usage:**
- Increase `detection_interval`
- Reduce number of cameras
- Use `person` instead of `face` detection
- Lower camera resolution

**False Absences:**
- Increase `presence_buffer`
- Lower `confidence_threshold`
- Adjust camera angles

**Missed Detections:**
- Decrease `detection_interval`
- Lower `confidence_threshold`
- Improve lighting conditions
- Adjust camera positioning

**Too Many Alerts:**
- Increase `absence_timeout`
- Increase `alert_repeat_interval`
- Review employee workflow patterns

---

For more help, see README.md or check logs/system.log
