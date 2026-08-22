---
name: listing-hardening
description: Use when verifying Stage 8.5–10 final listing assets, channel/page integrity, standalone Demo assembly, delivery parity, and final technical QA.
---

# Listing Hardening

## Core question

Are the exact final artifacts evidence-safe, channel-correct, technically valid, and ready to assemble/deliver?

## Plane boundary

This Skill owns Stage 8.5, Stage 9, and Stage 10. It consumes Production Freeze, exact final files, locked page/slot requirements, current channel/frontend evidence, and relevant approval state. It does not perform consumer strategy, VOC research, or visual generation brief work.

## Stage 8.5 exact-file audit

Run the **mandatory full audit** on the final production set through `listing-evidence-auditor` before Demo Assembly when final delivery is requested.

Fresh Stage 6.5 remains lightweight source intake. A **targeted early audit** is appropriate only for inherited/reused previously approved exact assets; the mandatory full audit belongs here after final assets exist.

Creative Approval is not Evidence Verification.

## Delivery State

Use a machine-readable Delivery State for:

- current channel/account capability used for the locked plan;
- exact locked assets and approval provenance;
- locked module/slot plan and canonical plan hash;
- asset-to-slot contract;
- implementation state;
- Production Freeze;
- exact auditor evidence;
- frontend fidelity evidence;
- delivery parity.

Run `scripts/validate_delivery_state.py` when available. Agent-authored claims do not replace executable gate results.

## Generic channel capability

Do not hard-code one marketplace's module ceiling into the global core. `CHANNEL_MODULE_BUDGET_GATE` consumes the current project's verified channel/account capability such as `channel.capabilities.declared_max_modules`.

If the relevant current capability cannot be verified, keep the gate `UNVERIFIED` rather than guessing from another marketplace/account.

## Gate separation

Keep these questions separate:

- `PRODUCTION_FREEZE_GATE`: is the complete creatively approved current set present?
- `PRE_DEMO_ASSET_GATE`: do exact final files match evidence/approval scope?
- `MODULE_ORIGIN_GATE`: does implementation still originate from the approved plan?
- `ASSET_SLOT_GATE`: are exact assets bound to allowed required slots?
- `FRONTEND_FIDELITY_GATE`: can a native channel shell be supported by current frontend evidence?
- `DELIVERY_PARITY_GATE`: does the assembled implementation match the locked plan and bindings?

One PASS does not substitute for another.

## Frontend fidelity

Platform Capability evidence is separate from Frontend Visual evidence. Official documentation can prove supported capabilities but not the exact current consumer-facing shell.

If a native shell cannot be verified, use a clearly labeled `Content Review Demo` rather than inventing marketplace/retailer chrome.

## Final Demo output

The final project Demo is one **single standalone HTML** file. Read `references/demo-output.md` and run `scripts/validate_demo_html.py` on the exact final file.

Static validation is necessary but not sufficient. Final runtime verification must include 1440px desktop and 390px mobile. If browser/runtime verification cannot be performed, interaction/mobile QA is **BLOCKED**; source inspection alone cannot claim PASS.

## Final QA

Use `references/final-qa.md`. Consumer Mode must remain free of internal workflow labels/notes. Review Mode, if present, must not corrupt the consumer layout.
