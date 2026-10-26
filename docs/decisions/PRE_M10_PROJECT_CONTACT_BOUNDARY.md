# Pre-M10 project-contact boundary

Owner authorization: master pre-M10 C01/C02 implementation. The existing M02
ContactWrite contract and fixed HYDROOVERITY ownership remain authoritative.
Project enquiries never create a utility membership, complaint, service request,
incident or external message.

The first implementation is a gated private-development foundation. Normal
process/environment configuration cannot enable intake. Tests may construct an
explicit SYNTHETIC_TEST_POLICY_ONLY configuration identifying the operator,
synthetic policy and capacity. Thirty days comes from the existing M02 pilot
contract; it is not an approved legal retention policy. D10 approval, a reviewed
operator procedure and actual deletion/hold operations remain live-release gates.

The runtime principal can insert only category/message/reply-email. It cannot
read inbox IDs, text or email, change ownership, review, hold or delete messages.
A constant capacity marker is the only selectable column; a global transaction
lock serializes count-and-insert. This permits bounded intake without a privileged
SECURITY DEFINER function or public inbox. Dedicated owner-only review audit is
append-only. Operator tools must use the existing separately held database owner
configuration, never a tenant ADMIN session or runtime credential.

Require current preauth/auth session, CSRF, Origin, 8 KiB body cap, bounded plain
text, fixed categories and no routing fields. Reject Idempotency-Key; generic 202
contains no record ID or retrieval secret. Apply existing expiring, daily-HMAC
rate buckets: three/minute per session and IP; five/day per normalized optional
reply email. No raw IP, session secret, automatic reply or fetched URL is stored.

Review output escapes text. Synthetic expiry/hold tests may exercise deletion;
normal intake and real purge activation stay disabled. Historical acceptance
statuses will change only after actual implementation and executed evidence.
