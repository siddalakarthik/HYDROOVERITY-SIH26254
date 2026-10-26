"use client";
import { useEffect, useState, type ReactNode } from "react";
import { clearPrivateState, orgPath } from "@/lib/api";
import {
  RecordFrameParser,
  reconnectDelay,
  recordFamilies,
  RecordSnapshotReady,
} from "@/lib/record-events";

export function RecordUpdates({
  org,
  mode,
  children,
}: {
  org: string;
  mode: "OPERATIONAL" | "SIMULATION";
  children?: ReactNode;
}) {
  const [snapshotReady, setSnapshotReady] = useState(false);
  const [status, setStatus] = useState("Checking record updates");
  useEffect(() => {
    const controller = new AbortController();
    let stopped = false;
    let cursor: string | undefined;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let refreshTimer: ReturnType<typeof setTimeout> | undefined;
    let failures = 0;
    let active: AbortController | undefined;
    let inFlight = false;
    let hasSnapshot = false;
    let lastRefresh = Number.NEGATIVE_INFINITY;
    let pendingFamilies: Set<string> | undefined = new Set();
    const seen = new Set<string>();
    const refresh = (affected?: string[]) => {
      if (!affected) pendingFamilies = undefined;
      else if (pendingFamilies)
        affected.forEach((family) => pendingFamilies!.add(family));
      if (refreshTimer || stopped) return;
      refreshTimer = setTimeout(
        () => {
          refreshTimer = undefined;
          if (!stopped) {
            lastRefresh = Date.now();
            const detail = {
              families: pendingFamilies ? [...pendingFamilies] : undefined,
            };
            pendingFamilies = new Set();
            window.dispatchEvent(
              new CustomEvent("hydro:record-refresh", { detail }),
            );
          }
        },
        Math.max(250, 5000 - (Date.now() - lastRefresh)),
      );
    };
    const clear = () => {
      stopped = true;
      controller.abort();
      active?.abort();
      clearTimeout(timer);
      clearTimeout(refreshTimer);
      seen.clear();
      cursor = undefined;
    };
    const address = `/api/v1${orgPath(org, "/events")}`;
    const stopForAccess = () => {
      setSnapshotReady(false);
      clear();
      clearPrivateState();
    };
    const connect = async () => {
      if (stopped || inFlight) return;
      inFlight = true;
      active = new AbortController();
      let intentionalReconnect = false;
      let retryFloor = 0;
      try {
        const headers = new Headers({ Accept: "text/event-stream" });
        if (cursor) headers.set("Last-Event-ID", cursor);
        const response = await fetch(`${address}?workspace_mode=${mode}`, {
          credentials: "same-origin",
          cache: "no-store",
          redirect: "error",
          signal: active.signal,
          headers,
        });
        if (
          response.status === 401 ||
          response.status === 403 ||
          response.status === 404
        ) {
          stopForAccess();
          return;
        }
        if (response.status === 429) {
          const seconds = Number(response.headers.get("Retry-After"));
          if (Number.isFinite(seconds) && seconds > 0)
            retryFloor = seconds * 1000;
        }
        if (
          !response.ok ||
          !response.body ||
          !response.headers.get("Content-Type")?.startsWith("text/event-stream")
        )
          throw new Error("Record updates unavailable");
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8", { fatal: true });
        const parser = new RecordFrameParser();
        try {
          while (!stopped) {
            const idle = setTimeout(() => void reader.cancel(), 35000);
            let chunk: ReadableStreamReadResult<Uint8Array>;
            try {
              chunk = await reader.read();
            } finally {
              clearTimeout(idle);
            }
            const { done, value } = chunk;
            if (done) break;
            for (const frame of parser.push(
              decoder.decode(value, { stream: true }),
            )) {
              if (stopped) return;
              if (frame.event === "authorization_lost") {
                stopForAccess();
                return;
              }
              if (frame.event === "reset_required") {
                // Server has committed the watermark before these snapshots begin.
                cursor = frame.id;
                seen.clear();
                if (hasSnapshot) refresh();
                else {
                  hasSnapshot = true;
                  setSnapshotReady(true);
                }
                setStatus("Refreshing authorized records");
              } else if (frame.event === "record_changed") {
                const data = frame.data as {
                  id?: unknown;
                  workspace_mode?: unknown;
                  event_type?: unknown;
                };
                if (
                  typeof data?.id !== "string" ||
                  data.workspace_mode !== mode
                )
                  throw new Error("Invalid record update");
                if (!seen.has(data.id)) {
                  if (seen.size >= 1000)
                    seen.delete(seen.values().next().value!);
                  seen.add(data.id);
                  refresh(recordFamilies(data.event_type));
                }
                if (frame.id) cursor = frame.id;
              } else if (frame.event === "checkpoint") {
                if (!frame.id) throw new Error("Missing record checkpoint");
                cursor = frame.id;
                failures = 0;
                setStatus("Record updates connected");
              } else if (frame.event === "reconnect_required") {
                intentionalReconnect = true;
                setStatus("Reconnecting record updates");
              }
            }
          }
        } finally {
          await reader.cancel().catch(() => undefined);
          reader.releaseLock();
        }
        if (!intentionalReconnect) throw new Error("Record connection ended");
      } catch {
        if (stopped || controller.signal.aborted) return;
        failures += 1;
        setStatus("Record updates disconnected · showing last loaded records");
        // A full stream slot must not prevent ordinary authorized snapshots.
        // The short history request commits the same watermark before children
        // start fetching; no duplicate speculative snapshot is necessary.
        if (!hasSnapshot && !retryFloor && !active.signal.aborted) {
          const deadline = setTimeout(() => active?.abort(), 20000);
          try {
            const response = await fetch(
              `${address}/history?workspace_mode=${mode}`,
              {
                credentials: "same-origin",
                cache: "no-store",
                redirect: "error",
                signal: active.signal,
              },
            );
            if ([401, 403, 404].includes(response.status)) {
              stopForAccess();
              return;
            }
            if (response.status === 429) {
              const seconds = Number(response.headers.get("Retry-After"));
              if (Number.isFinite(seconds) && seconds > 0)
                retryFloor = seconds * 1000;
            }
            const page = response.ok ? await response.json() : undefined;
            if (
              typeof page?.next_cursor === "string" &&
              /^[a-f0-9]{64}$/.test(page.next_cursor)
            ) {
              cursor = page.next_cursor;
              hasSnapshot = true;
              setSnapshotReady(true);
            }
          } catch {
            /* Stay visibly disconnected; reconnect is bounded below. */
          } finally {
            clearTimeout(deadline);
          }
        }
      } finally {
        inFlight = false;
      }
      if (!stopped)
        timer = setTimeout(
          () => void connect(),
          Math.max(
            retryFloor,
            reconnectDelay(intentionalReconnect ? 0 : failures - 1),
          ),
        );
    };
    const offline = () => {
      active?.abort();
      setStatus("Record updates disconnected · showing last loaded records");
    };
    const online = () => {
      clearTimeout(timer);
      void connect();
    };
    window.addEventListener("hydro:scope-cleared", clear);
    window.addEventListener("offline", offline);
    window.addEventListener("online", online);
    const poll = setInterval(() => refresh(), 30000);
    void connect();
    return () => {
      clear();
      clearInterval(poll);
      window.removeEventListener("hydro:scope-cleared", clear);
      window.removeEventListener("offline", offline);
      window.removeEventListener("online", online);
    };
  }, [org, mode]);
  return (
    <RecordSnapshotReady.Provider value={snapshotReady}>
      <p className="help" role="status">
        {status}. Record connectivity does not establish physical sensor
        freshness.
      </p>
      {children}
    </RecordSnapshotReady.Provider>
  );
}
