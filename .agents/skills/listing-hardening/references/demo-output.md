# Final Demo output contract

## Required delivery

The final project Demo is delivered as **one single standalone HTML file** such as `<project>-listing-demo.html`.

Do not deliver the project Demo as a ZIP and do not require an adjacent `assets` folder. Distribution/install ZIPs are separate from the user-facing project Demo.

## Standalone static requirements

- Runtime images/resources are physically embedded as portable `data:` URIs; inline SVG is allowed, but external/local SVG `<image>/<use>` references are not.
- CSS is inline. No external/local stylesheet, `@import`, or external/local `url(...)` dependency, including inline `style` attributes.
- JavaScript is inline. No `<script src>` dependency.
- Literal session-only `blob:` resources are not portable and are rejected.
- `<img srcset>` / `<source srcset>` may contain only embedded image candidates.
- Media resources must not depend on adjacent files or network assets.
- Responsive viewport and width breakpoint are required.
- Images use a responsive max-width contract.

Run the static preflight on the exact final file:

```bash
python3 .agents/skills/listing-hardening/scripts/validate_demo_html.py <project>-listing-demo.html --json
```

A non-PASS result blocks delivery. Static PASS proves portability/structure only; it does not prove interaction behavior.

## Carousel

A page with no planned carousel may remain a valid static Demo. When carousel interaction is present, the static preflight requires a carousel root, at least two slides, previous/next controls, and coherent inline structure, but `carousel_contract` remains runtime-required. JavaScript keywords or unused handler-like strings never constitute hard interaction proof.

## Runtime hard verification

Run the exact final file through:

```bash
python3 .agents/skills/listing-hardening/scripts/validate_demo_runtime.py <project>-listing-demo.html --output runtime-evidence.json
```

Browser runtime verification uses Playwright/Chromium, observes and blocks external network requests, and binds evidence to the exact HTML SHA-256.

It opens the Demo at:

- **1440px** desktop;
- **390px** mobile.

At both widths it verifies no horizontal overflow, no broken images, and no clipped primary copy/controls. When a carousel is present, the validator clicks next and previous and proves the visible state changes and returns.

Final Delivery State must bind this browser evidence to the exact Demo SHA through `DEMO_RUNTIME_GATE`.

**If Playwright/Chromium runtime verification cannot be performed, runtime Demo QA remains `UNVERIFIED/BLOCKED`.** Do not claim PASS from source inspection alone.
