# Global output contracts

Detailed machine contracts are owned by `listing-planning`, `listing-production`, `listing-hardening`, and `listing-evidence-auditor`. This reference summarizes the user-facing global objects.

## Project Definition

Keep these separate:

```yaml
market:
  country: DE
locale:
  id: de-DE
region_overlays:
  - EU
channel:
  type: amazon
  site: project-defined
category: project-defined
product:
  name: Example Product
offers:
  - single
page_targets:
  - single-listing
```

## Product / evidence baseline

Maintain Source Registry, Product Truth / Fact Ledger, conflicts, missing evidence, claim readiness, Market Evidence Registry, and Page Target / Product Boundary Matrix.

A market label without project/category evidence cannot populate consumer insight.

## Creative Strategy Kernel

Contains compressed production-relevant conclusions such as target user, core tension/promise, purchase reasons, barriers, Reasons to Believe, message priority, market implications, proof principles, visual direction, and anti-patterns.

## Production Handoff

The complete handoff contains:

- project market/locale/channel/category/offer/page target;
- approved page/region order;
- **complete current asset set**;
- per-asset role, slot, primary message, Evidence Mode, and status;
- source asset bindings and product invariants;
- Creative Strategy reference;
- global visual direction and benchmarks;
- Page Visual System direction for every current asset;
- prohibited output and blocked assets.

A current asset without Evidence Mode or Page Visual System direction is invalid in v0.3.2.

## Asset Ledger

Records candidate history, exact selected candidate/output reference, creative status, approval reference, reopen history, and final whole-set QA.

A user-selected output is Selection-Locked until explicit reopen.

## Final whole-set QA

Bind the exact current set, not only Asset IDs:

```yaml
set_qa:
  status: CLEAR
  reviewed_asset_ids:
    - G1
    - G2
  reviewed_output_refs:
    G1: file:g1-v1
    G2: file:g2-v2
  visual_review_ref: contact-sheet:final-v1
```

Any later output change makes the old set review stale.

## Production Freeze

Answers whether the complete current creatively approved exact-output set is ready for Hardening. It does not claim evidence verification.

## Delivery State

Hardening records current verified channel capability, exact locked assets/approval provenance, locked module/slot plan, asset-slot contract, implementation state, Production Freeze, auditor evidence, frontend fidelity, and final parity.

Machine-computed gates, not agent-authored declarations, decide final readiness.

## Review Mode

Review Mode may expose internal status/open items for review. Consumer Mode hides workflow labels, provisional notes, and internal gate narration while remaining semantically complete.
