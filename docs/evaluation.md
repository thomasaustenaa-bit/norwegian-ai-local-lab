# Evaluation plan

## Status

No benchmark results have been collected for this repository yet. Hardware profiles in the website and docs are planning categories only.

## Minimum record

For each run, capture:

- model name and quantization;
- inference runtime and version;
- operating system, CPU, GPU, and available memory;
- context and generation settings;
- language and prompt-set identifier (not the private prompt text);
- latency and completion-token usage when reported by the server;
- warm-up policy, repetition count, and date.

## Comparing runs

1. Use the same licensed prompt set and generation settings for every candidate.
2. Separate cold-start from warmed-up runs.
3. Repeat enough times to report a median and spread, not only a best run.
4. Review answer quality separately from speed. For Somali, involve fluent speakers and disclose reviewer and prompt-set limitations.
5. Report failed runs and missing server usage fields instead of silently dropping them.

Do not compare results from different prompt sets or hardware conditions as though they were equivalent. A local latency number is not a quality score or a general recommendation.
