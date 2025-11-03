"""
Flask REST API Server
Provides HTTP API for accessing system functionality.
"""

from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import cv2
import logging
import os
from datetime import datetime

from .controller import SystemController


logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class APIServer:
    """Flask API server for the monitoring system."""
    
    def __init__(self, controller: SystemController, config_manager):
        """
        Initialize API server.
        
        Args:
            controller: System controller instance
            config_manager: Configuration manager
        """
        self.controller = controller
        self.config = config_manager
        
        self.app = Flask(__name__)
        CORS(self.app)
        
        self._setup_routes()
        
        # Server configuration
        self.host = config_manager.get('ui.host', '127.0.0.1')
        self.port = config_manager.get('ui.port', 5000)
        self.debug = config_manager.get('ui.debug', False)
    
    def _setup_routes(self):
        """Setup API routes."""
        
        # System routes
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get system status."""
            try:
                status = self.controller.get_system_status()
                return jsonify({'success': True, 'data': status})
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/start', methods=['POST'])
        def start_system():
            """Start monitoring system."""
            try:
                if not self.controller.running:
                    self.controller.start()
                return jsonify({'success': True, 'message': 'System started'})
            except Exception as e:
                logger.error(f"Error starting system: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_system():
            """Stop monitoring system."""
            try:
                if self.controller.running:
                    self.controller.stop()
                return jsonify({'success': True, 'message': 'System stopped'})
            except Exception as e:
                logger.error(f"Error stopping system: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # Camera routes
        @self.app.route('/api/cameras', methods=['GET'])
        def get_cameras():
            """Get all cameras."""
            try:
                cameras = self.controller.video_manager.get_all_cameras_info()
                return jsonify({'success': True, 'data': cameras})
            except Exception as e:
                logger.error(f"Error getting cameras: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/cameras/<int:camera_id>/stream', methods=['GET'])
        def get_camera_stream(camera_id):
            """Get camera video stream."""
            def generate():
                while True:
                    frame = self.controller.get_live_frame(camera_id, with_detections=True)
                    
                    if frame is None:
                        break
                    
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if not ret:
                        break
                    
                    # Yield frame in multipart format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @self.app.route('/api/cameras/<int:camera_id>/snapshot', methods=['GET'])
        def get_camera_snapshot(camera_id):
            """Get single frame snapshot from camera."""
            try:
                frame = self.controller.get_live_frame(camera_id, with_detections=True)
                
                if frame is None:
                    return jsonify({'success': False, 'error': 'Camera not available'}), 404
                
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    return jsonify({'success': False, 'error': 'Failed to encode frame'}), 500
                
                return Response(buffer.tobytes(), mimetype='image/jpeg')
                
            except Exception as e:
                logger.error(f"Error getting snapshot: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # Employee routes
        @self.app.route('/api/employees', methods=['GET'])
        def get_employees():
            """Get all employees."""
            try:
                employees = self.controller.get_employee_list()
                # Remove face encoding from response (too large)
                for emp in employees:
                    emp.pop('face_encoding', None)
                return jsonify({'success': True, 'data': employees})
            except Exception as e:
                logger.error(f"Error getting employees: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/employees', methods=['POST'])
        def add_employee():
            """Add new employee."""
            try:
                data = request.get_json()
                employee_id = data.get('employee_id')
                name = data.get('name')
                image_path = data.get('image_path')
                
                if not employee_id or not name:
                    return jsonify({'success': False, 'error': 'Missing required fields'}), 400
                
                success = self.controller.register_employee(employee_id, name, image_path)
                
                if success:
                    return jsonify({'success': True, 'message': 'Employee registered'})
                else:
                    return jsonify({'success': False, 'error': 'Failed to register employee'}), 500
                    
            except Exception as e:
                logger.error(f"Error adding employee: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/employees/register', methods=['POST'])
        def register_employee_with_photo():
            """Register employee with captured photo."""
            try:
                import base64
                import numpy as np
                
                data = request.get_json()
                employee_id = data.get('employee_id')
                name = data.get('name')
                department = data.get('department', '')
                photo_data = data.get('photo_data')  # Base64 encoded image
                
                if not employee_id or not name or not photo_data:
                    return jsonify({'success': False, 'error': 'Missing required fields'}), 400
                
                # Decode base64 image
                try:
                    # Remove data URL prefix if present
                    if ',' in photo_data:
                        photo_data = photo_data.split(',')[1]
                    
                    # Decode base64
                    image_bytes = base64.b64decode(photo_data)
                    
                    # Convert to numpy array
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if image is None:
                        return jsonify({'success': False, 'error': 'Invalid image data'}), 400
                    
                    # Save image to employee_photos directory
                    photos_dir = os.path.join(PROJECT_ROOT, 'data', 'employee_photos')
                    os.makedirs(photos_dir, exist_ok=True)
                    
                    image_filename = f"{employee_id}.jpg"
                    image_path = os.path.join(photos_dir, image_filename)
                    
                    # Save image
                    cv2.imwrite(image_path, image)
                    logger.info(f"Saved employee photo: {image_path}")
                    
                except Exception as e:
                    logger.error(f"Error processing image: {e}")
                    return jsonify({'success': False, 'error': 'Failed to process image'}), 400
                
                # Register employee with the saved image
                success = self.controller.register_employee(employee_id, name, image_path, department)
                
                if success:
                    return jsonify({
                        'success': True, 
                        'message': f'Employee {employee_id} registered successfully',
                        'data': {
                            'employee_id': employee_id,
                            'name': name,
                            'department': department
                        }
                    })
                else:
                    # Clean up saved image if registration failed
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    return jsonify({'success': False, 'error': 'Failed to register employee'}), 500
                    
            except Exception as e:
                logger.error(f"Error registering employee: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/employees/<employee_id>/status', methods=['GET'])
        def get_employee_status(employee_id):
            """Get employee status."""
            try:
                status = self.controller.get_employee_status(employee_id)
                if status:
                    return jsonify({'success': True, 'data': status})
                else:
                    return jsonify({'success': False, 'error': 'Employee not found'}), 404
            except Exception as e:
                logger.error(f"Error getting employee status: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/detect', methods=['POST'])
        def detect_frame():
            """Process frame from browser for detection."""
            try:
                import base64
                import numpy as np
                
                data = request.get_json()
                image_data = data.get('image')
                camera_id = data.get('camera_id', 1)
                
                if not image_data:
                    return jsonify({'success': False, 'error': 'No image provided'}), 400
                
                # Decode base64 image
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    return jsonify({'success': False, 'error': 'Invalid image'}), 400
                
                # Perform detection
                detections = self.controller.detection_manager.detect(frame)
                
                # Format detections for browser
                formatted_detections = []
                detected_employees = []
                
                for detection in detections:
                    bbox = detection.get('bbox', {})
                    formatted_detections.append({
                        'bbox': {
                            'x': bbox.get('x', 0),
                            'y': bbox.get('y', 0),
                            'width': bbox.get('width', 0),
                            'height': bbox.get('height', 0)
                        },
                        'confidence': detection.get('confidence', 0),
                        'label': detection.get('label', 'Person')
                    })
                    
                    # Check if this is a known employee
                    employee_id = detection.get('employee_id')
                    if employee_id:
                        employee = self.controller.db.get_employee(employee_id)
                        if employee:
                            detected_employees.append({
                                'employee_id': employee_id,
                                'name': employee['name']
                            })
                
                return jsonify({
                    'success': True,
                    'data': {
                        'detections': formatted_detections,
                        'employees': detected_employees,
                        'count': len(formatted_detections)
                    }
                })
                
            except Exception as e:
                logger.error(f"Error in detection: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/presence/update', methods=['POST'])
        def update_presence():
            """Update employee presence from browser detection."""
            try:
                data = request.get_json()
                employee_id = data.get('employee_id')
                camera_id = data.get('camera_id', 1)
                
                if not employee_id:
                    return jsonify({'success': False, 'error': 'Missing employee_id'}), 400
                
                # Update tracking
                self.controller.tracker.update_detection(employee_id, camera_id)
                
                return jsonify({'success': True, 'message': 'Presence updated'})
                
            except Exception as e:
                logger.error(f"Error updating presence: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/employees/status', methods=['GET'])
        def get_all_employee_status():
            """Get status of all employees."""
            try:
                statuses = self.controller.get_employee_status()
                return jsonify({'success': True, 'data': statuses})
            except Exception as e:
                logger.error(f"Error getting employee statuses: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # Presence logs routes
        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            """Get presence logs."""
            try:
                employee_id = request.args.get('employee_id')
                limit = int(request.args.get('limit', 100))
                
                kwargs = {'limit': limit}
                if employee_id:
                    kwargs['employee_id'] = employee_id
                
                logs = self.controller.get_presence_logs(**kwargs)
                return jsonify({'success': True, 'data': logs})
            except Exception as e:
                logger.error(f"Error getting logs: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # Alert routes
        @self.app.route('/api/alerts', methods=['GET'])
        def get_alerts():
            """Get alerts."""
            try:
                unacknowledged_only = request.args.get('unacknowledged', 'false').lower() == 'true'
                alerts = self.controller.get_alerts(unacknowledged_only)
                return jsonify({'success': True, 'data': alerts})
            except Exception as e:
                logger.error(f"Error getting alerts: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
        def acknowledge_alert(alert_id):
            """Acknowledge an alert."""
            try:
                self.controller.acknowledge_alert(alert_id)
                return jsonify({'success': True, 'message': 'Alert acknowledged'})
            except Exception as e:
                logger.error(f"Error acknowledging alert: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # Serve static files (UI)
        @self.app.route('/')
        def index():
            """Serve main UI page."""
            ui_dir = os.path.join(PROJECT_ROOT, 'ui')
            return send_from_directory(ui_dir, 'index.html')
        
        @self.app.route('/<path:path>')
        def serve_static(path):
            """Serve static files."""
            ui_dir = os.path.join(PROJECT_ROOT, 'ui')
            return send_from_directory(ui_dir, path)
    
    def run(self):
        """Run the Flask server."""
        logger.info(f"Starting API server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=self.debug, threaded=True)
