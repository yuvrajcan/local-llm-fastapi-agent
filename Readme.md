
# Local LLM API & Agent Executor

A robust, offline-first REST API built with Python and FastAPI that serves local LLMs via Ollama. This project goes beyond simple text generation by implementing a LangChain Agent Executor, allowing the LLM to autonomously use tools and interact with the local file system.

## 🚀 Core Features
* **Autonomous Agents:** Features a Computer Use Agent (CUA) endpoint (`/agent/run`) where Llama 3.1 can execute custom Python tools (like local file writing).
* **Streaming Responses:** Real-time token streaming (`/generate/stream`) for fluid UI integrations.
* **Non-Blocking Logging:** Uses FastAPI `BackgroundTasks` to log all prompts, responses, and latency metrics to a local SQLite database (`api_logs.db`) without slowing down user requests.
* **100% Local & Private:** Runs entirely on your own hardware. No API keys, no data sharing.

## 🛠️ Tech Stack
* **Backend:** FastAPI, Python 3
* **AI/LLM:** Ollama, Meta Llama 3.1 (8B)
* **Orchestration:** LangChain (classic agents, tool-binding)
* **Database:** SQLite3

## ⚙️ Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn pydantic langchain-ollama langchain-classic

 2. Pull the Model

Ensure Ollama is installed and running on your system, then pull the tool-calling compatible model:

Bash
ollama pull llama3.1:latest

3. Start the Server
Note: We run on port 8080 or higher to avoid conflicts with other local services.

Bash
python -B -m uvicorn main:app --reload --port 8080

4. Test the Agent
Navigate to http://127.0.0.1:8080/docs to access the Swagger UI. Use the /agent/run endpoint to ask the agent to create a file on your machine!