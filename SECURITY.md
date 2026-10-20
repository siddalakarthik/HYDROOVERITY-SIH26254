# Security policy

This private foundation has no deployed application and no production credentials. It does not make a production-security or potable-water compliance claim.

## Reporting

Report a suspected vulnerability privately to repository owner `siddalakarthik` through an existing trusted team channel. Do not put credentials, personal information or exploitable infrastructure details in issue bodies, PRs or screenshots. No dedicated security mailbox or response-time commitment has been established. A private advisory channel can be configured after owner review; its availability is not assumed.

## Required future controls

Backend-enforced role/tenant authorization, safe session and password-recovery design, secure uploads, rate limits, input validation, audit trails, retention policy and safe exports are M02/M03 design requirements. Citizens see their own reports and coarse public status, not utility topology or private data. Device ingestion needs scoped identity, freshness/replay handling and explicit provenance. Simulator truth must not reach inference or ordinary accounts.

Use local `.env` files only for approved development secrets; never add them to Git or examples. Do not log secrets. The repository validator detects some common credential patterns but cannot certify absence of all secrets. Review staged diffs manually. If exposure occurs, revoke/rotate first, assess scope and coordinate safe history/log cleanup with the owner; deleting the current file is insufficient.

GitHub Actions uses read-only contents access, SHA-pinned checkout and no stored checkout credentials. No deployments, infrastructure control or cloud secrets are configured by M01. Review workflow changes carefully. Do not weaken TLS, auth or branch safeguards to resolve access failures.

No live municipal actuation, violent valve closure, unauthorized potable-line insertion or hydraulic shock tests are in scope. The printed collar carries no pipeline pressure load. External service water challenges never inject into the drinking-water line.
