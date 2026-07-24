## Traffic used

- [x] Application running
- [x] SigNoz running
- [x] One 20-request traffic cycle completed
- [x] 14 normal requests observed
- [x] 3 slow requests observed
- [x] 2 high-token requests observed
- [x] 1 error request observed

Notes:

- `signoz-signoz-0` was healthy and `signoz-ingester-1` was running.
- The application health and OpenAPI endpoints responded on port 8001.
- The corrected 20-request cycle completed with 19 successful responses and
  one intentional HTTP 500 response.
- Client-observed durations were approximately 788 ms for normal and
  high-token requests, 9.76 s for slow requests, and 770 ms for the error.
- The initial cycle exposed that `scenario=error` was not accepted. The
  scenario was added and the complete cycle was rerun from request 1.

## Traces

- [x] Parent HTTP span exists
- [x] `agent.run` is nested correctly
- [x] Expected child spans appear
- [x] Error trace has error status
- [x] Exception is recorded
- [x] GenAI attributes appear
- [x] Trace durations are realistic

Notes:

- Stored trace data contained 20 `POST /ask` roots and 20 `agent.run` spans
  for the validation cycle. All 20 agent spans referenced their HTTP root as
  parent.
- Each applicable trace contained `retrieval.search`, `prompt.render`,
  `tool.execute`, `llm.generate`, and `response.validate`. The error fails
  during `llm.generate`, so it correctly has no later validation span.
- The error HTTP root had status 500 and ERROR status. Both `agent.run` and
  `llm.generate` were marked ERROR and contained exception events with type,
  message, and stack trace.
- The LLM span contained provider `simulated`, model `demo-model`, operation
  `chat`, input/output token counts, and scenario.
- Average root durations from SigNoz were 786 ms normal, 787 ms high-token,
  9.756 s slow, and 767 ms error, closely matching client timings and
  remaining inside the parent span.

## Metrics

- [x] Counters increase
- [x] Histograms contain data
- [x] Provider attribute appears
- [x] Model attribute appears
- [x] No high-cardinality attributes exist
- [x] Units are correct

Notes:

- Request, error, input-token, and output-token delta samples increased after
  verification traffic.
- Agent and GenAI duration histograms exported bucket, count, sum, min, and
  max series. Slow observations reached the higher latency buckets.
- GenAI series can be grouped by provider `simulated`, model `demo-model`,
  operation, scenario, and status.
- Metric attribute keys are bounded: agent name, environment, error type,
  model, operation, provider, scenario, source, status, tool name/type, and
  generated histogram metadata. No prompt, response, trace/span ID,
  request/session ID, timestamp, or UUID is a metric attribute.
- Request/run/error units use count annotations, token metrics use `{token}`,
  duration metrics record seconds with unit `s`, and cost uses `USD`.

## Logs

- [x] Logs are structured
- [x] Trace IDs appear inside active spans
- [x] Span IDs appear inside active spans
- [x] Error logs appear for failures
- [x] No secrets are exported
- [x] No full prompts are exported
- [x] No full responses are exported

Notes:

- In-span records expose queryable event, operation, scenario, status,
  provider, model, duration, and token fields.
- Verification produced 13 correlated INFO records and 3 correlated ERROR
  records; all had native trace and span IDs.
- The error logs (`llm_request_failed`, `agent_run_failed`, and
  `request_failed`) share the failed trace ID.
- Searches found zero full generated prompts, zero large response bodies,
  and zero authorization/API-key/password indicators.
- The application logging setup was fixed to retain the OpenTelemetry OTLP
  handler while continuing to emit JSON to stdout.

## Collector

- [x] Collector metrics reach SigNoz
- [x] Collector instance can be identified
- [x] Receiver labels are available
- [x] Exporter labels are available
- [x] Queue size and capacity are visible
- [x] Failure and refusal counters are visible

Notes:

- Collector metrics were present at `http://127.0.0.1:8888/metrics` and in
  SigNoz metric storage.
- Resource identity is `service.name=otel-collector`,
  `service.instance.id=local-collector-01`, and
  `deployment.environment.name=development`.
- Receiver series expose `receiver=otlp` and `transport=http`; exporter
  series distinguish `clickhousetraces` and `metadataexporter`.
- Current metadata-exporter queue size was 0 with capacity 1000 for logs,
  metrics, and traces.
- Accepted/sent span counters were active at 1817 during validation.
  Send-failure and refused-span counters were present and both were 0.

## Dashboard gate

- [x] Traces passed
- [x] Metrics passed
- [x] Logs passed
- [x] Collector passed

Dashboard creation is permitted only after all four sections pass.
