# Installation and reuse

## Repository / Codex use

The v0.3.2 repository contains five sibling Skills:

```text
.agents/skills/
├── gtm-listing-demo/
├── listing-planning/
├── listing-production/
├── listing-hardening/
└── listing-evidence-auditor/
```

Open the repository in Codex App, CLI, or IDE and normally invoke only:

```text
$gtm-listing-demo
```

Build the repository/Codex distribution with:

```bash
python scripts/package_codex_bundle.py
```

Output:

```text
dist/gtm-listing-demo-codex-bundle.zip
```

## Personal Skill / one-install compatibility package

Run:

```bash
python .agents/skills/gtm-listing-demo/scripts/validate_skill.py
python .agents/skills/gtm-listing-demo/scripts/package_skill.py
```

Upload:

```text
dist/gtm-listing-demo.skill.zip
```

The compatibility package keeps `gtm-listing-demo` as the user-facing root and embeds the four stage/audit Skills under `internal-skills/`.

This does **not** make semantic review independent: the compatibility package is one model context. Deterministic file/hash/schema/approval/scope checks remain useful, but unresolved semantic role evidence stays `UNVERIFIED` / `HUMAN_REVIEW_REQUIRED` unless resolved by an appropriate human or genuinely independent review. See `SINGLE_CONTEXT_LIMITATION.txt`.

## Reusing in another repository

Preferred choices:

1. use the repository/Codex bundle when the target supports sibling repository Skills;
2. use the one-install compatibility ZIP when only one Personal Skill can be installed;
3. keep company/project data in a separate private overlay or project evidence rather than modifying the public core.

## Private overlay model

A private overlay may add:

- company claim rules;
- internal channel/account capabilities;
- approval roles;
- confidential product facts;
- private examples;
- internal design/asset references.

Precedence:

```text
current user request
> private/company overlay
> public gtm-listing-demo core and selected public profiles
> defaults
```

Public core files must not embed one company's assumptions.

## Updating

When a real project exposes a workflow failure:

1. determine whether the failure is generic or market/site/product specific;
2. add a failing generic regression first when the behavior belongs in the global core;
3. implement the smallest generic fix without copying product/private data;
4. run all stage/audit selftests and global profile/domain-leakage validation;
5. build both distributions;
6. inspect the Draft PR and CI artifact before merge/release.

Market/site-specific behavior belongs in explicit profiles or overlays rather than generic defaults.
