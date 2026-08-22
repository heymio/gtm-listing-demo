# Global QA checklist

## Product and offer QA

- Product facts, offer/page boundaries, and conditions match evidence.
- Earlier-generation capabilities are not silently inherited.
- Required P0/P1 and lower-priority final page roles needed by the Demo are covered.

## Claim QA

- Conflict/missing/prohibited facts do not enter consumer copy.
- Conditional claims retain their conditions.
- Current price, availability, certification/testing/performance/service terms are verified before formal release when relevant.
- Unsupported absolute/comparative/superlative claims are rejected.

## Channel QA

- Editable regions, interactions, and current account/site capabilities are verified.
- Module/slot count is checked against current verified capability evidence rather than a generic hard-coded ceiling.
- Platform-generated regions are not treated as brand-controlled.
- Platform Capability evidence remains separate from Frontend Visual evidence.

## Market and locale QA

- Market insights have project/category evidence.
- Locale profiles define language/formatting, not personas or priorities.
- Region overlays do not replace country/locale research.
- Consumer copy is native and channel-appropriate.

## Asset-level Creative QA

Each final asset has one dominant shopper task/message, appropriate product prominence, direct visual proof where required, controlled composition, credible realism, channel fit, source-faithful product identity, and explicit Evidence Mode.

## Set-level Creative QA

Review the ordered set for scene/composition/tone/product-scale/proof-form repetition and adjacent message redundancy. The final whole-set/contact-sheet review must bind exact current output refs; replacing one selected output invalidates the prior final set review.

## Evidence / Hardening QA

- Creative `USER_APPROVED` is not treated as evidence verification.
- Real final files are fingerprinted from disk.
- Approval binds exact current SHA, role, and scope.
- Duplicate identifiers fail before dictionary/index overwrite.
- Same-context semantic review does not self-certify independence.
- Required asset-set completeness and exact slot scope are verified before Demo consumption.

## Standalone Demo QA

- Final project deliverable is one `.html` file, not a Demo ZIP plus assets folder.
- Runtime images/resources are portable embedded `data:` resources; external/local dependencies are rejected.
- Mixed/external `srcset`, session-only literal `blob:` resources, external CSS/JS, and CSS imports/local URLs are rejected.
- Responsive viewport, width breakpoint, and responsive image behavior are present.
- If a carousel is present, controls/slides/inline click wiring are complete; a static page is allowed when no carousel is planned.

## Runtime QA

At 1440px desktop and 390px mobile verify:

- no horizontal overflow;
- no broken images;
- no clipped primary copy/controls;
- correct content order and image/text pairing;
- all planned interactions;
- Review Mode does not corrupt Consumer Mode.

If browser/runtime verification cannot be performed, mobile/interaction QA remains `BLOCKED`.

## Domain leakage QA

- generic workflow files contain no private company/product data;
- channel profiles contain no category selling points;
- locale profiles contain no consumer stereotypes;
- region overlays contain no regional persona;
- category/product/site-specific logic appears only in explicit profiles, overlays, examples/evals, private context, or project evidence.
