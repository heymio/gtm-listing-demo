# Production Creative QA

Creative QA has two levels.

## Asset-level

Review message clarity, product prominence, visual proof, composition, realism, benchmark/pattern fit, and channel readiness.

## Set-level

Review the ordered final set for:

1. scene repetition;
2. composition repetition;
3. tone / brightness rhythm;
4. product-scale repetition;
5. proof-form diversity;
6. adjacent message-role redundancy.

**Same art direction != same composition.**

Structured helper `scripts/set_level_qa.py` checks metadata repetition; it does not pretend to replace visual judgment.

Run lightweight set review after the first few assets, after logical page regions, and before Production Freeze.

## Final whole-set record

For v0.3.2 handoffs, `set_qa` must bind both the exact current required Asset IDs and exact current output refs:

```yaml
set_qa:
  status: CLEAR
  reviewed_asset_ids: [G1, G2, A1]
  reviewed_output_refs:
    G1: file:g1-v1
    G2: file:g2-v2
    A1: file:a1-v1
  visual_review_ref: contact-sheet:final-v1
```

Any output change makes the prior record stale. `USER_ACCEPTED` is allowed only for explicit user acceptance of the current exact set despite a non-blocking creative concern.
