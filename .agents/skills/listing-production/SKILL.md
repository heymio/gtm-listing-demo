---
name: listing-production
description: Use when producing Stage 7.5–8 listing assets from an approved Production Handoff and one-job Asset Packets across global channels.
---

# Listing Production

## Core question

Produce the approved artifacts.

## Plane boundary

This Skill owns Stage 7.5–8 only. It consumes the formal Production Handoff and Creative Strategy Kernel. It does not reinterpret Planning and does not perform final physical-file hardening.

## Inputs

Production may use only:

- Production Handoff;
- Creative Strategy Kernel;
- one current Asset Packet;
- referenced source assets;
- approved visual benchmarks/patterns.

Do not traverse full project history during ordinary production.

## Artifact-first mode

A request for one final asset should produce that artifact. Do not replace the requested asset with a workflow diagram, status board, asset map, or production-plan infographic.

## Creative status

`PLANNED` / `READY` / `REVIEW` / `REVISE` / `USER_APPROVED` / `BLOCKED`

**Creative Approval != Evidence Verification.** Creative acceptance does not prove exact-file identity, provenance, claim truth, or final delivery safety.

## One-job rule

Execute one Asset Packet at a time: one Asset ID, one channel/page role, one primary shopper task/message, output quantity 1.

Distinct final channel roles remain separate production jobs unless Planning explicitly authorizes reuse/derivative intent.

Batch continuation may preserve art direction only after the user accepts that direction. **Same art direction != same composition.**

## Minimal set context

Every v0.3.3 Asset Packet must carry:

- current Page Visual System direction;
- nearest same-region/page-region neighbor summaries;
- current Evidence Mode.

A missing `evidence_mode` or `set_context` makes the packet invalid.

## Evidence Mode

- `SOURCE_FAITHFUL` — faithful product/pack/offer identity is intrinsic; required identity/proof evidence must exist.
- `CREATIVE_MOCK` — lifestyle/atmosphere/spatial creative work may tolerate missing proof-grade evidence, but still requires identity evidence needed to keep the product faithful. Generated scene details are not Product Truth.
- `PROOF_VISUAL` — factual mechanism/UI/installation/dimension/compatibility/performance proof requires authoritative identity and proof evidence, and the final auditor packet must carry exact claim/fact/authoritative-source bindings.

Keep `identity_required` and `proof_required` source lists separate. Missing identity evidence blocks every mode. Missing proof-only evidence may produce `READY_WITH_LIMITATION` only for `CREATIVE_MOCK`; it cannot make a `PROOF_VISUAL` final-consumable.

## Candidate identity and Selection Lock

Every generated alternative for one Asset ID is a distinct candidate.

When the user selects an exact candidate:

1. mark it `USER_SELECTED`;
2. bind `selected_candidate_id` and exact `current_output_ref`;
3. set the asset to `USER_APPROVED`;
4. preserve candidate history and continue to the next required asset.

Until explicit reopen intent, do not replace the output, add a new candidate, or roll status back to `REVIEW` / `REVISE`.

## Set-level Creative QA

Asset-level quality does not guarantee page-level quality. Review the ordered set for scene, composition, tone/brightness, product scale, proof-form, and adjacent message-role repetition.

Before Production Freeze, record final whole-set/contact-sheet QA for the **current exact outputs**:

- `status`: `CLEAR` or explicit `USER_ACCEPTED`;
- `reviewed_asset_ids`: exact required Asset-ID set;
- `reviewed_output_refs`: exact Asset ID → current output ref mapping;
- `visual_review_ref`: reference to the reviewed set/contact sheet.

Any later output change makes the prior set QA stale.

## Required production set

Production completeness is not derived from `asset_set` alone. The current required IDs are the union of:

- authoritative `asset_set` entries;
- required IDs still present in the current page plan / required page regions;
- still-required blocked asset roles.

A required blocked asset must remain visible as a blocker; it cannot disappear from completion accounting merely because no final file exists yet. The required set must be non-empty for a Demo project to become ready for Hardening.

## Production Freeze v0.3.3

The Freeze records:

- positive `expected_assets` matching the current required set;
- `required_asset_ids`;
- exact `user_approved_assets`;
- `blocked_assets`;
- `revision_pending`;
- `approved_outputs`, keyed by Asset ID and containing exact `candidate_id` and `output_ref`;
- current `set_qa_status`;
- `ready_for_hardening`.

`ready_for_hardening=true` only when the required set is non-empty, every required asset is creatively approved and exactly bound, no blocker/revision remains, and current Set QA is ready. Hardening recomputes this contract rather than trusting the declared boolean.

## Scope Delta

Production may apply an explicit removal-only scope delta when the user narrows an already planned set. Removal updates `asset_set`, page order, and `page_visual_system` together.

Added assets or changes to role/message/evidence requirements cross Planning ownership. Return to Planning for a revised handoff.

## Smallest Sufficient Cleanup

Classify problems as `SINGLE_ASSET_DEFECT`, `SET_REPETITION`, `WRONG_MESSAGE_ROLE`, `EVIDENCE_LIMITATION`, `CLAIM_ERROR`, or `PRODUCT_DISTORTION`.

Default to the smallest sufficient intervention. Preserve approved assets where possible; do not broaden one defect into whole-set regeneration by default.

## Context firewall

Build image-generation/edit context only from the current Asset Packet and referenced sources. Do not inject Project State, auditor, gate, parity, or stage-status narration.

## Completion

Stage 8 completes only when the full current required production set is accounted for and current exact-output-bound whole-set QA is ready. Priority proof coverage alone is not completion.
