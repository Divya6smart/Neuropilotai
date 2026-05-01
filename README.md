# VoxOS Pro – Intelligent Voice & Vision PC Controller

VoxOS is a high-performance, full-stack AI application that allows you to control your entire PC using natural language voice commands and computer vision.

## 🚀 Pro Features
- **Unified Elite Dashboard**: A single, premium Glassmorphism interface for both Voice PC control and AI DevOps orchestration.
- **Intelligent Orchestrator**: Uses GPT-4o for complex planning with an **Automatic Local Fallback** (ensuring functionality even without API keys).
- **Domain-Specific Agents**: Specialized agents for Security Audits, Code Reviews, and System Automation.
- **Resilient Memory**: ChromaDB vector storage with a MockMemory fallback for zero-crash reliability.
- **One-Click Launch**: Self-healing `run.bat` that automatically clears port conflicts.

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
