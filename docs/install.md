# Installation and reuse

## Codex repository skill

The repository skill lives at:

```text
.agents/skills/gtm-listing-demo/
```

Open the repository in Codex App, CLI, or IDE and invoke:

```text
$gtm-listing-demo
```

## Personal Skill package

Run:

```bash
python .agents/skills/gtm-listing-demo/scripts/validate_skill.py
python .agents/skills/gtm-listing-demo/scripts/package_skill.py
```

Upload `dist/gtm-listing-demo.skill.zip` where Personal Skills are supported.

## Reusing in another repository

Choose one approach:

1. Install this Skill globally or as a Personal Skill.
2. Copy `.agents/skills/gtm-listing-demo/` into the target repository.
3. Use a private overlay that explicitly requires this public core.

## Private overlay model

Keep confidential material outside this public repository. A private overlay may add:

- company claim rules
- internal channel capabilities
- approval roles
- confidential product facts
- private examples
- internal Figma or asset references

Precedence:

```text
current user request
> private or company overlay
> public gtm-listing-demo core
> defaults
```

The private overlay must not modify the public core to embed one company's assumptions.

## Updating

After changing the public core:

1. update evals first when a new failure is discovered;
2. revise the Skill or profile;
3. run the validator;
4. build the ZIP;
5. review the CI artifact before release.
