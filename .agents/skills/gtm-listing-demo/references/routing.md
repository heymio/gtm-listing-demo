# Global routing contract

## Stage map

```text
Stage 0–7      → listing-planning
Stage 7.5–8    → listing-production
Stage 8.5–10   → listing-hardening
```

`listing-hardening` delegates exact-file evidence work to `listing-evidence-auditor` when required.

## Global Planning inputs

Planning owns selected configuration and evidence for:

```text
market
locale
region_overlays
channel
category
offer
page_targets
brand/private overlay
project evidence
```

These dimensions remain separate. A locale, market, or region name does not create consumer insight without project-specific evidence.

## Formal state objects

The workflow persists formal state instead of treating conversation history as the project database:

1. **Project Brief / Project Definition** — stable product, offer, claim, selected-profile, and channel conclusions.
2. **Creative Strategy Kernel** — compressed consumer and creative strategy relevant to production.
3. **Production Handoff** — complete page/asset requirements, Page Visual System, Evidence Mode, and production inputs.
4. **Asset Ledger / Production Freeze** — candidate history, exact selected output references, whole-set creative review, and complete current scope.
5. **Delivery State** — exact-file hardening evidence, role/scope binding, plan origin, frontend fidelity, and delivery parity.

Each downstream plane receives only the state objects and references it needs.

## Major Stage Checkpoint

Default user-facing checkpoint:

```text
Done:
Open:
Next:
```

Use detailed state manifests only for `PARTIAL`, `BLOCKED`, or explicit detailed audit/state review.

## Context firewall

Planning may be deep. Production must still be narrow.

Production receives only:

- Creative Strategy Kernel;
- Production Handoff;
- current one-job Asset Packet;
- referenced source assets;
- approved visual benchmarks/patterns.

Do not forward full workflow narration, prior failed attempts, gate definitions, auditor reports, change-impact maps, or Delivery State internals into ordinary production prompts.

Hardening receives the current Production Freeze, exact final files, locked page/slot requirements, relevant verification context, and current frontend evidence.

## User-facing continuity

The user normally invokes only `$gtm-listing-demo`. Internal stage Skills are routing targets, not separate user workflows.
