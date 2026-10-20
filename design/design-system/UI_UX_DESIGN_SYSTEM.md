# UI/UX design system

HYDROOVERITY Operations — original proposed visual system, not a claim of an existing brand or running UI. Issue #2. Default light theme prioritizes daylight field use and legible technical detail; dark palette is specified for later component verification, not double implementation now.

## Tokens

| Token | Light | Dark candidate | Purpose |
| --- | --- | --- | --- |
| canvas | #F4F7FA | #101820 | Page background |
| surface | #FFFFFF | #17232D | Panels/forms |
| text | #172B3A | #E8F0F5 | Main text |
| text-muted | #47596B | #B5C4D0 | Secondary labels |
| brand/action | #075985 | #7DD3FC | Water/infrastructure identity and primary controls |
| border | #CBD5E1 | #526575 | Separators; interactive boundaries need stronger contrast |
| danger | #991B1B | #FCA5A5 | Urgent/error text and icon |
| warning | #854D0E | #FDE68A | Review/stale/ambiguous |
| success | #166534 | #86EFAC | Completed action, never inferred leak verification |
| simulation | #6B21A8 | #D8B4FE | Persistent synthetic-source badge |

White text on dark action/danger/success fills; dark text on pale status fills (#FEE2E2,#FEF3C7,#DCFCE7,#F3E8FF). Never assume every token pair is accessible; the future component test matrix checks actual text/fill combinations. Text contrast target4.5:1, large text3:1, meaningful UI boundaries3:1; text/icon labels accompany colors. Automated ratios for the selected primary pairs are design checks, not whole-app WCAG conformance.

Typography: system sans stack, no external font dependency; body16px/1.5, compact metadata14px/1.45, labels14px/600, H1 32/40, H2 24/32, H3 20/28; tabular numerals for measurements. Avoid text below12px. Units always adjacent to values; unavailable value uses explicit reason. Use locale-aware dates in Asia/Kolkata with timezone visible; UTC remains export/storage truth. English initial copy; translation keys, plural forms, flexible widths and no embedded sentence fragments prepare Telugu/Hindi. No translations claimed.

Spacing scale4,8,12,16,24,32,48,64px; border radius6px inputs /10px panels; subtle elevation only on menus/dialogs. Desktop12-column grid, max content1440px, 24px gutters; sidebar240px collapses below1024px; mobile below640px single column with16px margins and at most four bottom-nav actions plus More. Preserve keyboard focus when navigation collapses. Touch target44px product default; meet WCAG2.2 target-size rules and exceptions, not a false claim that44px itself is the AA criterion.

## Components and behavior

- Tables: labeled sortable headers, stable filters, cursor pagination, no infinite-scroll-only operation; narrow screens show labeled rows/column chooser and horizontal scroll only for genuine data tables. Selection bulk actions revalidate each target; no bulk destructive default.
- Charts: fixed units/axes, timestamp range, source/quality overlay, table/text alternative and downloadable provenance. Never smooth missing observations into measurements. Sampling/aggregation explicitly labeled.
- Map: pipes/junctions/access points use distinct line/icon shapes; eligible, uncertain and unobserved spans have text legend. Candidate interval is a segment overlay with uncertainty, not an exact crack pin. Citizen map never loads internal geometry.
- Cards: title, value/state, reason, freshness, source; avoid decorative KPIs without denominator. Timelines identify observation, interpretation and workflow event separately.
- Forms: persistent label, units/help, required/optional distinction, client guidance plus authoritative server validation. Error summary links fields; retain safe input. Password manager/paste allowed. No color-only field errors.
- Buttons: one primary action; explicit verbs, pending label and busy state; disable duplicates while preserving focus. Secondary/tertiary links distinguish navigation from mutation.
- Dialogs: focus trap, heading/description, Escape/cancel, restore focus; consequential change shows resource, consequence and typed reason; no generic repeated confirmation for ordinary notes.
- Notifications: safe short message, timestamp and accessible live region; no raw contacts or infrastructure location in push/email. Inline errors are persistent; toasts supplement, never replace receipts.
- Offline component: Local draft / Queued / Syncing / Synced / Conflict / Failed, each text+icon; show online-required controls and draft expiry before entry.
- Skeletons match content shape; empty states explain permitted next action; error panels show request ID and retry; destructive retries never bypass idempotency.

## Accessibility and quality

Target [WCAG2.2 AA](https://www.w3.org/TR/WCAG22/): keyboard operation, skip link, meaningful landmarks/headings, visible unobscured focus, responsive reflow/200% text and400% zoom checks, reduced motion, no drag-only task assignment, accessible authentication and programmatic status messages. Test screen-reader forms and chart alternatives with real users/tools later. Theme contrast, touch and focus states require implementation tests. No accessibility certification or completed implementation claimed.
