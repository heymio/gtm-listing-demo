# Executable gates

Compute gates from Delivery State instead of trusting agent-authored declarations.

- `CHANNEL_MODULE_BUDGET_GATE` uses the current verified channel/account declared module ceiling, never a global hard-coded marketplace number.
- `APPROVAL_PROVENANCE_GATE` binds locked asset/plan hashes to explicit user approvals.
- `MODULE_ORIGIN_GATE` prevents implementation from changing locked module type/interaction.
- `TRANSFORM_AUTH_GATE` requires explicit transform authorization.
- `ASSET_SLOT_GATE` checks required exact assets and allowed scope.
- `PRODUCTION_FREEZE_GATE` requires the exact required Asset-ID set.
- `PRE_DEMO_ASSET_GATE` requires final auditor evidence for exact hashes.
- `FRONTEND_FIDELITY_GATE` separates native shell evidence from platform capability.
- `DELIVERY_PARITY_GATE` compares final implementation against locked plan and assets.
