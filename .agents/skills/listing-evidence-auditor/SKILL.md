---
name: listing-evidence-auditor
description: Use when independently reconciling final listing asset claims against real-file identity, approval provenance, visual role evidence, proof-claim evidence, and required asset-set completeness.
---

# Listing Evidence Auditor

## Trust boundary

The auditor is the exact-file evidence boundary. It does not decide marketing strategy and it does not repair creative work.

**Do not trust filenames. Do not trust Asset IDs. Do not trust agent-authored hashes.** Recompute physical identity from real files inside the allowed project root.

## Inputs

Audit input may contain candidate claims about:

- Asset ID and path;
- claimed role and allowed slot/page scope;
- current Evidence Mode;
- claimed approval event;
- claimed parent asset and transform;
- required slots / asset set;
- prior exact locked assets;
- expected visual roles;
- for `PROOF_VISUAL`, exact claim IDs, fact text, and authoritative source IDs.

These are claims to reconcile, not proof by themselves.

## Physical identity

For supported PNG / JPEG / WebP assets, recompute:

- path containment;
- file existence;
- SHA-256;
- byte size;
- signature family;
- extension family;
- positive dimensions;
- format completeness/integrity;
- real image decode and pixel load through Pillow.

v0.3.3 requires complete supported files rather than a plausible header alone. PNG checks IHDR/IDAT/IEND structure, CRC and zlib integrity; JPEG checks SOI/EOI and dimensions; WebP checks RIFF/WEBP size/dimensions. All supported formats must also pass a real Pillow verify/load cycle.

If the real decoder is unavailable, physical hard-verification does not PASS. Reject unsupported/invalid signatures, truncated or corrupt files, extension/signature mismatch, path escape, missing files, zero/invalid dimensions, and malformed identity records.

## Approval binding

Explicit user approval is valid for final use only when it binds the exact current physical SHA-256, expected visual role, and exact approved slot/page/offer scope.

A same-name or same-Asset-ID replacement with different bytes does not inherit prior approval. Exact recovery is allowed only when the physical hash, role, and scope match the previously locked exact asset.

## Provenance

Use explicit states such as:

- `ORIGINAL_VERIFIED`;
- `DERIVATIVE_VERIFIED`;
- `EXACT_RECOVERY_VERIFIED`;
- `PROVENANCE_UNKNOWN`;
- `PROVENANCE_CONFLICT`.

A derivative needs an auditable parent and explicit transform authorization. Planner claims cannot self-prove provenance.

## Semantic visual role

Semantic role review is separate from physical identity.

A role review from `human` may be trusted. A result labeled `independent_context` is trusted only when the host actually provides an independent context. Loading this auditor inside the same model/chat context is not independent semantic review.

Same-agent inline review must not self-certify `ROLE_MATCH`. When independence is unavailable, unresolved role evidence remains `ROLE_AMBIGUOUS` / `NOT_VISUALLY_AUDITED` and downstream state remains `HUMAN_REVIEW_REQUIRED` or `UNVERIFIED` as appropriate.

## PROOF_VISUAL claim binding

A `PROOF_VISUAL` must carry a non-empty set of exact claim bindings. Each binding includes:

- `claim_id`;
- exact `fact` being represented;
- one or more `authoritative_source_ids`.

File/role/approval agreement is not sufficient to prove a claim is true. Final-consumable proof status additionally requires trusted human review or genuinely independent semantic claim review whose `reviewed_claim_ids` exactly match the bound claims.

`CLAIM_MISMATCH` invalidates the asset. Missing, incomplete, same-context, or partially scoped claim review keeps the asset `HUMAN_REVIEW_REQUIRED` / non-final-consumable.

## Fail fast on ambiguous identity

Before building dictionaries/indexes, reject duplicate identifiers for:

- `assets.asset_id`;
- `approval_events.approval_event_id`;
- `prior_locked_assets.asset_id`;
- `slots.slot_id`;
- `expected_visual_roles.asset_id`;
- duplicate `claim_id` inside one `PROOF_VISUAL` binding set.

This prevents later rows from silently overwriting contradictory evidence.

## Required asset-set completeness

Every required slot must point to a final-consumable exact asset with matching approved scope. One invalidated, missing, unverified, claim-unverified, or out-of-scope required member blocks the asset-set gate.

## Effective states

Typical states include:

- `VERIFIED`;
- `HUMAN_APPROVED`;
- `PHYSICALLY_VERIFIED_ONLY`;
- `HUMAN_REVIEW_REQUIRED`;
- `UNVERIFIED`;
- `INVALIDATED`.

Creative `USER_APPROVED` is not automatically an evidence state.

## Independence and repair rule

The auditor **must not repair** a failing asset or silently change its role, source, approval, claim, or scope. Return evidence findings to the owning Planning / Production / Hardening plane.

If independent semantic review is needed, use a genuinely **independent context** or an appropriate human reviewer; a caller flag or same-context self-description is insufficient.
