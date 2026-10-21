"""Tighten persisted verifier/receipt invariants without rewriting history."""

from alembic import op

revision = "m03_002"
down_revision = "m03_001"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE roles ADD CONSTRAINT fixed_roles CHECK(code IN ('ADMIN','ENGINEER','SUPERVISOR','TECHNICIAN','CITIZEN','EVALUATOR'))"
    )
    op.execute(
        "ALTER TABLE sessions ADD CONSTRAINT session_verifiers CHECK(octet_length(token_hash)=32 AND octet_length(csrf_hash)=32)"
    )
    op.execute(
        "ALTER TABLE account_recovery_tokens ADD CONSTRAINT recovery_verifier CHECK(octet_length(token_hash)=32)"
    )
    op.execute(
        "ALTER TABLE invitations ADD CONSTRAINT invitation_verifier CHECK(octet_length(token_hash)=32)"
    )
    op.execute(
        "ALTER TABLE idempotency_records ADD CONSTRAINT committed_receipt CHECK(request_hash ~ '^[a-f0-9]{64}$' AND result_resource_id IS NOT NULL AND result_status IS NOT NULL AND result_status BETWEEN 200 AND 299 AND expires_at>created_at)"
    )
    op.execute(
        "ALTER TABLE work_order_actions ADD CONSTRAINT positive_action_base CHECK(base_version>0)"
    )
    op.execute(
        "ALTER TABLE evidence_records ADD CONSTRAINT manual_note_nonempty CHECK(manual_note IS NULL OR length(manual_note)>0)"
    )


def downgrade():
    # This revision only removes additional checks; data and history survive.
    for table, name in [
        ("evidence_records", "manual_note_nonempty"),
        ("work_order_actions", "positive_action_base"),
        ("idempotency_records", "committed_receipt"),
        ("invitations", "invitation_verifier"),
        ("account_recovery_tokens", "recovery_verifier"),
        ("sessions", "session_verifiers"),
        ("roles", "fixed_roles"),
    ]:
        op.drop_constraint(name, table, type_="check")
