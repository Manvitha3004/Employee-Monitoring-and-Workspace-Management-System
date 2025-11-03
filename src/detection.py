"""
Detection Module
Handles person and face detection in video frames.
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Any, Optional
import pickle

# Try to import face_recognition, but allow system to work without it
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition not available - face recognition features disabled")

logger = logging.getLogger(__name__)


class PersonDetector:
    """Detects persons in video frames using HOG or Haar Cascade."""
    
    def __init__(self):
        """Initialize person detector."""
        # Initialize HOG descriptor for person detection
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Alternatively, use Haar Cascade for upper body
        cascade_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'
        try:
            self.body_cascade = cv2.CascadeClassifier(cascade_path)
        except:
            self.body_cascade = None
            logger.warning("Full body cascade not available")
    
    def detect(self, frame: np.ndarray, confidence: float = 0.5) -> List[Tuple[int, int, int, int]]:
        """
        Detect persons in frame.
        
        Args:
            frame: Input image frame
            confidence: Detection confidence threshold
            
        Returns:
            List of bounding boxes (x, y, width, height)
        """
        try:
            # Resize frame for faster detection
            scale = 0.5
            small_frame = cv2.resize(frame, None, fx=scale, fy=scale)
            
            # Detect using HOG
            boxes, weights = self.hog.detectMultiScale(
                small_frame,
                winStride=(8, 8),
                padding=(4, 4),
                scale=1.05
            )
            
            # Filter by confidence and scale back
            detections = []
            for (x, y, w, h), weight in zip(boxes, weights):
                if weight >= confidence:
                    detections.append((
                        int(x / scale),
                        int(y / scale),
                        int(w / scale),
                        int(h / scale)
                    ))
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in person detection: {e}")
            return []


class FaceDetector:
    """Detects and recognizes faces in video frames."""
    
    def __init__(self, recognition_enabled: bool = True, tolerance: float = 0.6):
        """
        Initialize face detector.
        
        Args:
            recognition_enabled: Enable face recognition
            tolerance: Face recognition tolerance (lower = more strict)
        """
        self.recognition_enabled = recognition_enabled
        self.tolerance = tolerance
        self.known_faces: Dict[str, np.ndarray] = {}
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame using Haar Cascade (faster).
        
        Args:
            frame: Input image frame
            
        Returns:
            List of face bounding boxes (x, y, width, height)
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            return [tuple(f) for f in faces]
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []
    
    def detect_and_recognize(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect and recognize faces in frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of detected faces with recognition info
        """
        if not FACE_RECOGNITION_AVAILABLE:
            logger.warning("Face recognition not available - using basic face detection")
            # Fall back to basic face detection
            faces = self.detect_faces(frame)
            return [{
                'bbox': face,
                'location': None,
                'employee_id': None,
                'encoding': None
            } for face in faces]
        
        try:
            # Convert BGR to RGB for face_recognition library
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect face locations
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            
            if not face_locations:
                return []
            
            results = []
            
            # Get face encodings if recognition is enabled
            if self.recognition_enabled and self.known_faces:
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                    # Try to match face
                    employee_id = self._match_face(encoding)
                    
                    results.append({
                        'bbox': (left, top, right - left, bottom - top),
                        'location': (top, right, bottom, left),
                        'employee_id': employee_id,
                        'encoding': encoding
                    })
            else:
                # Just return locations without recognition
                for (top, right, bottom, left) in face_locations:
                    results.append({
                        'bbox': (left, top, right - left, bottom - top),
                        'location': (top, right, bottom, left),
                        'employee_id': None,
                        'encoding': None
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return []
    
    def _match_face(self, face_encoding: np.ndarray) -> Optional[str]:
        """
        Match face encoding against known faces.
        
        Args:
            face_encoding: Face encoding to match
            
        Returns:
            Employee ID if match found, None otherwise
        """
        if not self.known_faces:
            return None
        
        # Compare against all known faces
        known_ids = list(self.known_faces.keys())
        known_encodings = list(self.known_faces.values())
        
        matches = face_recognition.compare_faces(
            known_encodings,
            face_encoding,
            tolerance=self.tolerance
        )
        
        # Find best match
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return known_ids[best_match_index]
        
        return None
    
    def add_known_face(self, employee_id: str, face_encoding: np.ndarray):
        """
        Add a known face for recognition.
        
        Args:
            employee_id: Employee identifier
            face_encoding: Face encoding vector
        """
        self.known_faces[employee_id] = face_encoding
        logger.info(f"Added face encoding for employee {employee_id}")
    
    def add_known_face_from_image(self, employee_id: str, image_path: str) -> bool:
        """
        Add a known face from image file.
        
        Args:
            employee_id: Employee identifier
            image_path: Path to employee photo
            
        Returns:
            True if successful
        """
        if not FACE_RECOGNITION_AVAILABLE:
            logger.error("Face recognition not available - cannot add face from image")
            return False
        
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                self.add_known_face(employee_id, encodings[0])
                return True
            else:
                logger.warning(f"No face found in image {image_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading face from image: {e}")
            return False
    
    def remove_known_face(self, employee_id: str):
        """Remove a known face."""
        if employee_id in self.known_faces:
            del self.known_faces[employee_id]
            logger.info(f"Removed face encoding for employee {employee_id}")
    
    def load_known_faces(self, database_manager):
        """
        Load known faces from database.
        
        Args:
            database_manager: Database manager instance
        """
        try:
            employees = database_manager.get_all_employees()
            count = 0
            
            for emp in employees:
                if emp.get('face_encoding'):
                    # Deserialize face encoding
                    encoding = pickle.loads(emp['face_encoding'])
                    self.add_known_face(emp['employee_id'], encoding)
                    count += 1
            
            logger.info(f"Loaded {count} known faces from database")
            
        except Exception as e:
            logger.error(f"Error loading known faces: {e}")
    
    def get_face_encoding(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Get face encoding from a specific region.
        
        Args:
            frame: Input image frame
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            Face encoding or None
        """
        if not FACE_RECOGNITION_AVAILABLE:
            logger.error("Face recognition not available")
            return None
        
        try:
            x, y, w, h = bbox
            face_image = frame[y:y+h, x:x+w]
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            encodings = face_recognition.face_encodings(rgb_image)
            if len(encodings) > 0:
                return encodings[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting face encoding: {e}")
            return None


class DetectionManager:
    """Manages detection operations combining person and face detection."""
    
    def __init__(self, method: str = "face", recognition_enabled: bool = True):
        """
        Initialize detection manager.
        
        Args:
            method: Detection method ("face", "person", "both")
            recognition_enabled: Enable face recognition
        """
        self.method = method
        self.person_detector = PersonDetector() if method in ["person", "both"] else None
        self.face_detector = FaceDetector(recognition_enabled) if method in ["face", "both"] else None
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform detection on frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of detections with metadata
        """
        detections = []
        
        if self.method == "face" and self.face_detector:
            # Face detection and recognition
            faces = self.face_detector.detect_and_recognize(frame)
            for face in faces:
                detections.append({
                    'type': 'face',
                    'bbox': face['bbox'],
                    'employee_id': face['employee_id'],
                    'encoding': face['encoding']
                })
        
        elif self.method == "person" and self.person_detector:
            # Person detection only
            persons = self.person_detector.detect(frame)
            for bbox in persons:
                detections.append({
                    'type': 'person',
                    'bbox': bbox,
                    'employee_id': None,
                    'encoding': None
                })
        
        elif self.method == "both":
            # Both detections
            if self.face_detector:
                faces = self.face_detector.detect_and_recognize(frame)
                for face in faces:
                    detections.append({
                        'type': 'face',
                        'bbox': face['bbox'],
                        'employee_id': face['employee_id'],
                        'encoding': face['encoding']
                    })
            
            if self.person_detector:
                persons = self.person_detector.detect(frame)
                for bbox in persons:
                    # Check if not already detected as face
                    overlap = any(self._bbox_overlap(bbox, d['bbox']) > 0.5 
                                for d in detections if d['type'] == 'face')
                    if not overlap:
                        detections.append({
                            'type': 'person',
                            'bbox': bbox,
                            'employee_id': None,
                            'encoding': None
                        })
        
        return detections
    
    def _bbox_overlap(self, bbox1: Tuple[int, int, int, int], 
                     bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate IoU (Intersection over Union) between two bounding boxes."""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw detection boxes and labels on frame.
        
        Args:
            frame: Input image frame
            detections: List of detections
            
        Returns:
            Frame with drawn detections
        """
        output = frame.copy()
        
        for det in detections:
            x, y, w, h = det['bbox']
            employee_id = det.get('employee_id')
            det_type = det.get('type', 'unknown')
            
            # Choose color based on detection type and recognition
            if employee_id:
                color = (0, 255, 0)  # Green for recognized
                label = f"{employee_id}"
            elif det_type == 'face':
                color = (0, 255, 255)  # Yellow for unrecognized face
                label = "Unknown"
            else:
                color = (255, 0, 0)  # Blue for person
                label = "Person"
            
            # Draw rectangle
            cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
            
            # Draw label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(output, (x, y - 25), (x + label_size[0], y), color, -1)
            
            # Draw label text
            cv2.putText(output, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        return output
