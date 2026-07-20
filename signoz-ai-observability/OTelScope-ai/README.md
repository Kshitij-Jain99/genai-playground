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