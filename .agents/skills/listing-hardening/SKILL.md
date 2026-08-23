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

Run the **mandatory full audit** on the final production set through `listing-evidence-auditor` before Demo Assembly when final delivery is requested. Fresh Stage 6.5 remains lightweight source intake; targeted early audit is reserved for inherited/reused exact assets.

Creative Approval is not Evidence Verification.

## v0.3.3 fail-closed Delivery State

Delivery State 0.2 is the Demo-delivery schema. Mandatory pre-Demo verification is a workflow rule, not a caller-controlled option: `pre_9_required=false` cannot disable it, and a zero-size required final asset set cannot pass.

Required final assets are recomputed as a union across authoritative locked-plan, implementation, asset-slot-contract, explicit required-ID, blocker, and revision state. One non-empty source must never override another.

Production Freeze is revalidated here. Hardening requires:

- positive expected asset count matching the recomputed required set;
- exact required `user_approved_assets` set;
- no `blocked_assets` or `revision_pending` assets;
- Set QA status `CLEAR` or `USER_ACCEPTED`;
- `ready_for_hardening=true`;
- exact `asset_id -> candidate_id -> output_ref` binding for every required asset.

Agent-authored declarations do not replace executable gate results.

## Generic channel capability

Do not hard-code one marketplace's module ceiling into the global core. `CHANNEL_MODULE_BUDGET_GATE` consumes the current project's verified site/account capability such as `channel.capabilities.declared_max_modules`. Missing capability remains `UNVERIFIED`.

## Canonical final gates

Keep these questions separate:

- `PRODUCTION_FREEZE_GATE`: is the exact creatively approved current set complete and internally ready?
- `PRE_DEMO_ASSET_GATE`: do exact final files match evidence/approval scope?
- `MODULE_ORIGIN_GATE`: does implementation still originate from the approved plan?
- `ASSET_SLOT_GATE`: are exact assets bound to allowed required slots?
- `FRONTEND_FIDELITY_GATE`: is the claimed shell/order/interaction supported by evidence and approval?
- `DEMO_RUNTIME_GATE`: did the exact final HTML pass no-network browser QA?
- `DELIVERY_PARITY_GATE`: does the assembled implementation match the locked plan and bindings?

One PASS does not substitute for another.

## Frontend fidelity

Platform Capability evidence is separate from Frontend Visual evidence. Official documentation can prove supported capabilities but not the exact current consumer-facing shell.

`CHANNEL_NATIVE` requires evidence-backed shell/order/regions/desktop/interactions/content regions and no fabricated unsupported UI. If native fidelity cannot be supported, use an explicitly labeled `CONTENT_REVIEW` mode rather than inventing marketplace/retailer chrome. Frontend fidelity approval is bound to the exact approved payload.

## Final Demo output

The final project Demo is one **single standalone HTML** file. Run `scripts/validate_demo_html.py` as static preflight and `scripts/validate_demo_runtime.py` for hard runtime proof.

Static validation rejects external/local runtime dependencies, SVG external resources, inline-style external URLs, and other nonportable resources. Static carousel markup/JavaScript inspection never upgrades interaction to hard PASS.

Browser runtime verification is bound to the exact Demo SHA, observes/blocks external network requests, runs at 1440px desktop and 390px mobile, checks horizontal overflow, broken images and clipped primary elements, and actually clicks both carousel directions when a carousel is present.

If Playwright/Chromium cannot run, `DEMO_RUNTIME_GATE` remains `UNVERIFIED/BLOCKED`; source inspection cannot claim PASS.

## Final QA

Use `references/final-qa.md`. Consumer Mode must remain free of internal workflow labels/notes. Review Mode, if present, must not corrupt the consumer layout.
