"""
System Controller
Main controller that coordinates all system components.
"""

import logging
import threading
import time
from typing import Dict, List, Optional
import cv2
import numpy as np

from .config_manager import ConfigManager
from .database import DatabaseManager
from .video_capture import VideoCaptureManager
from .detection import DetectionManager
from .tracking import EmployeeTracker
from .alerts import AlertManager


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemController:
    """Main system controller coordinating all components."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize system controller.
        
        Args:
            config_path: Path to configuration file
        """
        logger.info("Initializing Employee Monitoring System...")
        
        # Initialize components
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(self.config.get('database.path', 'data/employees.db'))
        self.video_manager = VideoCaptureManager()
        self.alert_manager = AlertManager(self.config)
        self.tracker = EmployeeTracker(self.db, self.config, self.alert_manager)
        
        # Initialize detection manager
        detection_method = self.config.get_detection_method()
        recognition_enabled = self.config.get('detection.face_recognition_enabled', True)
        self.detection_manager = DetectionManager(detection_method, recognition_enabled)
        
        # Load known faces if recognition is enabled
        if recognition_enabled and self.detection_manager.face_detector:
            self.detection_manager.face_detector.load_known_faces(self.db)
        
        # Processing state
        self.running = False
        self.processing_thread = None
        self.detection_interval = self.config.get('detection.detection_interval', 1)
        self.frame_counter = 0
        
        logger.info("System initialized successfully")
    
    def start(self):
        """Start the monitoring system."""
        logger.info("Starting employee monitoring system...")
        
        # ✅ START CAMERAS for live monitoring feed
        self._initialize_cameras()
        
        # Start tracking
        self.tracker.start_monitoring()
        
        # Start processing
        self.running = True
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        
        logger.info("System started successfully with live camera feed")
        self.db.log_system_event('system_start', 'Monitoring system started with cameras')
    
    def stop(self):
        """Stop the monitoring system."""
        logger.info("Stopping employee monitoring system...")
        
        self.running = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=3.0)
        
        self.tracker.stop_monitoring()
        self.video_manager.stop_all()
        
        logger.info("System stopped")
        self.db.log_system_event('system_stop', 'Monitoring system stopped')
    
    def start_cameras(self):
        """Manually start cameras for monitoring (separate from system start)."""
        logger.info("Starting cameras for monitoring...")
        self._initialize_cameras()
    
    def _initialize_cameras(self):
        """Initialize all configured cameras."""
        cameras = self.config.get_enabled_cameras()
        
        for camera_config in cameras:
            camera_id = camera_config['id']
            source = camera_config['source']
            name = camera_config['name']
            
            success = self.video_manager.add_camera(camera_id, source, name)
            if success:
                logger.info(f"Camera '{name}' initialized successfully")
            else:
                logger.error(f"Failed to initialize camera '{name}'")
    
    def _processing_loop(self):
        """Main processing loop for detection and tracking."""
        while self.running:
            try:
                # Get frames from all cameras
                frames = self.video_manager.get_all_frames()
                
                # Process each frame
                for camera_id, frame in frames.items():
                    # Apply detection interval
                    if self.frame_counter % self.detection_interval == 0:
                        self._process_frame(camera_id, frame)
                
                self.frame_counter += 1
                
                # Small delay to prevent CPU overload
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(0.1)
    
    def _process_frame(self, camera_id: int, frame: np.ndarray):
        """
        Process a single frame for detection.
        
        Args:
            camera_id: Camera identifier
            frame: Video frame
        """
        try:
            # Perform detection
            detections = self.detection_manager.detect(frame)
            
            # Update tracking for detected employees
            for detection in detections:
                employee_id = detection.get('employee_id')
                
                if employee_id:
                    # Known employee detected
                    self.tracker.update_detection(employee_id, camera_id)
                else:
                    # Unknown person detected - could implement enrollment here
                    pass
                    
        except Exception as e:
            logger.error(f"Error processing frame from camera {camera_id}: {e}")
    
    def get_live_frame(self, camera_id: int, with_detections: bool = True) -> Optional[np.ndarray]:
        """
        Get live frame from camera with optional detection overlay.
        
        Args:
            camera_id: Camera identifier
            with_detections: Whether to draw detections on frame
            
        Returns:
            Frame or None
        """
        ret, frame = self.video_manager.get_frame(camera_id)
        
        if not ret or frame is None:
            return None
        
        if with_detections:
            # Perform detection
            detections = self.detection_manager.detect(frame)
            # Draw detections
            frame = self.detection_manager.draw_detections(frame, detections)
        
        return frame
    
    def get_system_status(self) -> Dict[str, any]:
        """Get overall system status."""
        return {
            'running': self.running,
            'cameras': {
                'total': len(self.video_manager.cameras),
                'active': self.video_manager.get_active_camera_count(),
                'cameras': self.video_manager.get_all_cameras_info()
            },
            'employees': {
                'present': len(self.tracker.get_present_employees()),
                'absent_on_timer': len(self.tracker.get_absent_employees())
            },
            'database': {
                'current_occupancy': self.db.get_current_occupancy()
            },
            'alerts': self.alert_manager.get_alert_status()
        }
    
    def add_camera(self, camera_id: int, source, name: str) -> bool:
        """Add a new camera at runtime."""
        return self.video_manager.add_camera(camera_id, source, name)
    
    def remove_camera(self, camera_id: int):
        """Remove a camera at runtime."""
        self.video_manager.remove_camera(camera_id)
    
    def register_employee(self, employee_id: str, name: str, image_path: str = None, department: str = None) -> bool:
        """
        Register a new employee.
        
        Args:
            employee_id: Employee identifier
            name: Employee name
            image_path: Path to employee photo (optional)
            department: Employee department (optional)
            
        Returns:
            True if successful
        """
        try:
            # Add employee to database
            if image_path and self.detection_manager.face_detector:
                # Load face encoding from image
                success = self.detection_manager.face_detector.add_known_face_from_image(
                    employee_id, image_path
                )
                
                if success:
                    # Get encoding to store in database
                    encoding = self.detection_manager.face_detector.known_faces[employee_id]
                    self.tracker.register_employee_encoding(employee_id, encoding, name, department)
                    logger.info(f"Employee {employee_id} registered with face recognition")
                    return True
                else:
                    logger.error(f"Failed to extract face from image for {employee_id}")
                    return False
            else:
                # Register without face recognition
                self.db.add_employee(employee_id, name, department=department)
                logger.info(f"Employee {employee_id} registered without face recognition")
                return True
                
        except Exception as e:
            logger.error(f"Error registering employee: {e}")
            return False
    
    def get_employee_list(self) -> List[Dict[str, any]]:
        """Get list of all employees."""
        return self.db.get_all_employees()
    
    def get_presence_logs(self, **kwargs) -> List[Dict[str, any]]:
        """Get presence logs with optional filters."""
        return self.db.get_presence_logs(**kwargs)
    
    def get_alerts(self, unacknowledged_only: bool = False) -> List[Dict[str, any]]:
        """Get alerts."""
        if unacknowledged_only:
            return self.db.get_unacknowledged_alerts()
        else:
            return self.db.get_recent_alerts()
    
    def acknowledge_alert(self, alert_id: int):
        """Acknowledge an alert."""
        self.db.acknowledge_alert(alert_id)
    
    def get_employee_status(self, employee_id: str = None) -> any:
        """Get employee status."""
        if employee_id:
            return self.tracker.get_employee_status(employee_id)
        else:
            return self.tracker.get_all_statuses()
