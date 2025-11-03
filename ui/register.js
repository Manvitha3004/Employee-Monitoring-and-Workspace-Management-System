// Employee Registration with Camera Capture

const API_BASE = 'http://localhost:5000/api';

let videoElement = null;
let canvas = null;
let capturedImageData = null;
let stream = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    videoElement = document.getElementById('videoElement');
    canvas = document.getElementById('canvas');
    
    setupEventListeners();
    checkCameraPermissions();
});

function setupEventListeners() {
    document.getElementById('startCamera').addEventListener('click', startCamera);
    document.getElementById('capturePhoto').addEventListener('click', capturePhoto);
    document.getElementById('retakePhoto').addEventListener('click', retakePhoto);
    document.getElementById('registrationForm').addEventListener('submit', registerEmployee);
    document.getElementById('cancelBtn').addEventListener('click', () => {
        window.location.href = '/';
    });
    
    // Enable register button when photo is captured and form is filled
    document.getElementById('employeeId').addEventListener('input', checkFormReady);
    document.getElementById('employeeName').addEventListener('input', checkFormReady);
}

async function checkCameraPermissions() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        
        if (videoDevices.length === 0) {
            showMessage('No camera detected. Please connect a camera.', 'error');
        }
    } catch (error) {
        console.error('Error checking camera:', error);
    }
}

async function startCamera() {
    try {
        // Check if getUserMedia is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showMessage('Camera API not supported in this browser. Please use Chrome, Edge, or Firefox.', 'error');
            return;
        }
        
        // Stop existing stream if any
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        
        showMessage('Requesting camera access... Please allow when prompted.', 'success');
        
        // Request camera access with fallback options
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: false
            });
        } catch (e) {
            // Fallback to basic video constraints
            console.warn('Detailed constraints failed, trying basic:', e);
            stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });
        }
        
        videoElement.srcObject = stream;
        
        // Wait for video to be ready
        await new Promise((resolve) => {
            videoElement.onloadedmetadata = () => {
                videoElement.play();
                resolve();
            };
        });
        
        // Enable capture button
        document.getElementById('startCamera').disabled = true;
        document.getElementById('capturePhoto').disabled = false;
        
        showMessage('✅ Camera started! Position yourself and click "Capture Photo"', 'success');
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        
        let errorMessage = 'Failed to access camera. ';
        
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            errorMessage += 'Camera permission denied. Please:\n' +
                          '1. Click the camera icon in your browser address bar\n' +
                          '2. Allow camera access for this site\n' +
                          '3. Refresh the page and try again';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            errorMessage += 'No camera found. Please:\n' +
                          '1. Connect a camera or webcam\n' +
                          '2. Ensure drivers are installed\n' +
                          '3. Refresh the page';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            errorMessage += 'Camera is in use by another application. Please:\n' +
                          '1. Close other apps using the camera (Zoom, Teams, Skype)\n' +
                          '2. Refresh the page and try again';
        } else if (error.name === 'OverconstrainedError') {
            errorMessage += 'Camera settings not supported. Try with a different camera.';
        } else if (error.name === 'SecurityError') {
            errorMessage += 'Access blocked for security reasons. Please:\n' +
                          '1. Make sure you\'re accessing via http://127.0.0.1:5000\n' +
                          '2. Check browser security settings\n' +
                          '3. Try a different browser (Chrome or Edge recommended)';
        } else {
            errorMessage += 'Unknown error: ' + error.message;
        }
        
        showMessage(errorMessage, 'error');
        
        // Show troubleshooting tips
        console.log('TROUBLESHOOTING TIPS:');
        console.log('1. Make sure you\'re accessing via http://127.0.0.1:5000 (not http://localhost:5000)');
        console.log('2. Allow camera permissions when prompted');
        console.log('3. Close other applications using the camera');
        console.log('4. Try a different browser (Chrome or Edge work best)');
        console.log('5. Check Windows Privacy Settings → Camera → Allow desktop apps');
    }
}

function capturePhoto() {
    if (!stream) {
        showMessage('Camera not started', 'error');
        return;
    }
    
    // Set canvas size to match video
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    
    // Draw video frame to canvas
    const context = canvas.getContext('2d');
    // Flip the image back (since video is mirrored)
    context.translate(canvas.width, 0);
    context.scale(-1, 1);
    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    
    // Get image data
    capturedImageData = canvas.toDataURL('image/jpeg', 0.9);
    
    // Show preview
    const capturedImage = document.getElementById('capturedImage');
    capturedImage.src = capturedImageData;
    capturedImage.style.display = 'block';
    document.getElementById('previewPlaceholder').style.display = 'none';
    
    // Update buttons
    document.getElementById('capturePhoto').style.display = 'none';
    document.getElementById('retakePhoto').style.display = 'inline-block';
    
    // Stop camera
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        videoElement.srcObject = null;
    }
    
    showMessage('Photo captured! Fill in employee details and register.', 'success');
    checkFormReady();
}

function retakePhoto() {
    // Reset preview
    document.getElementById('capturedImage').style.display = 'none';
    document.getElementById('previewPlaceholder').style.display = 'block';
    capturedImageData = null;
    
    // Reset buttons
    document.getElementById('capturePhoto').style.display = 'inline-block';
    document.getElementById('retakePhoto').style.display = 'none';
    document.getElementById('startCamera').disabled = false;
    document.getElementById('capturePhoto').disabled = true;
    
    checkFormReady();
}

function checkFormReady() {
    const employeeId = document.getElementById('employeeId').value.trim();
    const employeeName = document.getElementById('employeeName').value.trim();
    const registerBtn = document.getElementById('registerBtn');
    
    // Enable register button only if photo captured and required fields filled
    if (capturedImageData && employeeId && employeeName) {
        registerBtn.disabled = false;
    } else {
        registerBtn.disabled = true;
    }
}

async function registerEmployee(event) {
    event.preventDefault();
    
    if (!capturedImageData) {
        showMessage('Please capture a photo first', 'error');
        return;
    }
    
    const employeeId = document.getElementById('employeeId').value.trim();
    const employeeName = document.getElementById('employeeName').value.trim();
    const department = document.getElementById('department').value.trim();
    
    // Disable submit button
    const registerBtn = document.getElementById('registerBtn');
    registerBtn.disabled = true;
    registerBtn.textContent = 'Registering...';
    
    try {
        // Send registration request
        const response = await fetch(`${API_BASE}/employees/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                employee_id: employeeId,
                name: employeeName,
                department: department || null,
                photo_data: capturedImageData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(`✅ Employee ${employeeId} registered successfully!`, 'success');
            
            // Reset form after 2 seconds
            setTimeout(() => {
                if (confirm('Employee registered! Register another employee?')) {
                    window.location.reload();
                } else {
                    window.location.href = '/';
                }
            }, 2000);
            
        } else {
            showMessage(`Failed to register: ${data.error}`, 'error');
            registerBtn.disabled = false;
            registerBtn.textContent = '✅ Register Employee';
        }
        
    } catch (error) {
        console.error('Registration error:', error);
        showMessage(`Error: ${error.message}`, 'error');
        registerBtn.disabled = false;
        registerBtn.textContent = '✅ Register Employee';
    }
}

function showMessage(message, type) {
    const statusMessage = document.getElementById('statusMessage');
    // Convert newlines to <br> for better formatting
    const formattedMessage = message.replace(/\n/g, '<br>');
    statusMessage.innerHTML = formattedMessage;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 5000);
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});
