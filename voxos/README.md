# VoxOS Localhost – Voice + Vision PC Controller

VoxOS is a full-stack AI application that allows you to control your entire PC using voice commands directly from your browser. It combines speech recognition, vision-based screen control, and system automation.

## Core Features
- **Voice Control**: Capture voice directly from the browser using the Web Speech API.
- **Wake Word Detection**: Responds to "VoxOS" or "Jarvis".
- **Vision Engine**: Uses OCR (Pytesseract) to see text on your screen and click buttons automatically.
- **Multi-Tasking**: Understands complex commands like "open chrome and play music and click login".
- **System Automation**: Opens apps, types text, creates folders, and controls media.
- **Voice Feedback**: Responds with speech via `pyttsx3`.

## Project Structure
- `backend/`: Core logic for vision, system control, and task execution.
- `frontend/`: Premium web interface.
- `main.py`: FastAPI server.

## Installation

1. Install Tesseract OCR:
   - Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
   - Note the installation path (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`).
   - If not in your PATH, update `backend/vision/vision_engine.py` with the correct path.

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```
   OR
   ```bash
   uvicorn main:app --reload
   ```

4. Open in browser:
   Go to `http://localhost:8000`

## Usage
- Click the **Mic Button** to start listening.
- Say: "VoxOS, open notepad and type Hello World".
- Say: "VoxOS, open chrome and click login".
- The system will process your voice, parse tasks, and execute them sequentially with voice feedback.
