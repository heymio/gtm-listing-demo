---
name: gtm-listing-demo
description: Use when planning, reviewing, or producing product listing strategy, enhanced content, visual briefs, or interactive demos across markets, locales, sales channels, product categories, and offer variants from product documents, VOC, competitor pages, research, or design assets.
---

# GTM Listing Demo

## Core principle

Build one evidence-governed Product Truth and Product Strategy, then adapt them to the requested market, locale, channel, category, offer, and page targets.

## Configuration layers

Keep these layers separate:

| Layer | Responsibility |
|---|---|
| Core Workflow | Evidence, strategy, mapping, assets, visual proof, demo, and QA |
| Channel Profile | Editable slots, module families, platform rules, and interaction constraints |
| Locale Profile | Language, punctuation, formatting, units, dates, currency, and native copy review |
| Region Overlay | Cross-country regulatory and operational checks |
| Category Overlay | Optional product-category JTBD, VOC themes, claim risks, and proof patterns |
| Brand / Private Overlay | Company rules, internal capabilities, confidential claims, and approvals |
| Project Evidence | Actual facts, consumer needs, scenarios, keywords, assets, and decisions |

## Mandatory rules

1. Start with Project Definition, Source Gate, and Fact Gate.
2. Separate `market`, `locale`, `region_overlays`, `channel`, `category`, `offer`, and `page_targets`.
3. A locale profile may define language and formatting, but may not assert what consumers prefer.
4. A region overlay may define verification obligations, but may not create a regional persona.
5. A channel profile may define page structure, but may not contain product-category selling points.
6. Product and category insights require project evidence; country labels are not evidence.
7. VOC is an independent strategy input. Competitor listing capture does not replace user research.
8. One Product Truth layer may fork into Single, Kit, Bundle, and variant pages only after a Page Boundary Matrix exists.
9. `Message != Module`; use the actual channel module structure and pack messages where appropriate.
10. AI may create environments and concept backgrounds. Product geometry, UI, ports, controls, accessories, packaging, and functional proof require real assets or explicit provisional labels.
11. Every module must pass the Visual Evidence Matrix: `message → visual subject → evidence object → asset`.
12. Missing evidence blocks only dependent outputs. It never authorizes invented facts.
13. Review-only information must be hidden or replaced by neutral copy in consumer mode.
14. Current channel rules, legal requirements, pricing, certification, and platform capabilities must be verified from authoritative sources before formal release.

## Workflow

Read `references/workflow.md` and only the profiles selected in Project Definition.

```text
0 Project Definition
1 Source Intake
2 Source Normalization & Coverage Gate
3 Fact Lock
4 Consumer Strategy
4.2 Market & Localization Enrichment
5 Message Architecture
5.5 Channel Template Mapping
6 Channel-specific Listing IA
6.5 Asset Intake & Audit
7 Channel Slot / Module Planning
7.5 Visual Production Brief
8 Visual Production + Visual Evidence QA
9 Interactive Demo Assembly
10 Final QA + Claim Gate + Review Mode
```

## Required outputs

Before declaring the workflow complete, produce:

- Project Definition and selected profiles
- Source Registry and coverage status
- Fact Ledger, Conflict Ledger, Missing Evidence, Claim Readiness, and Gate Result
- Consumer Strategy and Market Evidence Registry
- Page Target / Product Boundary Matrix
- Message Architecture and Message-to-Slot Matrix
- Asset Manifest and Asset Gap Analysis
- Channel Slot / Module Plan
- Visual Production Brief and Visual Evidence Matrix
- Interactive demo or production-ready module specification
- Product, Claim, Channel, Market/Locale, Visual, Mobile, Technical, and Review Mode QA results

Use `references/contracts.md`.

## Stop and escalate

Pause only the affected output and ask a targeted question when:

- sources conflict on a consumer-visible fact;
- a claim depends on testing, certification, pricing, availability, subscription terms, or launch scope;
- a country or region assumption lacks category- and project-specific evidence;
- a channel module or editable slot cannot be verified;
- a product or UI asset is being reconstructed instead of sourced;
- offer boundaries cannot be separated;
- mobile interaction, asset paths, or consumer-mode hiding fail.

## Quality gate

Run every checklist in `references/qa.md`. In a repository execution environment, run:

```bash
python .agents/skills/gtm-listing-demo/scripts/validate_skill.py
```

When revising the skill, rerun the scenarios under `evals/`.
