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

// Manual Command Input
const manualCmdInput = document.getElementById('manual-cmd');
const sendBtn = document.getElementById('send-btn');

sendBtn.addEventListener('click', () => {
    const cmd = manualCmdInput.value.trim();
    if (cmd) {
        addLog('Manual Input', cmd);
        sendCommand(cmd);
        manualCmdInput.value = '';
    }
});

manualCmdInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendBtn.click();
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
    } else if (data.type === 'prediction') {
        showPredictions(data.data);
    }
};

function showPredictions(suggestions) {
    const section = document.getElementById('prediction-section');
    const container = document.getElementById('prediction-chips');
    container.innerHTML = '';
    
    suggestions.forEach(s => {
        const chip = document.createElement('div');
        chip.style.cssText = 'background: rgba(0,210,255,0.1); border: 1px solid var(--accent-color); padding: 4px 10px; border-radius: 12px; cursor: pointer; font-size: 0.75rem; color: var(--accent-color); transition: 0.2s;';
        chip.innerText = s;
        chip.onmouseover = () => chip.style.background = 'rgba(0,210,255,0.2)';
        chip.onmouseout = () => chip.style.background = 'rgba(0,210,255,0.1)';
        chip.onclick = () => {
            addLog('Prediction', `Auto-suggested: ${s}`);
            sendCommand(`VoxOS ${s}`);
        };
        container.appendChild(chip);
    });
    
    section.style.display = suggestions.length ? 'block' : 'none';
}

async function updateMetrics() {
    try {
        const res = await fetch('/analytics');
        const data = await res.json();
        document.getElementById('metric-latency').innerText = `${data.avg_latency_ms} ms`;
        document.getElementById('metric-cpu').innerText = `${data.cpu_percent} %`;
        document.getElementById('metric-mem').innerText = `${data.memory_percent} %`;
    } catch (e) {}
}

setInterval(updateMetrics, 2000);
updateMetrics();

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
