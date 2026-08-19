# Core evals

## E1 — Incomplete successor product

**Prompt:** “Use the earlier model's marketing document and the new model's project brief to produce final listing copy.”

**Pass:** Build Source and Fact Gates, mark inheritance as pending, and restrict downstream claims.

**Fail:** Copy earlier claims into the new product without evidence.

## E2 — Message count versus module count

**Prompt:** “There are eight selling points, so create eight equal banners.”

**Pass:** Explain `Message != Module`, pack messages according to verified channel modules, and keep slot roles distinct.

**Fail:** Produce one static banner per message without channel mapping.

## E3 — Visual evidence

**Prompt:** “Use the available packshot for every scenario because no other images exist.”

**Pass:** Build an Asset Gap and Visual Evidence Matrix; mark missing scenario proof instead of accepting the packshot.

**Fail:** Treat the packshot as universal proof.

## E4 — Offer boundary

**Prompt:** “The kit has an extra interface and storage path. Reuse those visuals on the single-product page.”

**Pass:** Reject cross-offer evidence and create a Page Boundary Matrix.

**Fail:** Let kit-only proof appear on the single page.

## E5 — Mobile preview

**Prompt:** “The downloaded HTML opens on a phone but the tabs do not respond.”

**Pass:** Diagnose the preview environment, verify asset paths, and provide a native or CSS-safe fallback for essential interactions.

**Fail:** Declare the demo desktop-only or change unrelated content.
