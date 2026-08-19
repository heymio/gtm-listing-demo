# gtm-listing-demo

`gtm-listing-demo` is a reusable AI skill and operating workflow for turning product evidence into market- and channel-specific listing strategy, content architecture, visual briefs, and interactive review demos.

It is intentionally **not hard-coded to one country, language, marketplace, or product category**.

## What it supports

- Multiple markets: JP, US, DE, IT, and additional country markets through profiles
- Multiple locales: `ja-JP`, `en-US`, `de-DE`, `it-IT`, and custom locale profiles
- Multiple channels: Amazon, direct-to-consumer product pages, retailer PDPs, and generic marketplaces
- Multiple offers: Single, Kit, Bundle, variants, and comparison-led page sets
- Incomplete inputs: source coverage gates and claim readiness prevent missing evidence from becoming facts
- Visual review: asset audits, visual evidence alignment, interactive demos, mobile checks, and review mode

## Architecture

The workflow separates six configuration layers:

```text
Core Workflow
├── Channel Profile
├── Locale Profile
├── Region Overlay
├── Category Overlay
├── Brand / Private Overlay
└── Project Evidence
```

These layers have different responsibilities:

- **Channel profiles** describe editable slots, module families, and platform constraints.
- **Locale profiles** describe language and formatting rules, not consumer stereotypes.
- **Region overlays** describe cross-country checks, not personas.
- **Category overlays** are optional and product-specific.
- **Private overlays** hold company rules, internal capabilities, and confidential examples.
- **Project evidence** determines actual consumer needs, scenarios, keywords, and claims.

## Core rules

1. Build one Product Truth layer before creating page variants.
2. Keep market, locale, region, channel, category, offer, and page target separate.
3. Do not let available assets determine the strategy.
4. Do not infer consumer needs from a country profile without project evidence.
5. `Message != Module`; pack messages into the actual module structure supported by the channel.
6. AI may create environments and concept backgrounds, but not product geometry, UI, interfaces, controls, or functional proof.
7. Every visual must pass `message → visual subject → evidence object → asset`.
8. Unconfirmed information remains review-only and cannot leak into consumer mode.

## Built-in profiles

### Channels

- Amazon
- Direct-to-consumer product page
- Retailer PDP
- Generic marketplace

### Locales

- `ja-JP`
- `en-US`
- `de-DE`
- `it-IT`

### Regions

- EU common overlay

### Categories

- A category template only. Product-specific category knowledge must be added deliberately and supported by evidence.

## Quick start

```yaml
market:
  country: DE
locale:
  id: de-DE
region_overlays:
  - EU
channel:
  type: amazon
  site: amazon.de
category: project-defined
page_targets:
  - single
  - kit
output:
  - strategy
  - module-plan
  - interactive-demo
```

Then ask:

```text
Use the gtm-listing-demo skill.
First create the Project Definition, Source Registry, Fact Ledger, and Page Boundary Matrix.
Then continue through market evidence, channel mapping, visual evidence QA, and the requested demo.
Keep all unsupported facts in PENDING CLAIM.
```

## Installation

### Codex App / CLI / IDE

Open this repository and invoke:

```text
$gtm-listing-demo
```

Codex can also select the repository skill when the request matches its description.

### ChatGPT Personal Skills

Run:

```bash
python .agents/skills/gtm-listing-demo/scripts/validate_skill.py
python .agents/skills/gtm-listing-demo/scripts/package_skill.py
```

Upload `dist/gtm-listing-demo.skill.zip` where Personal Skills are available.

See `docs/install.md` for repository, Personal Skill, and private-overlay usage.

## Public and private use

This public repository is the generic source of truth. Company facts, confidential product data, private Figma links, pricing, internal claims, and approval rules belong in a separate private overlay.

## Validation

```bash
python .agents/skills/gtm-listing-demo/scripts/validate_skill.py
```

The validator checks required files, frontmatter, profile coverage, category leakage, locale stereotyping, eval coverage, and packaging readiness.

## License

MIT.
