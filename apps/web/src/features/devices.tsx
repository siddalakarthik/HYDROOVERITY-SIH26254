"use client";
import Link from "next/link";
import { label, orgPath, uuid, type Model } from "@/lib/api";
import {
  ActionForm,
  Badge,
  Empty,
  Field,
  Heading,
  Notice,
  ResourceState,
  Select,
  useResource,
  value,
} from "@/components/ui";
import { Pager, usePage } from "@/components/pagination";

export function Devices({
  org,
  roles,
  id,
}: {
  org: string;
  roles: string[];
  id?: string;
}) {
  return id ? (
    <DeviceDetail org={org} id={id} />
  ) : (
    <DeviceList org={org} roles={roles} />
  );
}
function DeviceList({ org, roles }: { org: string; roles: string[] }) {
  const path = orgPath(org, "/devices");
  const devices = usePage<Model<"Device">>(path);
  return (
    <>
      <Heading eyebrow="Device register" title="Proposed device identities">
        Keep an accountable identity record before connecting hardware.
      </Heading>
      <Notice tone="warning">
        These records are proposed metadata. Health remains UNKNOWN.
        Registration does not approve physical provisioning, establish
        calibration, connect a sensor or prove field validation.
      </Notice>
      {roles.includes("ADMIN") && (
        <section className="panel">
          <h2>Register proposed device metadata</h2>
          <p>
            Recent sign-in is required. Acquisition context becomes immutable;
            incorrect profiles need a separately reviewed new identity.
          </p>
          <ActionForm
            path={path}
            submit="Register proposed identity"
            build={(form) =>
              ({
                serial_ref: value(form, "serial_ref"),
                device_kind: value(
                  form,
                  "device_kind",
                ) as Model<"DeviceWrite">["device_kind"],
                provisioning_environment: value(
                  form,
                  "environment",
                ) as Model<"DeviceWrite">["provisioning_environment"],
              }) satisfies Model<"DeviceWrite">
            }
            onDone={devices.refresh}
          >
            <Field
              name="serial_ref"
              label="Proposed serial or reference"
              required
              maxLength={80}
            />
            <Select
              name="device_kind"
              label="Proposed device type"
              options={[
                { value: "WATCH", label: "HYDRO-WATCH" },
                { value: "GUARD5", label: "GUARD-5" },
                { value: "EAR_PAIR", label: "HYDRO-EAR common-clock pair" },
                { value: "VIRTUAL", label: "Virtual simulation identity" },
              ]}
            />
            <Select
              name="environment"
              label="Declared acquisition context"
              options={[
                { value: "LABORATORY", label: "Laboratory proposal" },
                {
                  value: "FIELD",
                  label: "Field proposal — no deployment approval",
                },
                {
                  value: "SIMULATION",
                  label: "Simulation (virtual identity only)",
                },
              ]}
            />
          </ActionForm>
        </section>
      )}
      <ResourceState {...devices}>
        <section className="panel">
          <h2>Authorized identity register</h2>
          {devices.data?.items.length ? (
            <ul className="record-list">
              {devices.data.items.map((device) => (
                <li key={device.id}>
                  <div className="record-top">
                    <h3>
                      <Link href={`/app/${org}/devices/${device.id}`}>
                        {device.serial_ref}
                      </Link>
                    </h3>
                    <Badge>{device.health}</Badge>
                  </div>
                  <p>
                    {label(device.device_kind)} · {label(device.environment)} ·
                    Proposed metadata
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <Empty title="No proposed identities registered">
              No devices or measurements are fabricated for this utility.
            </Empty>
          )}
          <Pager {...devices} />
        </section>
      </ResourceState>
    </>
  );
}
function DeviceDetail({ org, id }: { org: string; id: string }) {
  const device = useResource<Model<"Device">>(
    orgPath(org, `/devices/${uuid(id)}`),
  );
  return (
    <>
      <Heading
        eyebrow="Proposed metadata"
        title="Device identity"
        action={
          <Link href={`/app/${org}/devices`}>All proposed identities</Link>
        }
      />
      <ResourceState {...device}>
        {device.data && (
          <section className="panel">
            <h2>{device.data.serial_ref}</h2>
            <Badge>{device.data.health}</Badge>
            <dl className="details-grid">
              <div>
                <dt>Type</dt>
                <dd>{label(device.data.device_kind)}</dd>
              </div>
              <div>
                <dt>Declared context</dt>
                <dd>{label(device.data.environment)} · proposed</dd>
              </div>
              <div>
                <dt>Device reference</dt>
                <dd className="mono">{device.data.id}</dd>
              </div>
            </dl>
            <Notice tone="warning">
              Physical provisioning has not been approved. Hardware credentials
              require an independently reviewed binding. The current credential
              boundary is tested only with isolated synthetic fixtures. No
              physical capture, channel health or calibration is established.
            </Notice>
            <button
              type="button"
              className="button secondary"
              disabled
              aria-describedby="credential-gate"
            >
              Issue hardware credential
            </button>
            <p id="credential-gate" className="help">
              Unavailable until actual hardware/operator provisioning review. No
              secret is created or cached by this page.
            </p>
          </section>
        )}
      </ResourceState>
    </>
  );
}
