# Workflow reference

## Stage 0 — Project Definition

Record:

- market country
- locale
- region overlays
- channel type and site
- product category
- product and offer definitions
- page targets
- output type
- review audience
- account or retailer capabilities

**Gate:** Market, locale, region, channel, category, offer, and page target are not collapsed into one field.

## Stage 1 — Source Intake

Collect product marketing documents, specifications, project approvals, pricing decisions, research, VOC, competitor pages, earlier-generation references, brand guidance, product renders, UI sources, and videos.

VOC remains an independent evidence stream. A competitor URL does not make VOC complete.

**Output:** Project Input Pack.

## Stage 2 — Source Normalization & Coverage Gate

For every source record product, offer, version, authority, freshness, completeness, allowed usage, and downstream dependencies.

Separate product-fact authority, commercial-decision authority, marketing-decision authority, consumer evidence, localization reference, channel reference, and visual reference.

Classify missing information by downstream impact.

**Output:** Source Registry, Missing Coverage, and `SOURCE_GATE`.

## Stage 3 — Fact Lock

Create:

- Fact Ledger
- Conflict Ledger
- Missing Evidence
- Claim Readiness
- Gate Result

For successor products, distinguish `INHERITED-PENDING`, `UPGRADED`, `NEW`, `CONFLICT`, and `MISSING`. An earlier product never proves a new product fact without explicit inheritance evidence.

**Gate:** Consumer copy cannot use `CONFLICT`, `MISSING`, `PROHIBITED`, or an unqualified `CONDITIONAL` fact.

## Stage 4 — Consumer Strategy

Draft Target User, JTBD, Pain Points, Purchase Barriers, Benefits, Reasons to Believe, Differentiators, and Message Priority from the evidence. The user reviews, confirms, or overrides.

Do not derive needs from the country name alone.

**Output:** Draft Consumer Strategy and Human Review Gate.

## Stage 4.2 — Market & Localization Enrichment

Research the intersection of:

```text
Product / Category
× Market
× Locale
× Channel
× Current evidence
```

External research may add need states, scenarios, terminology, search language, purchase motivation, objections, and channel conventions. It may not overwrite product facts.

Use current authoritative sources for regulations and platform rules. Separate evidence from inference.

**Output:** Market Evidence Registry and Localization Brief.

## Stage 5 — Message Architecture

Define the Core Promise, reasons to buy, trust evidence, objections, and message priority. Build shared product messages once, then fork by offer and page target.

**Output:** Message House and Message Priority.

## Stage 5.5 — Channel Template Mapping

Load the selected channel profile and verify the actual account or retailer capabilities. Map messages to the editable slots and module families available for the project.

Do not convert a message list directly into an equal number of static banners.

**Output:** Channel Capability Map and Message-to-Slot Matrix.

## Stage 6 — Channel-specific Listing IA

Define reader sequence inside the real channel structure. The same message may appear in several slots when its role changes, such as identity, summary, proof, scenario, comparison, or objection handling.

**Output:** Page IA for every page target.

## Stage 6.5 — Asset Intake & Audit

Accept static assets and design sources. Build an Asset Manifest containing object, source, quality, evidence supported, usable slots, status, and replacement requirement.

Classify gaps as render, photography, design, UI export, AI background, video, copy, or blocked.

**Output:** Asset Manifest and Asset Gap Analysis.

## Stage 7 — Channel Slot / Module Planning

For every slot or module define message role, interaction, evidence, existing asset, asset to create, copy status, and claim gate.

**Output:** Channel Slot / Module Plan.

## Stage 7.5 — Visual Production Brief

Specify composition, visual subject, evidence object, product placement, UI placement, text safe area, responsive behavior, asset source, and prohibited reconstruction.

**Output:** Visual Production Brief and Visual Evidence Matrix.

## Stage 8 — Visual Production + Visual Evidence QA

Use:

```text
approved environment or AI background
+ real product asset
+ real UI
+ functional graphic overlay
+ final copy
```

Reject a visual when the subject or evidence object cannot directly prove the message.

**Output:** Master visuals and channel adaptations.

## Stage 9 — Interactive Demo Assembly

Implement only the interactions required to review the proposed page: gallery, tabs, carousel, hotspot, storyboard or video, comparison, Q&A, variants, responsive layout, and review mode.

When downloaded-file previews may restrict JavaScript, use native HTML or CSS-safe controls for essential interactions.

**Output:** Interactive Review Demo.

## Stage 10 — Final QA

Run Product, Claim, Channel, Market/Locale, Visual, Mobile, Technical, and Review Mode QA. Report passed checks and open items separately.

**Output:** Final QA Result and Open Items.
