#!/usr/bin/env python3
"""Record one local OpenAI-compatible chat completion's timing and metadata."""

import argparse
import hashlib
import ipaddress
import json
import platform
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1", help="OpenAI-compatible API base URL")
    parser.add_argument("--model", default="local-model", help="Model identifier expected by the local server")
    parser.add_argument("--language", default="en", help="Language tag for this prompt, e.g. en or so")
    parser.add_argument("--prompt-id", default="smoke-en-01", help="Non-sensitive identifier for the prompt")
    parser.add_argument("--prompt-text", default="Reply with one short sentence: what is one benefit of running AI locally?", help="Text sent to the selected endpoint")
    parser.add_argument("--system-prompt", default="You are a concise assistant.", help="System instruction sent with this request")
    parser.add_argument("--max-tokens", type=int, default=128, help="Maximum generated tokens")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    parser.add_argument("--output", default="results.jsonl", help="JSON Lines output path")
    parser.add_argument("--hardware-note", default="", help="Optional non-sensitive CPU/GPU/memory note")
    parser.add_argument("--runtime-note", default="", help="Optional runtime and version note")
    parser.add_argument("--allow-remote", action="store_true", help="Allow a non-loopback endpoint; prompts will leave this machine")
    return parser.parse_args()


def is_loopback(host):
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def main():
    args = parse_args()
    parsed = urllib.parse.urlparse(args.base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise SystemExit("--base-url must be an http(s) URL")
    if not is_loopback(parsed.hostname) and not args.allow_remote:
        raise SystemExit("Remote endpoint blocked. Use a loopback URL or pass --allow-remote intentionally.")
    if args.max_tokens < 1:
        raise SystemExit("--max-tokens must be at least 1")

    base = args.base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        endpoint = base
    else:
        endpoint = base + "/chat/completions"
    body = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": args.system_prompt},
            {"role": "user", "content": args.prompt_text},
        ],
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "stream": False,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            payload = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace")
        raise SystemExit(f"Endpoint returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach endpoint: {exc.reason}") from exc
    elapsed = time.perf_counter() - started

    usage = payload.get("usage") or {}
    completion_tokens = usage.get("completion_tokens")
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "prompt_id": args.prompt_id,
        "language": args.language,
        "prompt_sha256": hashlib.sha256(args.prompt_text.encode("utf-8")).hexdigest(),
        "endpoint_host": parsed.hostname,
        "model_requested": args.model,
        "model_reported": payload.get("model"),
        "runtime_note": args.runtime_note,
        "hardware_note": args.hardware_note,
        "os": platform.platform(),
        "http_status": status,
        "elapsed_seconds": round(elapsed, 4),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": completion_tokens,
        "completion_tokens_per_second": round(completion_tokens / elapsed, 3) if completion_tokens is not None and elapsed > 0 else None,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(f"Recorded metadata in {output}; prompt and generated answer were not saved.")


if __name__ == "__main__":
    main()
