"""
Video Capture Manager
Handles video capture from multiple USB and IP cameras.
"""

import cv2
import threading
import queue
import time
import logging
from typing import Dict, Optional, Tuple, List
import numpy as np


logger = logging.getLogger(__name__)


class CameraStream:
    """Manages a single camera stream."""
    
    def __init__(self, camera_id: int, source, name: str = "Camera"):
        """
        Initialize camera stream.
        
        Args:
            camera_id: Unique camera identifier
            source: Camera source (int for USB, string for RTSP URL)
            name: Camera name for display
        """
        self.camera_id = camera_id
        self.source = source
        self.name = name
        self.capture = None
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = False
        self.thread = None
        self.last_frame = None
        self.last_frame_time = None
        self.connection_error = False
        
    def start(self) -> bool:
        """
        Start camera capture.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.capture = cv2.VideoCapture(self.source)
            
            # Set camera properties for better performance
            if isinstance(self.source, int):
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.capture.isOpened():
                logger.error(f"Failed to open camera {self.name} (source: {self.source})")
                return False
            
            self.running = True
            self.connection_error = False
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"Camera {self.name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera {self.name}: {e}")
            return False
    
    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        consecutive_failures = 0
        max_failures = 10
        
        while self.running:
            try:
                ret, frame = self.capture.read()
                
                if ret:
                    consecutive_failures = 0
                    self.connection_error = False
                    self.last_frame = frame.copy()
                    self.last_frame_time = time.time()
                    
                    # Update queue (remove old frame if full)
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                    
                    self.frame_queue.put(frame)
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        logger.warning(f"Camera {self.name} disconnected")
                        self.connection_error = True
                        time.sleep(5)  # Wait before retry
                        consecutive_failures = 0
                        # Try to reconnect
                        self._reconnect()
                    else:
                        time.sleep(0.1)
                        
            except Exception as e:
                logger.error(f"Error in capture loop for {self.name}: {e}")
                time.sleep(1)
    
    def _reconnect(self):
        """Attempt to reconnect to camera."""
        try:
            if self.capture:
                self.capture.release()
            
            self.capture = cv2.VideoCapture(self.source)
            
            if self.capture.isOpened():
                logger.info(f"Camera {self.name} reconnected")
                self.connection_error = False
            else:
                logger.warning(f"Failed to reconnect camera {self.name}")
                
        except Exception as e:
            logger.error(f"Error reconnecting camera {self.name}: {e}")
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read latest frame from camera.
        
        Returns:
            Tuple of (success, frame)
        """
        try:
            if not self.running or self.connection_error:
                return False, None
            
            # Try to get latest frame from queue
            try:
                frame = self.frame_queue.get(timeout=1.0)
                return True, frame
            except queue.Empty:
                # Return last known frame if queue is empty
                if self.last_frame is not None:
                    return True, self.last_frame.copy()
                return False, None
                
        except Exception as e:
            logger.error(f"Error reading frame from {self.name}: {e}")
            return False, None
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the most recent frame without blocking."""
        if self.last_frame is not None:
            return self.last_frame.copy()
        return None
    
    def stop(self):
        """Stop camera capture."""
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.capture:
            self.capture.release()
        
        logger.info(f"Camera {self.name} stopped")
    
    def is_active(self) -> bool:
        """Check if camera is active and working."""
        return self.running and not self.connection_error
    
    def get_properties(self) -> Dict[str, any]:
        """Get camera properties."""
        if not self.capture or not self.capture.isOpened():
            return {}
        
        return {
            'width': int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.capture.get(cv2.CAP_PROP_FPS)),
            'backend': self.capture.getBackendName()
        }


class VideoCaptureManager:
    """Manages multiple camera streams."""
    
    def __init__(self):
        """Initialize video capture manager."""
        self.cameras: Dict[int, CameraStream] = {}
        self.lock = threading.Lock()
        
    def add_camera(self, camera_id: int, source, name: str = None) -> bool:
        """
        Add and start a new camera.
        
        Args:
            camera_id: Unique camera identifier
            source: Camera source (int for USB, URL for IP camera)
            name: Camera name
            
        Returns:
            True if successful
        """
        with self.lock:
            if camera_id in self.cameras:
                logger.warning(f"Camera {camera_id} already exists")
                return False
            
            camera_name = name or f"Camera {camera_id}"
            camera = CameraStream(camera_id, source, camera_name)
            
            if camera.start():
                self.cameras[camera_id] = camera
                return True
            else:
                return False
    
    def remove_camera(self, camera_id: int):
        """Remove and stop a camera."""
        with self.lock:
            if camera_id in self.cameras:
                self.cameras[camera_id].stop()
                del self.cameras[camera_id]
                logger.info(f"Camera {camera_id} removed")
    
    def get_frame(self, camera_id: int) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Get latest frame from specific camera.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Tuple of (success, frame)
        """
        with self.lock:
            camera = self.cameras.get(camera_id)
            if camera:
                return camera.read()
            return False, None
    
    def get_all_frames(self) -> Dict[int, np.ndarray]:
        """
        Get latest frames from all active cameras.
        
        Returns:
            Dictionary mapping camera_id to frame
        """
        frames = {}
        with self.lock:
            for camera_id, camera in self.cameras.items():
                ret, frame = camera.read()
                if ret and frame is not None:
                    frames[camera_id] = frame
        return frames
    
    def get_camera_info(self, camera_id: int) -> Optional[Dict[str, any]]:
        """Get information about a specific camera."""
        with self.lock:
            camera = self.cameras.get(camera_id)
            if camera:
                return {
                    'id': camera.camera_id,
                    'name': camera.name,
                    'source': str(camera.source),
                    'active': camera.is_active(),
                    'error': camera.connection_error,
                    'properties': camera.get_properties()
                }
            return None
    
    def get_all_cameras_info(self) -> List[Dict[str, any]]:
        """Get information about all cameras."""
        with self.lock:
            return [self.get_camera_info(cam_id) for cam_id in self.cameras.keys()]
    
    def stop_all(self):
        """Stop all cameras."""
        with self.lock:
            for camera in self.cameras.values():
                camera.stop()
            self.cameras.clear()
            logger.info("All cameras stopped")
    
    def restart_camera(self, camera_id: int) -> bool:
        """Restart a specific camera."""
        with self.lock:
            camera = self.cameras.get(camera_id)
            if camera:
                source = camera.source
                name = camera.name
                camera.stop()
                del self.cameras[camera_id]
                
                # Small delay before restart
                time.sleep(0.5)
                
                return self.add_camera(camera_id, source, name)
            return False
    
    def get_active_camera_count(self) -> int:
        """Get count of active cameras."""
        with self.lock:
            return sum(1 for cam in self.cameras.values() if cam.is_active())
