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


## Dependencies

The project uses two dependency files:

- `requirements.txt` contains readable direct dependencies.
- `requirements-lock.txt` contains exact resolved package versions.

### Install development dependencies

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
opentelemetry-bootstrap -a install
python -m pip check


## Environment configuration

Create a local environment file:

```bash
cp .env.example .env