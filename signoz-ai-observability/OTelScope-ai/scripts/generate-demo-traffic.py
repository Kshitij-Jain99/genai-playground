#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import signal
import sys
import time
import urllib.error
import urllib.request
from itertools import cycle
from typing import Final

DEFAULT_URL: Final[str] = "http://127.0.0.1:8001/ask"
DEFAULT_INTERVAL_SECONDS: Final[float] = 2.0
DEFAULT_TIMEOUT_SECONDS: Final[float] = 30.0

SCENARIOS: Final[list[str]] = [
    "normal", "normal", "normal", "slow", "normal",
    "high-token", "normal", "normal", "normal", "error",
    "normal", "slow", "normal", "normal", "high-token",
    "normal", "normal", "slow", "normal", "normal",
]

QUESTIONS: Final[dict[str, str]] = {
    "normal": "Explain why observability is useful for an AI application.",
    "slow": "Analyze why an API request might be slow.",
    "high-token": "Give a detailed explanation of OpenTelemetry traces, metrics, and logs.",
    "error": "Demonstrate an application error for observability testing.",
}

running = True


def stop_gracefully(_signum: int, _frame: object) -> None:
    global running
    running = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate repeatable traffic for the local OTelScope AI app."
    )
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_SECONDS)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of requests; 0 means run continuously.",
    )
    return parser.parse_args()


def send_request(url: str, scenario: str, timeout: float) -> tuple[int, str]:
    payload = {
        "question": QUESTIONS[scenario],
        "scenario": scenario,
    }
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "OTelScope-Demo-Traffic/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def main() -> int:
    args = parse_args()

    if args.interval < 0:
        print("Error: --interval cannot be negative.", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("Error: --timeout must be greater than zero.", file=sys.stderr)
        return 2
    if args.count < 0:
        print("Error: --count cannot be negative.", file=sys.stderr)
        return 2

    signal.signal(signal.SIGINT, stop_gracefully)
    signal.signal(signal.SIGTERM, stop_gracefully)

    print("OTelScope AI demo traffic generator")
    print(f"Target:       {args.url}")
    print(f"Interval:     {args.interval}s")
    print(f"Timeout:      {args.timeout}s")
    print("Distribution: 70% normal, 15% slow, 10% high-token, 5% error")
    print("Press Ctrl+C to stop.\n")

    scenario_cycle = cycle(SCENARIOS)
    request_number = 0

    while running and (args.count == 0 or request_number < args.count):
        request_number += 1
        scenario = next(scenario_cycle)
        started = time.perf_counter()

        try:
            status, _ = send_request(args.url, scenario, args.timeout)
            elapsed_ms = (time.perf_counter() - started) * 1000
            symbol = "✓" if 200 <= status < 400 else "✗"
            print(
                f"[{request_number:04d}] {scenario:<10} {symbol} "
                f"status={status:<3} time={elapsed_ms:8.2f} ms",
                flush=True,
            )
        except urllib.error.URLError as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            print(
                f"[{request_number:04d}] {scenario:<10} ✗ "
                f"connection-error={exc.reason} time={elapsed_ms:8.2f} ms",
                flush=True,
            )
        except TimeoutError:
            elapsed_ms = (time.perf_counter() - started) * 1000
            print(
                f"[{request_number:04d}] {scenario:<10} ✗ "
                f"timeout time={elapsed_ms:8.2f} ms",
                flush=True,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            print(
                f"[{request_number:04d}] {scenario:<10} ✗ "
                f"unexpected-error={exc} time={elapsed_ms:8.2f} ms",
                flush=True,
            )

        if running and (args.count == 0 or request_number < args.count):
            time.sleep(args.interval)

    print(f"\nStopped after {request_number} request(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())