"use client";
import Link from "next/link";

import {
  Children,
  cloneElement,
  isValidElement,
  useEffect,
  useId,
  useRef,
  useState,
  type ReactElement,
  type ReactNode,
  type FormEvent,
} from "react";
import { AlertCircle, ArrowRight, Check, RefreshCw, Info } from "lucide-react";
import {
  api,
  ApiError,
  date,
  mutationIdentity,
  type Mutation,
} from "@/lib/api";

export function Notice({
  children,
  tone = "info",
}: {
  children: ReactNode;
  tone?: "info" | "warning";
}) {
  return (
    <div className={`notice ${tone}`}>
      <Info size={19} aria-hidden="true" />
      <div>{children}</div>
    </div>
  );
}
export function Badge({ children }: { children: ReactNode }) {
  return <span className="badge">{children}</span>;
}
export function Heading({
  eyebrow,
  title,
  children,
  action,
}: {
  eyebrow?: string;
  title: string;
  children?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <header className="page-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        {children && <p className="lede">{children}</p>}
      </div>
      {action}
    </header>
  );
}
export function Empty({
  title = "No records yet",
  children,
}: {
  title?: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty">
      <Info aria-hidden="true" size={26} />
      <h3>{title}</h3>
      <p>{children ?? "There are no permitted records in this view."}</p>
    </div>
  );
}
export function ErrorPanel({
  error,
  retry,
}: {
  error: unknown;
  retry?: () => void;
}) {
  const p = error instanceof ApiError ? error : null;
  return (
    <div className="error-panel" role="alert" tabIndex={-1}>
      <AlertCircle size={20} aria-hidden="true" />
      <div>
        <strong>
          {p?.status === 401
            ? "Please sign in again"
            : p?.status === 403
              ? "This action is not permitted"
              : p?.status === 404
                ? "Record unavailable"
                : p?.status === 412 || p?.status === 428
                  ? "Review the current version"
                  : "Request could not be completed"}
        </strong>
        <p>
          {p?.message ??
            "The request was interrupted. No receipt was confirmed."}
        </p>
        {p?.retryAfter && <p>Wait {p.retryAfter} seconds before retrying.</p>}
        {p?.requestId && <p className="meta">Request ID: {p.requestId}</p>}
        {p?.fields.length ? (
          <ul>
            {p.fields.map((field, index) => (
              <li key={index}>
                <button
                  type="button"
                  className="field-error-link"
                  onClick={(event) => {
                    const form = event.currentTarget.closest("form");
                    form
                      ?.querySelector<HTMLElement>(
                        `[name="${CSS.escape(field.field)}"]`,
                      )
                      ?.focus();
                  }}
                >
                  {field.field}: {field.message}
                </button>
              </li>
            ))}
          </ul>
        ) : null}
        {p?.status === 401 && <Link href="/login">Sign in</Link>}
        {(p?.status === 412 || p?.status === 428) && (
          <p>
            Refresh and review the changed record before submitting a new
            action.
          </p>
        )}
        {retry && (
          <button className="button secondary" type="button" onClick={retry}>
            <RefreshCw size={16} aria-hidden="true" />
            Refresh current data
          </button>
        )}
      </div>
    </div>
  );
}
export function useResource<T>(path: string | null) {
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState<{
    path: string | null;
    data?: T;
    etag?: string | null;
    error?: unknown;
    loading: boolean;
  }>({ path, loading: true });
  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    const clear = () => {
      controller.abort();
      setState({
        path,
        loading: false,
        error: new ApiError(
          401,
          "SCOPE_CHANGED",
          "Workspace or session changed. Reload authorized data.",
        ),
      });
    };
    window.addEventListener("hydro:scope-cleared", clear);
    api<T>(path, { signal: controller.signal })
      .then(({ data, etag }) => {
        if (!controller.signal.aborted)
          setState({ path, data, etag, loading: false });
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted)
          setState({ path, error, loading: false });
      });
    return () => {
      controller.abort();
      window.removeEventListener("hydro:scope-cleared", clear);
    };
  }, [path, revision]);
  const valid = state.path === path;
  return {
    data: valid ? state.data : undefined,
    etag: valid ? state.etag : undefined,
    error: valid ? state.error : undefined,
    loading: !valid || state.loading,
    refresh: () => {
      setState({ path, loading: true });
      setRevision((n) => n + 1);
    },
  };
}
export function ResourceState({
  loading,
  error,
  refresh,
  children,
}: {
  loading: boolean;
  error?: unknown;
  refresh: () => void;
  children: ReactNode;
}) {
  if (loading)
    return (
      <div className="loading" role="status">
        Loading authorized records…
      </div>
    );
  if (error) return <ErrorPanel error={error} retry={refresh} />;
  return <>{children}</>;
}
export function Freshness({ at }: { at?: string }) {
  return (
    <p className="meta freshness">
      Authorized records · Snapshot {date(at)} · Manual records are not sensor
      measurements.
    </p>
  );
}
export function Field({
  label,
  name,
  help,
  children,
  ...props
}: {
  label: string;
  name: string;
  help?: string;
  children?: ReactNode;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  const id = useId();
  const controls = Children.map(children, (child) =>
    isValidElement(child) &&
    typeof child.type === "string" &&
    ["input", "select", "textarea"].includes(child.type)
      ? cloneElement(
          child as ReactElement<{ id?: string; "aria-describedby"?: string }>,
          { id, "aria-describedby": help ? `${id}-help` : undefined },
        )
      : child,
  );
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {children ? (
        controls
      ) : (
        <input
          id={id}
          name={name}
          aria-describedby={help ? `${id}-help` : undefined}
          {...props}
        />
      )}{" "}
      {help && (
        <p id={`${id}-help`} className="help">
          {help}
        </p>
      )}
    </div>
  );
}
export function TextArea({
  label,
  name,
  minLength = 5,
  maxLength = 2000,
  defaultValue = "",
  help,
}: {
  label: string;
  name: string;
  minLength?: number;
  maxLength?: number;
  defaultValue?: string;
  help?: string;
}) {
  const [length, setLength] = useState(defaultValue.length);
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <textarea
        id={id}
        name={name}
        required
        minLength={minLength}
        maxLength={maxLength}
        defaultValue={defaultValue}
        onChange={(e) => setLength(e.target.value.length)}
        aria-describedby={`${id}-count${help ? ` ${id}-help` : ""}`}
      />
      <span id={`${id}-count`} className="help">
        {length} / {maxLength} characters
      </span>
      {help && (
        <p className="help" id={`${id}-help`}>
          {help}
        </p>
      )}
    </div>
  );
}
export function Select({
  name,
  label,
  options,
  defaultValue,
  required = true,
}: {
  name: string;
  label: string;
  options: { value: string; label: string }[];
  defaultValue?: string;
  required?: boolean;
}) {
  const [selected, setSelected] = useState(defaultValue ?? "");
  return (
    <Field name={name} label={label}>
      <select
        id={name}
        name={name}
        value={selected}
        onChange={(event) => setSelected(event.target.value)}
        required={required}
      >
        <option value="">Choose…</option>
        {options.map((o) => (
          <option value={o.value} key={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </Field>
  );
}
export const value = (f: FormData, name: string) =>
  String(f.get(name) ?? "").trim();
export function ActionForm({
  path,
  method = "POST",
  version,
  auth = false,
  build,
  onDone,
  children,
  submit = "Save record",
  description,
}: {
  path: string;
  method?: "POST" | "PATCH" | "PUT" | "DELETE";
  version?: string | number;
  auth?: boolean;
  build: (f: FormData, key: string) => unknown;
  onDone?: (data: unknown) => void;
  children?: ReactNode;
  submit?: string;
  description?: string;
}) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<unknown>();
  const [receipt, setReceipt] = useState<string>();
  const identity = useRef<Mutation | undefined>(undefined);
  const form = useRef<HTMLFormElement>(null);
  async function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    setPending(true);
    setError(undefined);
    setReceipt(undefined);
    try {
      const data = new FormData(event.currentTarget);
      // Build with an operation ID stable across deliberate identical-body retries.
      const preliminary = auth ? undefined : build(data, "operation");
      if (!auth)
        identity.current = mutationIdentity(identity.current, method, path, [
          version,
          preliminary,
        ]);
      const body = build(data, identity.current?.key ?? "");
      const result = await api<unknown>(path, {
        method,
        body,
        version,
        key: identity.current?.key,
      });
      identity.current = undefined;
      const r = result.data as { id?: string; message?: string };
      setReceipt(
        r.message ??
          (r.id ? `Saved. Receipt ${r.id}` : "Server confirmed the change."),
      );
      onDone?.(result.data);
    } catch (e) {
      setError(e);
      requestAnimationFrame(() =>
        form.current?.querySelector<HTMLElement>("[role=alert]")?.focus(),
      );
    } finally {
      setPending(false);
    }
  }
  return (
    <form ref={form} className="form" onSubmit={send} aria-busy={pending}>
      {description && <p>{description}</p>}
      {error !== undefined && <ErrorPanel error={error} />}
      <fieldset disabled={pending}>{children}</fieldset>
      <button className="button" type="submit" disabled={pending}>
        {pending ? "Waiting for receipt…" : submit}
        {!pending && <ArrowRight size={16} aria-hidden="true" />}
      </button>
      {receipt && (
        <div className="receipt" role="status">
          <Check size={18} aria-hidden="true" />
          {receipt}
        </div>
      )}
    </form>
  );
}
