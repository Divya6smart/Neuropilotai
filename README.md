# VoxOS Pro – Intelligent Voice & Vision PC Controller

VoxOS is a high-performance, full-stack AI application that allows you to control your entire PC using natural language voice commands and computer vision.

## 🚀 Pro Features
- **Intelligent Voice Control**: No wake-word required. Real-time interim speech recognition with high accuracy.
- **Vision Engine**: Uses OCR (Tesseract) to "see" your screen and perform actions like "click Login".
- **Performance Analytics**: Real-time dashboard monitoring API latency, CPU, and Memory usage.
- **AI Prediction Engine**: Predicts your next move and suggests actions to reduce friction.
- **One-Click Launch**: Includes a `run.bat` for instant startup and automatic browser opening.
- **Microservices Ready**: Fully containerized with Docker and Docker Compose (including Redis).

## 🛠️ Quick Start (One-Click)
1. **Double-click** `run.bat` in the project root.
2. The browser will automatically open to **http://localhost:8000**.
3. Click the **Mic** button and start speaking (e.g., "open notepad", "click search").

## 📂 Architecture
- **Backend**: FastAPI (Python) with Async execution and WebSocket streaming.
- **Frontend**: Vanilla JS + CSS (Glassmorphism design) with real-time analytics overlay.
- **Engines**: 
  - `VisionEngine`: Screen perception via OCR.
  - `SystemController`: Robust Windows automation.
  - `PredictionEngine`: AI-driven workflow suggestions.

## ⚙️ Configuration
- **Tesseract OCR**: Ensure Tesseract is installed for vision features to work.
- **API Keys**: Set your `OPENAI_API_KEY` for advanced reasoning features.

---
*Developed as part of the NeuroPilot AI ecosystem.*
