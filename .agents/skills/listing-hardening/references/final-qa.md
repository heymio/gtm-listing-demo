# Final QA

Final QA checks exact asset integrity, claims, channel/slot structure, frontend fidelity, delivery parity, standalone Demo dependencies, responsive/mobile behavior, and Review Mode separation.

Consumer Mode must hide internal statuses, gate notes, provisional labels, and implementation commentary while remaining semantically complete.

Review Mode may expose internal review metadata but must not corrupt Consumer Mode layout.

For final Demo runtime QA, verify 1440px desktop and 390px mobile, including horizontal overflow, broken images, clipped primary copy/controls, content order, image/text pairing, and all required interactions.

**If browser/runtime verification cannot be performed, interaction/mobile QA is BLOCKED.** Static source inspection cannot declare runtime PASS.
