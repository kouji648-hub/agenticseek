# AgenticSeek Development Partner Context

## Project Overview

**AgenticSeek** is an autonomous AI agent platform with browser automation, code execution, and GitHub integration capabilities.

- **Tech Stack**: FastAPI (Python 3.12), React 19, Vite, Playwright
- **Browser Engine**: Firefox (switched from Chromium due to crash issues)
- **LLM Integration**: DeepSeek API for chat, Claude API for advanced tasks
- **Repository**: https://github.com/kouji648-hub/agenticseek

## Current Status

✅ **Completed Features:**
- Backend API (FastAPI) running on port 7777
- Frontend React app with 7 tabs (Agent, Chat, Browser, Files, Code, GitHub, Deploy)
- Chat feature with follow-up questions (DeepSeek LLM)
- Browser automation with session persistence (Playwright Firefox)
- Desktop launcher (`~/Desktop/AgenticSeek起動.command`)
- Chromium crash fix → Firefox migration (Dec 25, 2025)

✅ **Working Endpoints:**
- `/health` - Health check
- `/browse` - Browser automation (Firefox)
- `/browse/login` - Automated login with session storage
- `/chat/message` - Chat with follow-up questions
- `/execute/python`, `/execute/javascript` - Code execution
- `/files`, `/github`, `/upload` - File & GitHub operations

## Development Preferences

### Code Style
- **Language**: 日本語でのコミュニケーションを優先
- **Documentation**: 日本語と英語の両方をサポート
- **Commit Messages**: 英語（技術的な詳細）+ 日本語（概要）

### Error Handling
- Always use try-catch-finally for resource cleanup
- Add timeouts to all async operations (30s for navigation, 10s for interactions)
- Use `is_closed()` and `is_connected()` checks before closing resources
- Return error responses instead of raising exceptions for API endpoints

### Browser Automation
- **Current**: Firefox (stable on this system)
- **Avoid**: Chromium (crashes immediately after launch)
- Create fresh browser instances per request (avoid global instances)
- Always clean up: page → browser → playwright in finally blocks

### Testing
- Test all changes before committing
- Use curl for API endpoint testing
- Verify browser automation with multiple sites (example.com, google.com, github.com)

## Project Files

### Core Files
- `server/api.py` - Main FastAPI backend (965 lines)
- `client/src/pages/Home.tsx` - Main UI with 7 tabs
- `client/src/components/Chat.tsx` - Chat UI component
- `server/search_improvement.py` - Search enhancement module

### Documentation
- `LAUNCHER_GUIDE.md` - Desktop launcher usage (Japanese)
- `CHAT_FEATURE_DOCUMENTATION.md` - Chat feature details
- `RAILWAY_DEPLOYMENT_GUIDE.md` - Deployment guide
- `CLAUDE_HANDOFF.md` - Project handoff documentation

### Configuration
- `server/requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `vite.config.ts` - Frontend build config

## Common Tasks

### Starting the Application
```bash
# Option 1: Desktop launcher
Double-click ~/Desktop/AgenticSeek起動.command

# Option 2: Manual
cd ~/agenticseek
source venv/bin/activate
python server/api.py &
npm run dev &
```

### Running Tests
```bash
# Health check
curl http://localhost:7777/health

# Browse test
curl -X POST http://localhost:7777/browse \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

### Git Workflow
```bash
git add .
git commit -m "Description

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push origin main
```

## Environment

- **OS**: macOS (Darwin 25.2.0)
- **Platform**: darwin
- **Working Directory**: `/Users/kawabatakouji/agenticseek`
- **Python**: 3.12 (venv)
- **Node**: Latest
- **Playwright**: v1.48+ (Firefox build v1429)

## API Keys & Configuration

```python
# server/api.py
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-d8d78811ea69434fad5d447b5c1027e3")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
```

## Important Notes

1. **Browser Crashes**: Always use Firefox, not Chromium
2. **Timeouts**: All browser operations need explicit timeouts
3. **Resource Cleanup**: Use try-finally blocks for all browser operations
4. **Confirmation**: User prefers automatic execution without confirmation prompts
5. **Language**: Respond in Japanese for user communication

## Recent Changes

**Latest Commit** (f1f87ae): Fix Playwright browser crash - Switch to Firefox
- Migrated from Chromium to Firefox due to immediate crash issues
- Added comprehensive error handling and timeouts
- All browse tests passing (example.com, google.com, github.com)

## Next Steps / Roadmap

- ✅ Browser automation (Firefox) - COMPLETED
- ✅ Chat with follow-up questions - COMPLETED
- ⏳ Railway deployment (optional)
- ⏳ Additional browser automation features
- ⏳ Database persistence for sessions

---

**Last Updated**: 2025-12-25
**Partner**: Claude Sonnet 4.5 via Claude Code
