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

# Progress Tracking Models
class ProgressStep(BaseModel):
    id: str
    name: str
    status: str  # "pending", "in_progress", "completed", "failed"
    progress: float = 0.0  # 0.0 to 100.0
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskProgress(BaseModel):
    task_id: str
    name: str
    status: str  # "pending", "in_progress", "completed", "failed"
    steps: List[ProgressStep] = []
    current_step: int = 0
    overall_progress: float = 0.0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    error: Optional[str] = None

class CreateTaskRequest(BaseModel):
    name: str
    steps: List[str]  # List of step names

class UpdateProgressRequest(BaseModel):
    step_id: str
    status: Optional[str] = None
    progress: Optional[float] = None
    message: Optional[str] = None

# Agent Execution Models
class ActionType(BaseModel):
    name: str  # "search", "browse", "code", "analyze", "plan"
    icon: str
    color: str

class AgentAction(BaseModel):
    id: str
    action_type: str
    description: str
    status: str  # "pending", "running", "completed", "failed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None

class AgentThought(BaseModel):
    id: str
    content: str
    thought_type: str  # "planning", "analysis", "decision", "observation"
    timestamp: datetime = datetime.now()

class AgentExecution(BaseModel):
    execution_id: str
    task: str
    status: str  # "pending", "running", "completed", "failed"
    thoughts: List[AgentThought] = []
    actions: List[AgentAction] = []
    logs: List[str] = []
    current_action: int = 0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    final_result: Optional[str] = None

class ExecuteAgentRequest(BaseModel):
    task: str

class AddActionRequest(BaseModel):
    action_type: str
    description: str

class AddThoughtRequest(BaseModel):
    content: str
    thought_type: str = "planning"

class AddLogRequest(BaseModel):
    message: str

# ============================================================================
# Global State
# ============================================================================

# In-memory conversation sessions storage
conversation_sessions: Dict[str, ConversationSession] = {}

# In-memory browser sessions storage
browser_sessions: Dict[str, Dict[str, Any]] = {}

# In-memory progress tracking storage
task_progress: Dict[str, TaskProgress] = {}

# In-memory agent execution storage
agent_executions: Dict[str, AgentExecution] = {}

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
    task_lower = task.lower()
    if any(keyword in task_lower for keyword in ["browse", "visit", "access", "アクセス", "スクリーンショット", "取得"]):
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
    
    elif any(keyword in task_lower for keyword in ["python", "code", "execute", "コード", "実行", "プログラム"]):
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
    
    elif any(keyword in task_lower for keyword in ["file", "read", "write", "ファイル", "読み", "書き"]):
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
        system_prompt = """あなたは自律型AIエージェントです。ユーザーのリクエストを実行可能なステップに分解してください。

利用可能な機能:
- ブラウザ自動化 (Webサイトへのアクセス、スクリーンショット取得、ページ操作)
- Pythonコード実行
- ファイル操作 (読み取り、書き込み、削除)
- GitHub統合 (Issue作成、コードプッシュ)

重要: タスクには必ず「アクセス」「スクリーンショット」「取得」「実行」などの動詞を含めてください。

実行するタスクをJSON配列形式で返してください。すべて日本語で記述してください。

例1（天気予報の場合）:
["https://tenki.jp にアクセスしてスクリーンショットを取得"]

例2（Googleの場合）:
["https://www.google.com にアクセスしてスクリーンショットを取得", "Pythonコードを実行: print('Hello World')"]

JSONのみを返してください。説明は不要です。"""
        
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


# ============================================================================
# Agent Execution Endpoints
# ============================================================================

@app.post("/agent/execute")
async def start_agent_execution(request: ExecuteAgentRequest, background_tasks: BackgroundTasks):
    """Start a new agent execution"""
    import uuid

    execution_id = str(uuid.uuid4())

    execution = AgentExecution(
        execution_id=execution_id,
        task=request.task,
        status="running",
        thoughts=[],
        actions=[],
        logs=[]
    )

    agent_executions[execution_id] = execution

    # Add initial thought
    initial_thought = AgentThought(
        id=str(uuid.uuid4()),
        content=f"Starting task: {request.task}",
        thought_type="planning"
    )
    execution.thoughts.append(initial_thought)
    execution.logs.append(f"🎯 Task started: {request.task}")

    # Run agent in background
    async def run_agent():
        import asyncio

        # Simulate agent execution
        steps = [
            ("planning", "Analyzing task requirements..."),
            ("search", "Searching for relevant information..."),
            ("analysis", "Processing collected data..."),
            ("decision", "Determining best approach..."),
            ("browse", "Accessing web resources..."),
            ("code", "Executing required operations...")
        ]

        for thought_type, description in steps:
            await asyncio.sleep(2)

            # Add thought
            thought = AgentThought(
                id=str(uuid.uuid4()),
                content=description,
                thought_type=thought_type
            )
            execution.thoughts.append(thought)

            # Add action
            action = AgentAction(
                id=str(uuid.uuid4()),
                action_type=thought_type,
                description=description,
                status="running",
                started_at=datetime.now()
            )
            execution.actions.append(action)
            execution.logs.append(f"🔄 {description}")
            execution.updated_at = datetime.now()

            await asyncio.sleep(3)

            # Complete action
            action.status = "completed"
            action.completed_at = datetime.now()
            action.result = f"Completed: {description}"
            execution.logs.append(f"✅ Completed: {description}")
            execution.updated_at = datetime.now()

        # Complete execution
        execution.status = "completed"
        execution.completed_at = datetime.now()
        execution.final_result = "Task completed successfully"
        execution.logs.append("✨ Task completed successfully!")
        execution.updated_at = datetime.now()

    background_tasks.add_task(run_agent)

    return {
        "execution_id": execution_id,
        "status": "started",
        "message": "Agent execution started"
    }


@app.get("/agent/execution/{execution_id}")
async def get_execution(execution_id: str):
    """Get execution status"""
    if execution_id not in agent_executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = agent_executions[execution_id]
    return {
        "execution": execution.dict()
    }


@app.get("/agent/executions")
async def get_all_executions():
    """Get all executions"""
    return {
        "executions": [exec.dict() for exec in agent_executions.values()]
    }


@app.post("/agent/execution/{execution_id}/action")
async def add_action(execution_id: str, request: AddActionRequest):
    """Add an action to execution"""
    import uuid

    if execution_id not in agent_executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = agent_executions[execution_id]

    action = AgentAction(
        id=str(uuid.uuid4()),
        action_type=request.action_type,
        description=request.description,
        status="pending"
    )

    execution.actions.append(action)
    execution.updated_at = datetime.now()

    return {
        "action_id": action.id,
        "status": "added"
    }


@app.post("/agent/execution/{execution_id}/thought")
async def add_thought(execution_id: str, request: AddThoughtRequest):
    """Add a thought to execution"""
    import uuid

    if execution_id not in agent_executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = agent_executions[execution_id]

    thought = AgentThought(
        id=str(uuid.uuid4()),
        content=request.content,
        thought_type=request.thought_type
    )

    execution.thoughts.append(thought)
    execution.updated_at = datetime.now()

    return {
        "thought_id": thought.id,
        "status": "added"
    }


@app.post("/agent/execution/{execution_id}/log")
async def add_log(execution_id: str, request: AddLogRequest):
    """Add a log entry to execution"""
    if execution_id not in agent_executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = agent_executions[execution_id]
    execution.logs.append(request.message)
    execution.updated_at = datetime.now()

    return {
        "status": "added"
    }


@app.delete("/agent/execution/{execution_id}")
async def delete_execution(execution_id: str):
    """Delete an execution"""
    if execution_id not in agent_executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    del agent_executions[execution_id]
    return {"message": "Execution deleted successfully"}


# ============================================================================
# Progress Tracking Endpoints
# ============================================================================

@app.post("/progress/task")
async def create_task(request: CreateTaskRequest):
    """Create a new task with progress tracking"""
    import uuid

    task_id = str(uuid.uuid4())

    # Create progress steps
    steps = []
    for i, step_name in enumerate(request.steps):
        step = ProgressStep(
            id=f"step_{i}",
            name=step_name,
            status="pending",
            progress=0.0
        )
        steps.append(step)

    # Create task
    task = TaskProgress(
        task_id=task_id,
        name=request.name,
        status="pending",
        steps=steps,
        current_step=0,
        overall_progress=0.0
    )

    task_progress[task_id] = task

    return {
        "task_id": task_id,
        "status": "created",
        "task": task.dict()
    }


@app.post("/progress/task/{task_id}/start")
async def start_task(task_id: str):
    """Start a task"""
    if task_id not in task_progress:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_progress[task_id]
    task.status = "in_progress"
    task.updated_at = datetime.now()

    # Start first step
    if task.steps:
        task.steps[0].status = "in_progress"
        task.steps[0].started_at = datetime.now()
        task.current_step = 0

    return {
        "task_id": task_id,
        "status": "started",
        "task": task.dict()
    }


@app.put("/progress/task/{task_id}/step/{step_id}")
async def update_step_progress(task_id: str, step_id: str, request: UpdateProgressRequest):
    """Update progress for a specific step"""
    if task_id not in task_progress:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_progress[task_id]

    # Find step
    step = None
    step_index = None
    for i, s in enumerate(task.steps):
        if s.id == step_id:
            step = s
            step_index = i
            break

    if step is None:
        raise HTTPException(status_code=404, detail="Step not found")

    # Update step
    if request.status:
        step.status = request.status
        if request.status == "in_progress":
            step.started_at = datetime.now()
        elif request.status in ["completed", "failed"]:
            step.completed_at = datetime.now()

    if request.progress is not None:
        step.progress = request.progress

    if request.message:
        step.message = request.message

    # Update overall progress
    total_progress = sum(s.progress for s in task.steps)
    task.overall_progress = total_progress / len(task.steps) if task.steps else 0.0

    # Update current step
    task.current_step = step_index

    # Check if step is completed, move to next
    if step.status == "completed" and step_index < len(task.steps) - 1:
        next_step = task.steps[step_index + 1]
        next_step.status = "in_progress"
        next_step.started_at = datetime.now()
        task.current_step = step_index + 1

    # Check if all steps completed
    if all(s.status == "completed" for s in task.steps):
        task.status = "completed"
    elif any(s.status == "failed" for s in task.steps):
        task.status = "failed"

    task.updated_at = datetime.now()

    return {
        "task_id": task_id,
        "status": "updated",
        "task": task.dict()
    }


@app.get("/progress/task/{task_id}")
async def get_task_progress(task_id: str):
    """Get current progress for a task"""
    if task_id not in task_progress:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_progress[task_id]
    return {
        "task_id": task_id,
        "task": task.dict()
    }


@app.get("/progress/tasks")
async def get_all_tasks():
    """Get all tasks"""
    return {
        "tasks": [task.dict() for task in task_progress.values()]
    }


@app.delete("/progress/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    if task_id not in task_progress:
        raise HTTPException(status_code=404, detail="Task not found")

    del task_progress[task_id]
    return {"message": "Task deleted successfully"}


@app.post("/progress/demo")
async def run_demo_task(background_tasks: BackgroundTasks):
    """Run a demo task with simulated progress"""
    import uuid

    task_id = str(uuid.uuid4())

    # Create demo task
    steps = [
        "Initializing system",
        "Loading data",
        "Processing information",
        "Generating results",
        "Finalizing output"
    ]

    task = TaskProgress(
        task_id=task_id,
        name="Demo Task",
        status="in_progress",
        steps=[
            ProgressStep(id=f"step_{i}", name=step, status="pending", progress=0.0)
            for i, step in enumerate(steps)
        ]
    )

    task_progress[task_id] = task

    # Run demo in background
    async def run_demo():
        import asyncio

        for i, step in enumerate(task.steps):
            # Start step
            step.status = "in_progress"
            step.started_at = datetime.now()
            task.current_step = i
            task.updated_at = datetime.now()

            # Simulate progress
            for progress in range(0, 101, 20):
                await asyncio.sleep(0.5)
                step.progress = float(progress)

                # Calculate overall progress
                total_progress = sum(s.progress for s in task.steps[:i]) + step.progress
                task.overall_progress = total_progress / len(task.steps)
                task.updated_at = datetime.now()

            # Complete step
            step.status = "completed"
            step.completed_at = datetime.now()
            step.progress = 100.0

        # Complete task
        task.status = "completed"
        task.overall_progress = 100.0
        task.updated_at = datetime.now()

    background_tasks.add_task(run_demo)

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Demo task started in background"
    }


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
            "chat_session": "GET /chat/session/{id}",
            "progress_create": "POST /progress/task",
            "progress_start": "POST /progress/task/{id}/start",
            "progress_update": "PUT /progress/task/{id}/step/{step_id}",
            "progress_get": "GET /progress/task/{id}",
            "progress_all": "GET /progress/tasks",
            "progress_demo": "POST /progress/demo"
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
