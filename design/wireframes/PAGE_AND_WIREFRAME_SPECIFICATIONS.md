# Page and wireframe specifications

Design only; issue #2. Route inventory is in PRODUCT_INFORMATION_ARCHITECTURE.md; API wire schemas are canonical in openapi-design.json. The page-to-operation list below defines the available action vocabulary, not a grant of every group operation to every page role. Render only relevant controls after intersecting page role, endpoint role, resource ownership/assignment and current state. Navigation links have no database effect. Each network action uses the endpoint's validated request, response, persistence and errors; do not substitute frontend-only success.

All pages: keyboard-accessible focus order, persistent organization/mode header, text status/reason, reconnect/freshness indicator. No exact leak marker without qualified evidence. Mutation success requires server receipt; error remains near its field/control and preserves safe draft values. Uniform 404 for inaccessible IDs; 401 asks sign-in, 403 explains missing capability without revealing resources, 409/412 offers compare/reload, 422 links fields, 429 shows retry time, 503 shows dependency failure. Every form has pending/disabled duplicate-submit state and confirmation only for consequential privileged actions. Raw tokens never appear in UI history or telemetry.

## PAGE-01 — /

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Understand mission and honest project status.
- Visible data: Understand mission and honest project status; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: Read static reviewed content; navigation to related explanation/report pages; no business write API.
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain content currently unavailable; provide safe navigation.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-02 — /solution

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Understand evidence-qualified integrated system.
- Visible data: Understand evidence-qualified integrated system; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: Read static reviewed content; navigation to related explanation/report pages; no business write API.
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain content currently unavailable; provide safe navigation.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-03 — /how-it-works

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Follow WATCH, GUARD-5, EAR and VERIFY.
- Visible data: Follow WATCH, GUARD-5, EAR and VERIFY; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: Read static reviewed content; navigation to related explanation/report pages; no business write API.
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain content currently unavailable; provide safe navigation.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-04 — /solution/guard5

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Inspect five conceptual channels and unvalidated collector mechanics.
- Visible data: Inspect five conceptual channels and unvalidated collector mechanics; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: Read static reviewed content; navigation to related explanation/report pages; no business write API.
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain content currently unavailable; provide safe navigation.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-05 — /solution/acoustics

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Understand eligible spans, intervals and abstention.
- Visible data: Understand eligible spans, intervals and abstention; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: Read static reviewed content; navigation to related explanation/report pages; no business write API.
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain content currently unavailable; provide safe navigation.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-06 — /benefits-and-limitations

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Compare intended benefits with coverage and validation limits.
- Visible data: Compare intended benefits with coverage and validation limits; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: Read static reviewed content; navigation to related explanation/report pages; no business write API.
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain content currently unavailable; provide safe navigation.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-07 — /project-status

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: See designed versus implemented versus physically validated status.
- Visible data: See designed versus implemented versus physically validated status; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /public/utilities/{slug}`; `GET /public/project-status`; `POST /public/contact`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-08 — /report

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Select an enabled utility and sign in to report.
- Visible data: Select an enabled utility and sign in to report; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /public/utilities/{slug}`; `GET /public/project-status`; `POST /public/contact`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-09 — /contact

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Submit a bounded question or feedback.
- Visible data: Submit a bounded question or feedback; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /public/utilities/{slug}`; `GET /public/project-status`; `POST /public/contact`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-10 — /privacy

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Understand data collection, retention and rights contact.
- Visible data: Understand data collection, retention and rights contact; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: Read static reviewed content; navigation to related explanation/report pages; no business write API.
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain content currently unavailable; provide safe navigation.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-11 — /terms

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Read proposed service and demonstration boundaries.
- Visible data: Read proposed service and demonstration boundaries; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: Read static reviewed content; navigation to related explanation/report pages; no business write API.
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain content currently unavailable; provide safe navigation.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Previously fetched public text may be cached; forms require online access.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-12 — /login

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Sign in using the single backend session.
- Visible data: Sign in using the single backend session; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /auth/csrf`; `POST /auth/register`; `POST /auth/login`; `POST /auth/recovery`; `POST /auth/reset`; `POST /auth/verify`; `POST /auth/invitation-accept`; `POST /auth/logout`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-13 — /register

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Register as citizen for enabled utility only.
- Visible data: Register as citizen for enabled utility only; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /auth/csrf`; `POST /auth/register`; `POST /auth/login`; `POST /auth/recovery`; `POST /auth/reset`; `POST /auth/verify`; `POST /auth/invitation-accept`; `POST /auth/logout`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-14 — /forgot-password

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Request generic account recovery.
- Visible data: Request generic account recovery; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /auth/csrf`; `POST /auth/register`; `POST /auth/login`; `POST /auth/recovery`; `POST /auth/reset`; `POST /auth/verify`; `POST /auth/invitation-accept`; `POST /auth/logout`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-15 — /reset-password

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Consume one-use reset token.
- Visible data: Consume one-use reset token; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /auth/csrf`; `POST /auth/register`; `POST /auth/login`; `POST /auth/recovery`; `POST /auth/reset`; `POST /auth/verify`; `POST /auth/invitation-accept`; `POST /auth/logout`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-16 — /verify-account

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Verify an account with one-use token.
- Visible data: Verify an account with one-use token; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /auth/csrf`; `POST /auth/register`; `POST /auth/login`; `POST /auth/recovery`; `POST /auth/reset`; `POST /auth/verify`; `POST /auth/invitation-accept`; `POST /auth/logout`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-17 — /accept-invitation

- Audience: PUBLIC; active tenant and endpoint-level authorization apply.
- Objective: Accept exact tenant staff invitation.
- Visible data: Accept exact tenant staff invitation; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /auth/csrf`; `POST /auth/register`; `POST /auth/login`; `POST /auth/recovery`; `POST /auth/reset`; `POST /auth/verify`; `POST /auth/invitation-accept`; `POST /auth/logout`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-18 — /account

- Audience: ALL; active tenant and endpoint-level authorization apply.
- Objective: Edit own profile and choose membership.
- Visible data: Edit own profile and choose membership; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /me`; `PATCH /me`; `GET /me/memberships`; `GET /me/sessions`; `DELETE /me/sessions/{session_id}`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-19 — /account/sessions

- Audience: ALL; active tenant and endpoint-level authorization apply.
- Objective: Inspect and revoke own sessions.
- Visible data: Inspect and revoke own sessions; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /me`; `PATCH /me`; `GET /me/memberships`; `GET /me/sessions`; `DELETE /me/sessions/{session_id}`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-20 — /citizen/{org}/reports

- Audience: CITIZEN; active tenant and endpoint-level authorization apply.
- Objective: View only own reports.
- Visible data: View only own reports; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `POST /orgs/{organization_id}/complaints`; `GET /orgs/{organization_id}/complaints`; `GET /orgs/{organization_id}/complaints/{complaint_id}`; `POST /orgs/{organization_id}/complaints/{complaint_id}/follow-ups`; `POST /orgs/{organization_id}/complaints/{complaint_id}/review`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no reports submitted; offer New report.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-21 — /citizen/{org}/reports/new

- Audience: CITIZEN; active tenant and endpoint-level authorization apply.
- Objective: Submit category, description, coarse area and consented photo.
- Visible data: Submit category, description, coarse area and consented photo; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `POST /orgs/{organization_id}/complaints`; `GET /orgs/{organization_id}/complaints`; `GET /orgs/{organization_id}/complaints/{complaint_id}`; `POST /orgs/{organization_id}/complaints/{complaint_id}/follow-ups`; `POST /orgs/{organization_id}/complaints/{complaint_id}/review`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no reports submitted; offer New report.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-22 — /citizen/{org}/reports/{id}

- Audience: CITIZEN; active tenant and endpoint-level authorization apply.
- Objective: Track safe updates, add followup and resolution feedback.
- Visible data: Track safe updates, add followup and resolution feedback; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `POST /orgs/{organization_id}/complaints`; `GET /orgs/{organization_id}/complaints`; `GET /orgs/{organization_id}/complaints/{complaint_id}`; `POST /orgs/{organization_id}/complaints/{complaint_id}/follow-ups`; `POST /orgs/{organization_id}/complaints/{complaint_id}/review`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no reports submitted; offer New report.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Read-only shell; connection required for current data.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-23 — /app/{org}/overview

- Audience: ENGINEER,SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Review supply states, active concerns, stale devices and coverage gaps.
- Visible data: Review supply states, active concerns, stale devices and coverage gaps; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/incidents`; `POST /orgs/{organization_id}/incidents`; `GET /orgs/{organization_id}/incidents/{incident_id}`; `GET /orgs/{organization_id}/incidents/{incident_id}/timeline`; `POST /orgs/{organization_id}/incidents/{incident_id}/transitions`; `POST /orgs/{organization_id}/incidents/{incident_id}/links`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-24 — /app/{org}/network

- Audience: ENGINEER,SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Explore surveyed graph and instrumented/unobserved spans.
- Visible data: Explore surveyed graph and instrumented/unobserved spans; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/junctions`; `POST /orgs/{organization_id}/junctions`; `GET /orgs/{organization_id}/junctions/{resource_id}`; `PATCH /orgs/{organization_id}/junctions/{resource_id}`; `GET /orgs/{organization_id}/pipes`; `POST /orgs/{organization_id}/pipes`; `GET /orgs/{organization_id}/pipes/{resource_id}`; `PATCH /orgs/{organization_id}/pipes/{resource_id}`; `GET /orgs/{organization_id}/access-points`; `POST /orgs/{organization_id}/access-points`; `GET /orgs/{organization_id}/access-points/{resource_id}`; `PATCH /orgs/{organization_id}/access-points/{resource_id}`; `GET /orgs/{organization_id}/coverage`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-25 — /app/{org}/monitoring

- Audience: ENGINEER,SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Read fresh and historic observations with explicit provenance.
- Visible data: Read fresh and historic observations with explicit provenance; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/observations`; `GET /orgs/{organization_id}/observations/{observation_id}`; `POST /orgs/{organization_id}/manual-observations`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-26 — /app/{org}/devices

- Audience: ENGINEER,SUPERVISOR,ADMIN; active tenant and endpoint-level authorization apply.
- Objective: Find devices by identity, health and source environment.
- Visible data: Find devices by identity, health and source environment; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/devices`; `POST /orgs/{organization_id}/devices`; `GET /orgs/{organization_id}/devices/{device_id}`; `GET /orgs/{organization_id}/devices/{device_id}/channels`; `GET /orgs/{organization_id}/devices/{device_id}/configurations`; `POST /orgs/{organization_id}/devices/{device_id}/configurations`; `POST /orgs/{organization_id}/devices/{device_id}/installations`; `POST /orgs/{organization_id}/devices/{device_id}/credentials`; `DELETE /orgs/{organization_id}/devices/{device_id}/credentials/{credential_id}`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-27 — /app/{org}/devices/{id}

- Audience: ENGINEER,SUPERVISOR,ADMIN; active tenant and endpoint-level authorization apply.
- Objective: Inspect permitted device metadata, diagnostics and calibration tabs.
- Visible data: Inspect permitted device metadata, diagnostics and calibration tabs; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/devices/{device_id}/health-events`; `GET /orgs/{organization_id}/devices/{device_id}/calibrations`; `POST /orgs/{organization_id}/devices/{device_id}/calibrations`; `GET /orgs/{organization_id}/collars/{device_id}/service-tests`; `POST /orgs/{organization_id}/collars/{device_id}/service-tests`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-28 — /app/{org}/collars/{id}

- Audience: ENGINEER,SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Inspect five channel timelines, EXT/BYPASS and service receipts.
- Visible data: Inspect five channel timelines, EXT/BYPASS and service receipts; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/devices/{device_id}/health-events`; `GET /orgs/{organization_id}/devices/{device_id}/calibrations`; `POST /orgs/{organization_id}/devices/{device_id}/calibrations`; `GET /orgs/{organization_id}/collars/{device_id}/service-tests`; `POST /orgs/{organization_id}/collars/{device_id}/service-tests`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-29 — /app/{org}/acoustics

- Audience: ENGINEER; active tenant and endpoint-level authorization apply.
- Objective: Choose authorized capture and eligible span.
- Visible data: Choose authorized capture and eligible span; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/acoustic-captures`; `POST /orgs/{organization_id}/acoustic-captures`; `GET /orgs/{organization_id}/acoustic-captures/{capture_id}`; `POST /orgs/{organization_id}/acoustic-captures/{capture_id}/estimates`; `GET /orgs/{organization_id}/acoustic-captures/{capture_id}/estimates`; `GET /orgs/{organization_id}/artifacts/{artifact_id}/download`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-30 — /app/{org}/acoustics/{id}

- Audience: ENGINEER; active tenant and endpoint-level authorization apply.
- Objective: Compare delay baselines, assumptions, interval and unresolved reasons.
- Visible data: Compare delay baselines, assumptions, interval and unresolved reasons; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/acoustic-captures`; `POST /orgs/{organization_id}/acoustic-captures`; `GET /orgs/{organization_id}/acoustic-captures/{capture_id}`; `POST /orgs/{organization_id}/acoustic-captures/{capture_id}/estimates`; `GET /orgs/{organization_id}/acoustic-captures/{capture_id}/estimates`; `GET /orgs/{organization_id}/artifacts/{artifact_id}/download`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-31 — /app/{org}/incidents

- Audience: ENGINEER,SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Filter and triage concerns without equating severity with confidence.
- Visible data: Filter and triage concerns without equating severity with confidence; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/incidents`; `POST /orgs/{organization_id}/incidents`; `GET /orgs/{organization_id}/incidents/{incident_id}`; `GET /orgs/{organization_id}/incidents/{incident_id}/timeline`; `POST /orgs/{organization_id}/incidents/{incident_id}/transitions`; `POST /orgs/{organization_id}/incidents/{incident_id}/links`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-32 — /app/{org}/incidents/{id}

- Audience: ENGINEER,SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Read immutable evidence timeline and authorize next investigation action.
- Visible data: Read immutable evidence timeline and authorize next investigation action; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/incidents`; `POST /orgs/{organization_id}/incidents`; `GET /orgs/{organization_id}/incidents/{incident_id}`; `GET /orgs/{organization_id}/incidents/{incident_id}/timeline`; `POST /orgs/{organization_id}/incidents/{incident_id}/transitions`; `POST /orgs/{organization_id}/incidents/{incident_id}/links`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-33 — /app/{org}/work-orders

- Audience: ENGINEER,SUPERVISOR,TECHNICIAN; active tenant and endpoint-level authorization apply.
- Objective: Use supervisor board or technician assigned-task list.
- Visible data: Use supervisor board or technician assigned-task list; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/work-orders`; `POST /orgs/{organization_id}/work-orders`; `GET /orgs/{organization_id}/work-orders/{work_order_id}`; `GET /orgs/{organization_id}/work-orders/{work_order_id}/brief`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/assignment`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/actions`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/transitions`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Cached minimal assigned task list only.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-34 — /app/{org}/work-orders/{id}

- Audience: ENGINEER,SUPERVISOR,TECHNICIAN; active tenant and endpoint-level authorization apply.
- Objective: Investigate, record work and submit for review.
- Visible data: Investigate, record work and submit for review; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/work-orders`; `POST /orgs/{organization_id}/work-orders`; `GET /orgs/{organization_id}/work-orders/{work_order_id}`; `GET /orgs/{organization_id}/work-orders/{work_order_id}/brief`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/assignment`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/actions`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/transitions`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Assigned task briefs and encrypted draft notes/photos only; no assignments, transitions or approvals offline.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-35 — /app/{org}/repairs/{id}/verification

- Audience: ENGINEER,SUPERVISOR,TECHNICIAN; active tenant and endpoint-level authorization apply.
- Objective: Review comparable before/after evidence and separate outcome.
- Visible data: Review comparable before/after evidence and separate outcome; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `POST /orgs/{organization_id}/repairs/{repair_id}/verifications`; `GET /orgs/{organization_id}/repairs/{repair_id}/verifications`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-36 — /app/{org}/complaints

- Audience: SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Review public-safe reports and link evidence without automatic confirmation.
- Visible data: Review public-safe reports and link evidence without automatic confirmation; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `POST /orgs/{organization_id}/complaints`; `GET /orgs/{organization_id}/complaints`; `GET /orgs/{organization_id}/complaints/{complaint_id}`; `POST /orgs/{organization_id}/complaints/{complaint_id}/follow-ups`; `POST /orgs/{organization_id}/complaints/{complaint_id}/review`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-37 — /app/{org}/maintenance

- Audience: SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Review overdue work and assign priorities and due dates.
- Visible data: Review overdue work and assign priorities and due dates; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/work-orders`; `POST /orgs/{organization_id}/work-orders`; `GET /orgs/{organization_id}/work-orders/{work_order_id}`; `GET /orgs/{organization_id}/work-orders/{work_order_id}/brief`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/assignment`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/actions`; `POST /orgs/{organization_id}/work-orders/{work_order_id}/transitions`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-38 — /app/{org}/analytics

- Audience: ENGINEER,SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Inspect explicit denominators, response time and observable coverage.
- Visible data: Inspect explicit denominators, response time and observable coverage; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `POST /orgs/{organization_id}/reports`; `GET /orgs/{organization_id}/reports/{report_id}`; `GET /orgs/{organization_id}/reports/{report_id}/download`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-39 — /app/{org}/reports

- Audience: ENGINEER,SUPERVISOR; active tenant and endpoint-level authorization apply.
- Objective: Request scoped CSV/PDF and download authorized completed export.
- Visible data: Request scoped CSV/PDF and download authorized completed export; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `POST /orgs/{organization_id}/reports`; `GET /orgs/{organization_id}/reports/{report_id}`; `GET /orgs/{organization_id}/reports/{report_id}/download`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-40 — /app/{org}/simulations

- Audience: ENGINEER; active tenant and endpoint-level authorization apply.
- Objective: Select allowed scenario/config and queue a reproducible run.
- Visible data: Select allowed scenario/config and queue a reproducible run; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/simulations/scenarios`; `POST /orgs/{organization_id}/simulations/runs`; `GET /orgs/{organization_id}/simulations/runs`; `GET /orgs/{organization_id}/simulations/runs/{run_id}`; `POST /orgs/{organization_id}/simulations/runs/{run_id}/cancel`; `GET /orgs/{organization_id}/simulations/runs/{run_id}/outputs`; `GET /orgs/{organization_id}/simulations/runs/{run_id}/evaluation`; `GET /orgs/{organization_id}/algorithm-configurations`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-41 — /app/{org}/simulations/{id}

- Audience: ENGINEER; active tenant and endpoint-level authorization apply.
- Objective: Inspect status and synthetic outputs; evaluation separately gated.
- Visible data: Inspect status and synthetic outputs; evaluation separately gated; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/simulations/scenarios`; `POST /orgs/{organization_id}/simulations/runs`; `GET /orgs/{organization_id}/simulations/runs`; `GET /orgs/{organization_id}/simulations/runs/{run_id}`; `POST /orgs/{organization_id}/simulations/runs/{run_id}/cancel`; `GET /orgs/{organization_id}/simulations/runs/{run_id}/outputs`; `GET /orgs/{organization_id}/simulations/runs/{run_id}/evaluation`; `GET /orgs/{organization_id}/algorithm-configurations`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-42 — /app/{org}/feedback

- Audience: ALL; active tenant and endpoint-level authorization apply.
- Objective: Review own feedback or authorized internal backlog.
- Visible data: Review own feedback or authorized internal backlog; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `POST /orgs/{organization_id}/feedback`; `GET /orgs/{organization_id}/feedback`; `POST /orgs/{organization_id}/feedback/{feedback_id}/review`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-43 — /app/{org}/notifications

- Audience: ALL; active tenant and endpoint-level authorization apply.
- Objective: Read only own safe notifications.
- Visible data: Read only own safe notifications; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/notifications`; `POST /orgs/{organization_id}/notifications/{notification_id}/read`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-44 — /app/{org}/admin/users

- Audience: ADMIN; active tenant and endpoint-level authorization apply.
- Objective: Invite, grant primary roles and suspend tenant memberships.
- Visible data: Invite, grant primary roles and suspend tenant memberships; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/memberships`; `POST /orgs/{organization_id}/invitations`; `PUT /orgs/{organization_id}/memberships/{membership_id}/roles`; `POST /orgs/{organization_id}/memberships/{membership_id}/status`; `GET /orgs/{organization_id}/audit-logs`; `GET /orgs/{organization_id}/integrations`; `PUT /orgs/{organization_id}/integrations`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-45 — /app/{org}/admin/settings

- Audience: ADMIN; active tenant and endpoint-level authorization apply.
- Objective: Manage tenant and integration references without returning secrets.
- Visible data: Manage tenant and integration references without returning secrets; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}`; `PATCH /orgs/{organization_id}`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## PAGE-46 — /app/{org}/admin/audit

- Audience: ADMIN; active tenant and endpoint-level authorization apply.
- Objective: Inspect safe privileged-action history.
- Visible data: Inspect safe privileged-action history; safe projection only, current timestamp and provenance where applicable.
- Controls/APIs: `GET /orgs/{organization_id}/memberships`; `POST /orgs/{organization_id}/invitations`; `PUT /orgs/{organization_id}/memberships/{membership_id}/roles`; `POST /orgs/{organization_id}/memberships/{membership_id}/status`; `GET /orgs/{organization_id}/audit-logs`; `GET /orgs/{organization_id}/integrations`; `PUT /orgs/{organization_id}/integrations`
- Permission: intersect listed audience with API role+scope; citizen own records, technician current assigned parent, evaluator separate grant.
- Loading: skeleton matching final layout with accessible busy region; no changing random metrics.
- Empty: explain no permitted records/configuration yet; show only a role-authorized next action.
- Error: apply typed error policy above; show request ID, not traces; retain user-entered nonsensitive draft.
- Offline: Current data and mutations require connection; never silently display cached values as fresh.
- Mobile: single primary column; controls >=44px product target; table becomes labeled rows; graph/chart has a list/text alternative.
- Acceptance: allowed role reaches its objective using authorized APIs; disallowed role and changed IDs fail; all states render; mode and freshness survive reload/export; no control reports success before receipt.

## Wireframe — Public landing

```text
[Header / report water issue]
[Mission + DESIGN / HARDWARE UNTESTED]
[WATCH | GUARD-5 | EAR: conceptual diagram]
[Who benefits / limits / evidence]
[Citizen entry] [How repair is verified]
[Team / privacy / terms]
```

Lead with purpose; below hero disclose observability and absence of hardware validation. CTA opens utility selector, not a fake live dashboard.

## Wireframe — Citizen report

```text
[Utility name / account]
[Step 1 category radios]
[Step 2 description + rough area]
[Optional photo + explicit consent]
[Review privacy / submit]
[Receipt tracking number / own reports]
```

Use persistent labels, 2000-character counter, photo progress/retry; no exact pipe/GPS request. Submission requires online receipt and Idempotency-Key.

## Wireframe — Utility command center

```text
[Org] [SIMULATED DATA / operational] [freshness]
[Supply state + reason] [open incidents] [device faults]
[Zone map + observable coverage legend]
[Priority investigation queue / next action]
[Recent evidence and assignment timeline]
```

Counts share declared mode/time filters. Severity and scientific confidence occupy separate columns. Unknown/empty values are em dashes with explanation.

## Wireframe — Network explorer

```text
[Zone/search/material/accessibility filters]
[Graph map 2/3 width] [selected segment panel]
[Junctions / length basis / uncertainty]
[Collars / eligible spans / gaps legend]
[Table alternative / coverage explanation]
```

Never interpolate unknown connectivity into confirmed graph. Mobile map sits above selected asset/list, not a tiny split screen.

## Wireframe — Acoustic investigation

```text
[Capture + endpoints + shared-clock quality]
[Pressure/path eligibility and assumptions]
[Two waveform previews / bounded fetch]
[Correlation baseline | GCC-PHAT]
[Candidate interval(s) OR unresolved reason]
[Create reviewed assessment / compare windows]
```

Display lag convention, speed/length uncertainty and mode. No single exact pin. Raw waveform download requires engineer permission and is outside SSE.

## Wireframe — GUARD-5 diagnostics

```text
[Collar/device health/context]
[A | B | C | EXT | BYPASS labeled traces]
[Water-arrival order + competing explanations]
[Service test history / drainage / crosstalk]
[Fault evidence / investigation next step]
```

Channel B and BYPASS have different labels; unsupported electrical supervision reads UNKNOWN. Challenge receipts are manual context, not proof of collector geometry.

## Wireframe — Mobile technician work order

```text
[My task / status / assignment lease]
[Approximate location + safe navigation consent]
[Evidence summary + safety checklist]
[Inspection notes / photo / materials]
[Repair receipt / local draft status]
[Sync queue] [Submit online for review]
```

Sticky footer never covers focused input. Local/queued/syncing/failed/accepted badges are text+icon. Assignment conflict preserves draft for supervisor reconciliation without applying it.

## Wireframe — Supervisor task board

```text
[Filters: priority / assignee / overdue / mode]
[Created | Assigned | In progress | Review]
[Each task: reason, due, owner, evidence status]
[Select task drawer / assign / schedule]
[Review receipt / request changes / complete]
```

Keyboard-accessible list alternative to drag/drop; assignment dialog validates active technician. Completion does not mark verification passed.

## Wireframe — Simulation laboratory

```text
[SIMULATED DATA banner]
[Scenario version + validity notes]
[Allowed parameter form / noise seed]
[Queue run / cancel request]
[Status/progress/partial-output flags]
[Outputs / comparison / gated evaluation]
```

No hidden leak source position in ordinary form/output. Evaluation gate is explicit, run must be sealed; regular engineer cannot access truth through guessed URL.

## Wireframe — Incident evidence timeline

```text
[Incident status / severity / mode / version]
[Competing explanations + source quality]
[Chronological observation / review / task / repair]
[Comparable BEFORE vs AFTER evidence]
[Verification outcome + limitations]
[Close / reopen / not verifiable with reason]
```

Historical evidence remains immutable; reopens append. Public complaint updates are authored separately from private timeline text.

## Review corrections for PAGE-09 and PAGE-12–19

PAGE-09 is the private HYDROOVERITY project contact form, not a utility complaint. Show30-day text/email retention, no utility selector, no public tracking number, safe generic202 and throttled/uncertain-send states; no automatic retry loop. A lost response may duplicate intake. PAGE-12–17 use preauth CSRF and no auth Idempotency-Key; do not automatically replay login/reset/invitation requests. Reset/verify/invite token replay422 prompts the documented account-state/recovery path. Invitation acceptance requires login as the verified invited email, even with no active tenant membership. PAGE-18–19 global final-state writes need self ownership/CSRF, no tenant business receipt. Login/session responses are never browser/service-worker cached; logout clears local vault even if a retry is needed.
