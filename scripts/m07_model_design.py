"""M07 design data for composition/validation only. No migrations or services."""
import copy


def database(base):
    db = copy.deepcopy(base)
    tables = {t["name"]: t for t in db["tables"]}
    new = []

    def add(name, columns, *, history=False, privacy="INTERNAL", global_scope=False, unique=(), invariants=(), constraints=()):
        common = [("id", "uuid", False)]
        if not global_scope:
            common.append(("organization_id", "uuid", False))
        common.append(("created_at", "timestamptz", False))
        if not history:
            common += [("updated_at", "timestamptz", False), ("version", "bigint", False)]
        parsed, fks = [], []
        for col, typ, null, *target in common + columns:
            parsed.append({"name": col, "type": typ, "nullable": null})
            if col == "organization_id":
                target = ["organizations"]
            if target:
                scope = "global" if global_scope else "tenant"
                target_scope = tables[target[0]]["scope"] if target[0] in tables else ("global" if target[0] == "dispatch_calendar_subjects" else "tenant")
                fks.append({"column": col, "target": target[0], "same_tenant": scope == target_scope == "tenant" and col != "organization_id"})
        value = {"name": name, "purpose": "M07 proposed " + name.replace("_", " "), "scope": "global" if global_scope else "tenant", "columns": parsed, "foreign_keys": fks, "unique": list(unique), "indexes": ["organization_id,id"] if not global_scope else ["user_id"], "privacy": privacy, "retention": "M07_POLICY_REVIEW_REQUIRED", "lifecycle": "append_only" if history else "mutable", "evidence": "Operational/manual record, never scientific verification or field-performance evidence", "invariants": list(invariants), "constraints": list(constraints), "status": "PROPOSED_NOT_MIGRATED"}
        tables[name] = value
        new.append(value)

    member = "organization_memberships"
    add("service_requests", [("owner_membership_id","uuid",False,member),("tracking_reference","text",False),("origin_complaint_id","uuid",True,"citizen_complaints"),("follow_up_of_id","uuid",True,"service_requests"),("category","M07ServiceCategory",False),("description","text",False),("coarse_area","text",False),("status","M07ServiceStatus",False),("cancellation_pending","boolean",False),("service_outcome","text",True),("accepted_at","timestamptz",True),("accepted_by_id","uuid",True,member)], privacy="PERSONAL", unique=["organization_id,tracking_reference", "organization_id,origin_complaint_id WHERE origin_complaint_id IS NOT NULL"], invariants=["OWNER_DERIVED_FROM_SESSION", "TRACKING_REFERENCE_128_BIT_NOT_BEARER", "NO_AUTOMATIC_INCIDENT", "MAX_20_ACTIVE_WORK_LINKS", "TERMINAL_RECURRENCE_NEW_LINKED_CASE"])
    add("service_request_events", [("request_id","uuid",False,"service_requests"),("sequence","bigint",False),("event_kind","text",False),("actor_id","uuid",True,member),("received_at","timestamptz",False),("observed_at","timestamptz",True),("internal_reason","text",False),("resource_type","text",False),("resource_id","uuid",True),("supersedes_id","uuid",True,"service_request_events")], history=True, unique=["organization_id,request_id,sequence"], invariants=["INTERNAL_ONLY", "SAFE_TYPED_EVENT_METADATA_NO_ACCESS_TEXT"])
    add("service_public_updates", [("request_id","uuid",False,"service_requests"),("sequence","bigint",False),("origin_event_id","uuid",False,"service_request_events"),("actor_id","uuid",True,member),("event_kind","text",False),("message","text",False),("template_code","text",True),("published_at","timestamptz",False),("appointment_id","uuid",True,"appointments"),("supersedes_id","uuid",True,"service_public_updates")], history=True, privacy="PERSONAL", unique=["organization_id,request_id,sequence", "organization_id,origin_event_id,template_code"], invariants=["SEPARATE_CITIZEN_PROJECTION", "NO_INTERNAL_REASON_COPY", "AUDITED_REDACTION_TOMBSTONE"])
    add("service_visit_preferences", [("request_id","uuid",False,"service_requests"),("intervals","jsonb",False),("access_needs","text",False)], privacy="PERSONAL", unique=["organization_id,request_id"], invariants=["MAX_5_FINITE_NONOVERLAPPING_INTERVALS", "PREFERENCE_NEVER_RESERVES_CAPACITY"])
    add("service_visit_access", [("request_id","uuid",False,"service_requests"),("ciphertext","bytea",False),("key_identifier","text",False),("consent_at","timestamptz",False),("review_required","boolean",False)], privacy="SENSITIVE_PERSONAL", unique=["organization_id,request_id"], invariants=["ENCRYPTION_KEY_RETENTION_DISCLOSURE_REVIEW_REQUIRED", "NO_CONTACT_IN_AUDIT_OUTBOX", "CURRENT_ASSIGNED_MINIMUM_DISCLOSURE_ONLY"])
    add("service_work_order_links", [("request_id","uuid",False,"service_requests"),("work_order_id","uuid",False,"work_orders"),("linked_by_id","uuid",False,member),("purpose","M07TaskPurpose",False),("ended_at","timestamptz",True)], unique=["organization_id,request_id,work_order_id"], invariants=["ACCEPTED_SERVICE_AND_TRIAGED_OPERATIONAL_INCIDENT", "MAX_20_ACTIVE_LINKS", "SHARED_WORK_NOT_RESIDENT_DISCLOSURE"])
    add("dispatch_calendar_subjects", [("user_id","uuid",False,"users"),("exclusive_dispatch_organization_id","uuid",False,"organizations"),("enrollment_receipt_id","uuid",False)], global_scope=True, privacy="SECURITY", unique=["user_id"], invariants=["ONE_SCHEDULING_TENANT_PER_GLOBAL_USER", "NO_GLOBAL_LIST_API", "NARROW_ENROLLMENT_FUNCTION_FIXED_SEARCH_PATH_NO_PUBLIC_EXECUTE", "TRANSFER_ONLY_WITH_NO_ACTIVE_FUTURE_ALLOCATION"])
    add("dispatch_technician_profiles", [("membership_id","uuid",False,member),("subject_id","uuid",False,"dispatch_calendar_subjects"),("active","boolean",False),("skill_codes","jsonb",False),("service_area_codes","jsonb",False),("max_daily_minutes","integer",True),("calendar_version","bigint",False),("reviewed_at","timestamptz",True)], unique=["organization_id,membership_id", "organization_id,subject_id"], invariants=["CURRENT_ACTIVE_TECHNICIAN_GRANT", "SUBJECT_USER_MATCHES_MEMBERSHIP_USER", "SUBJECT_EXCLUSIVE_ORG_MATCHES_PROFILE_ORG", "UNKNOWN_ACTIVE_WORK_BLOCKS_PUBLICATION"])
    add("dispatch_shifts", [("profile_id","uuid",False,"dispatch_technician_profiles"),("starts_at","timestamptz",False),("ends_at","timestamptz",False),("status","text",False),("reason","text",False)], invariants=["DATED_EXPLICIT_NO_RECURRING_DEFAULTS", "CANNOT_INVALIDATE_CONFIRMED_ALLOCATION"], constraints=[{"kind":"FINITE_HALF_OPEN_INTERVAL","start":"starts_at","end":"ends_at"}])
    add("dispatch_allocations", [("profile_id","uuid",False,"dispatch_technician_profiles"),("subject_id","uuid",False,"dispatch_calendar_subjects"),("appointment_id","uuid",True,"appointments"),("work_order_id","uuid",True,"work_orders"),("kind","text",False),("occupied_range","tstzrange",False),("active","boolean",False),("released_at","timestamptz",True),("reason","text",False)], unique=["organization_id,appointment_id WHERE active AND appointment_id IS NOT NULL"], invariants=["PROFILE_SUBJECT_AND_ORG_MATCH", "EXACT_TYPED_TARGET_FOR_KIND", "HALF_OPEN_FINITE_NONEMPTY", "NO_NOW_IN_PARTIAL_PREDICATE", "CONSERVATIVE_ARRIVAL_DURATION_BUFFERS", "SORTED_LOCK_ORDER_AND_LOCAL_DAILY_CAPS"], constraints=[{"kind":"EXCLUDE_GIST","keys":[["organization_id","="],["subject_id","="],["occupied_range","&&"]],"where":"active","extension":"btree_gist"}])
    add("appointment_windows", [("profile_id","uuid",False,"dispatch_technician_profiles"),("arrival_start","timestamptz",False),("arrival_end","timestamptz",False),("service_duration_minutes","integer",False),("before_buffer_minutes","integer",False),("after_buffer_minutes","integer",False),("category_codes","jsonb",False),("service_area_codes","jsonb",False),("policy_version","bigint",False),("calendar_version","bigint",False),("state","text",False)], invariants=["SUPERVISOR_PUBLISHED_UNIT_CAPACITY", "D5_EXPLICIT_AUTHORIZED_INPUTS", "FULL_RANGE_WITHIN_SHIFT_EXCLUDES_BLOCKS", "RESIDENT_DTO_EXCLUDES_PROFILE_CAPACITY"])
    add("appointment_requests", [("request_id","uuid",False,"service_requests"),("kind","text",False),("selected_window_id","uuid",False,"appointment_windows"),("replaces_appointment_id","uuid",True,"appointments"),("alternative_window_id","uuid",True,"appointment_windows"),("proposal_revision","bigint",True),("reviewed_expectations","jsonb",True),("offer_expires_at","timestamptz",True),("status","M07AppointmentRequestStatus",False),("public_message","text",True),("internal_reason","text",True)], unique=["organization_id,request_id WHERE status IN (PENDING,ALTERNATIVE_OFFERED)"], invariants=["NO_HOLD_OR_CAPACITY_PROMISE", "CITIZEN_OWNED", "IMMUTABLE_PROPOSAL_REVISION_EXPECTATIONS", "OLD_BOOKING_REMAINS_UNTIL_REPLACEMENT_COMMITS"])
    add("appointments", [("request_id","uuid",False,"service_requests"),("appointment_request_id","uuid",False,"appointment_requests"),("window_id","uuid",False,"appointment_windows"),("work_order_id","uuid",False,"work_orders"),("assignee_id","uuid",False,member),("subject_id","uuid",False,"dispatch_calendar_subjects"),("assignment_version","bigint",False),("arrival_start","timestamptz",False),("arrival_end","timestamptz",False),("service_duration_minutes","integer",False),("status","M07AppointmentStatus",False),("replaces_id","uuid",True,"appointments"),("cancellation_pending","boolean",False)], unique=["organization_id,appointment_request_id", "subject_id WHERE status=CHECKED_IN", "organization_id,request_id WHERE status IN (CONFIRMED,CHECKED_IN)"], invariants=["CONFIRM_AND_ASSIGN_AND_ALLOCATE_ATOMIC", "ONE_CURRENT_VISIT_PER_CASE_AND_WORK", "RESCHEDULE_ROLLBACK_PRESERVES_OLD", "NO_CHECKED_IN_CANCELLATION_FICTION", "ATTENDANCE_MANUAL_NOT_GPS_PROOF"])
    add("appointment_events", [("appointment_id","uuid",False,"appointments"),("actor_id","uuid",False,member),("event_type","text",False),("observed_at","timestamptz",False),("received_at","timestamptz",False),("assignment_version","bigint",False),("operation_id","uuid",False),("note","text",False),("supersedes_id","uuid",True,"appointment_events")], history=True, unique=["organization_id,appointment_id,operation_id"], invariants=["CURRENT_ASSIGNED_TECHNICIAN_OR_SUPERVISOR_CORRECTION", "NO_AUTO_WORK_COMPLETION"])
    add("dispatch_policy", [("configured","boolean",False),("booking_enabled","boolean",False),("horizon_days","integer",True),("minimum_lead_minutes","integer",True),("free_cancel_before_minutes","integer",True),("max_arrival_width_minutes","integer",True),("request_expiry_hours","integer",True),("offer_expiry_hours","integer",True),("max_daily_minutes","integer",True),("minimum_before_buffer_minutes","integer",True),("minimum_after_buffer_minutes","integer",True),("allowed_duration_minutes","jsonb",False)], unique=["organization_id"], invariants=["DISABLED_AND_UNCONFIGURED_UNTIL_AUTHORIZED", "NO_BUSINESS_AVAILABILITY_DEFAULTS", "POLICY_CHANGES_CANNOT_SILENTLY_INVALIDATE_PROMISES"])
    add("investigation_findings", [("work_order_id","uuid",False,"work_orders"),("recorded_by_id","uuid",False,member),("observed_at","timestamptz",False),("received_at","timestamptz",False),("operation_id","uuid",False),("findings","text",False),("no_repair_reason","text",False),("supersedes_id","uuid",True,"investigation_findings")], history=True, unique=["organization_id,work_order_id,operation_id"], invariants=["INVESTIGATION_PURPOSE_ONLY", "CURRENT_ASSIGNED_AND_VERSIONED", "MANUAL_PROVENANCE", "NO_FAKE_REPAIR_OR_VERIFICATION"])
    add("notification_preferences", [("membership_id","uuid",False,member),("channels","jsonb",False),("event_categories","jsonb",False),("quiet_hours","jsonb",True)], privacy="PERSONAL", unique=["organization_id,membership_id"], invariants=["RECIPIENT_SELF_ONLY", "IN_APP_ONLY_EXTERNAL_CHANNELS_FALSE", "NO_TIMELINE_SUPPRESSION", "PROVISION_ON_MEMBERSHIP_WRITE_NOT_GET"])
    # Use existing background_jobs with an event dedup key rather than a second
    # service_outbox_checkpoints queue/table. This resolves the proposal's choice.
    modifications = {
        "work_orders": [("task_purpose","M07TaskPurpose",False)],
        "attachments": [("derivative_digest","text",True),("derivative_storage_key","text",True),("processor_version","text",True),("scanner_version","text",True),("quota_reservation_id","uuid",True),("hold_reason","text",True),("audience","text",False)],
        "attachment_links": [("service_request_id","uuid",True,"service_requests"),("findings_id","uuid",True,"investigation_findings")],
        "feedback_items": [("service_request_id","uuid",True,"service_requests"),("service_rating","integer",True)],
        "background_jobs": [("source_event_id","uuid",True,"domain_events")],
    }
    for name, columns in modifications.items():
        table = tables[name]
        for col, typ, null, *target in columns:
            table["columns"].append({"name":col,"type":typ,"nullable":null})
            if target:
                table["foreign_keys"].append({"column":col,"target":target[0],"same_tenant":True})
        table["x-m07-status"] = "PROPOSED_DELTA_NOT_MIGRATED"
    tables["work_orders"].setdefault("invariants", []).extend(["EXISTING_ROWS_FUTURE_BACKFILL_REPAIR", "INVESTIGATION_SUBMISSION_REQUIRES_FINDINGS_NOT_REPAIR", "LEGACY_ASSIGNMENT_CANCELLATION_SCHEDULER_GUARD", "DUE_AT_NOT_BOOKING", "INCIDENT_FK_STAYS_REQUIRED"])
    tables["attachments"].setdefault("invariants", []).extend(["IMAGE_ONLY_NO_PDF_SVG_HTML_OFFICE", "SCANNER_PROCESSING_STORAGE_LICENSE_REVIEW_BEFORE_ENABLE", "QUARANTINE_FAIL_CLOSED_NO_ORIGINAL_DOWNLOAD", "SEPARATE_ORIGINAL_DERIVATIVE_DIGESTS", "5_MIB_12_MEGAPIXEL_LIMIT", "CURRENT_PARENT_ACL_ON_EVERY_STAGE"])
    tables["attachment_links"].setdefault("invariants", []).extend(["EXACTLY_ONE_TYPED_PARENT", "NO_RESIDENT_ACCESS_TO_SHARED_INTERNAL_MEDIA"])
    tables["background_jobs"].setdefault("invariants", []).extend(["M07_SERVICE_FANOUT_NOTIFICATION_IMAGE_JOBS_NO_TRUTH", "MAX_THREE_TOTAL_M07_DELIVERY_ATTEMPTS", "COMMIT_STATE_EVENT_JOB_TOGETHER"])
    tables["background_jobs"]["unique"].append("organization_id,kind,source_event_id WHERE source_event_id IS NOT NULL")
    for name in ["feedback_items","feedback_events","attachments","attachment_links","notifications","notification_delivery_attempts","background_jobs"]:
        tables[name]["retention"] = "M07_POLICY_REVIEW_REQUIRED"
    db["tables"] += new
    db["status"] = "M07_PROPOSED_COMPOSED_DESIGN_NOT_MIGRATED"
    db["retention_profiles"]["M07_POLICY_REVIEW_REQUIRED"] = "No approved live retention/SLA. Operator review of consent, encrypted storage, erasure, evidence holds and purge/backup process is mandatory; no invented TTL is approved."
    db["x-m07-new-tables"] = [t["name"] for t in new]
    db["x-m07-modified-tables"] = list(modifications)
    return db


def states():
    return {
        "status":"PROPOSED_NOT_EXECUTED",
        "service": {
            "SUBMITTED":["UNDER_REVIEW","WITHDRAWN"],
            "UNDER_REVIEW":["ACCEPTED","AWAITING_RESIDENT","DECLINED","WITHDRAWN"],
            "AWAITING_RESIDENT":["UNDER_REVIEW","WITHDRAWN"],
            "ACCEPTED":["SERVICE_IN_PROGRESS","SERVICE_REVIEW_PENDING","CANCELLED"],
            "SERVICE_IN_PROGRESS":["SERVICE_REVIEW_PENDING","CANCELLED"],
            "SERVICE_REVIEW_PENDING":["SERVICE_IN_PROGRESS","SERVICE_CLOSED","CANCELLED"],
            "SERVICE_CLOSED":[],"DECLINED":[],"WITHDRAWN":[],"CANCELLED":[]},
        "appointment_request": {"PENDING":["CONFIRMED","ALTERNATIVE_OFFERED","DECLINED","WITHDRAWN","EXPIRED"],"ALTERNATIVE_OFFERED":["CONFIRMED","DECLINED","WITHDRAWN","EXPIRED"],"CONFIRMED":[],"DECLINED":[],"WITHDRAWN":[],"EXPIRED":[]},
        "appointment": {"CONFIRMED":["CHECKED_IN","CANCELLED","SUPERSEDED","NO_SHOW"],"CHECKED_IN":["VISIT_FINISHED","NO_ACCESS","ABORTED"],"VISIT_FINISHED":[],"NO_ACCESS":[],"ABORTED":[],"NO_SHOW":[],"CANCELLED":[],"SUPERSEDED":[]},
        "invariants":["REQUEST_NOT_BOOKING","OLD_APPOINTMENT_STAYS_UNTIL_ATOMIC_REPLACEMENT","CANCELLATION_PENDING_NOT_CANCELLED","WORK_COMPLETION_NOT_VERIFICATION","SELF_REPAIR_REVIEW_DENIED","NOT_VERIFIABLE_ONLY","MEMBERSHIP_REVOKE_DENIES_NEW_CONFIRMATION_AND_FILE_ACCESS","NO_HARD_OVERLAP_OVERRIDE","OFFLINE_FINAL_ACTIONS_DISABLED"],
        "constraints": {"allocation":"finite half-open tstzrange; EXCLUDE organization_id=, subject_id=, occupied_range&& WHERE active; btree_gist","occupied_range":"[arrival_start-before_buffer,arrival_end+service_duration+after_buffer)","active_checkin":"UNIQUE(subject_id) WHERE status=CHECKED_IN","transaction_lock_order":["CURRENT_MEMBERSHIPS","SORTED_SERVICE_ROOTS","SORTED_WORK_ORDERS","SORTED_APPOINTMENT_REQUESTS_AND_APPOINTMENTS","ACTOR_IDEMPOTENCY","SORTED_SUBJECT_PROFILE","SORTED_WINDOW_SHIFT"],"reschedule":"old deactivate + new allocation + appointment + assignment/history/audit/outbox in one transaction; rollback restores old","daily_cap":"Asia/Kolkata local dates; count buffers; unknown work inhibits publishing","external_busy_time":"not guaranteed; one scheduling tenant per enrolled global user"},
        "policy_gates": {"availability_defaults":None,"live_retention_policy":None,"customer_sla":None,"external_channels":False,"pdf_documents":False,"offline":False,"max_total_delivery_attempts":3,"retry_delays_seconds":None,"encryption":"OWNER_REVIEW_REQUIRED","image_pipeline":"SCANNER_PROCESSING_STORAGE_LICENSE_OWNER_REVIEW_REQUIRED"}}
