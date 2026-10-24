-- Scheduling foundation. No utility configuration or capacity is invented.
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE dispatch_calendar_subjects(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL UNIQUE REFERENCES users(id),
 exclusive_dispatch_organization_id uuid NOT NULL REFERENCES organizations(id),
 enrollment_receipt_id uuid NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 UNIQUE(exclusive_dispatch_organization_id,id)
);
REVOKE ALL ON dispatch_calendar_subjects FROM hydro_app;

CREATE TABLE dispatch_technician_profiles(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 membership_id uuid NOT NULL, subject_id uuid NOT NULL, active boolean NOT NULL DEFAULT true,
 skill_codes jsonb NOT NULL CHECK(jsonb_typeof(skill_codes)='array' AND jsonb_array_length(skill_codes) BETWEEN 1 AND 20),
 service_area_codes jsonb NOT NULL CHECK(jsonb_typeof(service_area_codes)='array' AND jsonb_array_length(service_area_codes) BETWEEN 1 AND 20),
 max_daily_minutes integer NOT NULL CHECK(max_daily_minutes BETWEEN 1 AND 960),
 calendar_version bigint NOT NULL DEFAULT 1 CHECK(calendar_version>0), reviewed_at timestamptz NOT NULL DEFAULT now(),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 UNIQUE(organization_id,id), UNIQUE(organization_id,membership_id), UNIQUE(organization_id,subject_id), UNIQUE(organization_id,id,subject_id),
 FOREIGN KEY(organization_id,membership_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,subject_id) REFERENCES dispatch_calendar_subjects(exclusive_dispatch_organization_id,id)
);

-- The global registry has no runtime table access or global-list function.
-- Concurrent attempts by different utilities serialize on the unique global user.
CREATE FUNCTION hydro_dispatch_enroll(member uuid, receipt uuid) RETURNS uuid
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
DECLARE target public.organization_memberships; subject public.dispatch_calendar_subjects;
BEGIN
 IF NOT public.hydro_m07_role(ARRAY['ADMIN']) THEN RAISE EXCEPTION 'forbidden' USING ERRCODE='42501'; END IF;
 SELECT * INTO target FROM public.organization_memberships WHERE id=member
 AND organization_id::text=current_setting('hydro.organization_id',true) AND status='ACTIVE' FOR SHARE;
 IF target.id IS NULL OR NOT EXISTS(SELECT 1 FROM public.role_assignments a JOIN public.roles r ON r.id=a.role_id
 WHERE a.membership_id=target.id AND a.revoked_at IS NULL AND r.code='TECHNICIAN')
 THEN RAISE EXCEPTION 'active technician required' USING ERRCODE='23514'; END IF;
 INSERT INTO public.dispatch_calendar_subjects(user_id,exclusive_dispatch_organization_id,enrollment_receipt_id)
 VALUES(target.user_id,target.organization_id,receipt) ON CONFLICT(user_id) DO NOTHING;
 SELECT * INTO subject FROM public.dispatch_calendar_subjects WHERE user_id=target.user_id FOR UPDATE;
 IF subject.exclusive_dispatch_organization_id<>target.organization_id
 THEN RAISE EXCEPTION 'exclusive enrollment unavailable' USING ERRCODE='23505'; END IF;
 RETURN subject.id;
END $$;
REVOKE ALL ON FUNCTION hydro_dispatch_enroll(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hydro_dispatch_enroll(uuid,uuid) TO hydro_app;

CREATE FUNCTION hydro_dispatch_profile_identity() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM public.dispatch_calendar_subjects s JOIN public.organization_memberships m ON m.user_id=s.user_id
 WHERE s.id=NEW.subject_id AND m.id=NEW.membership_id AND m.organization_id=NEW.organization_id
 AND s.exclusive_dispatch_organization_id=NEW.organization_id)
 THEN RAISE EXCEPTION 'profile identity mismatch' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION hydro_dispatch_profile_identity() FROM PUBLIC;
CREATE TRIGGER dispatch_profile_identity BEFORE INSERT OR UPDATE ON dispatch_technician_profiles
FOR EACH ROW EXECUTE FUNCTION hydro_dispatch_profile_identity();

CREATE TABLE dispatch_shifts(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id), profile_id uuid NOT NULL,
 starts_at timestamptz NOT NULL, ends_at timestamptz NOT NULL, status text NOT NULL CHECK(status IN ('ACTIVE','WITHDRAWN')),
 reason text NOT NULL CHECK(length(reason) BETWEEN 5 AND 2000),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 CHECK(isfinite(starts_at) AND isfinite(ends_at) AND starts_at<ends_at AND ends_at<=starts_at+interval '24 hours'),
 UNIQUE(organization_id,id), FOREIGN KEY(organization_id,profile_id) REFERENCES dispatch_technician_profiles(organization_id,id),
 EXCLUDE USING gist(organization_id WITH =, profile_id WITH =, tstzrange(starts_at,ends_at,'[)') WITH &&) WHERE(status='ACTIVE')
);

CREATE TABLE dispatch_allocations(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id), profile_id uuid NOT NULL, subject_id uuid NOT NULL,
 appointment_id uuid, work_order_id uuid, kind text NOT NULL CHECK(kind IN ('UNAVAILABLE','WORK_BLOCK','APPOINTMENT')),
 occupied_range tstzrange NOT NULL, active boolean NOT NULL DEFAULT true, released_at timestamptz,
 reason text NOT NULL CHECK(length(reason) BETWEEN 5 AND 2000),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 CHECK(NOT isempty(occupied_range) AND NOT lower_inf(occupied_range) AND NOT upper_inf(occupied_range)
 AND isfinite(lower(occupied_range)) AND isfinite(upper(occupied_range)) AND lower_inc(occupied_range) AND NOT upper_inc(occupied_range)),
 CHECK(active=(released_at IS NULL)),
 CHECK((kind='UNAVAILABLE' AND work_order_id IS NULL AND appointment_id IS NULL)
 OR (kind='WORK_BLOCK' AND work_order_id IS NOT NULL AND appointment_id IS NULL)
 OR (kind='APPOINTMENT' AND work_order_id IS NOT NULL AND appointment_id IS NOT NULL)),
 UNIQUE(organization_id,id),
 FOREIGN KEY(organization_id,profile_id,subject_id) REFERENCES dispatch_technician_profiles(organization_id,id,subject_id),
 FOREIGN KEY(organization_id,work_order_id) REFERENCES work_orders(organization_id,id),
 EXCLUDE USING gist(organization_id WITH =, subject_id WITH =, occupied_range WITH &&) WHERE(active)
);
CREATE UNIQUE INDEX dispatch_one_appointment_allocation ON dispatch_allocations(organization_id,appointment_id) WHERE active AND appointment_id IS NOT NULL;

CREATE TABLE dispatch_policy(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL UNIQUE REFERENCES organizations(id),
 booking_enabled boolean NOT NULL DEFAULT false, configured boolean NOT NULL DEFAULT false,
 horizon_days integer CHECK(horizon_days BETWEEN 1 AND 60),
 minimum_lead_minutes integer CHECK(minimum_lead_minutes BETWEEN 0 AND 10080),
 free_cancel_before_minutes integer CHECK(free_cancel_before_minutes BETWEEN 0 AND 10080),
 max_arrival_width_minutes integer CHECK(max_arrival_width_minutes BETWEEN 1 AND 480),
 request_expiry_hours integer CHECK(request_expiry_hours BETWEEN 1 AND 168),
 offer_expiry_hours integer CHECK(offer_expiry_hours BETWEEN 1 AND 72),
 max_daily_minutes integer CHECK(max_daily_minutes BETWEEN 1 AND 960),
 minimum_before_buffer_minutes integer CHECK(minimum_before_buffer_minutes BETWEEN 0 AND 240),
 minimum_after_buffer_minutes integer CHECK(minimum_after_buffer_minutes BETWEEN 0 AND 240),
 allowed_duration_minutes jsonb NOT NULL DEFAULT '[]' CHECK(jsonb_typeof(allowed_duration_minutes)='array'),
 reason text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 CHECK(NOT booking_enabled OR configured),
 CHECK(NOT configured OR (horizon_days IS NOT NULL AND minimum_lead_minutes IS NOT NULL AND free_cancel_before_minutes IS NOT NULL
 AND max_arrival_width_minutes IS NOT NULL AND request_expiry_hours IS NOT NULL AND offer_expiry_hours IS NOT NULL
 AND max_daily_minutes IS NOT NULL AND minimum_before_buffer_minutes IS NOT NULL AND minimum_after_buffer_minutes IS NOT NULL
 AND jsonb_array_length(allowed_duration_minutes) BETWEEN 1 AND 20)),
 UNIQUE(organization_id,id)
);
INSERT INTO dispatch_policy(organization_id) SELECT id FROM organizations;
CREATE FUNCTION hydro_dispatch_initial_policy() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
BEGIN INSERT INTO public.dispatch_policy(organization_id) VALUES(NEW.id); RETURN NEW; END $$;
REVOKE ALL ON FUNCTION hydro_dispatch_initial_policy() FROM PUBLIC;
CREATE TRIGGER dispatch_initial_policy AFTER INSERT ON organizations FOR EACH ROW EXECUTE FUNCTION hydro_dispatch_initial_policy();
