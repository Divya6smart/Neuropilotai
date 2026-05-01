const micBtn = document.getElementById('mic-btn');
const statusText = document.getElementById('status-text');
const statusDot = document.getElementById('status-dot');
const logContainer = document.getElementById('log-container');
const visualizer = document.getElementById('visualizer');

let recognition;
let isListening = false;

// Initialize Web Speech API
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isListening = true;
        micBtn.classList.add('listening');
        statusText.innerText = 'Listening...';
        statusDot.style.backgroundColor = '#00ff88';
        statusDot.style.boxShadow = '0 0 10px #00ff88';
    };

    recognition.onend = () => {
        isListening = false;
        micBtn.classList.remove('listening');
        statusText.innerText = 'System Online';
        // Auto restart if it was continuous
        if (isListening) recognition.start();
    };

    recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim();
        console.log('Transcript:', transcript);
        
        // Wake word detection
        if (transcript.toLowerCase().includes('voxos') || transcript.toLowerCase().includes('jarvis')) {
            addLog('Voice Input', transcript);
            sendCommand(transcript);
        } else {
            console.log('No wake word detected in:', transcript);
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        statusText.innerText = 'Error: ' + event.error;
        statusDot.style.backgroundColor = '#ff4b2b';
        statusDot.style.boxShadow = '0 0 10px #ff4b2b';
    };
} else {
    alert('Web Speech API is not supported in this browser. Please use Chrome.');
}

micBtn.addEventListener('click', () => {
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
});

// Initialize WebSocket for real-time updates
const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'status') {
        statusText.innerText = data.message;
    } else if (data.type === 'execution') {
        addLog('Execution', data.message);
    } else if (data.type === 'tasks') {
        data.data.forEach(task => {
            addLog('Parsed Task', `${task.action}: ${task.params}`);
        });
    }
};

ws.onopen = () => {
    console.log('WebSocket connected');
};

ws.onclose = () => {
    console.log('WebSocket disconnected');
};

async function sendCommand(text) {
    statusText.innerText = 'Executing...';
    // The logs and status will be updated via WebSocket broadcast from the backend
    try {
        await fetch('/voice-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
    } catch (error) {
        console.error('API Error:', error);
        addLog('Error', 'Connection to backend failed');
    }
}

function addLog(type, message) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    
    const typeSpan = document.createElement('span');
    typeSpan.className = 'command';
    typeSpan.innerText = type;
    
    const resultSpan = document.createElement('span');
    resultSpan.className = 'result';
    resultSpan.innerText = message;
    
    entry.appendChild(typeSpan);
    entry.appendChild(resultSpan);
    
    logContainer.prepend(entry);
}

// Initial status check
async function checkStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        console.log('System Status:', data);
    } catch (e) {
        console.error('Backend not reachable');
    }
}

checkStatus();
