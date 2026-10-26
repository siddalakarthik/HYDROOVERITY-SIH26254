import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RecordFrameParser, reconnectDelay } from "../src/lib/record-events";
import { RecordUpdates } from "../src/components/record-updates";
import {
  ResourceState,
  Select,
  Field,
  useResource,
} from "../src/components/ui";

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

it("shares one stream, refetches after a committed reset and aborts on scope clear", async () => {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const stream = new ReadableStream<Uint8Array>({
    start(c) {
      controller = c;
    },
  });
  const fetch = vi.fn().mockResolvedValue(
    new Response(stream, {
      headers: { "Content-Type": "text/event-stream" },
    }),
  );
  vi.stubGlobal("fetch", fetch);
  const refreshed = vi.fn();
  window.addEventListener("hydro:record-refresh", refreshed);
  const view = render(
    <RecordUpdates
      org="11111111-1111-4111-8111-111111111111"
      mode="OPERATIONAL"
    />,
  );
  try {
    const id = "b".repeat(64);
    controller.enqueue(
      new TextEncoder().encode(
        `event: reset_required\nid: ${id}\ndata: {}\n\nevent: checkpoint\nid: ${id}\ndata: {}\n\n`,
      ),
    );
    await waitFor(() =>
      expect(screen.getByRole("status").textContent).toContain(
        "Record updates connected",
      ),
    );
    await waitFor(() => expect(refreshed).toHaveBeenCalledTimes(1));
    expect(screen.getByRole("status").textContent).toContain(
      "does not establish physical sensor freshness",
    );
    expect(fetch).toHaveBeenCalledTimes(1);
    window.dispatchEvent(new Event("offline"));
    await waitFor(() =>
      expect(screen.getByRole("status").textContent).toContain(
        "Record updates disconnected",
      ),
    );
    window.dispatchEvent(new Event("hydro:scope-cleared"));
    expect(fetch.mock.calls[0][1].signal.aborted).toBe(true);
  } finally {
    controller.close();
    view.unmount();
    window.removeEventListener("hydro:record-refresh", refreshed);
  }
});
