# Final Demo output contract

## Required delivery

The final project Demo is delivered as **one single standalone HTML file** such as `<project>-listing-demo.html`.

Do not deliver the project Demo as a ZIP and do not require an adjacent `assets` folder. Distribution/install ZIPs are separate from the user-facing project Demo.

## Standalone requirements

- Raster images/resources used at runtime are physically embedded as portable `data:` URIs; inline SVG is allowed.
- CSS is inline. No external/local stylesheet or `@import` dependency.
- JavaScript is inline. No `<script src>` dependency.
- Literal session-only `blob:` resources are not portable and are rejected.
- `<img srcset>` / `<source srcset>` may contain only embedded image candidates.
- CSS `url(...)` and media resources must not depend on adjacent files or network assets.
- Responsive viewport and width breakpoint are required.
- Images use a responsive max-width contract.

Run the static validator on the exact final file:

```bash
python .agents/skills/listing-hardening/scripts/validate_demo_html.py <project>-listing-demo.html --json
```

A non-PASS result blocks delivery.

## Carousel

When carousel interaction is planned, the final HTML needs a carousel root, at least two slides, previous/next controls, and inline click wiring. Static verification is necessary but not sufficient; exercise both directions in a browser.

## Runtime verification

Open the exact final file at:

- **1440px** desktop;
- **390px** mobile.

At both widths verify:

- no horizontal overflow;
- no broken images;
- no clipped primary copy or controls;
- correct approved content order;
- correct image/text pairing;
- required carousel/tabs/other review interactions operate;
- Review Mode does not corrupt Consumer Mode layout.

**If browser/runtime verification cannot be performed, mobile/interaction Demo QA is BLOCKED.** Do not claim PASS from source inspection alone.
