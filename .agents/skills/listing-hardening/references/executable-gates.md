# Executable gates

Compute gates from Delivery State and exact evidence. Never trust an agent-authored PASS declaration as a substitute for the executable result.

- `CHANNEL_MODULE_BUDGET_GATE` uses the current verified site/account declared module ceiling, never a global hard-coded marketplace number.
- `APPROVAL_PROVENANCE_GATE` binds locked asset/plan hashes to explicit user approvals.
- `MODULE_ORIGIN_GATE` prevents implementation from changing locked module type/interaction.
- `TRANSFORM_AUTH_GATE` requires explicit transform authorization.
- `ASSET_SLOT_GATE` checks required exact assets, implemented asset-bearing slot contracts, and allowed scope.
- `PRODUCTION_FREEZE_GATE` recomputes the non-empty required Asset-ID set, rejects blockers/revisions/stale Set QA/not-ready state, and requires exact `asset_id -> candidate_id -> output_ref` binding.
- `PRE_DEMO_ASSET_GATE` is mandatory for Demo Delivery State 0.2 and requires final auditor evidence for exact current hashes; caller input cannot disable it.
- `FRONTEND_FIDELITY_GATE` verifies evidence-backed channel-native shell/order/interaction or an explicitly labeled Content Review fallback with exact user approval provenance.
- `DEMO_RUNTIME_GATE` requires browser-runtime evidence bound to the exact Demo SHA, zero network requests, 1440px and 390px layout checks, and actual previous/next transitions when a carousel is present.
- `DELIVERY_PARITY_GATE` compares final implementation against the locked plan and asset bindings.

A mandatory gate that lacks executable evidence remains `UNVERIFIED` / `BLOCKED` or `FAIL`; `N/A` is not a caller-controlled bypass for Demo hardening.
