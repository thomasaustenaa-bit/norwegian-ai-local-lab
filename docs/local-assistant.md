# Bounded local workspace assistant

`tools/local_workspace_assistant.py` is the project's first agent prototype. It connects to an OpenAI-compatible model endpoint and lets the model work through a small set of named actions inside one directory selected by the operator.

## What it can do

- list regular files while excluding common dependency, Git, and journal directories;
- read UTF-8 text files up to 128 KiB;
- propose a complete replacement for one UTF-8 text file;
- display a unified diff and require the operator to type `APPLY` before writing;
- replace an approved file atomically and verify the written bytes;
- finish with evidence paths that must exist in the workspace;
- keep a private metadata journal in `.local-assistant/journal.jsonl` without storing the task text, file contents, or model responses.

The prototype has no shell tool, package installer, browser, credential access, background scheduler, or permission to read outside the selected workspace. Paths are resolved before use, reserved directories are excluded case-insensitively, and path traversal plus recognized symlink or junction escapes are rejected. Local endpoints cannot redirect file contents to a remote host unless the operator explicitly adds `--allow-remote`.

## Before running

Start an OpenAI-compatible local model server and note its model identifier. The default endpoint is `http://127.0.0.1:11434/v1`, which matches the installed Ollama runtime on the first development PC, but the project does not yet recommend a particular model or claim that every OpenAI-compatible server follows the same behavior. See [`runtime-profile-thomas-pc.md`](runtime-profile-thomas-pc.md) for the inventory and its limits.

Use a disposable test directory for the first run. Do not point an unvalidated model at an important workspace.

## Example

```bash
python tools/local_workspace_assistant.py \
  --workspace ./scratch-demo \
  --model your-local-model \
  "Read the project note and propose a clearer title."
```

The model may inspect files and propose a write. The file remains unchanged unless the operator types the exact word `APPLY` at the prompt. If input is not interactive, write proposals are rejected automatically.

## Privacy boundary

When the model chooses `read_file`, the complete contents of that UTF-8 text file, up to 128 KiB, are sent to the selected model endpoint. Keep the endpoint on loopback for local processing. `--allow-remote` means the task and the complete contents of every file the model reads may leave the computer; use it only with data and a service that the operator has deliberately approved.

## Current limitations

- The model must return one valid JSON action without Markdown or extra reasoning text.
- A proposed edit replaces the complete file; patch-level editing is not implemented.
- Only UTF-8 text files are supported.
- The prototype does not yet offer a dry-run transcript, task resumption, a reviewed memory file, or repeatable evaluation fixtures.
- Evidence paths in a `finish` action are checked for existence; the prototype does not independently prove that they support every statement in the model's summary.
- The containment checks are designed for normal local use and do not claim protection against a separate malicious process modifying the workspace concurrently.
- Presence of the code is not evidence that a particular model follows the protocol reliably. Model/runtime results will be published only after reproducible runs.
