# Output contracts

## Project Definition

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
product:
  name: Product name or placeholder
offers:
  - single
  - kit
page_targets:
  - single-listing
  - kit-listing
output:
  - strategy
  - module-plan
  - interactive-demo
```

## Selected Profiles

| Layer | Profile | Why selected | Verified source | Status |
|---|---|---|---|---|

## Source Registry

| Source ID | Product / Offer | Type | Version/date | Authority | Completeness | Allowed usage | Downstream dependency |
|---|---|---|---|---|---|---|---|

Use authorities such as `product fact`, `commercial decision`, `marketing decision`, `consumer evidence`, `locale reference`, `channel reference`, and `visual reference`.

## Fact Ledger

| Domain | Fact | Value | Conditions | Source | Status | Offer/page scope | Claim readiness |
|---|---|---|---|---|---|---|---|

Statuses: `CONFIRMED`, `CONDITIONAL`, `INHERITED-PENDING`, `CONFLICT`, `MISSING`, and `PROHIBITED`.

## Conflict Ledger

| ID | Field | Evidence A | Evidence B | Impact | Resolution owner | Temporary rule |
|---|---|---|---|---|---|---|

## Market Evidence Registry

| Need state / language / behavior | Market | Locale | Channel | Category | Evidence | Evidence type | Confidence | Permitted use |
|---|---|---|---|---|---|---|---|---|

A country label without evidence cannot populate this table.

## Page Target / Product Boundary Matrix

| Capability or message | Offer A | Offer B | Bundle | Evidence owner | Notes |
|---|---:|---:|---:|---|---|

A blank cell means the page must not inherit that capability.

## Consumer Strategy

```yaml
target_user:
jtbd:
pain_points:
purchase_barriers:
benefits:
reasons_to_believe:
differentiator:
message_priority:
  p0:
  p1:
  p2:
assumptions:
confirmed_by_user:
```

## Message-to-Slot Matrix

| Message | Slot 1 | Slot 2 | Slot 3 | Comparison | Objection handling |
|---|---:|---:|---:|---:|---:|

Use priority and role, not only binary presence.

## Asset Manifest

| Asset ID | Object | Source | Quality | Evidence supported | Usable slots | Status | Replacement required |
|---|---|---|---|---|---|---|---|

## Channel Slot / Module Plan

| Slot | Channel module family | Message role | Interaction | Evidence | Existing asset | Asset to create | Claim gate |
|---|---|---|---|---|---|---|---|

## Visual Evidence Matrix

| Module/tab | Main message | Visual subject | Evidence object | Asset | Alignment result |
|---|---|---|---|---|---|

`PASS` requires the visual to directly prove the copy. A packshot, product quantity, lifestyle scene, UI, and mechanism diagram are not interchangeable evidence.

## Review Mode

| Status | Meaning | Consumer mode |
|---|---|---|
| `LOCKED` | Current evidence supports formal production | Content visible, badge hidden |
| `PENDING CLAIM` | Requires product, commercial, legal, or test confirmation | Claim hidden or neutralized |
| `DEMO ASSET` | Visual direction only | Internal label hidden; replace before release |
| `PROVISIONAL UI` | Temporary interface evidence | Internal label hidden; replace before release |
