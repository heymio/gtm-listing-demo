---
name: listing-planning
description: Use when planning Stage 0–7 of a global listing project from evidence through market/channel strategy, page architecture, and the complete production handoff.
---

# Global Listing Planning

## Core question

What should we build, for this market/channel/offer, and why?

## Plane boundary

This Skill owns Stage 0–7 only. It may reason deeply across project evidence, Product Truth, VOC, competitor evidence, market, locale, region overlay, channel profile, category overlay, offer boundaries, claims, and page architecture. It does not perform final visual production or delivery hardening.

## Global configuration model

Keep these inputs separate:

- market;
- locale;
- region overlays;
- channel profile and marketplace/site;
- category overlay;
- offer and page target;
- brand/private overlay;
- project evidence.

A locale or region label does not establish consumer preference. Market/category insights require current project evidence.

## Required planning outputs

Planning ends with formal state objects rather than forwarding the full conversation:

1. Project Brief / Project Definition;
2. Creative Strategy Kernel;
3. Production Handoff;
4. Complete Demo-Required Production Set;
5. Page Visual System;
6. one Evidence Mode per final asset.

**Priority proof coverage does not equal the Complete Demo-Required Production Set.** Derive every final asset from the approved page architecture and shopper tasks, including lower-priority assets required by the final Demo.

## Source Asset Intake

Fresh projects use lightweight source-asset intake before production. Do not require a full project-wide exact-file audit before final assets exist. A targeted early audit is appropriate only when inheriting or reusing an exact previously approved file.

## Page Visual System

Inside the Production Handoff, define each final asset using:

- `visual_role`;
- `scene_family`;
- `composition_family`;
- `tone`;
- `product_scale`;
- `proof_form`;
- optional `neighbor_contrast_note` for intentional adjacent repetition.

**Same art direction != same composition.** Coherent brand language may repeat; accidental repetition of the full visual signature should not.

The Page Visual System is part of Stage 7 Planning. It is not a new numbered Stage or Hardening gate.

## Evidence Mode

Assign exactly one mode per final asset:

- `SOURCE_FAITHFUL` — faithful product/pack/offer identity is intrinsic;
- `CREATIVE_MOCK` — lifestyle/atmosphere/spatial concept work may tolerate missing proof-grade evidence, but generated details are not Product Truth;
- `PROOF_VISUAL` — factual mechanism/UI/installation/dimension/compatibility proof requires authoritative evidence.

Product-identity evidence and proof-grade evidence remain separate. Missing identity evidence needed to preserve the actual product blocks production; Creative Mock flexibility does not authorize product invention.

## Account Capability Profile

Channel/account capabilities may be reused only when a persistent record is recent, structurally valid, scoped to the intended channel/account, and non-conflicted. Missing, stale, malformed, future-dated, wrong-channel, or contradicted capability evidence must be re-verified.

Never infer current account permissions from a competitor page. Public profiles contain mechanisms, not private brand/account values.

## Channel planning

Load only the selected global channel profile. Verify actual editable regions, module families, interactions, ownership, and current account/site capability before formal planning.

`Message != Module`. A message list must not be mechanically converted into one static board per message.

Platform Capability evidence and Frontend Visual evidence are separate. Official documentation does not prove the current consumer-facing shell.

## Role separation

Different page regions remain separate production roles when their shopper task, geometry, interaction, or channel placement differs. Shared messaging does not automatically authorize reusing one asset across distinct final roles.

## Production Handoff

Every final asset object must retain at least:

- Asset ID;
- role;
- slot;
- primary message;
- Evidence Mode;
- production status.

The page plan, asset set, Page Visual System, source registry, Product Invariants, Creative Strategy reference, visual benchmarks, prohibited output, and blocked assets form one authoritative handoff.

Do not inject Project State, auditor results, delivery gates, or change-impact narration into this handoff.

## Planning QA

Read `references/planning-qa.md` before handoff. Run `scripts/validate_planning_contracts.py production-handoff <file>` when a repository runtime is available.
