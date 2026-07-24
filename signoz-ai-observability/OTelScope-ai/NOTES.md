Phase 1 application behavior:
The first application will have two endpoints:
-> GET  /health
-> POST /ask

# Commands
sudo apt update
sudo apt install -y python3-venv
sudo apt install -y python3-pip
python3 -m venv .venv
source .venv/bin/activate
which python
which pip
python -m pip install --upgrade pip (use python -m pip from now)

mkdir -p \
  app/api \
  app/core \
  app/models \
  app/services \
  app/telemetry \
  collector \
  dashboards/application \
  dashboards/collector \
  alerts \
  scripts \
  tests \
  docs

touch \
  app/__init__.py \
  app/api/__init__.py \
  app/core/__init__.py \
  app/models/__init__.py \
  app/services/__init__.py \
  app/telemetry/__init__.py

touch \
  app/main.py \
  app/core/config.py \
  app/models/chat.py \
  .env \
  .env.example \
  .gitignore \
  requirements.txt

tree -a -I '.venv|.git'

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

deactivate (to stop venv)
git status --ignored --short (check .env and other files must not be pushed to git)

Current Architecture:
Browser
   │
   ▼
FastAPI application
   │
   ▼
Simulated AI response

//------------------------------------------------------------------------------------

Phase-2:  Add OpenTelemetry auto-instrumentation for FastAPI
FastAPI
   ↓ automatic instrumentation
OpenTelemetry Python Agent
   ↓ OTLP/HTTP
SigNoz Collector at localhost:4318
   ↓
SigNoz UI at localhost:8080

At the end of this phase:

/health generates an HTTP trace.
/ask generates an HTTP trace.
Traces are exported using OTLP/HTTP.
SigNoz shows the service otelscope-ai-api.
No manual spans are added yet.
Your normal run-dev.sh remains available.
A separate run-with-otel.sh starts the instrumented application.

# Commands
source .venv/bin/activate
Start signoz docker container
Open http://localhost:8080 -> SigNoz opens

Add OpenTelemetry dependencies in requirements.txt
python -m pip install -r requirements.txt
python -m pip install opentelemetry-instrumentation-fastapi
opentelemetry-bootstrap -a install
which opentelemetry-instrument
opentelemetry-instrument --version
python -m pip list | grep opentelemetry

Add OpenTelemetry environment variables in .env
Create scripts/run-with-otel.sh
chmod +x scripts/run-with-otel.sh
Run ./scripts/run-with-otel.sh -> This script will send telemetry.
ls -l scripts/run-with-otel.sh

Generate telemetry from the browser
http://localhost:8001/health
http://localhost:8001/docs -> POST /ask execute

Find the application in SigNoz
http://localhost:8080 -> Services, Traces (filter by service.name = otelscope-ai-api)


# Second terminal:
source .venv/bin/activate
set -a
source .env
set +a
env | grep '^OTEL_' | sort

# Architecture after Phase 2
Browser
   │
   │ HTTP request
   ▼
FastAPI on localhost:8001
   │
   │ automatically created server span
   ▼
OpenTelemetry Python Agent
   │
   │ OTLP/HTTP protobuf
   ▼
SigNoz OpenTelemetry Collector
localhost:4318
   │
   ▼
SigNoz
localhost:8080

//------------------------------------------------------------------------------

Phase-3: Define and Lock Project Dependencies
requirements.txt -> Human-readable direct dependencies
requirements-lock.txt -> Exact installed dependency versions

# Commands:
source .venv/bin/activate
cp requirements.txt requirements.txt.backup
python -m pip install --upgrade pip
python -m pip --version
python -m pip install -r requirements.txt

opentelemetry-bootstrap -a install
python -m pip check
which opentelemetry-bootstrap -> must point inside bin/
which opentelemetry-instrument -> must point inside bin/
Do verification of various packages.
python -m compileall app
python -c "from app.main import app; print(app.title)"

./scripts/run-with-otel.sh
http://localhost:8001/docs
http://localhost:8080
Verify that otelscope-ai-api still appears.

Only do this after: 
    pip install succeeded
    pip check succeeded
    imports succeeded
    application started successfully
    traces reached SigNoz
Generate requirements-lock.txt
python -m pip freeze > requirements-lock.txt
python -m pip install --dry-run -r requirements-lock.txt
python -m pip check

requirements.txt -> Use it when reviewing or intentionally adding dependencies.
requirements-lock.txt -> Use it when you want another environment to install the exact same resolved package versions.
Test the lock file safely in a new temp virtual environment.

Add a dependency installation script: scripts/install-dependencies.sh
chmod +x scripts/install-dependencies.sh
Run only when in new machine ./scripts/install-dependencies.sh

# Architecture after Phase 3
requirements.txt
    │
    ├── FastAPI and Uvicorn
    ├── HTTPX
    ├── OpenTelemetry API and SDK
    ├── OTLP exporter
    ├── FastAPI/HTTPX/logging instrumentation
    └── pytest tooling
            │
            ▼
       Project .venv
            │
            ├── run-dev.sh
            ├── run-with-otel.sh
            └── application tests

requirements-lock.txt
    └── exact resolved versions for reproducibility

//-------------------------------------------------------------------

Phase-4: Configure Environment Variables
Configure the application and OpenTelemetry behavior without hardcoding values in Python.

source .venv/bin/activate
cp .env.example .env.example.phase3-backup
cp .env .env.phase3-backup
Update .env files
Update config.py
python -m compileall app

Create scripts/check-env.sh
chmod +x scripts/check-env.sh
Run ./scripts/check-env.sh

Add validation to run-with-otel.sh
./scripts/run-with-otel.sh

Generate telemetry
http://localhost:8001/health
http://localhost:8001/docs -> POST /ask
Verify traces: http://localhost:8080 -> Services -> otelscope-ai-api -> Traces

//-------------------------------------------------------------------

Phase-5: Manage the SigNoz Infrastructure

//------------------------------------------------------------------

Phase-6: Created and verified the main FastAPI app.

Updated main.py, chat.py, config.py
source .venv/bin/activate
python -m compileall app
python -c "from app.main import app; print(app.title, app.version)" -> Verify the application imports
python -c "from app.main import app; print([route.path for route in app.routes])" -> Verify the routes   

./scripts/run-dev.sh
http://localhost:8001
http://localhost:8001/health
http://localhost:8001/docs
Test normal question, whitespace handling, invalid input.

./scripts/run-with-otel.sh
http://localhost:8001/health
http://localhost:8001/docs
http://localhost:8080 -> Services and Traces

The architecture at the end of this phase is:
Browser / Swagger
        │
        ▼
FastAPI
├── GET /
├── GET /health
└── POST /ask
        │
        ├── Request validation
        ├── Environment-based configuration
        └── Simulated AI response

With OpenTelemetry enabled:
FastAPI
   │
   ▼
Automatic OpenTelemetry instrumentation
   │
   ▼
SigNoz Collector
   │
   ▼
SigNoz traces

//----------------------------------------------------------------------

Phase-7: OpenTelemetry Auto-Instrumentation
-> Replace run-with-otel.sh with a safer version.
-> Verify the required OpenTelemetry variables.
-> Confirm FastAPI instrumentation is installed.
-> Run the application with automatic instrumentation.
-> Verify HTTP traces in SigNoz.

python -m pip check
python -m pip install opentelemetry-instrumentation-fastapi
opentelemetry-bootstrap -a install
Updated scripts/run-with-otel.sh
chmod +x scripts/run-with-otel.sh
bash -n scripts/run-with-otel.sh  # syntax verify

Check the loaded OpenTelemetry environment:
set -a
source .env
set +a
env | grep '^OTEL_' | sort

http://localhost:8080
./scripts/run-with-otel.sh
http://localhost:8001/ # Gen traces
http://localhost:8001/health
http://localhost:8001/docs

Architecture: Browser
   │
   │ HTTP request
   ▼
FastAPI application
   │
   │ automatic FastAPI instrumentation
   ▼
OpenTelemetry Python Agent
   │
   │ OTLP/HTTP protobuf
   ▼
SigNoz OTLP receiver
localhost:4318
   │
   ▼
SigNoz UI
localhost:8080

//-------------------------------------------------------------------

Phase-8: Add Custom AI Workflow Spans
It adds manual child spans so that one /ask request appears as:
POST /ask
└── agent.run
    ├── prompt.render
    ├── retrieval.search
    ├── tool.execute
    ├── llm.generate
    └── response.validate

Create missing files:
touch \
  app/services/agent.py \
  app/services/prompt.py \
  app/services/retrieval.py \
  app/services/tools.py \
  app/services/llm.py \
  app/services/validation.py \
  app/telemetry/tracing.py \
  tests/__init__.py \
  tests/test_main.py

Updated tracing.py, retrieval.py, prompt.py, tools.py, llm.py, validation.py, agent.py
Updated chat.py, main.py
Updated test_main.py
python -m compileall app tests
python -c "from app.main import app; print(app.title, app.version)"
python -c "from app.services.agent import run_agent; print(run_agent)"
python -m pip check    
python -m pytest -v

./scripts/run-dev.sh -> Test 
./scripts/run-with-otel.sh -> Test Qs. ("Why is my API slow?", "How do OpenTelemetry spans work?", "How can SigNoz dashboards help?")
Verify traces http://localhost:8080 and each ones attribute, must not show private information like API Key, question asked, etc.

Final verification:
python -m compileall app tests
python -m pytest -v
bash -n scripts/run-with-otel.sh
git status --short
git status --ignored --short

Remove scripts.ccler file if its empty: 
rm scripts/ccler


//---------------------------------------------------------------------

Phase-9: Add Application Metrics
It adds metrics to the existing workflow without changing the span hierarchy.
OpenTelemetry supports synchronous Counter and Histogram instruments through a shared Meter. Counters are suitable for cumulative values such as requests, tokens, errors, and cost; histograms are suitable for durations.

Updated metrics.py, config.py, llm.py, retrieval.py, tools.py, agent.py
source .venv/bin/activate
python -m compileall app tests
./scripts/run-dev.sh -> http://localhost:8001/docs
./scripts/run-with-otel.sh -> http://localhost:8001/docs -> http://localhost:8080 -> Metrices(search for metrices in metrics-explorer)

Confirm forbidden attributes are absent from metrices: request_id, session_id, user_id, question, prompt, answer, api_key, authorization, trace_id as a metric attribute, span_id as a metric, attribute

Update test_llm.py
python -m pytest -v
python -m compileall app tests
python -m pytest -v
python -m pip check
bash -n scripts/run-with-otel.sh
git status --short
git status --ignored --short

Architecture:
POST /ask
   │
   ▼
agent.run
   │
   ├── Counter: app.agent.run.count
   ├── Histogram: app.agent.run.duration
   └── Counter: app.agent.error.count
   │
   ├── retrieval.search
   │      └── Histogram: app.retrieval.duration
   │
   ├── tool.execute
   │      └── Counter: app.tool.execution.count
   │
   └── llm.generate
          ├── Counter: app.gen_ai.request.count
          ├── Counter: app.gen_ai.input_tokens
          ├── Counter: app.gen_ai.output_tokens
          ├── Counter: app.gen_ai.estimated_cost
          └── Histogram: app.gen_ai.request.duration

Telemetry Flow:
Application metric instruments
        │
        ▼
OpenTelemetry MeterProvider
configured by opentelemetry-instrument
        │
        ▼
OTLP/HTTP
localhost:4318
        │
        ▼
SigNoz Metrics          

//--------------------------------------------------------------------

Phase-10: Structured Logs with Trace Correlation
It adds structured application logs to the traces and metrics already implemented.
A request will produce:
POST /ask trace
├── agent.run
│   ├── retrieval.search
│   ├── prompt.render
│   ├── tool.execute
│   ├── llm.generate
│   └── response.validate
│
├── metrics
│   ├── token counts
│   ├── request counts
│   ├── durations
│   └── estimated cost
│
└── correlated logs
    ├── agent_run_started
    ├── retrieval_completed
    ├── tool_execution_started
    ├── tool_execution_completed
    ├── llm_request_started
    ├── llm_request_completed
    ├── response_validation_completed
    └── agent_run_completed

source .venv/bin/activate
Update .env, config.py, logging.py, main.py, retrieval.py, tools.py, validation.py, llm.py, agent.py
python -m compileall app tests
./scripts/run-dev.sh -> http://localhost:8001/docs
./scripts/run-with-otel.sh -> http://localhost:8001/docs
Verify logs: http://localhost:8080
Validate log-to-trace and trace-to-log two way correlation.

Update test_logging.py
python -m pytest -v
Update test_main.py
Finally do Privacy verification.Inspect successful and failed logs.

Final checks:
python -m compileall app tests
python -m pytest -v
python -m pip check
bash -n scripts/run-with-otel.sh
git status --short
git status --ignored --short 

Architecture:
Browser
   │
   ▼
POST /ask
   │
   ▼
Automatic FastAPI span
   │
   ▼
agent.run
├── structured logs
├── metrics
│
├── retrieval.search
│   └── retrieval_completed log
│
├── prompt.render
│
├── tool.execute
│   ├── tool_execution_started log
│   └── tool_execution_completed log
│
├── llm.generate
│   ├── llm_request_started log
│   ├── llm_request_completed log
│   └── llm_request_failed log
│
└── response.validate
    ├── response_validation_completed log
    └── response_validation_failed log

Telemetry export:
Application
├── traces
├── metrics
└── structured logs
        │
        ▼
OpenTelemetry SDK
        │
        ▼
OTLP/HTTP :4318
        │
        ▼
SigNoz    


//---------------------------------------------------------------------

Phase-11: Build Realistic Deterministic Behaviour
Adds six controlled scenarios: normal, slow, failure, high-token, tool-failure, retrieval-empty

Update scenarios.py, chat.py, main.py, prompt.py, retrieval.py, tools.py, llm.py, validation.py, agent.py, main.py, test_main.py, config.py, scenario.py

Test all scenarios:
./scripts/run-dev.sh -> http://localhost:8001/docs
./scripts/run-with-otel.sh -> http://localhost:8001/docs

Verify metrices, Filter or group metrics by:
-> POST /ask → Try it out: Normal scenario, Slow scenario, LLM failure scenario, Tool failure scenario, High-token scenario, Empty retrieval scenario, Invalid scenario
-> Verify traces in SigNoz: Services → otelscope-ai-api → Traces [Check that each span contains: app.scenario]
-> Verify logs in SigNoz: Search agent_run_completed, llm_request_failed, tool_execution_failed
-> Verify metrics: Search for these group by scenario: app.agent.run.duration
app.agent.error.count
app.gen_ai.request.duration
app.gen_ai.output_tokens
app.gen_ai.estimated_cost
app.retrieval.duration
app.tool.execution.count

Final verification: 
python -m compileall app tests
SIMULATE_OPERATION_DELAYS=false python -m pytest -v -> All test must pass
python -m pip check
bash -n scripts/run-dev.sh
bash -n scripts/run-with-otel.sh
git status --short


//---------------------------------------------------------------------

Phase-12: Collector Internal Telemetry
1. Identify which Collector your application is using.
2. Enable and export its internal metrics.
3. Verify the exact metric names in SigNoz.
4. Build the dashboard and collector_instance variable.
The Collector exposes internal metrics on 127.0.0.1:8888/metrics by default. Recent Collector versions configure this through service.telemetry.metrics.readers; metric names and available dimensions can change between versions, so inspect the received metrics before building panels.

Upto Phase-11: Monitering AI Application,
Phase 12 is about monitoring the OpenTelemetry Collector itself.
The Collector is the middle layer. If it becomes slow, overloaded, drops data, or cannot export data, your dashboards may become incomplete even when your application is running correctly.
Monitoring only the AI app would leave a blind spot.
AI application observability (sender)
+
OpenTelemetry pipeline observability (delivery truck)
+
SigNoz dashboards (warehouse)

Identify the Collector container
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}" -> container with name/image includes [otel,collector, signoz, ingester]
docker inspect <collector-container-name> \  
  --format '{{json .Config.Cmd}}'            -> Inspet its command
docker inspect <collector-container-name> \
  --format '{{json .Mounts}}'               -> Look for configuration path of config.yaml

Conceptually:
OTelScope AI (http://localhost:8001)
   │
   │ traces, metrics, logs
   ▼
signoz-ingester-1 (my container name)
   │ (127.0.0.1:8888)
   ▼
SigNoz storage (http://localhost:8080)

cp /path/to/otel-collector-config.yaml \      
   /path/to/otel-collector-config.yaml.backup -> Back up the Collector configuration(ingester.yaml in my case)

docker restart signoz-ingester-1
docker ps --filter "name=signoz-ingester-1" -> Confirm the Collector is healthy
docker logs --tail 100 signoz-ingester-1

docker inspect signoz-ingester-1 \
  --format '{{.Config.Image}}'
docker image inspect signoz/signoz-otel-collector:latest \
  --format '{{json .RepoDigests}}'
docker image inspect signoz/signoz-otel-collector:latest \
  --format '{{json .Config.Labels}}'

Update ingester.yaml file
docker restart signoz-ingester-1
docker ps --filter "name=signoz-ingester-1"
docker logs --since 2m signoz-ingester-1

Publish port 8888 for browser testing
grep -Rni \
  "signoz/signoz-otel-collector" \
  /home/../../pours/deployment
Inside the signoz-ingester-1 service definition, change the ports:
ports:
  - "4317:4317"
  - "4318:4318"
  - "8888:8888"
docker compose \
  -f /home/../../pours/deployment/compose.yaml \
  config --services
docker compose \
  -f /home/../../pours/deployment/compose.yaml \
  up -d --force-recreate ingester
docker ps --filter "name=signoz-ingester-1"
docker ps --format "table {{.Names}}\t{{.Ports}}" \
  | grep signoz-ingester
docker logs --since 2m signoz-ingester-1

http://localhost:8888/metrics -> CTRL+F(otelcol_ and others search)
http://localhost:8080 -> Metrices -> otelcol and others search

Now:
Collector creates health metrics
        ↓
Port 8888 exposes them
        ↓
prometheus/collector-internal scrapes them
        ↓
metrics/collector-internal exports them
        ↓
SigNoz stores them


//-----------------------------------------------------------------

Phase-13: Create a repeatable traffic generator
For creating a dashboard we need lot of requests.
We need something like this: 
App
↑
Traffic Generator every 2 seconds(delay)
↓
normal
normal
normal
slow
normal
normal
high-token
normal
error
...

After 5–10 minutes you have:
hundreds of traces
hundreds of logs
metrics with trends
realistic graphs
enough data for screenshots

Architecture:
generate-demo-traffic.py
            │
            ▼
localhost:8001/ask
            │
            ▼
FastAPI
            │
            ▼
OpenTelemetry
            │
            ▼
Collector
            │
            ▼
SigNoz

Out of every 100 requests approximately: 70 normal, 15 slow, 10 expensive, 5 failures
This makes dashboards predictable.
The script uses an exact 20-request cycle: 
14 normal      = 70%
3 slow         = 15%
2 high-token   = 10%
1 error        = 5%

Update generate-demo-traffic.py
chmod +x scripts/generate-demo-traffic.py
ls -l scripts/generate-demo-traffic.py
./scripts/run-with-otel.sh -> http://127.0.0.1:8001/docs

New terminal:
source .venv/bin/activate
python scripts/generate-demo-traffic.py \
  --count 20 \
  --interval 1
python scripts/generate-demo-traffic.py \
  --count 100 \
  --interval 0.5

Open: http://localhost:8080
Check:
Services for request traffic
Traces for normal, slow, high-token, and error requests
Logs for correlated application logs
Metrics for request counts, latency, tokens, cost, and errors

//-----------------------------------------------------------------------

Phase-14: Validate telemetry before dashboards
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" -> All req. containers should be working
./scripts/run-with-otel.sh -> http://127.0.0.1:8001/docs (1 ask req)
python scripts/generate-demo-traffic.py \
  --count 20 \
  --interval 1                        -> http://localhost:8080
Go to Trace(service.name = otelscope-ai)  
 - Validated the complete telemetry pipeline before dashboard creation
    using an exact 20-request cycle: 14 normal, 3 slow, 2 high-token,
    and 1 error.

  - Verified traces in SigNoz:
      - POST /ask is the root span.
      - agent.run is correctly nested.
      - Retrieval, prompt, tool, LLM, and validation child spans
        appear.

      - Error spans have ERROR status and exception events.
      - GenAI provider, model, operation, token, and scenario
        attributes are present.

      - Trace durations match client-observed durations.

  - Added the missing error scenario in app/core/scenarios.py. Updated
    app/services/llm.py so this scenario generates the intentional
    failure.

  - Updated app/main.py:
      - The demo error scenario now returns HTTP 500.
      - Removed an invalid duplicate lifespan yield.

  - Fixed log exporting in app/telemetry/logging.py by preserving
    OpenTelemetry’s OTLP logging handler.

  - Verified metrics:
      - Request, error, and token counters increase.
      - Duration histograms contain observations.
      - Provider and model attributes are queryable.
      - Units are correct.
      - No high-cardinality request IDs, prompts, or trace IDs are
        used.

  - Verified logs:
      - Logs contain structured fields and trace/span IDs.
      - Error logs correlate with the failed trace.
      - No secrets, full prompts, or full responses are exported.

  - Verified Collector telemetry:
      - Collector metrics appear on port 8888 and in SigNoz.
      - Instance identity is local-collector-01.
      - Receiver/exporter labels, queue size/capacity, and failure/
        refusal counters are available.

  - Added regression coverage in tests/test_main.py and tests/
    test_logging.py.

  - Recorded the final PASS result and supporting evidence in
    VALIDATION.md.

//-------------------------------------------------------------------

Phase-15: 

