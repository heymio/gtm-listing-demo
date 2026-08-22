# Installation and reuse

## Repository / Codex use

Global v0.3.3 contains five sibling Skills:

```text
.agents/skills/
├── gtm-listing-demo/
├── listing-planning/
├── listing-production/
├── listing-hardening/
└── listing-evidence-auditor/
```

Normally invoke only:

```text
$gtm-listing-demo
```

Build the repository/Codex distribution with:

```bash
python3 scripts/package_codex_bundle.py
```

Output:

```text
dist/gtm-listing-demo-codex-bundle.zip
```

The v0.3.3 Codex bundle is deterministic, rejects symlink inputs, and extracts itself to run `validate_overlay.py` before the packager reports success.

## Hard-verification runtime dependencies

Physical image hard verification uses Pillow. Demo runtime hard verification uses Playwright with Chromium.

```bash
python3 -m pip install Pillow playwright
python3 -m playwright install chromium
```

On Linux CI or a fresh Linux environment:

```bash
python3 -m playwright install --with-deps chromium
```

These are hard-verification dependencies, not optional quality enhancements. If Pillow is unavailable, PNG/JPEG/WebP assets do not receive physical hard-verification PASS. If Playwright/Chromium cannot run, `DEMO_RUNTIME_GATE` remains `UNVERIFIED/BLOCKED`; static inspection cannot upgrade it to PASS.

## Personal Skill / one-install compatibility package

Run:

```bash
python3 .agents/skills/gtm-listing-demo/scripts/validate_skill.py
python3 .agents/skills/gtm-listing-demo/scripts/package_skill.py
```

Upload:

```text
dist/gtm-listing-demo.skill.zip
```

The compatibility package keeps `gtm-listing-demo` as the user-facing root and embeds the four stage/audit Skills under `internal-skills/`. It excludes repository-only selftests and validates the extracted installation with package-local `scripts/validate_install.py`. It is deterministic and rejects symlink inputs.

This does **not** make semantic review independent: the compatibility package is one model context. Deterministic file/hash/schema/approval/scope checks remain useful, but unresolved semantic role or proof-claim evidence stays `UNVERIFIED` / `HUMAN_REVIEW_REQUIRED` unless resolved by an appropriate human or genuinely independent review. See `SINGLE_CONTEXT_LIMITATION.txt`.

## Final hard-verification contract

For Demo Delivery State 0.2:

- mandatory pre-Demo verification cannot be disabled by caller input;
- required final asset set must be non-empty and is recomputed from all authoritative sources;
- Production Freeze binds every Asset ID to exact `candidate_id` and `output_ref` and must be blocker/revision-free with current Set QA;
- `FRONTEND_FIDELITY_GATE` is executable and evidence-backed;
- `DEMO_RUNTIME_GATE` requires exact-Demo-SHA no-network browser evidence at 1440px and 390px;
- carousel next/previous must be proven by actual browser behavior when a carousel is present;
- `PROOF_VISUAL` requires claim/fact/authoritative-source binding plus trusted claim review.

## Reusing in another repository

Preferred choices:

1. use the repository/Codex bundle when the target supports sibling repository Skills;
2. use the one-install compatibility ZIP when only one Personal Skill can be installed;
3. keep company/project data in a separate private overlay or project evidence rather than modifying the public core.

## Private overlay model

A private overlay may add company claim rules, internal channel/account capabilities, approval roles, confidential product facts, private examples, and internal design/asset references.

Precedence:

```text
current user request
> private/company overlay
> public gtm-listing-demo core and selected public profiles
> defaults
```

Public core files must not embed one company's assumptions.

## Formal v0.3.3 Release

The release workflow runs the complete hard-verification/build path on the exact candidate SHA with `contents: read`. Pull requests execute the same build path but cannot publish. Only a `push` to `main` may enter the separate publish job, which receives `contents: write`, does not check out or execute repository code, rechecks current `main`, metadata, tag state, and download-local SHA-256 checksums, then publishes the immutable Release.

Release assets:

```text
gtm-listing-demo.skill.zip
gtm-listing-demo-codex-bundle.zip
SHA256SUMS.txt
```

## Updating

When a real project exposes a workflow failure:

1. determine whether the failure is generic or market/site/product specific;
2. add a failing generic regression first when the behavior belongs in the global core;
3. implement the smallest generic fix without copying product/private data;
4. run all stage/audit selftests, real decoder/browser regressions, and global profile/domain-leakage validation;
5. build both distributions twice and confirm identical SHA-256;
6. inspect the Draft PR and CI artifacts before merge/release.

Market/site-specific behavior belongs in explicit profiles or overlays rather than generic defaults.
