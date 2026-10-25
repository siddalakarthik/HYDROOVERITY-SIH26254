-- Private-development communications. No external destinations or media storage.
CREATE TABLE notification_preferences (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 membership_id uuid NOT NULL, version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 in_app boolean NOT NULL DEFAULT false, event_categories jsonb NOT NULL DEFAULT '[]', quiet_hours jsonb,
 UNIQUE(organization_id,id), UNIQUE(organization_id,membership_id),
 FOREIGN KEY(organization_id,membership_id) REFERENCES organization_memberships(organization_id,id),
 CHECK(jsonb_typeof(event_categories)='array' AND event_categories <@ '["SERVICE_PROGRESS","APPOINTMENT","WORK_ASSIGNMENT","SERVICE_FEEDBACK"]'::jsonb),
 CHECK(quiet_hours IS NULL OR (jsonb_typeof(quiet_hours)='object' AND quiet_hours->>'timezone'='Asia/Kolkata'))
);
CREATE TABLE feedback_items (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 owner_membership_id uuid NOT NULL, service_request_id uuid, complaint_id uuid,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 summary text NOT NULL CHECK(length(summary) BETWEEN 5 AND 200), description text NOT NULL CHECK(length(description) BETWEEN 5 AND 2000),
 service_rating integer CHECK(service_rating BETWEEN 1 AND 5),
 status text NOT NULL DEFAULT 'NEW' CHECK(status IN ('NEW','TRIAGED','PLANNED','RESOLVED','DECLINED')),
 resolution_note text CHECK(length(resolution_note)<=2000), severity text, assignee_membership_id uuid,
 CHECK(service_request_id IS NULL OR complaint_id IS NULL), CHECK(service_rating IS NULL OR service_request_id IS NOT NULL),
 UNIQUE(organization_id,id),
 FOREIGN KEY(organization_id,owner_membership_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,service_request_id) REFERENCES service_requests(organization_id,id),
 FOREIGN KEY(organization_id,complaint_id) REFERENCES citizen_complaints(organization_id,id),
 FOREIGN KEY(organization_id,assignee_membership_id) REFERENCES organization_memberships(organization_id,id)
);
CREATE TABLE feedback_events (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 feedback_id uuid NOT NULL, actor_id uuid NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 resulting_version bigint NOT NULL, status text NOT NULL, public_note text, private_severity text,
 UNIQUE(organization_id,id), UNIQUE(organization_id,feedback_id,resulting_version),
 FOREIGN KEY(organization_id,feedback_id) REFERENCES feedback_items(organization_id,id),
 FOREIGN KEY(organization_id,actor_id) REFERENCES organization_memberships(organization_id,id)
);
CREATE TABLE background_jobs (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 domain_event_id uuid NOT NULL, kind text NOT NULL CHECK(kind='NOTIFICATION_FANOUT'),
 targets jsonb NOT NULL CHECK(jsonb_typeof(targets)='array' AND jsonb_array_length(targets)<=2),
 state text NOT NULL DEFAULT 'QUEUED' CHECK(state IN ('QUEUED','RUNNING','SUCCEEDED','FAILED')),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 lease_token uuid, lease_until timestamptz, attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 3),
 next_attempt_at timestamptz, safe_error_code text,
 UNIQUE(organization_id,id), UNIQUE(organization_id,domain_event_id,kind),
 FOREIGN KEY(organization_id,domain_event_id) REFERENCES domain_events(organization_id,id),
 CHECK((state='RUNNING')=(lease_token IS NOT NULL AND lease_until IS NOT NULL))
);
CREATE TABLE notifications (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 recipient_id uuid NOT NULL, domain_event_id uuid NOT NULL, service_request_id uuid,
 template_version text NOT NULL CHECK(template_version='M07C-1'), channel text NOT NULL CHECK(channel='IN_APP'),
 event_category text NOT NULL CHECK(event_category IN ('SERVICE_PROGRESS','APPOINTMENT','WORK_ASSIGNMENT','SERVICE_FEEDBACK')),
 resource_type text NOT NULL CHECK(resource_type IN ('service_requests','appointments','appointment_requests','work_orders','feedback_items')),
 resource_id uuid NOT NULL, resource_version bigint NOT NULL CHECK(resource_version>0),
 message text NOT NULL CHECK(length(message)<=500), resource_path text NOT NULL CHECK(left(resource_path,1)='/'),
 state text NOT NULL DEFAULT 'QUEUED' CHECK(state IN ('QUEUED','SENDING','DELIVERED','RETRY_WAIT','FAILED','SUPPRESSED')),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0), read_at timestamptz, delivered_at timestamptz,
 attempt_number integer NOT NULL DEFAULT 0 CHECK(attempt_number BETWEEN 0 AND 3), attempted_at timestamptz, next_attempt_at timestamptz, safe_error_code text,
 UNIQUE(organization_id,id), UNIQUE(organization_id,recipient_id,domain_event_id,template_version,channel),
 FOREIGN KEY(organization_id,recipient_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,domain_event_id) REFERENCES domain_events(organization_id,id),
 FOREIGN KEY(organization_id,service_request_id) REFERENCES service_requests(organization_id,id),
 CHECK(read_at IS NULL OR delivered_at IS NOT NULL), CHECK((state='DELIVERED')=(delivered_at IS NOT NULL))
);
CREATE TABLE notification_delivery_attempts (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 notification_id uuid NOT NULL, attempt_number integer NOT NULL CHECK(attempt_number BETWEEN 1 AND 3),
 created_at timestamptz NOT NULL DEFAULT now(), state text NOT NULL, safe_error_code text,
 UNIQUE(organization_id,id), UNIQUE(organization_id,notification_id,attempt_number),
 FOREIGN KEY(organization_id,notification_id) REFERENCES notifications(organization_id,id)
);
CREATE INDEX notification_inbox ON notifications(organization_id,recipient_id,created_at DESC,id DESC) WHERE state='DELIVERED';
CREATE INDEX notification_job_claim ON background_jobs(organization_id,state,next_attempt_at,created_at);
CREATE FUNCTION hydro_notification_preferences_provision() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 INSERT INTO notification_preferences(organization_id,membership_id) VALUES(NEW.organization_id,NEW.id);
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION hydro_notification_preferences_provision() FROM PUBLIC;
CREATE TRIGGER notification_preferences_provision AFTER INSERT ON organization_memberships FOR EACH ROW EXECUTE FUNCTION hydro_notification_preferences_provision();
INSERT INTO notification_preferences(organization_id,membership_id) SELECT organization_id,id FROM organization_memberships;
