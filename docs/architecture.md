# Reference architecture

## Goals

1. Keep prompts, retrieved documents, and model inference on the user's PC by default.
2. Separate the user interface, model gateway, inference runtime, and evaluation record so each can be replaced independently.
3. Start on ordinary PC hardware and make memory, speed, quality, and energy trade-offs visible.
4. Include Somali and English examples without claiming language quality before fluent review.

## Data path

```text
User task
  -> local client
  -> local gateway (model selection, limits, request metadata)
  -> inference runtime (CPU/GPU, quantized model)
  -> response to client
  -> optional measurement metadata to a local JSONL file
```

The measurement harness sends one request to an OpenAI-compatible chat-completions endpoint. It does not save prompt text or response text. Operators should still review prompts before sending them, especially if they change the endpoint from loopback to a remote host.

## Component boundaries

| Component | Responsibility | Initial interface |
| --- | --- | --- |
| Client | Accept a task and show the response | Any local UI or CLI |
| Gateway | Route requests and apply operator-defined limits | OpenAI-compatible HTTP API |
| Runtime | Load and serve a local model | Replaceable local inference server |
| Model files | Quantized model weights and tokenizer | Explicitly downloaded local files |
| Evaluation harness | Send a controlled prompt and record metadata | `tools/bench_local.py` |

## Security and privacy defaults

- Use a loopback endpoint (`127.0.0.1` or `::1`) by default.
- Do not persist prompt text, model output, credentials, or personal documents in result records.
- Keep model downloads and licenses visible to the operator.
- Treat remote endpoints as an explicit opt-in.
- Record software versions and model identifiers so results can be reproduced.

## Not in scope yet

This first version does not provide a chat UI, model downloader, document ingestion, authentication, remote inference, or measured performance results. Those can be added when there is a tested need and clear privacy behavior.
