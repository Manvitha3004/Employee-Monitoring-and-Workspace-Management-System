// Live Camera Monitoring - Browser-based
// Uses getUserMedia API for camera access

const API_BASE = 'http://localhost:5000/api';

let videoStream = null;
let detectionEnabled = false;
let detectionInterval = null;
let frameCount = 0;
let lastFpsUpdate = Date.now();
let currentFps = 0;

// DOM Elements
const video = document.getElementById('video-feed');
const canvas = document.getElementById('detection-overlay');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('start-camera');
const stopBtn = document.getElementById('stop-camera');
const toggleDetectionBtn = document.getElementById('toggle-detection');
const offlineMsg = document.getElementById('camera-offline');
const messageArea = document.getElementById('message-area');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkSystemStatus();
});

function setupEventListeners() {
    startBtn.addEventListener('click', startCamera);
    stopBtn.addEventListener('click', stopCamera);
    toggleDetectionBtn.addEventListener('click', toggleDetection);
    
    // Update canvas size when video loads
    video.addEventListener('loadedmetadata', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    });
}

// Camera Control
async function startCamera() {
    try {
        showMessage('Requesting camera access...', 'info');
        
        // Request camera access
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        });
        
        // Set video source
        video.srcObject = videoStream;
        
        // Update UI
        offlineMsg.style.display = 'none';
        video.style.display = 'block';
        startBtn.disabled = true;
        stopBtn.disabled = false;
        toggleDetectionBtn.disabled = false;
        
        document.getElementById('camera-status').textContent = 'Online';
        document.getElementById('camera-status').style.color = '#4CAF50';
        
        showMessage('Camera started successfully! ✅', 'success');
        
        // Start FPS counter
        startFpsCounter();
        
    } catch (error) {
        console.error('Camera error:', error);
        
        let errorMsg = 'Failed to access camera. ';
        if (error.name === 'NotAllowedError') {
            errorMsg += 'Permission denied. Please allow camera access.';
        } else if (error.name === 'NotFoundError') {
            errorMsg += 'No camera found.';
        } else if (error.name === 'NotReadableError') {
            errorMsg += 'Camera is in use by another application.';
        } else {
            errorMsg += error.message;
        }
        
        showMessage(errorMsg, 'error');
    }
}

function stopCamera() {
    if (videoStream) {
        // Stop all tracks
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
        video.srcObject = null;
    }
    
    // Stop detection
    if (detectionEnabled) {
        toggleDetection();
    }
    
    // Update UI
    offlineMsg.style.display = 'block';
    video.style.display = 'none';
    startBtn.disabled = false;
    stopBtn.disabled = true;
    toggleDetectionBtn.disabled = true;
    
    document.getElementById('camera-status').textContent = 'Offline';
    document.getElementById('camera-status').style.color = '#999';
    document.getElementById('fps-display').textContent = '0 FPS';
    
    clearCanvas();
    showMessage('Camera stopped', 'info');
}

// Detection Control
function toggleDetection() {
    detectionEnabled = !detectionEnabled;
    
    if (detectionEnabled) {
        toggleDetectionBtn.textContent = '🔴 Disable Detection';
        toggleDetectionBtn.className = 'btn btn-secondary';
        document.getElementById('detection-status').textContent = 'ON';
        document.getElementById('detection-status').style.color = '#4CAF50';
        
        // Start detection loop
        detectionInterval = setInterval(processFrame, 100); // 10 FPS detection
        showMessage('Detection enabled - Analyzing frames...', 'success');
    } else {
        toggleDetectionBtn.textContent = '🔍 Enable Detection';
        toggleDetectionBtn.className = 'btn btn-success';
        document.getElementById('detection-status').textContent = 'OFF';
        document.getElementById('detection-status').style.color = '#999';
        
        // Stop detection loop
        if (detectionInterval) {
            clearInterval(detectionInterval);
            detectionInterval = null;
        }
        
        clearCanvas();
        document.getElementById('people-count').textContent = '0';
        document.getElementById('employee-list').innerHTML = '<span style="color: #999;">Detection disabled</span>';
        showMessage('Detection disabled', 'info');
    }
}

// Frame Processing
async function processFrame() {
    if (!video.videoWidth || !video.videoHeight) return;
    
    try {
        // Capture frame from video
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = video.videoWidth;
        tempCanvas.height = video.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(video, 0, 0);
        
        // Convert to base64
        const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);
        
        // Send to backend for detection
        const response = await fetch(API_BASE + '/detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData,
                camera_id: 1
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            if (result.success) {
                updateDetections(result.data);
            }
        }
    } catch (error) {
        console.error('Detection error:', error);
    }
}

function updateDetections(data) {
    clearCanvas();
    
    const detections = data.detections || [];
    const employees = data.employees || [];
    
    // Update count
    document.getElementById('people-count').textContent = detections.length;
    
    // Draw bounding boxes
    detections.forEach(detection => {
        const { bbox, confidence, label } = detection;
        
        // Draw rectangle
        ctx.strokeStyle = '#4CAF50';
        ctx.lineWidth = 3;
        ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);
        
        // Draw label background
        ctx.fillStyle = '#4CAF50';
        ctx.fillRect(bbox.x, bbox.y - 25, bbox.width, 25);
        
        // Draw label text
        ctx.fillStyle = 'white';
        ctx.font = '16px Arial';
        ctx.fillText(`${label} (${(confidence * 100).toFixed(0)}%)`, bbox.x + 5, bbox.y - 8);
    });
    
    // Update employee list
    if (employees.length > 0) {
        const employeeHTML = employees.map(emp => 
            `<span class="employee-tag">${emp.name} (${emp.employee_id})</span>`
        ).join('');
        document.getElementById('employee-list').innerHTML = employeeHTML;
        
        // Update tracking in backend
        employees.forEach(emp => {
            updateEmployeePresence(emp.employee_id);
        });
    } else {
        document.getElementById('employee-list').innerHTML = detections.length > 0 
            ? '<span style="color: #999;">Unknown persons detected</span>'
            : '<span style="color: #999;">No people detected</span>';
    }
}

async function updateEmployeePresence(employeeId) {
    try {
        await fetch(API_BASE + '/presence/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                employee_id: employeeId,
                camera_id: 1
            })
        });
    } catch (error) {
        console.error('Error updating presence:', error);
    }
}

// Utility Functions
function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function startFpsCounter() {
    setInterval(() => {
        const now = Date.now();
        const elapsed = (now - lastFpsUpdate) / 1000;
        currentFps = (frameCount / elapsed).toFixed(1);
        
        document.getElementById('fps-display').textContent = currentFps + ' FPS';
        
        frameCount = 0;
        lastFpsUpdate = now;
    }, 1000);
    
    // Count frames
    function countFrame() {
        if (videoStream) {
            frameCount++;
            requestAnimationFrame(countFrame);
        }
    }
    countFrame();
}

function showMessage(text, type) {
    const msgClass = type === 'error' ? 'error-message' : 
                     type === 'success' ? 'success-message' : 
                     'info-message';
    
    messageArea.innerHTML = `<div class="${msgClass}">${text}</div>`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageArea.innerHTML = '';
    }, 5000);
}

async function checkSystemStatus() {
    try {
        const response = await fetch(API_BASE + '/status');
        const data = await response.json();
        
        if (!data.success || !data.data.running) {
            showMessage('⚠️ System is offline. Start the system from the dashboard first.', 'error');
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}
