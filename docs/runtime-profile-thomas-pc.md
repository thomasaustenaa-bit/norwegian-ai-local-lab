# Runtime profile: Thomas's Windows PC

This is a point-in-time inventory of the first development machine, captured on 2026-10-03. It records what was present without changing providers, credentials, models, services, scheduled jobs, or Hermes settings.

## Machine

| Component | Observed value |
| --- | --- |
| Operating system | Microsoft Windows 11 Home, build 26300 |
| Processor | AMD Ryzen 5 9600X, 6 cores / 12 logical processors |
| System memory | 16,278,106,112 bytes visible to Windows, about 15.2 GiB |
| Graphics processor | NVIDIA GeForce RTX 5060 Ti |
| Graphics memory | 16,311 MiB reported by `nvidia-smi` |
| NVIDIA driver | 591.86 reported by `nvidia-smi` |
| WSL | Linux Mint, WSL 2; stopped during the inventory |

This profile corrects conflicting processor descriptions in earlier project notes. Future run records should cite this verified profile and capture their own runtime settings instead of copying assumptions from those notes.

## Ollama

Ollama 0.35.1 was installed and already listening on the standard local port. No model was loaded during the snapshot. The inventory endpoint reported these stored model packages:

| Model identifier | Stored size |
| --- | ---: |
| `deepseek-r1:14b` | about 8.37 GiB |
| `deepseek-coder-v2:16b` | about 8.29 GiB |
| `deepseek-r1:8b` | about 4.87 GiB |
| `gemma3:12b` | about 7.59 GiB |
| `gpt-oss:20b` | about 12.85 GiB |

Stored size is not a claim about runtime memory, speed, quality, context length, or whether the model can follow the assistant's JSON action protocol. No generation or benchmark was run as part of this inventory.

## Hermes Agent

The installed command reported:

- Hermes Agent `v0.21.5+3173.gb4410b4.dirty (2026.9.24)`;
- embedded Python 3.14.7 and OpenAI SDK 2.24.0;
- a Git-based installation with an update available at inventory time;
- an external Nous Portal model as its current default, rather than Ollama;
- built-in file memory plus the local `kartotek` provider;
- a running gateway, active scheduled jobs, and broad file, terminal, browser, code, memory, and delegation tool categories.

No update was applied and no provider or tool setting was changed. Credentials were present in the installation, but their values are not part of this repository.

Hermes's offline prompt-size report also showed a large fixed context surface for a fresh CLI session: 43 tool schemas occupied 72,367 JSON bytes, in addition to the system prompt, skills index, memory, and user profile. This is one reason the project's first prototype exposes only four small actions and does not inherit the machine-wide Hermes tool set.

## What is verified and what is pending

Verified in this snapshot:

- the Windows, CPU, memory, GPU, driver, and WSL inventory above;
- Ollama's installed version, active local listener, and stored model identifiers;
- the installed Hermes version and redacted component status;
- that the project's bounded assistant can target Ollama's usual loopback URL by configuration.

Still pending:

- a model generation run through the bounded assistant;
- protocol-following results for each candidate model;
- warm and cold latency, token rate, VRAM, RAM, power, and task-quality measurements;
- failure and interruption records;
- review by a second person on a clean setup.

Until those items exist, the repository should describe the machine as available for evaluation, not as a proven assistant deployment.

## Repeat the inventory

The snapshot was assembled from the following read-only PowerShell commands. Review output before publishing it: Hermes status is designed to redact key values, but it still describes configured providers, integrations, and services.

```powershell
Get-CimInstance Win32_OperatingSystem |
  Select-Object Caption, Version, BuildNumber, TotalVisibleMemorySize

Get-CimInstance Win32_Processor |
  Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

nvidia-smi --query-gpu=name,memory.total,driver_version `
  --format=csv,noheader,nounits

ollama --version
Invoke-RestMethod http://127.0.0.1:11434/api/tags |
  Select-Object -ExpandProperty models |
  Select-Object name, size, modified_at

hermes --version
hermes status --all
hermes memory status
hermes prompt-size --platform cli --json
wsl.exe --list --verbose
```

The commands inspect the current machine; they do not install models, update Hermes, change providers, or start WSL. If Ollama is not already running, the inventory endpoint will be unavailable and that fact should be recorded instead of starting it silently.
