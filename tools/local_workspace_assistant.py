#!/usr/bin/env python3
"""Run a bounded local-model assistant inside one explicitly selected workspace."""

import argparse
import datetime as dt
import difflib
import hashlib
import ipaddress
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path, PurePosixPath


SYSTEM_PROMPT = """You are controlling a deliberately restricted local workspace assistant.
Return exactly one JSON object and no Markdown.

Allowed actions:
{"action":"list_files","path":"."}
{"action":"read_file","path":"relative/path.txt"}
{"action":"write_file","path":"relative/path.txt","content":"complete replacement content","reason":"short reason"}
{"action":"finish","summary":"what was completed","evidence":["relative/path.txt"]}

Rules:
- Use one action per response.
- Paths must be relative to the workspace.
- Inspect relevant files before proposing a write.
- A write is only a proposal; the host application asks the user before applying it.
- Do not request shell commands, network calls, credentials, system settings, or paths outside the workspace.
- Do not claim a result unless an observation confirms it.
- Finish when the task is complete or explain the concrete limitation in the summary.
"""

EXCLUDED_DIRECTORIES = {".git", ".local-assistant", ".venv", "__pycache__", "node_modules"}
EXCLUDED_DIRECTORY_KEYS = {name.casefold() for name in EXCLUDED_DIRECTORIES}
MAX_LISTED_FILES = 250
MAX_FILE_BYTES = 128 * 1024
MAX_WRITE_BYTES = 256 * 1024


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", help="Task for the local assistant")
    parser.add_argument("--workspace", required=True, help="Existing directory the assistant may access")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434/v1", help="OpenAI-compatible API base URL")
    parser.add_argument("--model", required=True, help="Model identifier expected by the local server")
    parser.add_argument("--max-steps", type=int, default=8, help="Maximum model/tool iterations")
    parser.add_argument("--max-tokens", type=int, default=800, help="Maximum tokens in each model response")
    parser.add_argument("--allow-remote", action="store_true", help="Allow prompts and file excerpts to leave this machine")
    return parser.parse_args()


def is_loopback(host):
    if not host:
        return False
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class RestrictedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, allow_remote):
        super().__init__()
        self.allow_remote = allow_remote

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirect_host = urllib.parse.urlparse(newurl).hostname
        if not self.allow_remote and not is_loopback(redirect_host):
            raise urllib.error.HTTPError(
                newurl,
                code,
                "Remote redirect blocked; use --allow-remote only when intended",
                headers,
                fp,
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def ensure_workspace(path_text):
    workspace = Path(path_text).expanduser().resolve(strict=True)
    if not workspace.is_dir():
        raise SystemExit("--workspace must be an existing directory")
    return workspace


def resolve_workspace_path(workspace, relative_text, must_exist=False):
    if not isinstance(relative_text, str) or not relative_text.strip():
        raise ValueError("path must be a non-empty string")
    pure = PurePosixPath(relative_text.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError("path must stay inside the workspace")
    if any(part.casefold() in EXCLUDED_DIRECTORY_KEYS for part in pure.parts):
        raise ValueError("path is inside a reserved or excluded directory")
    candidate = (workspace / Path(*pure.parts)).resolve(strict=must_exist)
    try:
        common = os.path.commonpath((str(workspace), str(candidate)))
    except ValueError as exc:
        raise ValueError("path must stay inside the workspace") from exc
    if Path(common) != workspace:
        raise ValueError("path must stay inside the workspace")
    resolved_parts = candidate.relative_to(workspace).parts
    if any(part.casefold() in EXCLUDED_DIRECTORY_KEYS for part in resolved_parts):
        raise ValueError("resolved path is inside a reserved or excluded directory")
    return candidate


def relative_label(workspace, path):
    label = path.relative_to(workspace).as_posix()
    return label or "."


def list_files(workspace, requested_path):
    root = resolve_workspace_path(workspace, requested_path, must_exist=True)
    if not root.is_dir():
        raise ValueError("list_files path must be a directory")
    results = []
    for current_root, directories, filenames in os.walk(root, followlinks=False):
        current = Path(current_root)
        directories[:] = sorted(
            name
            for name in directories
            if name.casefold() not in EXCLUDED_DIRECTORY_KEYS and not is_link_or_junction(current / name)
        )
        for filename in sorted(filenames):
            candidate = current / filename
            if is_link_or_junction(candidate):
                continue
            results.append(relative_label(workspace, candidate))
            if len(results) >= MAX_LISTED_FILES:
                return {"files": results, "truncated": True}
    return {"files": results, "truncated": False}


def read_text_file(workspace, requested_path):
    path = resolve_workspace_path(workspace, requested_path, must_exist=True)
    if not path.is_file() or path.is_symlink():
        raise ValueError("read_file path must be a regular file")
    raw = path.read_bytes()
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError(f"file exceeds the {MAX_FILE_BYTES}-byte read limit")
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("only UTF-8 text files can be read") from exc
    return {"path": relative_label(workspace, path), "content": content, "sha256": sha256_bytes(raw)}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def is_link_or_junction(path):
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and is_junction())


def journal_event(workspace, event):
    journal_dir = workspace / ".local-assistant"
    if journal_dir.exists() and is_link_or_junction(journal_dir):
        raise RuntimeError("journal directory cannot be a symlink or junction")
    journal_dir.mkdir(mode=0o700, exist_ok=True)
    if journal_dir.resolve(strict=True).parent != workspace:
        raise RuntimeError("journal directory escaped the workspace")
    journal_path = journal_dir / "journal.jsonl"
    if journal_path.exists() and is_link_or_junction(journal_path):
        raise RuntimeError("journal file cannot be a symlink or junction")
    record = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(), **event}
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(journal_path, flags, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")


def make_diff(label, before, after):
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{label}",
            tofile=f"b/{label}",
        )
    )


def propose_and_apply_write(workspace, action, inspected_files):
    requested_path = action.get("path")
    content = action.get("content")
    reason = action.get("reason")
    if not isinstance(content, str) or not isinstance(reason, str) or not reason.strip():
        raise ValueError("write_file requires string content and a short reason")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_WRITE_BYTES:
        raise ValueError(f"proposed content exceeds the {MAX_WRITE_BYTES}-byte write limit")

    path = resolve_workspace_path(workspace, requested_path, must_exist=False)
    existed_before = path.exists()
    if existed_before and (not path.is_file() or is_link_or_junction(path)):
        raise ValueError("write_file target must be a regular file or a new file")
    parent = path.parent.resolve(strict=True)
    resolve_workspace_path(workspace, relative_label(workspace, parent), must_exist=True)
    before_raw = path.read_bytes() if existed_before else b""
    if len(before_raw) > MAX_WRITE_BYTES:
        raise ValueError("existing file exceeds the write limit")
    try:
        before = before_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("only UTF-8 text files can be replaced") from exc

    label = relative_label(workspace, path)
    if existed_before and label not in inspected_files:
        raise ValueError("an existing file must be read before a replacement can be proposed")
    diff = make_diff(label, before, content)
    print(f"\nProposed change: {reason}\n")
    print(diff or "(No content change)")
    if not diff:
        return {"path": label, "approved": False, "outcome": "no_change"}
    if not os.isatty(0):
        return {"path": label, "approved": False, "outcome": "approval_unavailable"}

    approved = input("Apply this change? Type APPLY to continue: ").strip() == "APPLY"
    if not approved:
        return {"path": label, "approved": False, "outcome": "rejected"}

    exists_at_write = path.exists()
    if exists_at_write != existed_before:
        raise RuntimeError("target changed after the displayed diff; no write was applied")
    if existed_before and path.read_bytes() != before_raw:
        raise RuntimeError("target changed after the displayed diff; no write was applied")
    if path.parent.resolve(strict=True) != parent:
        raise RuntimeError("target parent changed after approval; no write was applied")

    with tempfile.NamedTemporaryFile("wb", dir=parent, delete=False) as temporary:
        temporary.write(encoded)
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    verified = path.read_bytes()
    if verified != encoded:
        raise RuntimeError("write verification failed")
    return {
        "path": label,
        "approved": True,
        "outcome": "written_and_verified",
        "before_sha256": sha256_bytes(before_raw),
        "after_sha256": sha256_bytes(verified),
    }


def endpoint_url(base_url):
    base = base_url.rstrip("/")
    return base if base.endswith("/chat/completions") else base + "/chat/completions"


def call_model(opener, endpoint, model, messages, max_tokens):
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": False,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with opener.open(request, timeout=300) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace")
        raise RuntimeError(f"endpoint returned HTTP {exc.code}: {detail or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"could not reach endpoint: {exc.reason}") from exc
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("endpoint response did not contain assistant message content") from exc
    if not isinstance(content, str):
        raise RuntimeError("assistant message content was not text")
    try:
        action = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("model response was not one valid JSON object") from exc
    if not isinstance(action, dict):
        raise RuntimeError("model response must be a JSON object")
    return action, content


def execute_action(workspace, action, inspected_files):
    name = action.get("action")
    if name == "list_files":
        return list_files(workspace, action.get("path", "."))
    if name == "read_file":
        result = read_text_file(workspace, action.get("path"))
        inspected_files.add(result["path"])
        return result
    if name == "write_file":
        result = propose_and_apply_write(workspace, action, inspected_files)
        if result.get("outcome") == "written_and_verified":
            inspected_files.add(result["path"])
        return result
    if name == "finish":
        summary = action.get("summary")
        evidence = action.get("evidence", [])
        if not isinstance(summary, str) or not isinstance(evidence, list):
            raise ValueError("finish requires a summary string and evidence list")
        verified_evidence = []
        for item in evidence:
            path = resolve_workspace_path(workspace, item, must_exist=True)
            verified_evidence.append(relative_label(workspace, path))
        return {"finished": True, "summary": summary, "evidence": verified_evidence}
    raise ValueError("unknown action; allowed actions are list_files, read_file, write_file, and finish")


def main():
    args = parse_args()
    if args.max_steps < 1 or args.max_steps > 30:
        raise SystemExit("--max-steps must be between 1 and 30")
    if args.max_tokens < 64:
        raise SystemExit("--max-tokens must be at least 64")

    workspace = ensure_workspace(args.workspace)
    parsed = urllib.parse.urlparse(args.base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise SystemExit("--base-url must be an http(s) URL")
    if not args.allow_remote and not is_loopback(parsed.hostname):
        raise SystemExit("remote endpoint blocked; use a loopback URL or pass --allow-remote intentionally")

    opener = urllib.request.build_opener(RestrictedRedirectHandler(args.allow_remote))
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(
                {"task": args.task, "workspace_name": workspace.name, "initial_state": "No files inspected yet."},
                ensure_ascii=False,
            ),
        },
    ]
    session_id = uuid.uuid4().hex
    journal_event(
        workspace,
        {
            "event": "session_started",
            "session_id": session_id,
            "model": args.model,
            "endpoint_host": parsed.hostname,
        },
    )
    inspected_files = set()

    for step in range(1, args.max_steps + 1):
        action = {"action": "invalid_response"}
        raw_response = ""
        try:
            action, raw_response = call_model(
                opener, endpoint_url(args.base_url), args.model, messages, args.max_tokens
            )
            result = execute_action(workspace, action, inspected_files)
        except (RuntimeError, ValueError, OSError) as exc:
            result = {"error": str(exc)}

        action_name = action.get("action", "invalid_response") if isinstance(action, dict) else "invalid_response"
        journal = {
            "event": "step",
            "session_id": session_id,
            "step": step,
            "action": action_name,
            "outcome": result.get("outcome"),
        }
        if isinstance(result.get("path"), str):
            journal["path"] = result["path"]
        if "approved" in result:
            journal["approved"] = result["approved"]
        if "error" in result:
            journal["error"] = True
        journal_event(workspace, journal)

        if result.get("finished"):
            print(f"\n{result['summary']}")
            if result["evidence"]:
                print("Evidence: " + ", ".join(result["evidence"]))
            journal_event(
                workspace,
                {"event": "session_finished", "session_id": session_id, "step": step},
            )
            return

        messages.append({"role": "assistant", "content": raw_response})
        messages.append({"role": "user", "content": json.dumps({"observation": result}, ensure_ascii=False)})

    journal_event(
        workspace,
        {"event": "step_limit_reached", "session_id": session_id, "max_steps": args.max_steps},
    )
    raise SystemExit(f"Stopped after {args.max_steps} steps without a verified finish action")


if __name__ == "__main__":
    main()
