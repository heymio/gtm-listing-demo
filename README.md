# gtm-listing-demo

`gtm-listing-demo` is a reusable global workflow for turning product evidence into market- and channel-specific listing strategy, focused visual production, evidence-safe final assets, and a verified review Demo.

It is intentionally **not hard-coded to one country, language, marketplace, brand, or product category**.

## One normal invocation

Use one repository and one user-facing Skill:

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

- **Channel profiles** define editable regions, module/slot families, interaction contracts, and verification needs.
- **Locale profiles** define language and formatting rules, not consumer stereotypes.
- **Region overlays** define cross-country verification obligations, not personas.
- **Category overlays** are optional and evidence-driven.
- **Private overlays** hold company rules, internal capabilities, confidential facts, and approvals.
- **Project evidence** determines actual consumer needs, scenarios, keywords, claims, and product truth.

`market`, `locale`, `region_overlays`, `channel`, `category`, `offer`, and `page_targets` remain distinct inputs.

## Creative-first execution architecture

v0.3.2 separates stage-local execution behind a thin router:

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

The repository contains five sibling Skills:

```text
.agents/skills/
├── gtm-listing-demo/
├── listing-planning/
├── listing-production/
├── listing-hardening/
└── listing-evidence-auditor/
```

### Planning: think deeply

Planning preserves product/offer truth, claims, VOC, market and localization research, selected profiles, channel architecture, and message strategy.

Planning ends with formal state rather than forwarding the whole conversation:

- Project Brief / Project Definition;
- Creative Strategy Kernel;
- Production Handoff;
- **Complete Demo-Required Production Set**;
- **Page Visual System**;
- one **Evidence Mode** per final asset.

Priority proof coverage is not the same as a complete Demo asset set.

The Page Visual System gives every final asset deliberate visual direction such as scene family, composition family, tone, product scale, and proof form. Core rule: **Same art direction != same composition.**

Evidence Mode is one of:

```text
SOURCE_FAITHFUL
CREATIVE_MOCK
PROOF_VISUAL
```

Product-identity evidence is kept separate from proof-grade evidence. A Creative Mock may tolerate missing proof evidence with an explicit limitation, but may not invent the product when identity evidence is missing.

A reusable Account Capability Profile may answer recurring channel/account questions only when the record is recent, structurally valid, correctly scoped, and non-conflicted.

### Production: produce narrowly

Production is artifact-first and receives only the Creative Strategy Kernel, Production Handoff, current one-job Asset Packet, referenced source assets, and approved benchmarks/patterns.

v0.3.2 production safeguards include:

- one Asset ID / one final role / one shopper task / quantity 1 per Asset Packet;
- required Evidence Mode and minimal Page Visual System neighbor context;
- Production Context Firewall;
- exact candidate history;
- **Selection Lock** after the user selects a candidate;
- asset-level Creative QA;
- **Set-level Creative QA** for scene/composition/tone/scale/proof/message repetition;
- final whole-set/contact-sheet QA bound to exact current output references;
- removal-only **Scope Delta** inside Production; additions or material role/message/evidence changes return to Planning;
- **Smallest Sufficient Cleanup** instead of broad regeneration.

A selected output cannot be silently replaced, given another candidate, or rolled back to review status until explicit reopen intent.

### Hardening: verify rigorously

Creative Approval is separate from Evidence Verification.

`listing-evidence-auditor` recomputes exact-file trust from real files, including path containment, existence, SHA-256, supported image signatures, extension agreement, dimensions, approval binding, semantic role evidence, and required asset-set completeness. Same-context semantic review cannot promote itself to independent review.

`listing-hardening` owns Delivery State and machine-computed checks including:

- current verified channel/account module budget;
- approval provenance;
- module/slot origin;
- transform authorization;
- asset-to-slot integrity;
- Production Freeze completeness;
- Pre-Demo exact-file evidence;
- frontend fidelity;
- final delivery parity.

The global core does not hard-code one marketplace's account/module ceiling. Channel limits come from current verified project capability evidence.

Platform Capability evidence and Frontend Visual evidence remain separate. If a native channel shell cannot be verified, use a clearly labeled **Content Review Demo** instead of inventing channel chrome.

## Final Demo contract

The final project Demo is delivered as **one standalone `.html` file**.

- no adjacent `assets/` directory;
- no Demo ZIP as the user-facing deliverable;
- runtime images/resources embedded as portable `data:` URIs;
- inline CSS and JavaScript;
- no external/local runtime asset dependency;
- mixed/external `srcset` and literal session-only `blob:` resources rejected;
- responsive viewport, width breakpoint, and responsive image rules required;
- when a carousel is present, previous/next controls and verifiable inline click wiring are required;
- a valid static page is allowed when no carousel is planned.

Static validation is necessary but not sufficient. Final runtime QA requires the exact HTML to be opened at:

- **1440px desktop**;
- **390px mobile**.

At both widths verify no horizontal overflow, no broken images, no clipped primary copy/controls, correct content order and image/text pairing, required interactions, and Review Mode/Consumer Mode integrity.

If browser/runtime verification cannot be performed, mobile/interaction QA remains **BLOCKED** rather than being self-declared PASS.

## Built-in global profiles

### Channels

- Amazon generic marketplace profile
- Direct-to-consumer product page
- Retailer PDP
- Generic marketplace fallback

Channel/site/account-specific capabilities must still be verified for the actual project.

### Locales

- `ja-JP`
- `en-US`
- `de-DE`
- `it-IT`
- custom profiles can be added

### Regions

- EU common overlay

### Categories

- category template only; product/category selling logic requires deliberate evidence-backed overlays or project evidence.

## Checkpoints and retry behavior

Major Stage Checkpoints are the default. Normal checkpoint output is concise:

```text
Done:
Open:
Next:
```

`continue`, `next`, `go`, and equivalent transition commands advance the workflow instead of triggering unbounded retries. For the same asset and same identified problem, autonomous retry budget is two attempts without new input/evidence.

## Distribution

### Repository / Codex bundle

```bash
python scripts/package_codex_bundle.py
```

Output:

```text
dist/gtm-listing-demo-codex-bundle.zip
```

This contains the five sibling Skills under `.agents/skills/`.

### One-install compatibility package

```bash
python .agents/skills/gtm-listing-demo/scripts/package_skill.py
```

Output:

```text
dist/gtm-listing-demo.skill.zip
```

This keeps one user-facing Skill and embeds Planning / Production / Hardening / Evidence Auditor under `gtm-listing-demo/internal-skills/`. It is still one model context, so packaging the auditor does not create independent semantic review. `SINGLE_CONTEXT_LIMITATION.txt` documents that boundary.

## Validation

```bash
python .agents/skills/gtm-listing-demo/scripts/validate_skill.py
python .agents/skills/gtm-listing-demo/scripts/selftest_router.py
python .agents/skills/listing-planning/scripts/selftest_planning.py
python .agents/skills/listing-production/scripts/selftest_production.py
python .agents/skills/listing-evidence-auditor/scripts/selftest_auditor.py
python .agents/skills/listing-hardening/scripts/selftest_hardening.py
python .agents/skills/listing-hardening/scripts/selftest_demo_output.py
python .agents/skills/gtm-listing-demo/scripts/selftest_project_state_validator.py
python .agents/skills/gtm-listing-demo/scripts/validate_overlay.py
python .agents/skills/gtm-listing-demo/scripts/package_skill.py
python scripts/package_codex_bundle.py
```

## Public and private boundary

The public repository remains generic. Market/site-specific rules belong in explicit profiles; brand/account facts and confidential project data belong in private overlays/project evidence. Product-pilot learnings may become generic regression rules only after the product-specific content is removed.

## Version

`0.3.2`

## License

MIT.
