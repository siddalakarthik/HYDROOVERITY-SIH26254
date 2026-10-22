"use client";
import { useState, type FormEvent } from "react";
import Link from "next/link";
import { api, type Model } from "@/lib/api";
import {
  Field,
  ErrorPanel,
  ResourceState,
  useResource,
  Notice,
} from "@/components/ui";

export function PublicStatus() {
  const resource = useResource<Model<"ProjectStatus">>(
    "/public/project-status",
  );
  return (
    <ResourceState {...resource}>
      {resource.data && (
        <>
          <div className="status-ledger">
            <div>
              <strong>Backend-reported stage</strong>
              <span>{resource.data.stage}</span>
            </div>
            <div>
              <strong>Hardware validation</strong>
              <span>Not established</span>
            </div>
            <div>
              <strong>Field validation</strong>
              <span>Not established</span>
            </div>
          </div>
          <ul className="plain-list">
            {resource.data.limitations.map((text) => (
              <li key={text}>{text}</li>
            ))}
          </ul>
          <Notice>
            Current backend editorial status is shown as returned by the
            service. It is not a live measurement or a statement of field
            readiness.
          </Notice>
        </>
      )}
    </ResourceState>
  );
}
export function UtilityLookup() {
  const [utility, setUtility] = useState<Model<"PublicUtility">>();
  const [error, setError] = useState<unknown>();
  const [pending, setPending] = useState(false);
  async function lookup(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setError(undefined);
    setUtility(undefined);
    const slug = String(new FormData(e.currentTarget).get("slug") ?? "");
    try {
      setUtility(
        (
          await api<Model<"PublicUtility">>(
            `/public/utilities/${encodeURIComponent(slug)}`,
          )
        ).data,
      );
    } catch (e) {
      setError(e);
    } finally {
      setPending(false);
    }
  }
  return (
    <div className="reading-column">
      <form className="form" onSubmit={lookup}>
        <Field
          label="Utility code"
          name="slug"
          required
          pattern="[a-z0-9-]+"
          maxLength={80}
          help="Use the utility code supplied by your water-service provider. There is no public complaint search."
        />
        <button className="button" disabled={pending}>
          {pending ? "Looking up utility…" : "Find utility"}
        </button>
      </form>
      {error !== undefined && <ErrorPanel error={error} />}{" "}
      {utility && (
        <section className="panel">
          <h2>{utility.name}</h2>
          <p>Citizen reporting is enabled for this utility.</p>
          <div className="actions">
            <Link className="button" href="/login">
              Sign in to report
            </Link>
            <Link
              href={`/register?utility=${encodeURIComponent(utility.slug)}`}
            >
              Create a citizen account
            </Link>
          </div>
          <p className="help">
            After sign-in, choose this utility from your actual memberships.
          </p>
        </section>
      )}
      <Notice>
        Report an observed issue and a rough area. Photo upload and precise
        location collection are not enabled.
      </Notice>
    </div>
  );
}
