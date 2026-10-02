# Evaluation plan

## Status

No benchmark results have been collected for this repository yet. The assistant architecture is proposed, not implemented. Hardware profiles in the website and docs are planning categories only.

## Minimum record

For each run, capture:

- model name and quantization;
- inference runtime and version;
- operating system, CPU, GPU, and available memory;
- context and generation settings;
- language and prompt-set identifier (not the private prompt text);
- latency and completion-token usage when reported by the server;
- warm-up policy, repetition count, and date.

For agent tasks, also record the task-set version, allowed workspace, tools enabled, approval decisions, whether the task was completed, how the result was verified, and any unsupported claims or recovery steps. Do not collect private file contents or raw prompts in the public run record.

## Comparing runs

1. Use the same licensed prompt set and generation settings for every candidate.
2. Separate cold-start from warmed-up runs.
3. Repeat enough times to report a median and spread, not only a best run.
4. Review answer quality separately from speed. For Norwegian, English, and Somali, involve fluent reviewers and disclose reviewer and prompt-set limitations.
5. Report failed runs and missing server usage fields instead of silently dropping them.
6. For multi-step tasks, compare task completion, permission behavior, resumption, and failure recovery separately from generation speed.

Do not compare results from different prompt sets or hardware conditions as though they were equivalent. A local latency number is not a quality score or a general recommendation.
