---
name: gtm-listing-demo
description: Use when running a market- and channel-specific listing project from source intake through strategy, focused visual production, hardening, and standalone demo review across global markets, locales, channels, categories, offers, and page targets.
---

# GTM Listing Demo Router

## Purpose

One project, one normal invocation: `$gtm-listing-demo`.

The user-facing Skill is a thin Router. Stage-specific work lives in sibling execution Skills so deep market/product reasoning, focused visual production, and final delivery hardening do not compete inside one always-on instruction context.

Operating principle:

> Think deeply. Produce narrowly. Verify rigorously.

## Global configuration model

The Router preserves the global configuration model and passes selected configuration into Planning:

| Layer | Responsibility |
|---|---|
| Core Workflow | Evidence, strategy, mapping, assets, visual proof, demo, and QA |
| Channel Profile | Editable slots, module families, platform rules, and interaction constraints |
| Locale Profile | Language, punctuation, formatting, units, dates, currency, and native copy review |
| Region Overlay | Cross-country regulatory and operational checks |
| Category Overlay | Optional product-category JTBD, VOC themes, claim risks, and proof patterns |
| Brand / Private Overlay | Company rules, internal capabilities, confidential claims, and approvals |
| Project Evidence | Actual facts, consumer needs, scenarios, keywords, assets, and decisions |

Keep `market`, `locale`, `region_overlays`, `channel`, `category`, `offer`, and `page_targets` distinct. A locale or region label is never consumer evidence by itself.

## Stage routing

Read `references/routing.md` and route by current stage:

- Stage 0–7 → `listing-planning`
- Stage 7.5–8 → `listing-production`
- Stage 8.5–10 → `listing-hardening`
- `listing-hardening` delegates exact-file evidence work to `listing-evidence-auditor`.

Do not duplicate detailed stage rules in this Router.

### Skill resolution

In the repository/Codex distribution, resolve stage names as sibling Skills under `.agents/skills/`.

In the one-install compatibility package, the stage/audit Skills may be embedded under `internal-skills/<skill-name>/`. Embedded loading is a single-context fallback: formal handoff boundaries still apply, but merely loading the auditor inside the same model context is not independent semantic review.

The user still invokes only `$gtm-listing-demo`.

## Major Stage Checkpoint

Use **Major Stage Checkpoint** execution by default. Complete the current major stage to a reviewable state, then stop for user review before entering the next major stage unless the user gives a Transition Command or explicitly requests autonomous execution.

Normal checkpoint display stays concise:

```text
Done:
Open:
Next:
```

Show detailed state manifests only for `PARTIAL`, `BLOCKED`, or explicit audit/state review.

## Transition Command

Treat `continue`, `next`, `go`, `go next`, `继续`, `下一步`, and equivalent wording as a **Transition Command** unless the user explicitly asks to keep improving the current artifact.

On a Transition Command:

1. stop further retry/regeneration for the current artifact/problem;
2. preserve the best current result and truthful unresolved status;
3. persist the current formal handoff/state;
4. advance to the next stage or asset;
5. do not silently reopen prior work.

A Transition Command never promotes missing evidence into a false PASS.

## Retry Budget

For the same artifact and the same identified problem, allow at most **two autonomous attempts** without new user input or new evidence. After the Retry Budget is exhausted, surface the current result, revision need, or blocker.

A Transition Command advances immediately.

## Context Firewall

The Router enforces a **Context Firewall** between execution planes.

Planning may use deep product, offer, claim, VOC, market, locale, region, category, competitor, channel, and project-evidence reasoning. It compresses resolved production-relevant conclusions into formal handoff objects.

Production receives only:

- Creative Strategy Kernel;
- Production Handoff;
- current one-job Asset Packet;
- referenced source assets;
- approved visual benchmarks/patterns.

Do not inject full workflow narration, long research history, prior failed attempts, auditor reports, or delivery-state machinery into ordinary visual-production prompts.

Hardening receives Production Freeze, exact final files, locked page/slot requirements, relevant verification context, and frontend evidence. It does not need the full strategy conversation.

## Plane boundaries

### Planning

`listing-planning` answers:

> What should we build, for this market/channel/offer, and why?

It owns Product Truth, offer/page boundaries, claim readiness, consumer strategy, market/locale enrichment, selected profiles, channel architecture, module/slot planning, Creative Strategy Kernel, and the Complete Demo-Required Production Set.

### Production

`listing-production` answers:

> Produce the approved artifacts.

It is artifact-first. It uses one-job Asset Packets, preserves product identity, applies visual direction and evidence rules, records candidate history and creative approval, performs asset-level and set-level Creative QA, and creates Production Freeze only for the complete current production scope.

### Hardening

`listing-hardening` answers:

> Are the exact final artifacts safe, channel-correct, technically valid, and ready to assemble/deliver?

It owns final file identity, evidence and role/scope verification, channel/frontend fidelity, Demo assembly, delivery parity, standalone HTML validation, and final QA.

## State and resume

Conversation history is not the project database. Preserve formal project state through:

- Project Brief / Project Definition;
- Creative Strategy Kernel;
- Production Handoff;
- Asset Ledger / Production Freeze;
- Delivery State.

Use project/workspace files when the runtime supports them; otherwise maintain compact structured state without dumping control-plane detail into every user-facing response.

## Team Golden Path

```text
Upload source material
→ review Product / Offer / Claim baseline
→ review Consumer / Market Strategy
→ review channel page plan
→ review Creative Strategy / complete production asset set
→ review generated visuals
→ review verified standalone demo
```

Ordinary users should not need to manually invoke internal Skills or understand validators, hashes, provenance, or state-machine internals.

## Public-safety boundary

Keep reusable public logic market-, category-, brand-, and product-neutral unless content intentionally lives in a selected profile, example, eval, private overlay, or project evidence.
