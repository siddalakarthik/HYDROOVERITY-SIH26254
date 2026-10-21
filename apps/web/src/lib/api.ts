import type { components, operations } from "./generated";

export type Model<K extends keyof components["schemas"]> =
  components["schemas"][K];
export type Page<T> = { items: T[]; next_cursor: string | null; as_of: string };
export type OperationId = keyof operations;
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public requestId = "",
    public retryAfter = "",
    public fields: { field: string; message: string }[] = [],
  ) {
    super(message);
  }
}
export function uuid(value: string) {
  if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      value,
    )
  )
    throw new ApiError(
      422,
      "INVALID_IDENTIFIER",
      "The resource identifier is invalid.",
    );
  return encodeURIComponent(value);
}
export function orgPath(org: string, suffix = "") {
  return `/orgs/${uuid(org)}${suffix}`;
}
export function query(values: Record<string, string | undefined>) {
  const p = new URLSearchParams();
  for (const [key, value] of Object.entries(values))
    if (value) p.set(key, value);
  return p.size ? `?${p.toString()}` : "";
}
export type Mutation = { key: string; signature: string };
export function mutationIdentity(
  previous: Mutation | undefined,
  method: string,
  path: string,
  body: unknown,
): Mutation {
  const signature = JSON.stringify([method, path, body]);
  return previous?.signature === signature
    ? previous
    : { key: crypto.randomUUID(), signature };
}
let epoch = 0;
let csrfState: { token: string; expires: number } | undefined;
const pending = new Set<AbortController>();
export function clearPrivateState() {
  epoch += 1;
  csrfState = undefined;
  pending.forEach((controller) => controller.abort());
  pending.clear();
  if (typeof window !== "undefined")
    window.dispatchEvent(new Event("hydro:scope-cleared"));
}
type Options = {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  key?: string;
  version?: string | number;
  signal?: AbortSignal;
};
async function transport<T>(
  path: string,
  options: Options = {},
): Promise<{ data: T; etag: string | null }> {
  if (
    !path.startsWith("/") ||
    path.startsWith("//") ||
    /[\\#\r\n]/.test(path) ||
    path.includes("..")
  )
    throw new ApiError(400, "INVALID_PATH", "Invalid API path.");
  const controller = new AbortController();
  const started = epoch;
  const abort = () => controller.abort();
  options.signal?.addEventListener("abort", abort, { once: true });
  if (options.signal?.aborted) controller.abort();
  pending.add(controller);
  const timer = setTimeout(abort, 20000);
  try {
    const h = new Headers({ Accept: "application/json" });
    const method = options.method ?? "GET";
    if (options.body !== undefined) {
      if (new TextEncoder().encode(JSON.stringify(options.body)).length > 16384)
        throw new ApiError(
          413,
          "BODY_TOO_LARGE",
          "This request exceeds the backend’s 16 KiB body limit. Reduce the submitted content.",
        );
      h.set("Content-Type", "application/json");
    }
    if (method !== "GET") {
      if (!csrfState || csrfState.expires < Date.now() + 5000) {
        const csrf = await transport<Model<"Csrf">>("/auth/csrf", {
          signal: controller.signal,
        });
        csrfState = {
          token: csrf.data.csrf_token,
          expires: Date.parse(csrf.data.expires_at) || Date.now() + 60000,
        };
      }
      h.set("X-CSRF-Token", csrfState.token);
      if (options.key) h.set("Idempotency-Key", options.key);
      if (options.version !== undefined)
        h.set(
          "If-Match",
          typeof options.version === "number"
            ? `"${options.version}"`
            : options.version,
        );
    }
    const response = await fetch(`/api/v1${path}`, {
      method,
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
      headers: h,
      credentials: "same-origin",
      cache: "no-store",
      signal: controller.signal,
      redirect: "error",
    });
    const value = await response.json().catch(() => null);
    if (!response.ok) {
      const problem = value?.error;
      if (problem?.code === "CSRF_DENIED") csrfState = undefined;
      if (response.status === 401 && !path.startsWith("/auth/"))
        clearPrivateState();
      throw new ApiError(
        response.status,
        problem?.code ?? "UNAVAILABLE",
        problem?.message ?? "The service could not complete this request.",
        problem?.request_id ?? response.headers.get("X-Request-ID") ?? "",
        response.headers.get("Retry-After") ?? "",
        problem?.field_errors ?? [],
      );
    }
    if (started !== epoch)
      throw new DOMException("Workspace changed", "AbortError");
    if (method !== "GET" && path.startsWith("/auth/")) csrfState = undefined;
    return { data: value as T, etag: response.headers.get("ETag") };
  } catch (error) {
    if (
      error instanceof ApiError ||
      (error instanceof DOMException && error.name === "AbortError")
    )
      throw error;
    throw new ApiError(
      0,
      "CONNECTION_UNAVAILABLE",
      "Connection unavailable. No receipt was confirmed. Check your connection before deliberately retrying.",
    );
  } finally {
    clearTimeout(timer);
    pending.delete(controller);
    options.signal?.removeEventListener("abort", abort);
  }
}
// Serialize writes so a second CSRF bootstrap cannot invalidate an in-flight write.
let queue: Promise<unknown> = Promise.resolve();
export function api<T>(path: string, options: Options = {}) {
  if (!options.method || options.method === "GET")
    return transport<T>(path, options);
  const scope = epoch;
  const result = queue.then(() => {
    if (scope !== epoch)
      throw new DOMException("Workspace changed", "AbortError");
    return transport<T>(path, options);
  });
  queue = result.catch(() => undefined);
  return result;
}
export function date(value?: string | null) {
  if (!value || !Number.isFinite(Date.parse(value))) return "Not recorded";
  return `${new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(value))} IST`;
}
export function label(value: string) {
  return value
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/^./, (c) => c.toUpperCase());
}
