# Global QA checklist

## Product and offer QA

- Product facts, offer/page boundaries, and conditions match evidence.
- Earlier-generation capabilities are not silently inherited.
- Required P0/P1 and lower-priority final page roles needed by the Demo are covered.

## Claim QA

- Conflict/missing/prohibited facts do not enter consumer copy.
- Conditional claims retain their conditions.
- Current price, availability, certification/testing/performance/service terms are verified before formal release when relevant.
- Unsupported absolute/comparative/superlative claims are rejected.
- `PROOF_VISUAL` assets carry exact claim IDs, fact text, authoritative source IDs, and trusted review covering those exact claims.

## Channel QA

- Editable regions, interactions, and current account/site capabilities are verified.
- Module/slot count is checked against current verified capability evidence rather than a generic hard-coded ceiling.
- Platform-generated regions are not treated as brand-controlled.
- Platform Capability evidence remains separate from Frontend Visual evidence.
- Channel-native frontend fidelity is evidence-backed and exact-payload approved; otherwise use an explicitly labeled Content Review Demo.

## Market and locale QA

- Market insights have project/category evidence.
- Locale profiles define language/formatting, not personas or priorities.
- Region overlays do not replace country/locale research.
- Consumer copy is native and channel-appropriate.

## Asset-level Creative QA

Each final asset has one dominant shopper task/message, appropriate product prominence, direct visual proof where required, controlled composition, credible realism, channel fit, source-faithful product identity, and explicit Evidence Mode.

## Set-level Creative QA

Review the ordered set for scene/composition/tone/product-scale/proof-form repetition and adjacent message redundancy. The final whole-set/contact-sheet review must bind exact current output refs; replacing one selected output invalidates the prior final set review.

## Evidence / Hardening QA

- Creative `USER_APPROVED` is not treated as evidence verification.
- Required final IDs are recomputed from all authoritative plan/implementation/contract/blocker sources; one list cannot override the rest.
- Demo required set is non-empty and mandatory pre-Demo audit cannot be disabled by caller state.
- Production Freeze has no blockers/revisions, current Set QA, `ready_for_hardening=true`, and exact `asset_id -> candidate_id -> output_ref` bindings.
- Real final files are fingerprinted from disk and supported raster formats pass Pillow verify/load.
- Approval binds exact current SHA, role, and scope.
- Duplicate identifiers fail before dictionary/index overwrite.
- Same-context semantic review does not self-certify independence.
- Required asset-set completeness and exact slot scope are verified before Demo consumption.

## Standalone Demo QA

- Final project deliverable is one `.html` file, not a Demo ZIP plus assets folder.
- Runtime images/resources are portable embedded `data:` resources; external/local dependencies are rejected.
- Mixed/external `srcset`, session-only literal `blob:` resources, external CSS/JS, SVG external refs, CSS imports, and external/local `url(...)` references including inline styles are rejected.
- Responsive viewport, width breakpoint, and responsive image behavior are present.
- Static pages without carousel remain valid.
- If a carousel is present, static structure is checked but interaction remains `RUNTIME_REQUIRED`; keyword presence or unused JavaScript text is never hard PASS.

## Runtime QA

Browser runtime evidence is bound to the exact final HTML SHA. It must observe zero external network requests and verify at 1440px desktop and 390px mobile:

- no horizontal overflow;
- no broken images;
- no clipped primary copy/controls;
- actual next/previous carousel state transitions when carousel exists;
- Review Mode does not corrupt Consumer Mode.

If Playwright/Chromium verification cannot be performed, `DEMO_RUNTIME_GATE` remains `UNVERIFIED/BLOCKED`.

## Distribution / release QA

- one-install and Codex bundles are deterministic for identical source trees;
- packaging rejects symlink inputs and validates extracted packages;
- release build validates the exact candidate SHA under read-only permissions;
- publish job does not check out or execute repository code, receives write permission only when publishing, rechecks current main and checksums, handles absent tags safely, and targets the repository explicitly.

## Domain leakage QA

- generic workflow files contain no private company/product data;
- channel profiles contain no category selling points;
- locale profiles contain no consumer stereotypes;
- region overlays contain no regional persona;
- category/product/site-specific logic appears only in explicit profiles, overlays, examples/evals, private context, or project evidence.
