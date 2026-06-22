from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
from langchain_ollama import ChatOllama
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from tools import agent_tools
import sqlite3
import time

app = FastAPI(title="Local LLM API", description="API wrapper for local Ollama models")
llm = ChatOllama(model="llama3.1", temperature=0, base_url="http://127.0.0.1:11434")

class GenerateRequest(BaseModel):
    prompt:     str

class AgentRequest(BaseModel):
    prompt: str

# 1. Initialize the SQLite Database
def init_db():
    conn = sqlite3.connect("api_logs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            response TEXT,
            latency REAL
        )
    ''')
    conn.commit()
    conn.close()

# Run the setup function when the app starts
init_db()

# 2. Function to save data in the background
def save_log_to_db(prompt: str, response: str, latency: float):
    conn = sqlite3.connect("api_logs.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO request_logs (prompt, response, latency) VALUES (?, ?, ?)", 
        (prompt, response, latency)
    )
    conn.commit()
    conn.close()

@app.get("/health")
async def health_check():
    return {"status": "active", "message": "The API is up and running."}

# 3. Update the standard endpoint to track time and save to DB
@app.post("/generate")
async def generate_text(request: GenerateRequest, background_tasks: BackgroundTasks):
    start_time = time.time() # Start the stopwatch
    
    response = llm.invoke(request.prompt)
    
    end_time = time.time() # Stop the stopwatch
    latency = end_time - start_time
    
    # Save to database in the background so the user doesn't wait
    background_tasks.add_task(save_log_to_db, request.prompt, response, latency)
    
    return {
        "prompt": request.prompt, 
        "response": response,
        "latency_seconds": round(latency, 2)
    }

# Your streaming endpoint remains unchanged for now
@app.post("/generate/stream")
async def generate_stream(request: GenerateRequest):
    async def stream_generator():
        async for chunk in llm.astream(request.prompt):
            yield chunk
    return StreamingResponse(stream_generator(), media_type="text/plain")

@app.post("/agent/run")
async def run_agent(request: AgentRequest):
    print("🚀🚀🚀 ENDPOINT HIT! ATTEMPTING TO USE LLAMA 3.1 🚀🚀🚀")
    
    # 1. Initialize the LLM 
    llm = ChatOllama(model="llama3.1:latest", temperature=0, base_url="http://127.0.0.1:11434")

    # 2. Build the Agent's Brain (The Prompt Template)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an advanced Computer Use Agent. You can execute local Python scripts to complete tasks. Always use the appropriate tool when a user asks you to create or write a file."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 3. Assemble the Agent
    agent = create_tool_calling_agent(llm, agent_tools, prompt)
    
    # 4. Create the Executor (Verbose=True lets us watch it think in the terminal)
    agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)

    # 5. Run the Agent
    try:
        result = await agent_executor.ainvoke({"input": request.prompt})
        return {"response": result["output"]}
    except Exception as e:
        return {"error": str(e)}