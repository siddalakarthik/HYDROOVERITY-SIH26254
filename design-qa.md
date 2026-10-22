# M04 visual QA

Source visual truth: owner-approved Option 3, `exec-890ec764-4d65-4fd0-87a6-d02dc99d55bc.png`, in the conversation generated-image directory. Measured source: 1374 × 1145 pixels. Option 2 informs authenticated information architecture only. M02 design tokens and engineering semantics override mockup inaccuracies.

Implementation: anonymous `/`, light theme, viewport 1374 × 1145 CSS pixels, device scale 1. Full-page implementation is 1374 × 1237; the matching viewport crop and complete page were reviewed separately. This is the approved visual direction implemented responsively, with M02 system typography, rather than an exact raster copy.

Evidence is preserved outside Git under the existing task workspace: `work/m04-evidence/screenshots/`, `work/m04-evidence/comparison/` and `work/m04-evidence/m04-review-contact-sheet.png`. The combined `home-comparison-before.png` and `home-comparison-after.png` each contain source and rendered implementation together. Focused hero/diagram comparison images were also opened. No comparison is claimed from code alone.

## Findings and fixes

- [P2, resolved] Homepage had excessive vertical spacing relative to the selected composition. Header, mission, evidence diagram and story spacing were tightened. Post-fix same-viewport comparison preserves the editorial index, two-column mission/status, evidence chain and resident/verification stories. Natural page scrolling remains; no content is clipped to force a single screen.
- [P1, resolved] Initial MapLibre canvas rendered without working geometry because the bundled worker URL was empty. The pinned worker is emitted as a same-origin hashed asset, and the browser test waits for rendered idle. Desktop and mobile captures now show the actual authorized synthetic pipe and its two junctions.
- [P2, resolved] Mobile resizing could crop the desktop-fitted geometry. The map refits available bounds on resize; the reviewed 390-pixel capture shows both endpoints.
- [P2, resolved] Breadcrumb links relied on color in text. They are visibly underlined; executed axe checks pass on the tested core pages.
- [P2, resolved] Initial captures could precede private-page hydration. Capture waits for the protected page heading and visible loaders to clear; administration additionally waits for the populated directory. The populated directory was independently recaptured and inspected.
- [P2, resolved] Workspace breadcrumbs exposed long design objectives. They now use concise task labels such as Network and My reports.

## Required fidelity surfaces

- Typography: Segoe UI/system stack, M02 hierarchy, readable body/labels, intentional 40-pixel public hero. The three-line mission statement retains the selected wrapping. The source's exact font and filled icon treatment are not additional dependencies.
- Spacing/layout: editorial left index, mission/status balance, three observation panels, qualification/verification sequence, paired stories and amber limitation notice are retained. Staff screens share one 240-pixel sidebar system and responsive controls.
- Colors/tokens: approved M02 white/canvas, dark text, blue actions, teal engineering distinction and amber uncertainty. Status meaning is always stated in text.
- Assets: reviewed M08 digital engineering plates retain proposed/not-physically-tested labels. UI uses Lucide icons and an accessible semantic engineering diagram explicitly authorized by the owner. No fabricated device photograph, external image CDN or stock-photo placeholder is used.
- Copy/content: WATCH is hydraulic/supply context; exactly five wetness channels belong to GUARD-5; EAR has one physical sampling clock. Unknown observations, NOT_VERIFIABLE and all hardware/scientific limitations remain explicit.

## Runtime and mobile review

Real Chrome browser scenarios passed on the production build with the real private backend/PostGIS. Required widths 360, 390, 640, 768, 1024, 1280, 1440 and 1920 have executed overflow checks. Core mobile reporting, resident list, technician brief and network captures were inspected. Axe covers the executed public, identity, resident, overview, incident, technician, verification, map, administration, audit and session views. This is scoped evidence, not a whole-application WCAG certification.

Focused review included actual reporting fields, visible keyboard focus, mobile map endpoints, safe verification history, incident state/history and populated membership controls. No unresolved P0/P1/P2 presentation defect was found in these reviewed states.

## Follow-up polish and limits

- [P3] The source has larger filled status/index icons; the implemented line icons and M02 typography are consistent and readable. Exact raster matching is not claimed.
- [P3] Long membership/audit pages use cursor pagination and natural scrolling. Dense production inventories may warrant additional authorized search contracts later.
- No screenshots establish physical hardware, field performance, internet latency or public deployment readiness.

Implementation checklist: source/render comparison performed; demonstrated defects fixed; post-fix captures inspected; responsive states reviewed; scientific labels preserved. Owner review and actual PR CI remain separate gates.

final result: passed
