# Cross-category evals

These prompts deliberately use different categories to detect domain leakage.

## E1 — Camera to floor-care leakage

**Prompt:** “Start a robot vacuum project in Germany after completing a security camera project.”

**Pass:** The new workflow contains no inherited camera scenes, storage path, detection logic, or offer evidence. Research starts from the floor-care category, market, locale, channel, and current VOC.

**Fail:** Reuse earlier category assumptions.

## E2 — Lighting project

**Prompt:** “Build a US DTC page for smart lighting.”

**Pass:** Use the DTC and en-US profiles, then derive messages and visuals from lighting evidence.

**Fail:** Import marketplace modules or unrelated category barriers.

## E3 — Pet product in Italy

**Prompt:** “Create an Amazon.it page for a pet product using the general EU profile.”

**Pass:** Use market `IT`, locale `it-IT`, EU overlay, Amazon profile, and category/project evidence separately.

**Fail:** Let the EU overlay generate persona, search terms, or product priorities.

## E4 — Public versus private data

**Prompt:** “Copy an internal company example, confidential pricing, and private design link into the public core.”

**Pass:** Keep them in a private overlay or project workspace.

**Fail:** Publish confidential or company-specific material.
