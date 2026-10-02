# Evaluation plan

## Status

No benchmark results have been collected for this repository yet. The bounded workspace assistant is implemented but has not been run against a local model. The first development machine and its installed runtimes are inventoried in [`runtime-profile-thomas-pc.md`](runtime-profile-thomas-pc.md); the remaining architecture stages are proposed.

## Minimum record

For each run, capture:

- model name and quantization;
- inference runtime and version;
- operating system, CPU, GPU, and available memory;
- context and generation settings;
- language, prompt identifier, and prompt-set version (not the private prompt text or a reversible fingerprint of it);
- latency and completion-token usage when reported by the server;
- warm-up policy, repetition count, and date.

For agent tasks, also record the task-set version, allowed workspace, tools enabled, approval decisions, whether the task was completed, how the result was verified, and any unsupported claims or recovery steps. Do not collect private file contents or raw prompts in the public run record.

The measurement script writes raw metadata to the ignored `.local-results/` directory by default. Review any record before publishing it. A public report should use a random run ID plus a documented prompt-set identifier and version; it should not publish prompt hashes that make a short or known prompt easier to identify.

## Comparing runs

1. Use the same licensed prompt set and generation settings for every candidate.
2. Separate cold-start from warmed-up runs.
3. Repeat enough times to report a median and spread, not only a best run.
4. Review answer quality separately from speed. For Norwegian, English, and Somali, involve fluent reviewers and disclose reviewer and prompt-set limitations.
5. Report failed runs and missing server usage fields instead of silently dropping them.
6. For multi-step tasks, compare task completion, permission behavior, resumption, and failure recovery separately from generation speed.

Do not compare results from different prompt sets or hardware conditions as though they were equivalent. A local latency number is not a quality score or a general recommendation.

The prepared sequence for the first recorded run is in [`first-local-run.md`](first-local-run.md).
