# OpenForge V1 visual system

This document is the implementation contract for the V1 public surface. The source of truth is `site/app/globals.css` and `site/app/page.tsx`; the direction statement is the comment at the top of `sdk/python/openforge/web/index.html`.

## Intent

OpenForge should feel like an **open print-room dispatch jacket**: warm uncoated paper, dense ink, registration marks, hairline rules, proof stamps, and unequal job-sheet columns. The first viewport must show the product loop in use—intent, routing, and Activity 001—not a slogan hero or generic dashboard.

The UI is **registration proof, not a marketplace**. It explains how a need locks onto independent nodes and records the resulting activity. Do not introduce prices, ratings, popularity charts, competitive leaderboards, or “best match” language. Imported, claimed, connected, and verified are evidence states, not quality rankings:

- **Imported:** publicly discovered.
- **Claimed:** submitted by an operator.
- **Connected:** a working interface exists.
- **Verified:** supporting evidence has been reviewed.

Always render the state name with its visual marker; color alone must never carry the distinction.

## Palette and tokens

Use the existing semantic CSS custom properties. New component styles should consume these tokens rather than repeat their hex values.

| Token | Value | Role |
| --- | --- | --- |
| `--paper` | `#f1ebdc` | Main uncoated-paper canvas |
| `--paper-light` | `#faf7ee` | Focused fields and lifted paper surfaces |
| `--ink` | `#17201d` | Primary text, rules, registration marks |
| `--muted` | `#56605a` | Supporting copy and metadata |
| `--rule` | `#a7aa9f` | Quiet dividers and inactive indicators |
| `--blue` | `#1747c9` | Registration/evidence signal and selected controls |
| `--red` | `#b8321f` | Routing trunk and primary action signal |
| `--yellow` | `#edc94b` | Active route, match, and attention signal |
| `--saffron` | `#d8a236` | Activity ledger stock and claimed state |
| `--dark` | `#202824` | Routing and protocol fields |
| `--page` | `min(100% - 48px, 1540px)` | Desktop content measure |

White, pale-blue support text, and translucent shadows/rules are allowed only where the implemented dark, blue, or saffron surfaces need them. Keep the palette flat and print-like; shadows are sparse registration-depth cues, not a card system. Selection uses yellow on ink. Focus uses a two-color ring: registration blue plus paper on light surfaces, inverted to paper plus blue on dark or cobalt surfaces. The inner outline is 3px wide with a 3px offset.

## Typography

- Use the self-hosted **Newsreader** family for display headlines, ledger numerals, and editorial moments. Fallback: Georgia, then serif. Headlines are regular weight, tightly tracked (`-0.025em` to `-0.035em`), and compact in line height (`0.94`–`1`).
- Use the UI sans stack—Inter, Helvetica Neue, Helvetica, Arial, sans-serif—for navigation, controls, body copy, labels, and table content.
- Use monospace for machine-facing tokens, counts, capability syntax, protocol samples, and route-state readouts.
- Labels and folio metadata are small, bold, uppercase, and tracked. Body copy remains readable at roughly `1.5`–`1.7` line height. Preserve `text-wrap: pretty` on headings and paragraphs.

Do not replace the serif/sans/mono contrast with one universal font, oversized SaaS headings, or decorative type effects. The local Newsreader asset must remain self-hosted; do not add a remote font dependency.

## Layout and spacing

The page is a sequence of full-width editorial bands sharing `--page`. Desktop `--page` is capped at 1540px with 24px side gutters. Major lower sections use 108px vertical padding and 1px ink rules.

The workbench is the signature composition: three unequal columns—intent sheet `0.84fr`, dominant routing field `1.38fr`, ledger `0.84fr`—with a minimum height of 720px. The routing field is inset vertically, dark, and visually dominant. Intent content breathes against the left edge; the saffron ledger reads as a separate inserted sheet. Prefer asymmetry, rules, and content alignment over rounded containers. Corners remain square.

Use the implemented spacing rhythm as the baseline: 5–10px for tags and micro-gaps, 16–30px within components, 34–48px between component groups, and 82–108px between major sections. Use `clamp()` where display size or gutters should scale. Avoid adding a parallel spacing scale unless the CSS is deliberately tokenized in a future refactor.

Responsive behavior is structural:

- At `1160px`, reduce outer gutters, collapse the workbench to two columns, and move the ledger to a full-width row.
- At `820px`, stack the workbench and two-column sections, hide primary nav and table headings, reduce section padding, and turn node rows into a two-column reading order.
- At `520px`, use 11px page gutters, let dark/ledger sheets bleed to the viewport edge, simplify node metadata, and stack the footer.

## Components and states

- **Masthead and wordmark:** compact utilitarian type plus the crosshair registration mark. Links underline on hover; the source link remains visible when the primary nav is hidden.
- **Intent sheet:** label fields as production inputs, use transparent square-edged fields with a single ink underline, and switch focused fields to `--paper-light`. The red full-width route action is the sole dominant action in the first viewport.
- **Routing field:** preserve the intent token → trunk → branches → node sequence. Default branches are quiet dashed rules; routing or matched branches register in yellow with the `register-line` motion. Matched nodes use both the `.lit` marker and text. Result copy explains why matching occurred.
- **Activity ledger:** saffron stock, hairline chronology, editorial numerals, and a slightly rotated proof stamp. Treat it as a public record, never a KPI card or success claim.
- **Draft activity:** appears only after a match is opened. It names participants and makes the next external step explicit.
- **Filters and node index:** filters are a ruled strip; the active filter uses `aria-pressed="true"`, blue text, and a blue underline. Rows stay plain and data-dense. Capability tags are code-like labels, not colorful pills. Preserve table roles when the layout reflows.
- **Connection state:** pair the status dot with its state label. `imported` is neutral/rule, `claimed` saffron, `connected` red, and `verified` blue. These colors communicate evidence progression only.
- **Join sheet and protocol block:** blue is the invitation/registration surface; dark is the machine/protocol surface. Keep examples literal and copyable.
- **Loading/disabled:** while routing, disable the primary action, use explicit progress copy, and keep `cursor: wait`. Do not rely on opacity alone to explain the state.
- **Hover/focus:** hover may underline or invert the established signal color. Every interactive element must retain the global visible `:focus-visible` outline; never remove it without an equally strong replacement.

## Accessibility and motion

Keep the skip link as the first focusable control and reveal it on focus. Forms require visible labels, native required/disabled behavior, and plain-language status text. Dynamic routing results and the draft activity use polite live regions. Decorative registration marks, route SVGs, arrows, and dots are hidden from assistive technology; their meaning is repeated in text.

Maintain WCAG AA contrast for text and at least 3:1 for controls/focus indicators. Verify custom text colors against their actual paper, saffron, blue, or dark background. Keep tap targets comfortably operable even when typography is small. The layout must remain usable from the 320px body minimum upward without horizontal page scrolling; local code and filter regions may scroll.

Honor `prefers-reduced-motion: reduce`: disable smooth scrolling and collapse animations to an effectively instantaneous duration. Routing must remain understandable with no animation.

## Anti-patterns

Do not add:

- a centered marketing hero, glassmorphism, gradient mesh, rounded-card dashboard, or generic SaaS component styling;
- marketplace cues such as prices, star ratings, ranks, “top providers,” or claims that evidence state implies quality;
- decorative illustration that competes with the routing registration field;
- excessive shadows, radii, pills, icons, or additional accent colors;
- color-only status, hover-only disclosure, hidden keyboard focus, or motion required to understand a result;
- remote font loading, novelty display fonts, or typography that erases the Newsreader/UI/mono hierarchy;
- uniform equal columns or containerized cards that flatten the dispatch-jacket composition;
- invented metrics, network-effect claims, or activity copy that overstates what the public record proves.
