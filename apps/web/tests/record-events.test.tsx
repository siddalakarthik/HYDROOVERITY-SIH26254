import {
  act,
  fireEvent,
  render,
  renderHook,
  screen,
  waitFor,
} from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import {
  RecordFrameParser,
  reconnectDelay,
  recordAffects,
  recordFamilies,
} from "../src/lib/record-events";
import { RecordUpdates } from "../src/components/record-updates";
import { useMemberships } from "../src/lib/use-memberships";
import {
  ResourceState,
  Select,
  Field,
  useResource,
} from "../src/components/ui";

it("recovers an initial membership throttle only after Retry-After", async () => {
  vi.useFakeTimers();
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          error: { code: "RATE_LIMITED", message: "SYNTHETIC limit" },
        }),
        { status: 429, headers: { "Retry-After": "2" } },
      ),
    )
    .mockResolvedValue(
      new Response(JSON.stringify({ items: [], next_cursor: null })),
    );
  vi.stubGlobal("fetch", fetch);
  const view = renderHook(() => useMemberships());
  try {
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(view.result.current.error).toBeTruthy();
    expect(view.result.current.data).toBeUndefined();
    await act(async () => {
      window.dispatchEvent(new Event("focus"));
      await vi.advanceTimersByTimeAsync(1999);
    });
    expect(fetch).toHaveBeenCalledTimes(1);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1);
    });
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(view.result.current.error).toBeUndefined();
    expect(view.result.current.data).toEqual([]);
  } finally {
    view.unmount();
    vi.useRealTimers();
  }
});

it("qualifies last loaded membership on a transient recheck and purges it on real denial", async () => {
  vi.useFakeTimers();
  let status = 200;
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockImplementation((url: string) =>
        Promise.resolve(
          new Response(
            JSON.stringify(
              status === 200
                ? url.includes("memberships")
                  ? { items: [], next_cursor: null }
                  : {}
                : { error: { code: "SYNTHETIC_FAILURE" } },
            ),
            { status, headers: status === 429 ? { "Retry-After": "2" } : {} },
          ),
        ),
      ),
  );
  const view = renderHook(() => useMemberships());
  try {
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
    });
    status = 429;
    await act(async () => {
      window.dispatchEvent(new Event("focus"));
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(view.result.current.data).toEqual([]);
    expect(view.result.current.warning).toContain("last loaded access");
    status = 200;
    await act(async () => {
      await vi.advanceTimersByTimeAsync(2000);
    });
    expect(view.result.current.warning).toBeUndefined();
    status = 403;
    await act(async () => {
      window.dispatchEvent(new Event("focus"));
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(view.result.current.data).toBeUndefined();
    expect(view.result.current.error).toBeTruthy();
  } finally {
    view.unmount();
    vi.useRealTimers();
  }
});

it("coalesces an event burst without repeated whole-page refetches", async () => {
  vi.useFakeTimers();
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const stream = new ReadableStream<Uint8Array>({
    start(c) {
      controller = c;
    },
  });
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(stream, {
        headers: { "Content-Type": "text/event-stream" },
      }),
    ),
  );
  const refreshed = vi.fn();
  window.addEventListener("hydro:record-refresh", refreshed);
  const view = render(
    <RecordUpdates
      org="11111111-1111-4111-8111-111111111111"
      mode="OPERATIONAL"
    />,
  );
  const emit = (i: number) =>
    controller.enqueue(
      new TextEncoder().encode(
        `event: record_changed\nid: ${"b".repeat(64)}\ndata: {"id":"synthetic-${i}","workspace_mode":"OPERATIONAL","event_type":"record_changed.citizen_complaints"}\n\n`,
      ),
    );
  try {
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
      emit(0);
      await vi.advanceTimersByTimeAsync(250);
    });
    expect(refreshed).toHaveBeenCalledTimes(1);
    await act(async () => {
      for (let i = 1; i <= 10; i++) emit(i);
      await vi.advanceTimersByTimeAsync(4999);
    });
    expect(refreshed).toHaveBeenCalledTimes(1);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1);
    });
    expect(refreshed).toHaveBeenCalledTimes(2);
  } finally {
    view.unmount();
    controller.close();
    window.removeEventListener("hydro:record-refresh", refreshed);
    vi.useRealTimers();
  }
});

it("retains drafts on transient refresh failure but purges records on current access denial", async () => {
  let status = 200;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(() =>
      Promise.resolve(
        new Response(
          JSON.stringify(
            status === 200
              ? { version: 1 }
              : {
                  error: {
                    code: "SYNTHETIC_FAILURE",
                    message: "SYNTHETIC refresh rejected",
                  },
                },
          ),
          { status },
        ),
      ),
    ),
  );
  function Form() {
    const resource = useResource<{ version: number }>(
      "/synthetic-private-record",
    );
    return (
      <ResourceState {...resource}>
        <Field name="draft" label="Private draft" />
      </ResourceState>
    );
  }
  render(<Form />);
  const draft = await screen.findByLabelText("Private draft");
  fireEvent.change(draft, { target: { value: "SYNTHETIC unsent draft" } });
  status = 503;
  window.dispatchEvent(new Event("hydro:record-refresh"));
  await screen.findByText("Refresh failed. Showing the last loaded records.");
  expect(screen.getByLabelText("Private draft")).toBe(draft);
  expect((draft as HTMLInputElement).value).toBe("SYNTHETIC unsent draft");
  status = 403;
  window.dispatchEvent(new Event("hydro:record-refresh"));
  await waitFor(() =>
    expect(screen.queryByLabelText("Private draft")).toBeNull(),
  );
  expect(screen.getByRole("alert")).toBeTruthy();
});

describe("bounded record frames", () => {
  it("reassembles fragments and ignores heartbeat comments", () => {
    const parser = new RecordFrameParser();
    expect(parser.push(": heartbeat\n\nevent: check")).toEqual([]);
    expect(
      parser.push(
        `point\nid: ${"a".repeat(64)}\ndata: {"cursor":"opaque"}\n\n`,
      ),
    ).toEqual([
      { event: "checkpoint", id: "a".repeat(64), data: { cursor: "opaque" } },
    ]);
  });
  it("rejects oversized frames, invalid cursors and malformed data", () => {
    expect(() =>
      new RecordFrameParser().push("x".repeat(256 * 1024 + 1)),
    ).toThrow();
    expect(() =>
      new RecordFrameParser().push("id: 123\ndata: {}\n\n"),
    ).toThrow();
    expect(() => new RecordFrameParser().push("data: {broken}\n\n")).toThrow();
    expect(() =>
      new RecordFrameParser().push("data: {}\n\n".repeat(101)),
    ).toThrow();
  });
  it("uses bounded jitter rather than immediate failure loops", () => {
    expect(reconnectDelay(0, 1)).toBe(1000);
    expect(reconnectDelay(100, 1)).toBe(30000);
    expect(reconnectDelay(3, 0)).toBe(6000);
  });
});

it("background snapshots preserve selected category, typing and mounted input identity", async () => {
  const fetch = vi
    .fn()
    .mockImplementation(() =>
      Promise.resolve(
        new Response(JSON.stringify({ version: fetch.mock.calls.length })),
      ),
    );
  vi.stubGlobal("fetch", fetch);
  function Form() {
    const state = useResource<{ version: number }>("/synthetic-record");
    return (
      <ResourceState {...state}>
        <Select
          name="category"
          label="Service category"
          options={[{ value: "VISIBLE_LEAK", label: "Visible leak" }]}
        />
        <Field name="description" label="Issue description" />
        <p>Record version {state.data?.version}</p>
      </ResourceState>
    );
  }
  render(<Form />);
  const category = await screen.findByLabelText("Service category");
  const description = screen.getByLabelText("Issue description");
  fireEvent.change(category, { target: { value: "VISIBLE_LEAK" } });
  fireEvent.change(description, {
    target: { value: "SYNTHETIC draft survives refresh" },
  });
  description.focus();
  window.dispatchEvent(new Event("hydro:record-refresh"));
  await waitFor(() =>
    expect(screen.getByText("Record version 2")).toBeTruthy(),
  );
  expect(screen.getByLabelText("Service category")).toBe(category);
  expect((category as HTMLSelectElement).value).toBe("VISIBLE_LEAK");
  expect((description as HTMLInputElement).value).toBe(
    "SYNTHETIC draft survives refresh",
  );
  expect(document.activeElement).toBe(description);
});

it("fetches one snapshot only after the committed stream barrier, then refetches on reset", async () => {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const stream = new ReadableStream<Uint8Array>({
    start(c) {
      controller = c;
    },
  });
  const fetch = vi.fn().mockImplementation((url: string) =>
    Promise.resolve(
      url.includes("/events?")
        ? new Response(stream, {
            headers: { "Content-Type": "text/event-stream" },
          })
        : new Response(JSON.stringify({ version: 1 })),
    ),
  );
  vi.stubGlobal("fetch", fetch);
  function Snapshot() {
    const resource = useResource<{ version: number }>(
      "/orgs/11111111-1111-4111-8111-111111111111/complaints",
    );
    return (
      <p data-testid="snapshot">
        {resource.data?.version ?? "Waiting for barrier"}
      </p>
    );
  }
  const refreshed = vi.fn();
  window.addEventListener("hydro:record-refresh", refreshed);
  const view = render(
    <RecordUpdates
      org="11111111-1111-4111-8111-111111111111"
      mode="OPERATIONAL"
    >
      <Snapshot />
    </RecordUpdates>,
  );
  try {
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(screen.getByTestId("snapshot").textContent).toBe(
      "Waiting for barrier",
    );
    const emit = () =>
      controller.enqueue(
        new TextEncoder().encode(
          `event: reset_required\nid: ${"b".repeat(64)}\ndata: {}\n\nevent: checkpoint\nid: ${"b".repeat(64)}\ndata: {}\n\n`,
        ),
      );
    emit();
    await waitFor(() =>
      expect(screen.getByTestId("snapshot").textContent).toBe("1"),
    );
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(refreshed).not.toHaveBeenCalled();
    emit();
    await waitFor(() => expect(refreshed).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(3));
    expect(screen.getByRole("status").textContent).toContain(
      "does not establish physical sensor freshness",
    );
    window.dispatchEvent(new Event("offline"));
    await waitFor(() =>
      expect(screen.getByRole("status").textContent).toContain(
        "Record updates disconnected",
      ),
    );
    window.dispatchEvent(new Event("hydro:scope-cleared"));
    expect(fetch.mock.calls[0][1].signal.aborted).toBe(true);
  } finally {
    view.unmount();
    controller.close();
    window.removeEventListener("hydro:record-refresh", refreshed);
  }
});

it("uses the committed history barrier when stream capacity is unavailable", async () => {
  const fetch = vi
    .fn()
    .mockImplementation((url: string) =>
      Promise.resolve(
        new Response(
          JSON.stringify(
            url.includes("/history?")
              ? { next_cursor: "c".repeat(64) }
              : url.includes("/events?")
                ? { error: { code: "STREAM_CAPACITY" } }
                : { version: 2 },
          ),
          { status: url.includes("/events?") ? 503 : 200 },
        ),
      ),
    );
  vi.stubGlobal("fetch", fetch);
  function Snapshot() {
    const resource = useResource<{ version: number }>(
      "/orgs/11111111-1111-4111-8111-111111111111/complaints",
    );
    return <p data-testid="snapshot">{resource.data?.version ?? "Waiting"}</p>;
  }
  const view = render(
    <RecordUpdates
      org="11111111-1111-4111-8111-111111111111"
      mode="OPERATIONAL"
    >
      <Snapshot />
    </RecordUpdates>,
  );
  try {
    await waitFor(() =>
      expect(screen.getByTestId("snapshot").textContent).toBe("2"),
    );
    expect(fetch.mock.calls.map((args) => args[0])).toEqual([
      expect.stringContaining("/events?"),
      expect.stringContaining("/events/history?"),
      expect.stringContaining("/complaints"),
    ]);
    expect(screen.getByRole("status").textContent).toContain(
      "Record updates disconnected",
    );
  } finally {
    view.unmount();
  }
});

it("invalidates only authorized affected resource families", () => {
  const org = "/orgs/11111111-1111-4111-8111-111111111111";
  const families = recordFamilies("record_changed.citizen_complaints");
  expect(recordAffects(`${org}/complaints?limit=50`, families)).toBe(true);
  expect(recordAffects(`${org}/work-orders/record`, families)).toBe(false);
  expect(recordAffects(org)).toBe(false);
  expect(
    recordAffects(
      `${org}/repairs/record/verifications`,
      recordFamilies("record_changed.verification_records"),
    ),
  ).toBe(true);
  expect(() =>
    recordFamilies("record_changed.restricted_simulation_truth"),
  ).toThrow();
});
