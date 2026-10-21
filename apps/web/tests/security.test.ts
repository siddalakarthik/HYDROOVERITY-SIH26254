import { afterEach, describe, expect, it, vi } from "vitest";
import {
  api,
  ApiError,
  clearPrivateState,
  date,
  mutationIdentity,
  orgPath,
  query,
  uuid,
} from "../src/lib/api";
import {
  lineCoordinates,
  position,
  featureCollection,
} from "../src/lib/geometry";
const id = "00000000-0000-4000-8000-000000000001";
const json = (
  body: unknown,
  status = 200,
  headers: Record<string, string> = {},
) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
afterEach(() => clearPrivateState());
describe("Safe API request boundaries", () => {
  it("rejects invalid identifiers and external destinations before fetch", async () => {
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);
    expect(() => uuid("../other")).toThrow(ApiError);
    expect(() => orgPath("bad")).toThrow(ApiError);
    await expect(api("https://example.invalid")).rejects.toThrow(
      "Invalid API path",
    );
    expect(fetch).not.toHaveBeenCalled();
    expect(orgPath(id, "/pipes")).toBe(`/orgs/${id}/pipes`);
  });
  it("encodes cursors and preserves explicit filter scope", () =>
    expect(query({ cursor: "a+/=", status: "NEW", empty: undefined })).toBe(
      "?cursor=a%2B%2F%3D&status=NEW",
    ));
  it("reuses only identical business mutation identities", () => {
    const first = mutationIdentity(undefined, "POST", "/complaints", [
      1,
      { description: "same" },
    ]);
    expect(
      mutationIdentity(first, "POST", "/complaints", [
        1,
        { description: "same" },
      ]),
    ).toBe(first);
    expect(
      mutationIdentity(first, "POST", "/complaints", [
        2,
        { description: "same" },
      ]).key,
    ).not.toBe(first.key);
    expect(
      mutationIdentity(first, "POST", "/complaints", [
        1,
        { description: "changed" },
      ]).key,
    ).not.toBe(first.key);
  });
  it("bootstraps CSRF and forwards exact version and business key without readable session tokens", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(json({ csrf_token: "test-only-csrf" }))
      .mockResolvedValueOnce(json({ id }, 201));
    vi.stubGlobal("fetch", fetch);
    await api(`/orgs/${id}/complaints`, {
      method: "POST",
      key: id,
      version: 3,
      body: { description: "test" },
    });
    const [path, options] = fetch.mock.calls[1];
    expect(path).toBe(`/api/v1/orgs/${id}/complaints`);
    expect(options.credentials).toBe("same-origin");
    expect(options.cache).toBe("no-store");
    expect(options.headers.get("X-CSRF-Token")).toBe("test-only-csrf");
    expect(options.headers.get("If-Match")).toBe('"3"');
    expect(options.headers.get("Idempotency-Key")).toBe(id);
    expect(options.headers.has("Cookie")).toBe(false);
  });
  it("does not attach idempotency to authentication or global writes", async () => {
    const fetch = vi
      .fn()
      .mockImplementation(() =>
        Promise.resolve(json({ csrf_token: "test-only", message: "ok" })),
      );
    vi.stubGlobal("fetch", fetch);
    await api("/auth/logout", { method: "POST" });
    expect(fetch.mock.calls[1][1].headers.has("Idempotency-Key")).toBe(false);
  });
  it("normalizes version conflicts and retry-after without automatic replay", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(json({ csrf_token: "test-only" }))
      .mockResolvedValueOnce(
        json(
          {
            error: {
              code: "VERSION_CONFLICT",
              message: "Refetch current record",
              request_id: id,
              field_errors: [],
            },
          },
          412,
          { "Retry-After": "60" },
        ),
      );
    vi.stubGlobal("fetch", fetch);
    await expect(
      api("/me", {
        method: "PATCH",
        version: 1,
        body: { display_name: "Test" },
      }),
    ).rejects.toMatchObject({
      status: 412,
      code: "VERSION_CONFLICT",
      requestId: id,
      retryAfter: "60",
    });
    expect(fetch).toHaveBeenCalledTimes(2);
  });
  it("rejects stale read results after a scope switch", async () => {
    let resolve: (value: Response) => void = () => undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn(
        () =>
          new Promise<Response>((r) => {
            resolve = r;
          }),
      ),
    );
    const request = api("/me");
    clearPrivateState();
    resolve(json({ id }));
    await expect(request).rejects.toMatchObject({ name: "AbortError" });
  });
  it("prevents a queued old-workspace write from executing after a scope switch", async () => {
    let finish: (value: Response) => void = () => undefined;
    const fetch = vi.fn(
      () =>
        new Promise<Response>((r) => {
          finish = r;
        }),
    );
    vi.stubGlobal("fetch", fetch);
    const first = api("/auth/logout", { method: "POST" });
    const second = api("/me", {
      method: "PATCH",
      body: { display_name: "Other" },
    });
    await Promise.resolve();
    clearPrivateState();
    finish(json({ csrf_token: "old" }));
    await expect(first).rejects.toMatchObject({ name: "AbortError" });
    await expect(second).rejects.toMatchObject({ name: "AbortError" });
    expect(fetch).toHaveBeenCalledTimes(1);
  });
  it("rejects oversized bodies before sending private content", async () => {
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);
    await expect(
      api("/me", {
        method: "PATCH",
        body: { display_name: "x".repeat(17000) },
      }),
    ).rejects.toMatchObject({ status: 413 });
    expect(fetch).not.toHaveBeenCalled();
  });
});
describe("Geographic and scientific presentation", () => {
  it("uses longitude then latitude and rejects invalid or nonfinite coordinates", () => {
    expect(position(78, 17)).toEqual([78, 17]);
    expect(() => position(181, 17)).toThrow(ApiError);
    expect(() => position(78, 91)).toThrow(ApiError);
    expect(() => position(NaN, 17)).toThrow(ApiError);
  });
  it("retains entered geometry rather than fabricating path connectivity", () => {
    expect(lineCoordinates("78,17\n78.1,17.2")).toEqual([
      [78, 17],
      [78.1, 17.2],
    ]);
    expect(() => lineCoordinates("78,17")).toThrow(ApiError);
    expect(() => lineCoordinates(",17\n78,18")).toThrow(ApiError);
    expect(featureCollection([], []).features).toEqual([]);
  });
  it("formats UTC records in India time without inventing missing observations", () => {
    expect(date("2026-10-21T00:00:00Z")).toContain("05:30");
    expect(date("bad")).toBe("Not recorded");
    expect(date(null)).toBe("Not recorded");
  });
});
