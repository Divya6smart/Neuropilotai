# NeuroPilot AI – Predictive Computer-Use Agent

NeuroPilot AI is an autonomous, self-learning, and predictive computer-use agent. It follows a real-world Perception → Reasoning → Action loop to interact with a computer using vision and mouse/keyboard control, bypassing APIs. It features a multi-agent architecture, a predictive engine, and a multi-layer biometric security system.

## Features
- **Computer Control**: Uses OCR and vision to detect UI elements, moves the mouse, clicks, and types autonomously.
- **Predictive Engine**: Learns user habits to predict and execute next actions.
- **Multi-Agent System**: Comprises Planner, Executor, Critic, and Learning agents.
- **Self-Healing**: Retries failed actions with alternative strategies.
- **Security System**: Employs face recognition, voice authentication, liveness detection, continuous tracking, and encrypted biometric storage.

## Setup Instructions

1. Install system dependencies for OCR and audio:
   - **Tesseract OCR**: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - Ensure Tesseract is added to your system PATH or configured in `vision.py`.
   - **PyAudio** might require specific C++ build tools on Windows.

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Run the Backend API:
   ```bash
   uvicorn main:app --reload
   ```

5. Run the Frontend Dashboard (Streamlit):
   ```bash
   cd frontend
   streamlit run app.py
   ```

## Demo Use Cases
- "Open Notepad and type 'Hello World'"
- "Search for 'Latest AI news' on YouTube"
- Predictively preparing a workspace (opening IDE, browser, and terminal) when the user logs in.
