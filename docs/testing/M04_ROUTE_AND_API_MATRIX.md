# M04 routes and implemented API integration

All routes and permission boundaries derive from approved M02. Availability describes current frontend delivery; executed workflows and limitations are recorded separately in [the ledger](M04_EXECUTION_LEDGER.md). The browser imports only the reachable 58-operation M03 contract. The 59 deferred canonical operations are not active integrations.

## Canonical route availability

| Route | Availability | Roles | Frontend module |
| --- | --- | --- | --- |
| `/` | INFORMATIONAL | PUBLIC | `public` |
| `/solution` | INFORMATIONAL | PUBLIC | `public` |
| `/how-it-works` | INFORMATIONAL | PUBLIC | `public` |
| `/solution/guard5` | INFORMATIONAL | PUBLIC | `public` |
| `/solution/acoustics` | INFORMATIONAL | PUBLIC | `public` |
| `/benefits-and-limitations` | INFORMATIONAL | PUBLIC | `public` |
| `/project-status` | ACTIVE_READ_ONLY | PUBLIC | `public` |
| `/report` | ACTIVE_FUNCTIONAL | PUBLIC | `public` |
| `/contact` | INFORMATIONAL | PUBLIC | `public` |
| `/privacy` | INFORMATIONAL | PUBLIC | `public` |
| `/terms` | INFORMATIONAL | PUBLIC | `public` |
| `/login` | ACTIVE_FUNCTIONAL | PUBLIC | `auth` |
| `/register` | ACTIVE_FUNCTIONAL | PUBLIC | `auth` |
| `/forgot-password` | ACTIVE_FUNCTIONAL | PUBLIC | `auth` |
| `/reset-password` | ACTIVE_FUNCTIONAL | PUBLIC | `auth` |
| `/verify-account` | ACTIVE_FUNCTIONAL | PUBLIC | `auth` |
| `/accept-invitation` | ACTIVE_FUNCTIONAL | PUBLIC | `auth` |
| `/account` | ACTIVE_FUNCTIONAL | ALL | `auth` |
| `/account/sessions` | ACTIVE_FUNCTIONAL | ALL | `auth` |
| `/citizen/{org}/reports` | ACTIVE_FUNCTIONAL | CITIZEN | `complaints` |
| `/citizen/{org}/reports/new` | ACTIVE_FUNCTIONAL | CITIZEN | `complaints` |
| `/citizen/{org}/reports/{id}` | ACTIVE_FUNCTIONAL | CITIZEN | `complaints` |
| `/app/{org}/overview` | ACTIVE_READ_ONLY | ENGINEER,SUPERVISOR | `incidents` |
| `/app/{org}/network` | ACTIVE_FUNCTIONAL | ENGINEER,SUPERVISOR | `network` |
| `/app/{org}/monitoring` | DEFERRED | ENGINEER,SUPERVISOR | `unavailable` |
| `/app/{org}/devices` | DEFERRED | ENGINEER,SUPERVISOR,ADMIN | `unavailable` |
| `/app/{org}/devices/{id}` | DEFERRED | ENGINEER,SUPERVISOR,ADMIN | `unavailable` |
| `/app/{org}/collars/{id}` | DEFERRED | ENGINEER,SUPERVISOR | `unavailable` |
| `/app/{org}/acoustics` | DEFERRED | ENGINEER | `unavailable` |
| `/app/{org}/acoustics/{id}` | DEFERRED | ENGINEER | `unavailable` |
| `/app/{org}/incidents` | ACTIVE_FUNCTIONAL | ENGINEER,SUPERVISOR | `incidents` |
| `/app/{org}/incidents/{id}` | ACTIVE_FUNCTIONAL | ENGINEER,SUPERVISOR | `incidents` |
| `/app/{org}/work-orders` | ACTIVE_FUNCTIONAL | ENGINEER,SUPERVISOR,TECHNICIAN | `work` |
| `/app/{org}/work-orders/{id}` | ACTIVE_FUNCTIONAL | ENGINEER,SUPERVISOR,TECHNICIAN | `work` |
| `/app/{org}/repairs/{id}/verification` | ACTIVE_FUNCTIONAL | ENGINEER,SUPERVISOR,TECHNICIAN | `work` |
| `/app/{org}/complaints` | ACTIVE_FUNCTIONAL | SUPERVISOR | `complaints` |
| `/app/{org}/maintenance` | DEFERRED | SUPERVISOR | `unavailable` |
| `/app/{org}/analytics` | DEFERRED | ENGINEER,SUPERVISOR | `unavailable` |
| `/app/{org}/reports` | DEFERRED | ENGINEER,SUPERVISOR | `unavailable` |
| `/app/{org}/simulations` | DEFERRED | ENGINEER | `unavailable` |
| `/app/{org}/simulations/{id}` | DEFERRED | ENGINEER | `unavailable` |
| `/app/{org}/feedback` | DEFERRED | ALL | `unavailable` |
| `/app/{org}/notifications` | DEFERRED | ALL | `unavailable` |
| `/app/{org}/admin/users` | ACTIVE_FUNCTIONAL | ADMIN | `administration` |
| `/app/{org}/admin/settings` | ACTIVE_READ_ONLY | ADMIN | `administration` |
| `/app/{org}/admin/audit` | ACTIVE_READ_ONLY | ADMIN | `administration` |

## Implemented backend operations

Forms and resource views use generated request/response schemas and fixed same-origin paths. This inventory is integration scope, not a claim that every operation has separate browser coverage. M03 real-database regressions retain all 58 positive projections.

| Operation | Method | Path |
| --- | --- | --- |
| `authentication_get_auth_csrf` | GET | `/auth/csrf` |
| `authentication_post_auth_register` | POST | `/auth/register` |
| `authentication_post_auth_login` | POST | `/auth/login` |
| `authentication_post_auth_recovery` | POST | `/auth/recovery` |
| `authentication_post_auth_reset` | POST | `/auth/reset` |
| `authentication_post_auth_verify` | POST | `/auth/verify` |
| `authentication_post_auth_invitation_accept` | POST | `/auth/invitation-accept` |
| `authentication_post_auth_logout` | POST | `/auth/logout` |
| `current_user_get_me` | GET | `/me` |
| `current_user_patch_me` | PATCH | `/me` |
| `current_user_get_me_memberships` | GET | `/me/memberships` |
| `current_user_get_me_sessions` | GET | `/me/sessions` |
| `current_user_delete_me_sessions_session_id` | DELETE | `/me/sessions/{session_id}` |
| `public_get_public_utilities_slug` | GET | `/public/utilities/{slug}` |
| `public_get_public_project_status` | GET | `/public/project-status` |
| `organization_get_orgs_organization_id` | GET | `/orgs/{organization_id}` |
| `water_zones_get_orgs_organization_id_zones` | GET | `/orgs/{organization_id}/zones` |
| `water_zones_post_orgs_organization_id_zones` | POST | `/orgs/{organization_id}/zones` |
| `water_zones_get_orgs_organization_id_zones_resource_id` | GET | `/orgs/{organization_id}/zones/{resource_id}` |
| `water_zones_patch_orgs_organization_id_zones_resource_id` | PATCH | `/orgs/{organization_id}/zones/{resource_id}` |
| `pipeline_assets_get_orgs_organization_id_junctions` | GET | `/orgs/{organization_id}/junctions` |
| `pipeline_assets_post_orgs_organization_id_junctions` | POST | `/orgs/{organization_id}/junctions` |
| `pipeline_assets_get_orgs_organization_id_junctions_resource_id` | GET | `/orgs/{organization_id}/junctions/{resource_id}` |
| `pipeline_assets_patch_orgs_organization_id_junctions_resource_id` | PATCH | `/orgs/{organization_id}/junctions/{resource_id}` |
| `pipeline_assets_get_orgs_organization_id_pipes` | GET | `/orgs/{organization_id}/pipes` |
| `pipeline_assets_post_orgs_organization_id_pipes` | POST | `/orgs/{organization_id}/pipes` |
| `pipeline_assets_get_orgs_organization_id_pipes_resource_id` | GET | `/orgs/{organization_id}/pipes/{resource_id}` |
| `pipeline_assets_patch_orgs_organization_id_pipes_resource_id` | PATCH | `/orgs/{organization_id}/pipes/{resource_id}` |
| `evidence_get_orgs_organization_id_evidence_assessments` | GET | `/orgs/{organization_id}/evidence-assessments` |
| `evidence_post_orgs_organization_id_evidence_assessments` | POST | `/orgs/{organization_id}/evidence-assessments` |
| `evidence_get_orgs_organization_id_evidence_assessments_assessment_id` | GET | `/orgs/{organization_id}/evidence-assessments/{assessment_id}` |
| `incidents_get_orgs_organization_id_incidents` | GET | `/orgs/{organization_id}/incidents` |
| `incidents_post_orgs_organization_id_incidents` | POST | `/orgs/{organization_id}/incidents` |
| `incidents_get_orgs_organization_id_incidents_incident_id` | GET | `/orgs/{organization_id}/incidents/{incident_id}` |
| `incidents_get_orgs_organization_id_incidents_incident_id_timeline` | GET | `/orgs/{organization_id}/incidents/{incident_id}/timeline` |
| `incidents_post_orgs_organization_id_incidents_incident_id_transitions` | POST | `/orgs/{organization_id}/incidents/{incident_id}/transitions` |
| `incidents_post_orgs_organization_id_incidents_incident_id_links` | POST | `/orgs/{organization_id}/incidents/{incident_id}/links` |
| `work_orders_get_orgs_organization_id_work_orders` | GET | `/orgs/{organization_id}/work-orders` |
| `work_orders_post_orgs_organization_id_work_orders` | POST | `/orgs/{organization_id}/work-orders` |
| `work_orders_get_orgs_organization_id_work_orders_work_order_id` | GET | `/orgs/{organization_id}/work-orders/{work_order_id}` |
| `work_orders_get_orgs_organization_id_work_orders_work_order_id_brief` | GET | `/orgs/{organization_id}/work-orders/{work_order_id}/brief` |
| `work_orders_post_orgs_organization_id_work_orders_work_order_id_assignment` | POST | `/orgs/{organization_id}/work-orders/{work_order_id}/assignment` |
| `work_orders_post_orgs_organization_id_work_orders_work_order_id_actions` | POST | `/orgs/{organization_id}/work-orders/{work_order_id}/actions` |
| `work_orders_post_orgs_organization_id_work_orders_work_order_id_transitions` | POST | `/orgs/{organization_id}/work-orders/{work_order_id}/transitions` |
| `repairs_post_orgs_organization_id_work_orders_work_order_id_repairs` | POST | `/orgs/{organization_id}/work-orders/{work_order_id}/repairs` |
| `repairs_get_orgs_organization_id_work_orders_work_order_id_repairs` | GET | `/orgs/{organization_id}/work-orders/{work_order_id}/repairs` |
| `verification_post_orgs_organization_id_repairs_repair_id_verifications` | POST | `/orgs/{organization_id}/repairs/{repair_id}/verifications` |
| `verification_get_orgs_organization_id_repairs_repair_id_verifications` | GET | `/orgs/{organization_id}/repairs/{repair_id}/verifications` |
| `complaints_post_orgs_organization_id_complaints` | POST | `/orgs/{organization_id}/complaints` |
| `complaints_get_orgs_organization_id_complaints` | GET | `/orgs/{organization_id}/complaints` |
| `complaints_get_orgs_organization_id_complaints_complaint_id` | GET | `/orgs/{organization_id}/complaints/{complaint_id}` |
| `complaints_post_orgs_organization_id_complaints_complaint_id_follow_ups` | POST | `/orgs/{organization_id}/complaints/{complaint_id}/follow-ups` |
| `complaints_post_orgs_organization_id_complaints_complaint_id_review` | POST | `/orgs/{organization_id}/complaints/{complaint_id}/review` |
| `administration_get_orgs_organization_id_memberships` | GET | `/orgs/{organization_id}/memberships` |
| `administration_post_orgs_organization_id_invitations` | POST | `/orgs/{organization_id}/invitations` |
| `administration_put_orgs_organization_id_memberships_membership_id_roles` | PUT | `/orgs/{organization_id}/memberships/{membership_id}/roles` |
| `administration_post_orgs_organization_id_memberships_membership_id_status` | POST | `/orgs/{organization_id}/memberships/{membership_id}/status` |
| `administration_get_orgs_organization_id_audit_logs` | GET | `/orgs/{organization_id}/audit-logs` |

## Integration rules and contract gaps

- FastAPI owns sessions, current membership and every tenant/role/ownership decision. Private UI requests begin only after current access resolves; state is cleared on logout, scope switch, expired sessions or changed membership. Workspace checks repeat on focus and every 30 seconds. Browser back/forward cache restoration reloads protected views.
- Secure HttpOnly SameSite cookies are sent only to the same origin. CSRF and deliberate mutation identities exist in memory. Auth/global writes reject business idempotency; tenant changes retain one key only for identical body/version retries. There is no automatic mutation replay.
- Versioned changes send If-Match. Stale/missing versions produce visible refetch guidance. The API rejects oversized request bodies before transmission; safe errors show server request IDs and Retry-After.
- Cursor pages retain backend as_of/next_cursor. Counts and material/quality filters explicitly describe current pages; they are not global telemetry metrics.
- Supervisors have no membership-directory API. Technician assignment accepts an administrator-supplied current membership ID, validated by the backend. No invented staff search endpoint was added.
- Raw-evidence discovery and acquisition are deferred. Manual assessment accepts only already-authorized evidence IDs; acoustic candidate creation remains unavailable. No evaluation truth, seeds or scientific detector inputs enter ordinary public artifacts.
- Zone reads omit demand-accounting settings. Editing requires a complete explicitly reviewed accounting definition, never inferred booleans or an invented current configuration.
- Independent manual verification supports NOT_VERIFIABLE only. PASSED/FAILED and comparable measured windows cannot be fabricated by the frontend.
- Attachments, external email delivery, telemetry, simulation integration, notifications and offline writes are deferred. Contact is informational and organization settings are read only.
- Local browser tests use actual authorized PostGIS geometry labeled SYNTHETIC. No real field infrastructure inventory was supplied or fabricated; ordinary authorized asset entry is implemented.
