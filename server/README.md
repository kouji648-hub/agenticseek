# AgenticSeek Backend API

Autonomous AI Agent with Browser Automation, File Operations, Code Execution, and GitHub Integration.

## Features

- **AI Agent Execution**: Natural language task planning and execution using DeepSeek LLM
- **Browser Automation**: Playwright-based web automation with screenshots
- **Code Execution**: Python and JavaScript code execution
- **File Operations**: Read, write, delete, and list files
- **GitHub Integration**: Repository management and issue creation
- **File Upload**: Upload files to the server

## Installation

### Prerequisites

- Python 3.8+
- Node.js (for JavaScript execution)

### Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

3. Set environment variables:
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export ANTHROPIC_API_KEY="your-claude-api-key"  # Optional
export GITHUB_TOKEN="your-github-token"  # Optional
```

## Running the Server

### Development

```bash
python api.py
```

The server will start on `http://localhost:7777`

### Using the startup script

```bash
chmod +x start.sh
./start.sh
```

## API Endpoints

### Health Check
```
GET /health
```

### AI Agent
```
POST /agent
{
  "prompt": "Visit Google and take a screenshot",
  "max_steps": 10
}
```

### Browser Automation
```
POST /browse
{
  "url": "https://www.google.com",
  "actions": []
}
```

### Code Execution

**Python:**
```
POST /execute/python
{
  "code": "print('Hello World')"
}
```

**JavaScript:**
```
POST /execute/javascript
{
  "code": "console.log('Hello World')"
}
```

### File Operations
```
POST /files
{
  "operation": "read|write|delete|list",
  "path": "path/to/file",
  "content": "file content (for write operation)"
}
```

### GitHub Operations
```
POST /github
{
  "action": "list_repos|create_issue|push_code",
  "owner": "username",
  "repo": "repository-name",
  "data": {}
}
```

### File Upload
```
POST /upload
Content-Type: multipart/form-data
file: <binary file data>
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:7777/docs`
- ReDoc: `http://localhost:7777/redoc`

## Architecture

### Components

1. **FastAPI Server**: Main API framework
2. **Playwright**: Browser automation
3. **DeepSeek LLM**: Natural language processing and task planning
4. **Claude API**: Optional alternative LLM
5. **GitHub API**: Repository integration

### Workflow

1. User sends a natural language prompt to the Agent endpoint
2. LLM breaks down the prompt into executable tasks
3. Each task is executed based on its type:
   - Browser tasks: Use Playwright
   - Code tasks: Execute with subprocess
   - File tasks: Use file system operations
   - GitHub tasks: Use GitHub API
4. Results are collected and returned to the user

## Configuration

### Environment Variables

- `DEEPSEEK_API_KEY`: DeepSeek API key (required)
- `ANTHROPIC_API_KEY`: Claude API key (optional)
- `GITHUB_TOKEN`: GitHub personal access token (optional)
- `PORT`: Server port (default: 7777)

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad request
- 500: Server error

Error responses include a `detail` field with error description.

## Performance Considerations

- Browser instances are reused across requests for better performance
- Screenshots are base64-encoded for easy transmission
- Code execution has a 30-second timeout
- File operations are limited to the `/tmp/agenticseek` directory

## Security

- CORS is enabled for all origins (can be restricted in production)
- API keys should be stored securely using environment variables
- File operations are sandboxed to the work directory
- Code execution is limited to safe operations

## Troubleshooting

### Playwright installation fails
```bash
# Install system dependencies
sudo apt-get install -y libgconf-2-4 libatk1.0-0 libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb

# Then install Playwright
playwright install chromium
```

### API key errors
- Verify that environment variables are set correctly
- Check API key validity and permissions
- Ensure network connectivity

### Browser automation issues
- Check that Chromium is installed
- Verify that the target website is accessible
- Check browser console for errors

## Development

### Adding new capabilities

1. Create a new endpoint in `api.py`
2. Add request/response models
3. Implement the functionality
4. Update the agent task executor to handle the new task type
5. Test with the frontend

### Testing

```bash
# Test health check
curl http://localhost:7777/health

# Test Python execution
curl -X POST http://localhost:7777/execute/python \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello World\")"}'
```

## License

MIT

## Support

For issues and questions, please open an issue on GitHub or contact the development team.
