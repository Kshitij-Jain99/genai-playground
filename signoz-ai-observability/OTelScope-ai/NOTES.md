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





