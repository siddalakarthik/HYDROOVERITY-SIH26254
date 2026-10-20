# Initial threat model

Status: M01 design notes only; controls below are requirements, not implemented security claims.

| Asset / trust boundary | Failure or abuse | Planned control / verification gate |
| --- | --- | --- |
| Citizen/public -> utility APIs | Other residents' data or sensitive topology exposed | Backend tenant/ownership/role checks; coarse public locations; deny tests in M03/M09 |
| User session -> privileged operations | Impersonation, CSRF, account recovery abuse | M02 session/recovery/CSRF design, hashing/rate limits; audit privileged actions |
| Device/simulator -> observation ingest | Spoofed/replayed/stale data or fake field provenance | Scoped device identity, validation, timestamps/idempotency/quality; explicit source environment |
| Scenario truth -> detector/ordinary API | Ground-truth leakage creates misleading accuracy | Separate restricted truth storage/contracts and explicit exclusion tests |
| Worker offline queue -> authoritative records | Duplicate/reordered writes, lost updates or stolen local notes | M02 idempotency/conflict/re-auth/local-retention design; offline retry tests |
| Upload/export -> other users | Executable content, oversized payloads or contact leakage | Content/type/size checks, private storage/access controls, consent and safe export policy |
| Source/CI -> credentials and supply chain | Secrets in commits/logs; untrusted workflow execution | Ignore rules, review/limited scan, pinned action/read-only CI/no secret use; no privileged PR triggers |
| Digital design -> real infrastructure | Unsafe actuation or pressure/potable boundary violated | No control implementation in M01; explicit authorization and engineering safety review before physical work |

No new production identities, cloud resources, secrets, public pages or device endpoints are configured. GitHub repository stays private and collaborators are not invited. This is not a penetration test. Follow [SECURITY.md](../../SECURITY.md) for reporting and exposure response.
