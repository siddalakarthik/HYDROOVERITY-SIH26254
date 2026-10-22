# Role permission matrix

M07 review note: [candidate operation metadata](../../data/schemas/m07-api-inventory.json) carries the proposed action-by-action roles, guards and required permissions; [candidate architecture](m07/README.md) describes separate citizen/staff/technician DTOs. These grants are not seeded into the existing runtime. The following permission families are proposed, not blanket access:

| Permission family | Candidate role boundary |
| --- | --- |
| service_requests.read/write | Citizen owns submitted case and permitted requests; supervisor tenant triage/publication/closure. No general ADMIN/ENGINEER/TECHNICIAN case read. |
| dispatch.read/write | Per-operation citizen owned appointment decisions; supervisor operations; ADMIN governance only; technician current assigned visit or self calendar. A shared family never bypasses endpoint role/parent/action checks. |
| notification_preferences.read/write | Active membership's own recipient preferences; no arbitrary destination and in-app only. |
| investigation_findings.read/write | Supervisor/engineer technical read; current assigned technician read/write; investigation-purpose work only. |
| Existing uploads/feedback/notifications | Retain current-parent/owner/current-recipient checks in the deferred candidate; no implementation or ADMIN wildcard. |

Mixed-role users cannot approve their own repair. Internal timeline audience and administrative attendance corrections remain supervisor-only; technician calendars expose no other tenant or private resident contact. Governance enrollment/policy edits require fresh reauthentication and reason. All other existing role restrictions below remain authoritative for current operations.

Issue #2. Deny by default. Global user identity -> active organization_membership -> scoped role_assignments -> explicit permission. No universal super-admin. Multiple memberships/roles are allowed; switching UI organization revalidates membership and clears cached data. PUBLIC means anonymous/preauth only; ALL means authenticated active membership. EVALUATOR is an explicitly owner-reviewed extra grant for engineers, never inherited by ADMIN or accepted through ordinary role edit. DEVICE and SIMULATOR are separate machine identities, not human roles.

For every request: authenticate; bind path organization; load active membership/grants; load resource under organization predicate; apply own/assigned/parent checks; validate transition/version; persist/audit/outbox in one transaction. Role revocation invalidates access immediately, including open streams and downloads. A worker's task ID, stale cached assignment or device lease is not authorization. Citizen queries always include reporter membership and return citizen-safe DTOs; existence failures are uniform404. Privileged changes require recent reauthentication (within10 minutes), reason and safe audit, including last-admin protection.

Endpoint operations are the canonical fine-grained matrix below. The permission codes are explicit allow-lists; same permission code never bypasses per-operation role/scope restrictions. No automatic staff invitations or evaluator grants are performed by this milestone.

| Operation | Roles | Required permission | Additional checks |
| --- | --- | --- | --- |
| `GET /auth/csrf` | PUBLIC | `authentication.read` | preauth/session |
| `POST /auth/register` | PUBLIC | `authentication.write` | preauth/session |
| `POST /auth/login` | PUBLIC | `authentication.write` | preauth/session |
| `POST /auth/recovery` | PUBLIC | `authentication.write` | preauth/session |
| `POST /auth/reset` | PUBLIC | `authentication.write` | preauth/session |
| `POST /auth/verify` | PUBLIC | `authentication.write` | preauth/session |
| `POST /auth/invitation-accept` | ALL | `authentication.write` | verified global identity + invited email; server-bound tenant/role |
| `POST /auth/logout` | PUBLIC | `authentication.write` | presented session cleanup only, CSRF required; no membership prerequisite |
| `GET /me` | ALL | `current_user.read` | self |
| `PATCH /me` | ALL | `current_user.write` | self |
| `GET /me/memberships` | ALL | `current_user.read` | self |
| `GET /me/sessions` | ALL | `current_user.read` | self |
| `DELETE /me/sessions/{session_id}` | ALL | `current_user.write` | self |
| `GET /public/utilities/{slug}` | PUBLIC | `public.read` | public allowlist |
| `GET /public/project-status` | PUBLIC | `public.read` | public allowlist |
| `POST /public/contact` | PUBLIC | `public.write` | preauth/session + fixed private project inbox; no tenant selection |
| `GET /orgs/{organization_id}` | ALL | `organization.read` | active membership |
| `PATCH /orgs/{organization_id}` | ADMIN | `organization.write` | tenant + fresh reauth |
| `GET /orgs/{organization_id}/zones` | ENGINEER, SUPERVISOR | `water_zones.read` | tenant |
| `POST /orgs/{organization_id}/zones` | ENGINEER | `water_zones.write` | tenant |
| `GET /orgs/{organization_id}/zones/{resource_id}` | ENGINEER, SUPERVISOR | `water_zones.read` | tenant |
| `PATCH /orgs/{organization_id}/zones/{resource_id}` | ENGINEER | `water_zones.write` | tenant + If-Match |
| `GET /orgs/{organization_id}/junctions` | ENGINEER, SUPERVISOR | `pipeline_assets.read` | tenant |
| `POST /orgs/{organization_id}/junctions` | ENGINEER | `pipeline_assets.write` | tenant |
| `GET /orgs/{organization_id}/junctions/{resource_id}` | ENGINEER, SUPERVISOR | `pipeline_assets.read` | tenant |
| `PATCH /orgs/{organization_id}/junctions/{resource_id}` | ENGINEER | `pipeline_assets.write` | tenant + If-Match |
| `GET /orgs/{organization_id}/pipes` | ENGINEER, SUPERVISOR | `pipeline_assets.read` | tenant |
| `POST /orgs/{organization_id}/pipes` | ENGINEER | `pipeline_assets.write` | tenant |
| `GET /orgs/{organization_id}/pipes/{resource_id}` | ENGINEER, SUPERVISOR | `pipeline_assets.read` | tenant |
| `PATCH /orgs/{organization_id}/pipes/{resource_id}` | ENGINEER | `pipeline_assets.write` | tenant + If-Match |
| `GET /orgs/{organization_id}/access-points` | ENGINEER, SUPERVISOR | `pipeline_assets.read` | tenant |
| `POST /orgs/{organization_id}/access-points` | ENGINEER | `pipeline_assets.write` | tenant |
| `GET /orgs/{organization_id}/access-points/{resource_id}` | ENGINEER, SUPERVISOR | `pipeline_assets.read` | tenant |
| `PATCH /orgs/{organization_id}/access-points/{resource_id}` | ENGINEER | `pipeline_assets.write` | tenant + If-Match |
| `GET /orgs/{organization_id}/coverage` | ENGINEER, SUPERVISOR | `pipeline_assets.read` | tenant |
| `GET /orgs/{organization_id}/supply-windows` | ENGINEER, SUPERVISOR | `water_zones.read` | tenant |
| `GET /orgs/{organization_id}/devices` | ENGINEER, SUPERVISOR, ADMIN | `devices.read` | tenant |
| `POST /orgs/{organization_id}/devices` | ADMIN | `devices.write` | tenant + fresh reauth |
| `GET /orgs/{organization_id}/devices/{device_id}` | ENGINEER, SUPERVISOR, ADMIN | `devices.read` | tenant |
| `GET /orgs/{organization_id}/devices/{device_id}/channels` | ENGINEER, SUPERVISOR | `devices.read` | tenant |
| `GET /orgs/{organization_id}/devices/{device_id}/configurations` | ENGINEER | `devices.read` | tenant |
| `POST /orgs/{organization_id}/devices/{device_id}/configurations` | ENGINEER | `devices.write` | tenant |
| `POST /orgs/{organization_id}/devices/{device_id}/installations` | ENGINEER | `devices.write` | tenant |
| `POST /orgs/{organization_id}/devices/{device_id}/credentials` | ADMIN | `devices.write` | tenant + fresh reauth |
| `DELETE /orgs/{organization_id}/devices/{device_id}/credentials/{credential_id}` | ADMIN | `devices.write` | tenant + fresh reauth |
| `GET /orgs/{organization_id}/devices/{device_id}/health-events` | ENGINEER, SUPERVISOR | `diagnostics.read` | tenant |
| `GET /orgs/{organization_id}/devices/{device_id}/calibrations` | ENGINEER | `diagnostics.read` | tenant |
| `POST /orgs/{organization_id}/devices/{device_id}/calibrations` | ENGINEER | `diagnostics.write` | tenant |
| `GET /orgs/{organization_id}/collars/{device_id}/service-tests` | ENGINEER, SUPERVISOR | `diagnostics.read` | tenant |
| `POST /orgs/{organization_id}/collars/{device_id}/service-tests` | TECHNICIAN | `diagnostics.write` | assigned work order + matching device |
| `GET /orgs/{organization_id}/observations` | ENGINEER, SUPERVISOR | `observations.read` | tenant |
| `GET /orgs/{organization_id}/observations/{observation_id}` | ENGINEER, SUPERVISOR | `observations.read` | tenant |
| `POST /orgs/{organization_id}/manual-observations` | ENGINEER | `observations.write` | tenant |
| `POST /ingest/hardware/observations` | DEVICE | `ingestion.write` | credential-bound organization/device/environment |
| `POST /ingest/simulation/observations` | SIMULATOR | `ingestion.write` | credential-bound tenant + active run lease |
| `GET /orgs/{organization_id}/evidence-assessments` | ENGINEER, SUPERVISOR | `evidence.read` | tenant |
| `GET /orgs/{organization_id}/evidence-assessments/{assessment_id}` | ENGINEER, SUPERVISOR | `evidence.read` | tenant |
| `POST /orgs/{organization_id}/evidence-assessments` | ENGINEER | `evidence.write` | tenant |
| `GET /orgs/{organization_id}/acoustic-captures` | ENGINEER | `acoustics.read` | tenant |
| `POST /orgs/{organization_id}/acoustic-captures` | ENGINEER | `acoustics.write` | tenant + provenance-bound artifact |
| `GET /orgs/{organization_id}/acoustic-captures/{capture_id}` | ENGINEER | `acoustics.read` | tenant |
| `POST /orgs/{organization_id}/acoustic-captures/{capture_id}/estimates` | ENGINEER | `acoustics.write` | tenant |
| `GET /orgs/{organization_id}/acoustic-captures/{capture_id}/estimates` | ENGINEER | `acoustics.read` | tenant |
| `GET /orgs/{organization_id}/artifacts/{artifact_id}/download` | ENGINEER | `acoustics.read` | tenant + nontruth artifact ACL |
| `GET /orgs/{organization_id}/incidents` | ENGINEER, SUPERVISOR | `incidents.read` | tenant |
| `POST /orgs/{organization_id}/incidents` | ENGINEER, SUPERVISOR | `incidents.write` | tenant |
| `GET /orgs/{organization_id}/incidents/{incident_id}` | ENGINEER, SUPERVISOR | `incidents.read` | tenant |
| `GET /orgs/{organization_id}/incidents/{incident_id}/timeline` | ENGINEER, SUPERVISOR | `incidents.read` | tenant |
| `POST /orgs/{organization_id}/incidents/{incident_id}/transitions` | SUPERVISOR | `incidents.write` | tenant + If-Match |
| `POST /orgs/{organization_id}/incidents/{incident_id}/links` | SUPERVISOR | `incidents.write` | tenant + If-Match |
| `GET /orgs/{organization_id}/work-orders` | SUPERVISOR, ENGINEER, TECHNICIAN | `work_orders.read` | tenant; TECHNICIAN assigned only |
| `POST /orgs/{organization_id}/work-orders` | SUPERVISOR | `work_orders.write` | tenant |
| `GET /orgs/{organization_id}/work-orders/{work_order_id}` | SUPERVISOR, ENGINEER, TECHNICIAN | `work_orders.read` | tenant; TECHNICIAN assigned only |
| `GET /orgs/{organization_id}/work-orders/{work_order_id}/brief` | TECHNICIAN | `work_orders.read` | current assigned membership |
| `POST /orgs/{organization_id}/work-orders/{work_order_id}/assignment` | SUPERVISOR | `work_orders.write` | tenant + If-Match |
| `POST /orgs/{organization_id}/work-orders/{work_order_id}/actions` | TECHNICIAN | `work_orders.write` | assigned + version/assignment checks |
| `POST /orgs/{organization_id}/work-orders/{work_order_id}/transitions` | SUPERVISOR, TECHNICIAN | `work_orders.write` | tenant; worker assigned + permitted edge |
| `POST /orgs/{organization_id}/work-orders/{work_order_id}/repairs` | TECHNICIAN | `repairs.write` | assigned + If-Match |
| `GET /orgs/{organization_id}/work-orders/{work_order_id}/repairs` | SUPERVISOR, ENGINEER, TECHNICIAN | `repairs.read` | tenant; worker assigned only |
| `POST /orgs/{organization_id}/repairs/{repair_id}/verifications` | SUPERVISOR | `verification.write` | tenant + If-Match + comparable evidence |
| `GET /orgs/{organization_id}/repairs/{repair_id}/verifications` | ENGINEER, SUPERVISOR, TECHNICIAN | `verification.read` | tenant; worker assigned parent only |
| `POST /orgs/{organization_id}/complaints` | CITIZEN | `complaints.write` | self in enabled reporting tenant |
| `GET /orgs/{organization_id}/complaints` | CITIZEN, SUPERVISOR | `complaints.read` | tenant; citizen owned only |
| `GET /orgs/{organization_id}/complaints/{complaint_id}` | CITIZEN, SUPERVISOR | `complaints.read` | tenant; citizen owned only |
| `POST /orgs/{organization_id}/complaints/{complaint_id}/follow-ups` | CITIZEN | `complaints.write` | owned complaint + If-Match |
| `POST /orgs/{organization_id}/complaints/{complaint_id}/review` | SUPERVISOR | `complaints.write` | tenant + If-Match |
| `POST /orgs/{organization_id}/feedback` | ALL | `feedback.write` | tenant; citizen owns complaint if linked |
| `GET /orgs/{organization_id}/feedback` | ALL | `feedback.read` | tenant; citizen own only; internal staff per role |
| `POST /orgs/{organization_id}/feedback/{feedback_id}/review` | SUPERVISOR, ADMIN | `feedback.write` | tenant + If-Match |
| `POST /orgs/{organization_id}/attachments` | ALL | `uploads.write` | owned complaint/draft or authorized assigned task |
| `PUT /orgs/{organization_id}/attachments/{attachment_id}/content` | ALL | `uploads.write` | ticket owner + target authorization |
| `POST /orgs/{organization_id}/attachments/{attachment_id}/complete` | ALL | `uploads.write` | ticket owner + target authorization |
| `GET /orgs/{organization_id}/attachments/{attachment_id}` | ALL | `uploads.read` | parent resource ACL + own citizen restriction |
| `GET /orgs/{organization_id}/attachments/{attachment_id}/download` | ALL | `uploads.read` | CLEAN + parent ACL rechecked |
| `DELETE /orgs/{organization_id}/attachments/{attachment_id}` | ALL | `uploads.write` | owner + evidence-pin/retention check |
| `GET /orgs/{organization_id}/simulations/scenarios` | ENGINEER | `simulations.read` | tenant |
| `POST /orgs/{organization_id}/simulations/runs` | ENGINEER | `simulations.write` | tenant + allowed scenario |
| `GET /orgs/{organization_id}/simulations/runs` | ENGINEER | `simulations.read` | tenant |
| `GET /orgs/{organization_id}/simulations/runs/{run_id}` | ENGINEER | `simulations.read` | tenant |
| `POST /orgs/{organization_id}/simulations/runs/{run_id}/cancel` | ENGINEER | `simulations.write` | tenant; creator or simulation control grant |
| `GET /orgs/{organization_id}/simulations/runs/{run_id}/outputs` | ENGINEER | `simulations.read` | tenant |
| `GET /orgs/{organization_id}/simulations/runs/{run_id}/evaluation` | ENGINEER+EVALUATOR | `simulations.read` | tenant + sealed completed run + audited evaluation grant |
| `GET /orgs/{organization_id}/algorithm-configurations` | ENGINEER | `simulations.read` | tenant |
| `GET /orgs/{organization_id}/notifications` | ALL | `notifications.read` | self membership only |
| `POST /orgs/{organization_id}/notifications/{notification_id}/read` | ALL | `notifications.write` | self membership only |
| `POST /orgs/{organization_id}/reports` | ENGINEER, SUPERVISOR | `reports.write` | tenant + projection-specific permission |
| `GET /orgs/{organization_id}/reports/{report_id}` | ENGINEER, SUPERVISOR | `reports.read` | creator + current grants |
| `GET /orgs/{organization_id}/reports/{report_id}/download` | ENGINEER, SUPERVISOR | `reports.read` | creator + current grants + not expired |
| `GET /orgs/{organization_id}/memberships` | ADMIN | `administration.read` | tenant + fresh session |
| `POST /orgs/{organization_id}/invitations` | ADMIN | `administration.write` | tenant + fresh reauth |
| `PUT /orgs/{organization_id}/memberships/{membership_id}/roles` | ADMIN | `administration.write` | tenant + fresh reauth + last-admin guard |
| `POST /orgs/{organization_id}/memberships/{membership_id}/status` | ADMIN | `administration.write` | tenant + fresh reauth + last-admin guard |
| `GET /orgs/{organization_id}/audit-logs` | ADMIN | `administration.read` | tenant + security permission |
| `GET /orgs/{organization_id}/integrations` | ADMIN | `administration.read` | tenant |
| `PUT /orgs/{organization_id}/integrations` | ADMIN | `administration.write` | tenant + fresh reauth |
| `GET /orgs/{organization_id}/events` | ALL | `realtime.read` | tenant + per-event current permission |
| `GET /orgs/{organization_id}/events/history` | ALL | `realtime.read` | tenant + per-event current permission |

## Review guard metadata

OpenAPI x-authorization-guards and inventory authorization_guards explicitly carry TENANT, CITIZEN_OWNED, TECHNICIAN_ASSIGNED, nontruth artifact classification/parent ACL and sealed ENGINEER_AND_EVALUATOR checks. They are service requirements, not implemented middleware or proof of enforcement. Citizen-safe DTOs remain separate from internal incident/device/topology views. Every lookup, filtered list, nested reference, export, SSE reconnect and retry repeats current authorization. Do not infer an ADMIN wildcard from a UI portal. Ordinary artifact manifests/listings must exclude restricted truth IDs as well as their contents; evaluation requires its separate sealed-run route and restricted principal.
