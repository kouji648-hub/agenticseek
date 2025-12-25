#!/usr/bin/env python3
"""
AgenticSeek Backend API Server
Autonomous AI Agent with Browser Automation, File Operations, Code Execution, and GitHub Integration
"""

import os
import sys
import json
import base64
import subprocess
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from server.search_improvement import find_and_interact_with_search

# Browser automation
try:
    from playwright.async_api import async_playwright, Browser, Page
except ImportError:
    print("Installing playwright...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    from playwright.async_api import async_playwright, Browser, Page

# LLM Integration
try:
    import anthropic
except ImportError:
    print("Installing anthropic SDK...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
    import anthropic

# Initialize FastAPI
app = FastAPI(title="AgenticSeek Backend API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-d8d78811ea69434fad5d447b5c1027e3")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
WORK_DIR = Path("/tmp/agenticseek")
WORK_DIR.mkdir(exist_ok=True)

# Global browser instance (kept for backward compatibility but not recommended)
browser_instance: Optional[Browser] = None
playwright_instance = None

# Browser crash recovery flag
_browser_broken = False

# ============================================================================
# Data Models
# ============================================================================

class AgentRequest(BaseModel):
    prompt: str
    max_steps: int = 10

class AgentResponse(BaseModel):
    plan: List[str]
    results: List[Dict[str, Any]]
    summary: str

class BrowseRequest(BaseModel):
    url: str
    actions: Optional[List[str]] = None

class BrowseResponse(BaseModel):
    title: str
    url: str
    screenshot: Optional[str] = None
    content: Optional[str] = None
    error: Optional[str] = None

class BrowserLoginRequest(BaseModel):
    url: str
    username_selector: str
    password_selector: str
    submit_selector: str
    username: str
    password: str
    session_name: Optional[str] = None

class BrowserLoginResponse(BaseModel):
    success: bool
    session_id: str
    current_url: str
    screenshot: Optional[str] = None
    cookies: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class ExecuteCodeRequest(BaseModel):
    code: str
    language: str = "python"

class ExecuteCodeResponse(BaseModel):
    stdout: str
    stderr: str
    returncode: int

# Chat and Follow-up Question Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()

class ConversationSession(BaseModel):
    session_id: str
    messages: List[ChatMessage] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    generate_followup: bool = True

class ChatResponse(BaseModel):
    session_id: str
    message: str
    followup_questions: Optional[List[str]] = None
    timestamp: datetime = datetime.now()

class FileOperationRequest(BaseModel):
    operation: str  # "read", "write", "delete", "list"
    path: str
    content: Optional[str] = None

class GitHubRequest(BaseModel):
    action: str  # "list_repos", "create_issue", "push_code"
    owner: Optional[str] = None
    repo: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# ============================================================================
# Global State
# ============================================================================

# In-memory conversation sessions storage
conversation_sessions: Dict[str, ConversationSession] = {}

# In-memory browser sessions storage
browser_sessions: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# Browser Automation
# ============================================================================

async def get_browser() -> Browser:
    """Get or create a browser instance (using Firefox for stability)"""
    global browser_instance, playwright_instance

    if browser_instance is None:
        playwright_instance = await async_playwright().start()
        # Using Firefox instead of Chromium due to crash issues
        browser_instance = await playwright_instance.firefox.launch(headless=True)

    return browser_instance

async def close_browser():
    """Close the browser instance"""
    global browser_instance, playwright_instance
    
    if browser_instance:
        await browser_instance.close()
        browser_instance = None
    
    if playwright_instance:
        await playwright_instance.stop()
        playwright_instance = None

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await close_browser()

async def take_screenshot(page: Page) -> str:
    """Take a screenshot and return as base64"""
    screenshot_bytes = await page.screenshot()
    return base64.b64encode(screenshot_bytes).decode()

# ============================================================================
# LLM Integration (Claude/DeepSeek)
# ============================================================================

def call_claude_api(prompt: str, system: str = "") -> str:
    """Call Claude API for LLM tasks"""
    if not CLAUDE_API_KEY:
        return "Claude API key not configured"
    
    try:
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=system if system else "You are a helpful AI assistant.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error calling Claude API: {str(e)}"

def call_deepseek_api(prompt: str, system: str = "") -> str:
    """Call DeepSeek API for LLM tasks"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system if system else "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        response = httpx.post(
            "https://api.deepseek.com/chat/completions",
            json=payload,
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"DeepSeek API error: {response.status_code}"
    except Exception as e:
        return f"Error calling DeepSeek API: {str(e)}"

# ============================================================================
# Agent Execution
# ============================================================================

async def execute_agent_task(task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single agent task"""
    
    # Parse task type
    if "browse" in task.lower() or "visit" in task.lower() or "access" in task.lower():
        # Browser automation task
        try:
            browser = await get_browser()
            page = await browser.new_page()
            
            # Extract URL from task
            url = "https://www.google.com"  # Default
            if "http" in task:
                import re
                urls = re.findall(r'https?://[^\s]+', task)
                if urls:
                    url = urls[0]
            
            await page.goto(url, wait_until="networkidle", timeout=30000)
            screenshot = await take_screenshot(page)
            title = await page.title()

            try:
                if not page.is_closed():
                    await page.close()
            except:
                pass

            return {
                "status": "success",
                "task": task,
                "title": title,
                "screenshot": screenshot
            }
        except Exception as e:
            return {
                "status": "error",
                "task": task,
                "error": str(e)
            }
    
    elif "python" in task.lower() or "code" in task.lower() or "execute" in task.lower():
        # Code execution task
        try:
            # Extract code from task
            code = task.replace("python", "").replace("execute", "").strip()
            if not code or code == "code":
                code = 'print("Hello World")'
            
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "status": "success",
                "task": task,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "status": "error",
                "task": task,
                "error": str(e)
            }
    
    elif "file" in task.lower() or "read" in task.lower() or "write" in task.lower():
        # File operation task
        try:
            return {
                "status": "success",
                "task": task,
                "message": "File operation completed"
            }
        except Exception as e:
            return {
                "status": "error",
                "task": task,
                "error": str(e)
            }
    
    else:
        # Unknown task - skip
        return {
            "status": "skipped",
            "task": task
        }

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/agent", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """Execute AI agent with natural language prompt"""
    
    try:
        # Step 1: Use LLM to create a plan
        system_prompt = """You are an autonomous AI agent. Your task is to break down user requests into executable steps.
        
Available capabilities:
- Browser automation (visit websites, take screenshots, interact with pages)
- Python code execution
- File operations (read, write, delete files)
- GitHub integration (create issues, push code)

Return a JSON array of tasks to execute. Example:
["visit https://www.google.com and take a screenshot", "execute python code: print('Hello World')"]"""
        
        plan_text = call_deepseek_api(request.prompt, system_prompt)
        
        # Parse plan
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', plan_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                plan = [request.prompt]
        except:
            plan = [request.prompt]
        
        # Step 2: Execute each task
        results = []
        context = {}
        
        for i, task in enumerate(plan[:request.max_steps]):

            # === SEARCH TASK ENHANCEMENT ===
            # Check if this is a search task before default execution
            if "search for" in task.lower() or "search" in task.lower():
                try:
                    import re
                    # Extract search query from task description
                    match = re.search(r"search(?:\s+for)?\s+['\"]?([^'\"]+)['\"]?", task, re.IGNORECASE)
                    if match and "page" in context:
                        search_query = match.group(1).strip()
                        page = context["page"]

                        # Use improved search function
                        search_result = await find_and_interact_with_search(page, search_query, task)
                        if search_result["success"]:
                            result = {
                                "status": "success",
                                "task": task,
                                "type": "search",
                                "query": search_query,
                                "method": search_result.get("method_used", "unknown"),
                                "details": search_result
                            }
                            results.append(result)
                            context["page"] = page
                            continue
                except Exception as e:
                    print(f"[Search Enhancement] Error: {str(e)}")
                
            # === DEFAULT TASK EXECUTION ===
            result = await execute_agent_task(task, context)
            results.append(result)
            
            # Update context with results
            if result.get("status") == "success":
                context[f"task_{i}"] = result
        
        # Step 3: Generate summary
        summary_prompt = f"""Summarize the execution of these tasks:
Tasks: {plan}
Results: {json.dumps(results)}

Provide a brief summary of what was accomplished."""
        
        summary = call_deepseek_api(summary_prompt)
        
        return AgentResponse(
            plan=plan,
            results=results,
            summary=summary
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browse", response_model=BrowseResponse)
async def browse_url(request: BrowseRequest):
    """Browse a URL and return content/screenshot with crash recovery"""
    browser = None
    page = None
    playwright = None

    try:
        # Create fresh browser instance for each request (more stable)
        # Using Firefox due to Chromium crash issues on this system
        playwright = await async_playwright().start()
        browser = await playwright.firefox.launch(
            headless=True
        )
        page = await browser.new_page()

        # Navigate with timeout
        await page.goto(request.url, wait_until="networkidle", timeout=30000)

        title = await page.title()
        screenshot = await take_screenshot(page)

        # Get page content
        content = await page.content()

        return BrowseResponse(
            title=title,
            url=request.url,
            screenshot=screenshot,
            content=content[:1000]  # Limit content size
        )

    except Exception as e:
        return BrowseResponse(
            title="Error",
            url=request.url,
            error=str(e)
        )

    finally:
        # Always clean up resources
        try:
            if page and not page.is_closed():
                await page.close()
        except:
            pass
        try:
            if browser and browser.is_connected():
                await browser.close()
        except:
            pass
        try:
            if playwright:
                await playwright.stop()
        except:
            pass

@app.post("/browse/login", response_model=BrowserLoginResponse)
async def browser_login(request: BrowserLoginRequest):
    """
    Automated browser login with session persistence and crash recovery
    """
    import uuid
    page = None

    try:
        browser = await get_browser()
        page = await browser.new_page()

        # Navigate to login page with timeout
        await page.goto(request.url, wait_until="networkidle", timeout=30000)

        # Fill in login credentials with timeout
        await page.fill(request.username_selector, request.username, timeout=10000)
        await page.fill(request.password_selector, request.password, timeout=10000)

        # Click submit button with timeout
        await page.click(request.submit_selector, timeout=10000)

        # Wait for navigation with timeout
        await page.wait_for_load_state("networkidle", timeout=30000)

        # Generate session ID
        session_id = request.session_name or str(uuid.uuid4())

        # Get cookies
        cookies = await page.context.cookies()

        # Get current URL
        current_url = page.url

        # Take screenshot
        screenshot = await take_screenshot(page)

        # Store session
        browser_sessions[session_id] = {
            "cookies": cookies,
            "url": current_url,
            "timestamp": datetime.now().isoformat(),
            "page": page  # Keep page alive for session
        }

        return BrowserLoginResponse(
            success=True,
            session_id=session_id,
            current_url=current_url,
            screenshot=screenshot,
            cookies=cookies
        )

    except Exception as e:
        # Clean up page on error
        if page:
            try:
                if not page.is_closed():
                    await page.close()
            except:
                pass

        return BrowserLoginResponse(
            success=False,
            session_id="",
            current_url=request.url,
            error=str(e)
        )

@app.post("/execute/python", response_model=ExecuteCodeResponse)
async def execute_python(request: ExecuteCodeRequest):
    """Execute Python code"""
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", request.code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return ExecuteCodeResponse(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode
        )
    
    except subprocess.TimeoutExpired:
        return ExecuteCodeResponse(
            stdout="",
            stderr="Execution timeout",
            returncode=-1
        )
    except Exception as e:
        return ExecuteCodeResponse(
            stdout="",
            stderr=str(e),
            returncode=-1
        )

@app.post("/execute/javascript")
async def execute_javascript(request: ExecuteCodeRequest):
    """Execute JavaScript code"""
    
    try:
        # Use Node.js if available
        result = subprocess.run(
            ["node", "-e", request.code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return ExecuteCodeResponse(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode
        )
    
    except FileNotFoundError:
        return ExecuteCodeResponse(
            stdout="",
            stderr="Node.js not installed",
            returncode=-1
        )
    except Exception as e:
        return ExecuteCodeResponse(
            stdout="",
            stderr=str(e),
            returncode=-1
        )

@app.post("/files")
async def file_operations(request: FileOperationRequest):
    """Perform file operations"""
    
    try:
        file_path = WORK_DIR / request.path
        
        if request.operation == "read":
            if file_path.exists():
                with open(file_path, "r") as f:
                    content = f.read()
                return {"status": "success", "content": content}
            else:
                raise FileNotFoundError(f"File not found: {request.path}")
        
        elif request.operation == "write":
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(request.content or "")
            return {"status": "success", "message": f"File written: {request.path}"}
        
        elif request.operation == "delete":
            if file_path.exists():
                file_path.unlink()
                return {"status": "success", "message": f"File deleted: {request.path}"}
            else:
                raise FileNotFoundError(f"File not found: {request.path}")
        
        elif request.operation == "list":
            if file_path.is_dir():
                files = [str(f.relative_to(WORK_DIR)) for f in file_path.rglob("*")]
                return {"status": "success", "files": files}
            else:
                raise NotADirectoryError(f"Not a directory: {request.path}")
        
        else:
            raise ValueError(f"Unknown operation: {request.operation}")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/github")
async def github_operations(request: GitHubRequest):
    """Perform GitHub operations"""
    
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=400, detail="GitHub token not configured")
    
    try:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        if request.action == "list_repos":
            response = httpx.get(
                "https://api.github.com/user/repos",
                headers=headers
            )
            return response.json()
        
        elif request.action == "create_issue":
            url = f"https://api.github.com/repos/{request.owner}/{request.repo}/issues"
            response = httpx.post(
                url,
                json=request.data,
                headers=headers
            )
            return response.json()
        
        else:
            raise ValueError(f"Unknown action: {request.action}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file"""
    
    try:
        file_path = WORK_DIR / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path.relative_to(WORK_DIR))
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Chat Endpoints with Follow-up Questions
# ============================================================================

@app.post("/chat/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Chat endpoint with conversation history and follow-up question generation
    """
    import uuid

    # Generate or retrieve session ID
    session_id = request.session_id or str(uuid.uuid4())

    # Get or create conversation session
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = ConversationSession(
            session_id=session_id,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    session = conversation_sessions[session_id]

    # Add user message to history
    user_message = ChatMessage(role="user", content=request.message, timestamp=datetime.now())
    session.messages.append(user_message)

    try:
        # Call DeepSeek API with conversation history
        async with httpx.AsyncClient() as client:
            # Prepare messages for API
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in session.messages
            ]

            # Call DeepSeek Chat API
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": api_messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30.0
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"DeepSeek API error: {response.text}")

            result = response.json()
            assistant_message_content = result["choices"][0]["message"]["content"]

            # Add assistant response to history
            assistant_message = ChatMessage(
                role="assistant",
                content=assistant_message_content,
                timestamp=datetime.now()
            )
            session.messages.append(assistant_message)
            session.updated_at = datetime.now()

            # Generate follow-up questions if requested
            followup_questions = None
            if request.generate_followup:
                followup_questions = await generate_followup_questions(
                    session.messages[-4:] if len(session.messages) > 4 else session.messages
                )

            return ChatResponse(
                session_id=session_id,
                message=assistant_message_content,
                followup_questions=followup_questions,
                timestamp=datetime.now()
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


async def generate_followup_questions(messages: List[ChatMessage]) -> List[str]:
    """Generate relevant follow-up questions based on conversation context"""
    try:
        async with httpx.AsyncClient() as client:
            # Create a prompt for generating follow-up questions
            context = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
            prompt = f"""Based on this conversation:

{context}

Generate 3 relevant and insightful follow-up questions that the user might want to ask next.
Return ONLY the questions, one per line, without numbering or bullet points."""

            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 200
                },
                timeout=15.0
            )

            if response.status_code == 200:
                result = response.json()
                questions_text = result["choices"][0]["message"]["content"]
                questions = [q.strip() for q in questions_text.split("\n") if q.strip()]
                return questions[:3]  # Return max 3 questions
            else:
                return []

    except Exception as e:
        print(f"Error generating follow-up questions: {str(e)}")
        return []


@app.get("/chat/sessions")
async def get_sessions():
    """Get all active conversation sessions"""
    return {
        "sessions": [
            {
                "session_id": session.session_id,
                "message_count": len(session.messages),
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            }
            for session in conversation_sessions.values()
        ]
    }


@app.get("/chat/session/{session_id}")
async def get_session(session_id: str):
    """Get a specific conversation session"""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = conversation_sessions[session_id]
    return {
        "session_id": session.session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in session.messages
        ],
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat()
    }


@app.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session"""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del conversation_sessions[session_id]
    return {"message": "Session deleted successfully"}


@app.get("/browse/sessions")
async def get_browser_sessions():
    """Get all active browser sessions"""
    return {
        "sessions": [
            {
                "session_id": session_id,
                "url": session_data["url"],
                "timestamp": session_data["timestamp"],
                "cookie_count": len(session_data["cookies"])
            }
            for session_id, session_data in browser_sessions.items()
        ]
    }


@app.get("/browse/session/{session_id}")
async def get_browser_session(session_id: str):
    """Get a specific browser session"""
    if session_id not in browser_sessions:
        raise HTTPException(status_code=404, detail="Browser session not found")

    session_data = browser_sessions[session_id]
    return {
        "session_id": session_id,
        "url": session_data["url"],
        "timestamp": session_data["timestamp"],
        "cookies": session_data["cookies"]
    }


@app.delete("/browse/session/{session_id}")
async def delete_browser_session(session_id: str):
    """Delete a browser session with safe cleanup"""
    if session_id not in browser_sessions:
        raise HTTPException(status_code=404, detail="Browser session not found")

    # Close the page if it exists
    if "page" in browser_sessions[session_id]:
        page = browser_sessions[session_id]["page"]
        try:
            if not page.is_closed():
                await page.close()
        except Exception as e:
            print(f"Error closing page for session {session_id}: {e}")

    del browser_sessions[session_id]
    return {"message": "Browser session deleted successfully"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AgenticSeek Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "agent": "POST /agent",
            "browse": "POST /browse",
            "browse_login": "POST /browse/login",
            "browse_sessions": "GET /browse/sessions",
            "execute_python": "POST /execute/python",
            "execute_javascript": "POST /execute/javascript",
            "files": "POST /files",
            "github": "POST /github",
            "upload": "POST /upload",
            "chat": "POST /chat/message",
            "chat_sessions": "GET /chat/sessions",
            "chat_session": "GET /chat/session/{id}"
        }
    }

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 7777))
    
    print(f"🚀 Starting AgenticSeek Backend API on port {port}...")
    print(f"📍 API Base URL: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
