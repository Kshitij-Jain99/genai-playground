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

Phase-2: 
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


