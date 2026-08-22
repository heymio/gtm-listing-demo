# Global workflow reference

The user normally invokes `$gtm-listing-demo`; detailed execution belongs to the stage-local Skills.

## Stage 0 — Project Definition

Record market, locale, region overlays, channel/site, category, product/offer definitions, page targets, output type, review audience, and known account/retailer capabilities. Keep these dimensions separate.

## Stage 1 — Source Intake

Collect product/commercial sources, research/VOC, current channel references, brand guidance, product/UI/visual sources, and relevant earlier-generation material. VOC remains an independent evidence stream.

## Stage 2 — Source Normalization & Coverage

Separate product-fact authority, commercial/marketing decision authority, consumer evidence, locale reference, channel reference, and visual reference. Missing evidence blocks only dependent outputs.

## Stage 3 — Product / Offer / Claim Lock

Create stable Product Truth, offer/page boundaries, conflicts, missing evidence, and claim readiness. Earlier-generation facts never prove a successor fact without explicit inheritance evidence.

## Stage 4 — Consumer Strategy

Build target user, JTBD, barriers, purchase reasons, Reasons to Believe, differentiators, and message priority from evidence. Do not derive consumer needs from a market/country name.

## Stage 4.2 — Market & Localization Enrichment

Research Product/Category × Market × Locale × Channel × current project evidence. Separate observed evidence from inference; do not overwrite Product Truth.

## Stage 5 — Message Architecture

Build the Core Promise, purchase reasons, proof principles, objections, and priorities, then fork by offer/page target where required.

## Stage 5.5 — Channel Mapping

Load the selected global channel profile and verify current site/account capabilities. `Message != Module`; map strategy to real editable regions and interaction families.

Platform Capability evidence is separate from Frontend Visual evidence.

## Stage 6 — Page IA

Define shopper sequence inside the real channel/page structure for every page target. Shared topics may appear in several regions when their shopper role differs.

## Stage 6.5 — Lightweight Source Asset Intake

Inventory source assets and identify missing render/photo/UI/design/evidence needs. A fresh project does not require a full project-wide exact-file audit here. Use a targeted early audit only for inherited/reused exact assets that must carry prior approval forward.

## Stage 7 — Final Page / Asset Planning

Produce the Creative Strategy Kernel, complete page plan, **Complete Demo-Required Production Set**, Page Visual System, Evidence Mode for every final asset, source bindings, and Production Handoff.

Priority proof coverage does not make a partial asset set complete.

## Stage 7.5–8 — Focused Visual Production

`listing-production` executes one Asset Packet at a time with artifact-first behavior, identity/proof source rules, Selection Lock, set-level Creative QA, exact-output-bound final whole-set review, Scope Delta, and Production Freeze.

## Stage 8.5 — Pre-Demo Exact-File Audit

`listing-hardening` delegates the complete current final set to `listing-evidence-auditor`. Exact files, hashes, approvals, role/scope evidence, and required-set completeness must be reconciled before final Demo consumption.

## Stage 9 — Demo Assembly

Assemble only approved/verified project content into the locked page/channel architecture. Reproduce a native shell only when current frontend evidence supports it; otherwise use a clearly labeled Content Review Demo.

The user-facing final project Demo is one standalone `.html` file with portable embedded runtime resources.

## Stage 10 — Final QA

Run exact asset, claim, channel, market/locale, frontend, delivery parity, standalone dependency, responsive/mobile, interaction, and Review Mode QA.

Static validation is necessary but not sufficient. Runtime verification requires 1440px desktop and 390px mobile. If browser/runtime verification cannot be performed, mobile/interaction status remains `BLOCKED`.
