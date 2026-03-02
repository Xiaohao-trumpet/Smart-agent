# Quick Start Guide

Get the Conversational AI System running in 5 minutes!

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for OpenWebUI)
- API key for your model backend (e.g., Qwen API key)

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your API key
# Required: API_KEY=your_api_key_here
```

For Qwen (default):
```env
MODEL_NAME=qwen-plus
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
API_KEY=your_qwen_api_key_here
```

For local Ollama:
```env
MODEL_NAME=llama3
BASE_URL=http://localhost:11434/v1
API_KEY=dummy
```

## Step 3: Start the Backend

```bash
# Quick start
python run_backend.py

# Or with uvicorn directly
uvicorn backend.main:app --reload
```

Backend will be available at: `http://localhost:8000`

## Step 4: Test the Backend

```bash
# Health check
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Hello, how are you?"
  }'
```

## Step 5: Start OpenWebUI (Optional)

### Option A: Docker Compose (Recommended)

```bash
cd frontend
docker-compose up -d
```

Access OpenWebUI at: `http://localhost:3000`

### Option B: Docker Run

```bash
docker run -d \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/api/v1 \
  -e OPENAI_API_KEY=dummy \
  -e WEBUI_AUTH=false \
  --name openwebui \
  ghcr.io/open-webui/open-webui:main
```

## Step 6: Start Chatting!

1. Open browser to `http://localhost:3000`
2. Start a new conversation
3. Type your message and press Enter
4. Enjoy chatting with your AI assistant!

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_api.py -v
```

## Troubleshooting

### Backend won't start

**Check Python version:**
```bash
python --version  # Should be 3.11+
```

**Verify dependencies:**
```bash
pip install -r requirements.txt
```

**Check environment variables:**
```bash
cat .env  # Verify API_KEY is set
```

### OpenWebUI can't connect

**Verify backend is running:**
```bash
curl http://localhost:8000/health
```

**Check Docker logs:**
```bash
docker logs openwebui
```

**On Windows, use host.docker.internal:**
```env
OPENAI_API_BASE_URL=http://host.docker.internal:8000/api/v1
```

### Model API errors

**Test API connection:**
```bash
curl -X POST $BASE_URL/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-plus",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Explore the code in `backend/` directory
- Customize prompts in `backend/prompts/`
- Add your own system prompts for different scenarios

## Common Commands

```bash
# Start backend
python run_backend.py

# Run tests
pytest

# Start with Docker Compose
cd frontend && docker-compose up -d

# Stop Docker Compose
cd frontend && docker-compose down

# View logs
docker logs -f openwebui
docker logs -f chat-backend

# Clean up
docker-compose down -v
```

## API Examples

### Chat Request

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "What is the weather like?",
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### Delete Session

```bash
curl -X DELETE http://localhost:8000/api/v1/session/user123
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Development Tips

1. **Use reload mode** for development:
   ```bash
   python run_backend.py  # Auto-reload enabled
   ```

2. **Check API docs** at `http://localhost:8000/docs`

3. **View logs** in JSON format for easy parsing

4. **Test with curl** before using OpenWebUI

5. **Use different prompt scenes** by setting `SYSTEM_PROMPT_SCENE` env var

## Support

For issues:
1. Check logs for error messages
2. Verify configuration in `.env`
3. Test API with curl
4. Review [README.md](README.md) troubleshooting section
