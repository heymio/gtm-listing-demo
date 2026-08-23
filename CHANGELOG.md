# Changelog

## 0.3.3 — Global fail-closed hard verification

- Made Delivery State 0.2 fail closed: mandatory pre-Demo verification cannot be disabled by caller state and an empty required asset set cannot pass.
- Recomputed required final assets as a union across locked plan, implementation, asset-slot contracts, explicit required IDs, and blocker/revision state instead of trusting one non-empty source.
- Strengthened Production Freeze with exact `asset_id -> candidate_id -> output_ref` bindings, blocker/revision rejection, current Set QA requirements, and recomputed readiness.
- Added canonical executable `FRONTEND_FIDELITY_GATE` and `DEMO_RUNTIME_GATE` while retaining channel capability limits as profile/site/account evidence rather than fixed marketplace defaults.
- Added real Pillow-backed PNG/JPEG/WebP decode/load verification; missing decoder or damaged pixel data cannot receive physical hard-verification PASS.
- Added `PROOF_VISUAL` claim/fact/authoritative-source binding and trusted claim-review requirements.
- Separated standalone HTML static preflight from runtime interaction proof; added SVG/inline-style external-resource rejection and removed static keyword-based carousel hard PASS.
- Added real no-network Playwright/Chromium QA at 1440px and 390px with broken-image, overflow, clipping, and actual carousel next/previous verification.
- Made one-install and five-Skill Codex ZIPs deterministic, symlink-safe, reproducible, and self-validating after extraction.
- Added exact-SHA release automation with a read-only validation/build job and isolated no-checkout publish job; absent-tag handling and explicit repository targeting follow the hardened Japan v0.3.3 release lessons.
- Preserved Global market/locale/region/channel/category/profile architecture and excluded Japan/site/product-specific defaults from the generic core.

## 0.3.2 — Global creative-first execution baseline

- Replaced the monolithic runtime with a thin `$gtm-listing-demo` Router plus sibling `listing-planning`, `listing-production`, `listing-hardening`, and `listing-evidence-auditor` Skills while retaining one normal user invocation.
- Preserved the existing global Market / Locale / Region Overlay / Channel / Category / Private Overlay / Project Evidence separation and existing multi-market profile coverage.
- Added Major Stage Checkpoints, Transition Command behavior, Context Firewall, concise `Done / Open / Next` transitions, and a two-attempt autonomous Retry Budget.
- Added formal Planning state including Creative Strategy Kernel, structured Production Handoff, **Complete Demo-Required Production Set**, Page Visual System, and one Evidence Mode per final asset.
- Added strict structured Planning contract validation and a generic Account Capability Profile resolver for recent, correctly scoped, non-conflicted channel/account capability reuse.
- Added one-job Asset Packets, artifact-first production, identity-vs-proof source separation, candidate history, full Selection Lock, set-level Creative QA, exact-output-bound whole-set review, removal-only Scope Delta, and Smallest Sufficient Cleanup.
- Added independent exact-file Evidence Auditor architecture with real-file SHA/signature/dimension checks, exact approval binding, duplicate-identifier fail-fast behavior, required asset-set completeness, and explicit same-context semantic-review limitations.
- Added generic Delivery State and executable hardening gates for channel budget, approval provenance, module origin, transform authorization, asset-slot integrity, Production Freeze, Pre-Demo exact-file evidence, frontend fidelity, and delivery parity. Channel limits come from current verified capability evidence rather than a marketplace-specific hard-coded ceiling.
- Added channel-native fidelity rules separating Platform Capability evidence from Frontend Visual evidence, with `Content Review Demo` fallback when a native shell cannot be verified.
- Added a final project Demo contract of one standalone `.html` file with portable embedded `data:` resources, inline CSS/JS, external/local dependency rejection, mixed/external `srcset` rejection, session-only `blob:` rejection, responsive validation, and optional-carousel-aware interaction validation.
- Added mandatory runtime QA requirements at 1440px desktop and 390px mobile; when browser/runtime verification is unavailable, mobile/interaction QA remains `BLOCKED` rather than being self-certified.
- Added a one-install compatibility ZIP embedding the four internal execution/audit Skills plus a single-context semantic-audit limitation, and a five-Skill repository/Codex bundle. Packaging performs embedded behavioral smoke tests.
- Added global v0.3.2 regression coverage derived from later workflow lessons while excluding market-specific consumer assumptions, site-specific account limits, private brand facts, and product-specific pilot content from generic defaults.

## 0.2.0 — 2026-08-19

- Published the first standalone public core.
- Generalized the workflow across markets, locales, channels, categories, and offer variants.
- Separated Channel, Locale, Region, Category, Private Overlay, and Project Evidence responsibilities.
- Added Amazon, DTC, retailer PDP, and generic marketplace profiles.
- Added `ja-JP`, `en-US`, `de-DE`, and `it-IT` locale profiles.
- Added an EU region overlay that does not create a consumer persona.
- Added category and profile templates.
- Added cross-market, cross-channel, and cross-category regression evals.
- Added domain-leakage validation and Skill ZIP packaging.
