# Norwegian AI Local Lab — pilot brief

**Status:** Proposed pilot; no results collected yet  
**Project:** Independent open-source evaluation project  
**Contributors:** Thomas and Arne, as listed in the repository

## Problem

The project aims to find out whether a home PC can support a useful personal assistant with dependable continuity and carefully limited tools. A useful result needs reproducible tasks, visible permissions, and human review, not a claim of general intelligence or a single speed score.

## Proposed work

1. Verify the actual hardware and reproduce one local inference setup on each contributor's PC.
2. Build a bounded prototype that can read one named workspace, propose a small file change, wait for approval, and verify the resulting diff.
3. Add user-reviewed project notes and a visible backlog so work can resume across sessions without unattended task execution.
4. Evaluate a small, self-authored or appropriately licensed task set in Norwegian, English, and Somali. Record completion, unsupported claims, permission handling, recovery, latency, memory use, and reviewer notes separately.
5. Compare with an approved hosted workflow only when access is legitimately provided and its terms allow the evaluation.
6. Publish the method, sanitized metadata, limitations, and a short decision guide. Do not publish private prompts, personal data, credentials, or vendor-confidential information.

## Pilot measures

These are proposed acceptance checks, not current achievements:

- A second contributor can reproduce the setup from the written guide on their own PC.
- Every reported run has a model identifier, runtime version, machine notes, settings, language, prompt-set version, and timestamp.
- Repeated runs are summarized with a median and spread; failed and incomplete runs remain visible.
- Language quality is reviewed by fluent speakers using a published rubric. Latency is not presented as a quality score.
- The final report contains no claim broader than the devices, prompts, settings, and reviewers actually used.
- The prototype does not execute arbitrary model-generated shell commands or pending backlog items without the user's approval.

## Why a hosted workspace could help

A time-limited team workspace could support collaborative review of the project plan, code, and non-sensitive evaluation notes, and help compare a hosted workflow with the local reference path. It would not provide local inference, API credentials, or permission to send private data. Access would only be used under the provider's stated terms and a clearly defined test plan.

## Data and safety boundaries

- Use synthetic or properly licensed prompts for public demonstrations.
- Do not upload customer, employer, health, financial, or other sensitive information.
- Keep hosted evaluation data separate from local-model benchmark records.
- Use a service only through its supported interface; do not route consumer subscription access through an unofficial API.
- Document model and dataset licenses before distributing anything.

## Current project state

The repository currently has a starter script for one OpenAI-compatible local endpoint and a proposed assistant architecture. It has no working agent prototype, published benchmark results, validated production deployment, customer case study, or third-party endorsement. The next milestone is verifying the hardware and reproducing one local setup, followed by a small approval-gated file task.
