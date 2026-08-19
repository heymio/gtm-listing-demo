# QA checklist

## Product and offer QA

- All P0/P1 messages are covered.
- Every number has a source and condition.
- Earlier-generation capabilities are not silently inherited.
- Offer and page boundaries match the Page Boundary Matrix.
- No page uses hardware, service, UI, storage, or accessories owned by another offer.

## Claim QA

- `CONFLICT`, `MISSING`, and `PROHIBITED` facts do not enter consumer copy.
- Conditional claims include their conditions.
- Price, availability, release date, certification, testing, performance, AI scope, cloud scope, and subscription terms are locked before release.
- No unsupported absolute, comparative, or superlative claim is used.

## Channel QA

- Editable slots and module families are verified for the current account or retailer.
- Module counts, fields, image rules, and interactions match current channel documentation.
- Platform-generated areas are not designed as brand-controlled content.
- Comparisons match real offer or product relationships.

## Market and locale QA

- Market insights have category- and project-specific evidence.
- Locale rules contain language and formatting, not personas or product priorities.
- Region overlays do not replace country and locale research.
- Consumer copy is native and channel-appropriate.
- Search language is researched for the selected category, locale, and channel.
- Regulations and legal copy are verified from current authoritative sources.

## Visual Evidence QA

For every module or tab:

1. Main copy contains one primary promise.
2. Visual subject is the object or scenario named by the copy.
3. Evidence object proves the mechanism or benefit.
4. Asset source is approved or explicitly provisional.

## Mobile and Technical QA

- Gallery, tabs, carousel, hotspot, storyboard or video, comparison, Q&A, variants, and review mode work on desktop and mobile.
- Asset references resolve.
- Standalone HTML has no unintended local dependencies.
- ZIP archives preserve relative paths.
- Console and page errors are zero.
- Copy remains readable without zooming.
- Wide comparisons have a usable mobile behavior.

## Review Mode QA

Review mode shows module type, status, open claim, provisional asset, and internal notes.

Consumer mode hides internal terms, placeholder commercial data, module labels, claim gates, and review-only explanations while remaining semantically complete.

## Domain leakage QA

- Core workflow files contain no company-specific product data.
- Channel profiles contain no category selling points.
- Locale profiles contain no consumer stereotypes.
- Region overlays contain no regional persona.
- Category-specific logic appears only in category overlays, examples, evals, private overlays, or project evidence.
