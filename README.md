# YelpCamp_AI_MCP

AI chatbot for YelpCamp.

## Local Setup

1. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Set `GEMINI_API_KEY` in your `.env` file.
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Run the application:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

## Testing

Run all tests:
```bash
uv run python -m pytest
```
