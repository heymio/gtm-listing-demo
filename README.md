# gtm-listing-demo

`gtm-listing-demo` is a reusable global workflow for turning product evidence into market- and channel-specific listing strategy, focused visual production, evidence-safe final assets, and a verified review Demo.

It is intentionally **not hard-coded to one country, language, marketplace, brand, or product category**.

## One normal invocation

```text
$gtm-listing-demo
```

A normal project can run from source intake through strategy, visual production, hardening, and Demo review without manually invoking the internal execution Skills.

## Global configuration model

The global core keeps these layers separate:

```text
Core Workflow
├── Channel Profile
├── Locale Profile
├── Region Overlay
├── Category Overlay
├── Brand / Private Overlay
└── Project Evidence
```

`market`, `locale`, `region_overlays`, `channel`, `site/account capability`, `category`, `offer`, and `page_targets` remain distinct inputs. Locale and region profiles do not create consumer stereotypes; actual project evidence determines consumer needs and product truth.

## Execution architecture

v0.3.3 retains the v0.3.2 creative-first architecture and hardens the final verification boundary:

```text
$gtm-listing-demo
        ↓
Thin Router
        ↓
listing-planning      Stage 0–7
        ↓
listing-production    Stage 7.5–8
        ↓
listing-hardening     Stage 8.5–10
        ↓
listing-evidence-auditor
```

The repository contains five sibling Skills under `.agents/skills/`.

### Planning: think deeply

Planning preserves product/offer truth, claims, VOC, market and localization research, selected profiles, channel architecture, and message strategy. It ends with formal Project Brief / Project Definition, Creative Strategy Kernel, Production Handoff, **Complete Demo-Required Production Set**, **Page Visual System**, and one **Evidence Mode** per final asset.

Priority proof coverage is not the same as a complete Demo asset set. Same art direction does not imply the same composition.

Evidence Mode is one of:

```text
SOURCE_FAITHFUL
CREATIVE_MOCK
PROOF_VISUAL
```

Product-identity evidence is separate from proof-grade evidence. A Creative Mock may tolerate missing proof evidence with an explicit limitation, but may not invent product identity. `PROOF_VISUAL` in v0.3.3 requires explicit claim/fact/authoritative-source binding before it can become final-consumable.

A reusable Account Capability Profile may answer recurring channel/account questions only when the record is recent, structurally valid, correctly scoped, and non-conflicted.

### Production: produce narrowly

Production remains artifact-first with one-job Asset Packets, Production Context Firewall, candidate history, exact Selection Lock, asset-level and set-level Creative QA, exact-output-bound whole-set review, removal-only Scope Delta, and Smallest Sufficient Cleanup.

v0.3.3 strengthens Production Freeze:

- required IDs are the union of `asset_set`, page-plan requirements, and still-required blocked roles;
- every final Asset ID binds to an exact selected `candidate_id` and `output_ref`;
- a non-empty complete asset set is required;
- blockers, revision-pending assets, stale Set QA, or missing exact output bindings prevent hardening readiness.

Creative Approval remains separate from Evidence Verification.

### Hardening: verify rigorously

For Demo Delivery State 0.2, hard verification is fail closed. Caller-authored `pre_9_required=false` cannot disable mandatory pre-Demo verification, and an empty required asset set cannot pass.

Hardening recomputes required assets from all authoritative sources instead of trusting one non-empty list. Canonical final gates include:

```text
PRODUCTION_FREEZE_GATE
PRE_DEMO_ASSET_GATE
FRONTEND_FIDELITY_GATE
DEMO_RUNTIME_GATE
```

The global core never hard-codes one marketplace's account/module ceiling. Channel limits come from current verified site/account capability evidence.

`FRONTEND_FIDELITY_GATE` supports evidence-backed channel-native fidelity and a clearly labeled Content Review fallback when native shell/order/interactions cannot be verified.

## Evidence auditor

`listing-evidence-auditor` is the exact-file trust boundary. v0.3.3 adds real Pillow decode/load on top of structural format validation:

- PNG: complete IHDR/IDAT/IEND, CRC and zlib integrity;
- JPEG: SOI/EOI and valid dimensions;
- WebP: RIFF/WEBP size and valid dimensions;
- all supported formats: real decoder verification.

Missing Pillow or damaged pixel data cannot receive physical hard-verification PASS.

`PROOF_VISUAL` assets carry exact claim IDs, facts, and authoritative source IDs. File/role/approval agreement alone is insufficient; trusted human or genuinely independent claim review must cover the exact bound claims. Same-context semantic review cannot self-certify independent evidence.

## Final Demo contract

The final project Demo is one standalone `.html` file with embedded `data:` resources and inline CSS/JavaScript. Static preflight rejects local/external resources, SVG external references, inline-style external URLs, mixed/external `srcset`, external scripts/stylesheets, and session-only literal `blob:` resources.

A static page without a carousel is valid when the page design does not require one. If carousel markup is present, static structure checks are only a preflight; static JavaScript keywords never equal interaction hard PASS.

Final runtime QA uses Playwright/Chromium on the exact HTML SHA with network blocked/observed and checks:

- **1440px desktop**;
- **390px mobile**;
- zero external network requests;
- no horizontal overflow;
- no broken images;
- no clipped primary copy/controls;
- actual carousel next and previous transitions when a carousel is present.

If browser/runtime verification cannot run, `DEMO_RUNTIME_GATE` remains `UNVERIFIED/BLOCKED`.

## Built-in global profiles

Channels include generic Amazon, DTC product page, retailer PDP, and generic marketplace fallback. Locales include `ja-JP`, `en-US`, `de-DE`, and `it-IT`; EU common region overlay is available. Category selling logic remains evidence-driven. Channel/site/account-specific capabilities must still be verified for the actual project.

Public compatibility profiles and Planning runtime profiles are mirror-checked in CI so they cannot silently drift.

## Checkpoints and retry behavior

Major Stage Checkpoints remain the default with concise `Done / Open / Next`. Explicit transition commands advance the workflow. Ambiguous pause wording must not be interpreted as unconditional stage advancement; current-asset acceptance stays local to Production unless stage completion conditions are satisfied. Autonomous retry budget remains bounded.

## Hard-verification dependencies

Repository/Codex hard verification requires:

```bash
python3 -m pip install Pillow playwright
python3 -m playwright install chromium
```

Linux CI uses:

```bash
python3 -m playwright install --with-deps chromium
```

## Distribution

### Repository / Codex bundle

```bash
python3 scripts/package_codex_bundle.py
```

Output: `dist/gtm-listing-demo-codex-bundle.zip`.

### One-install compatibility package

```bash
python3 .agents/skills/gtm-listing-demo/scripts/package_skill.py
```

Output: `dist/gtm-listing-demo.skill.zip`.

Both v0.3.3 packages are deterministic and symlink-safe. The one-install package excludes repository-only selftests and runs package-local `validate_install.py` after extraction. The Codex bundle extracts itself and runs `validate_overlay.py`. The one-install bundle remains a single model context, so embedded auditor loading does not create independent semantic review.

## Validation

```bash
python3 .agents/skills/gtm-listing-demo/scripts/selftest_fail_closed_v033.py
python3 .agents/skills/gtm-listing-demo/scripts/validate_skill.py
python3 .agents/skills/gtm-listing-demo/scripts/selftest_router.py
python3 .agents/skills/listing-planning/scripts/selftest_planning.py
python3 .agents/skills/listing-production/scripts/selftest_production.py
python3 .agents/skills/listing-hardening/scripts/selftest_hardening.py
python3 .agents/skills/listing-hardening/scripts/selftest_demo_output.py
python3 .agents/skills/listing-hardening/scripts/selftest_demo_runtime_v033.py
python3 .agents/skills/listing-evidence-auditor/scripts/selftest_auditor.py
python3 .agents/skills/listing-evidence-auditor/scripts/selftest_image_decode_v033.py
python3 .agents/skills/gtm-listing-demo/scripts/selftest_project_state_validator.py
python3 .agents/skills/gtm-listing-demo/scripts/selftest_distribution_v033.py
python3 .agents/skills/gtm-listing-demo/scripts/validate_overlay.py
python3 .agents/skills/gtm-listing-demo/scripts/package_skill.py
python3 scripts/package_codex_bundle.py
```

## Release model

v0.3.3 release automation validates the exact candidate SHA in a read-only build job. Pull requests exercise that complete build path but cannot publish. Only a push to current `main` can enter the separate publish job, which has `contents: write`, does not check out/execute repository code, rechecks current-main SHA, release metadata, absent/existing tag state, and download-local checksums, then publishes the immutable Release using an explicit repository target.

## Public and private boundary

The public repository remains generic. Market/site-specific rules belong in explicit profiles; brand/account facts and confidential project data belong in private overlays/project evidence. Product-pilot learnings may become generic regressions only after product-specific content is removed.

## Version

`0.3.3`

## License

MIT.
