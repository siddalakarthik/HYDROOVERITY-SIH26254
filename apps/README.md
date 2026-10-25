# Web application

The accepted M04 Next.js / React / TypeScript application is merged, with M06 scientific integration and M07-A/B/C service, dispatch and communications increments. The full application remains private-development only; the public repository is not a public service deployment.

Start with the [web setup guide](web/README.md), [runtime capability map](web/src/lib/route-capabilities.json), [M09 executed acceptance](../docs/testing/M09_FULL_SYSTEM_ACCEPTANCE.md) and [current completion register](../docs/testing/PRE_M10_COMPLETION_REGISTER.md). The web guide's original M04 counts describe its historical 58-operation starting point; the combined backend currently exposes 111 implemented operations, not every proposed design endpoint.

Public pages explain qualified evidence and limitations. Authenticated routes cover residents, supervisors, engineers, technicians and administrators, using backend identity and permissions. Infrastructure maps use authorized stored geometry. No sensors, bookings, shifts or field measurements are fabricated for presentation.

For local authentication, use the real API and verified localhost HTTPS. HTTP public-page previews do not establish a working login. Preserve accepted visual Option 3 and the shared authenticated design system; run the existing real browser, responsive, accessibility, type, lint and build checks for changes.
