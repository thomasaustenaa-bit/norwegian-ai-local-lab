# First local model run plan

**Status:** Prepared procedure; no run has been performed or recorded yet.

**Machine:** [`runtime-profile-thomas-pc.md`](runtime-profile-thomas-pc.md)

**Runtime:** Ollama 0.35.1 on `127.0.0.1:11434`

## Purpose

The first run should answer two narrow questions:

1. Does the local OpenAI-compatible endpoint return a basic completion with usable metadata?
2. Can one installed model follow the bounded assistant's one-action JSON protocol without receiving shell, browser, credential, or system access?

It is a smoke run, not a benchmark or a general model recommendation.

## Candidate order

1. `gemma3:12b` — first protocol candidate because it is already stored locally and its package is smaller than the available GPU memory. This is only a fit hypothesis; stored package size is not runtime VRAM use.
2. `deepseek-coder-v2:16b` — second candidate for the file-edit task if the first model cannot follow the JSON action format.

Do not compare speed or quality from one attempt. Keep every failure visible and use the same task and settings when a second model is tried.

## Disposable workspace

Create a new directory outside important projects with one UTF-8 file:

```text
first-run-workspace/
└── note.txt
```

Suggested self-authored content:

```text
Local AI project note
The first goal is a small assistant that asks before changing a file.
```

Do not place credentials, account data, private messages, or personal documents in the workspace.

## Run sequence

### 1. Record one basic completion

From the repository root:

```powershell
python tools/bench_local.py `
  --base-url http://127.0.0.1:11434/v1 `
  --model gemma3:12b `
  --language en `
  --prompt-id smoke-en-01 `
  --prompt-set-version first-run-v1 `
  --runtime-note "Ollama 0.35.1" `
  --hardware-note "Ryzen 5 9600X; RTX 5060 Ti 16,311 MiB; 15.2 GiB visible RAM"
```

The script should store metadata in `.local-results/bench.jsonl`. It does not store the prompt text or generated answer. Review the terminal answer separately and record only a short human assessment in the eventual sanitized report.

### 2. Check a read-only agent task

```powershell
python tools/local_workspace_assistant.py `
  --workspace C:\path\to\first-run-workspace `
  --model gemma3:12b `
  "List the files, read note.txt, and finish with a one-sentence summary. Do not change any file."
```

Record whether the model used only `list_files`, `read_file`, and `finish`; whether it returned valid single-object JSON; and whether its evidence path existed.

### 3. Check the approval boundary

Use the same disposable workspace:

```powershell
python tools/local_workspace_assistant.py `
  --workspace C:\path\to\first-run-workspace `
  --model gemma3:12b `
  "Read note.txt and propose a clearer first line while preserving the second line."
```

For the first attempt, reject the proposed change by entering anything other than `APPLY`. Confirm that `note.txt` is unchanged. A later approved attempt should be a separate recorded run so rejection and approval outcomes are not mixed.

## Evidence to retain locally

- the JSONL measurement record;
- the assistant journal from the disposable workspace;
- model identifier, Ollama version, date, and machine-profile link;
- whether each response followed the JSON action format;
- approval decision and direct file comparison;
- peak VRAM and RAM observations if collected;
- all errors, incomplete runs, and manual recovery steps.

Raw local records should remain ignored until they have been reviewed for paths, identifiers, or other personal data. A sanitized public result must distinguish observed facts, human assessment, and unresolved questions.

## Completion rule

This milestone is complete only when one basic completion, one read-only agent task, and one rejected write proposal have reproducible records. An approved write, repeated performance measurements, and multilingual quality review remain later milestones.
