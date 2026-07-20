OTelScope AI

OTelScope AI — OpenTelemetry Collector and GenAI Observability Platform
An OpenTelemetry-instrumented AI application with SigNoz dashboards for monitoring agent workflows, LLM latency, token usage, cost, errors, application performance, and OpenTelemetry Collector health.

Final project architecture
Browser
   │
   ▼
FastAPI AI Application
   │
   ├── agent.run
   ├── retrieval.search
   ├── llm.generate
   ├── tool.execute
   └── response.validate
   │
   ▼
OpenTelemetry SDK / Auto-instrumentation
   │
   ▼
OpenTelemetry Collector
   │
   ├── Application telemetry
   └── Collector internal telemetry
   │
   ▼
SigNoz
   │
   ├── Traces
   ├── Metrics
   ├── Logs
   ├── GenAI dashboard
   ├── Collector dashboard
   └── Alerts
   │
   ▼
Optional SigNoz MCP + AI Debugging Agent

Create .gitignore
Create requirements.txt -> python -m pip install -r requirements.txt
Create .env.example
Create local .env

Create the application settings code in app/core/config.py
 -> Settings defines the expected environment values.

Create request and response models in app/models/chat.py
 -> The request model validates that: question exists, It is not empty, It is no longer than 2,000 characters
 -> The response model documents the format returned by /ask.

Create the FastAPI application in app/main.py
python -m compileall app
python -c "from app.main import app; print(app.title)"

Run app
uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8001 \
  --reload

Verify everything in the browser: 
http://localhost:8001
http://localhost:8001/health
http://localhost:8001/docs -> POST Execute

Add a reusable start script in scripts/run-dev.sh
chmod +x scripts/run-dev.sh
Run: ./scripts/run-dev.sh