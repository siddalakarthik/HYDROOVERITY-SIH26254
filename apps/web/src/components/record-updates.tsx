"use client";
import { useEffect, useState } from "react";
import { clearPrivateState, orgPath } from "@/lib/api";
import { RecordFrameParser, reconnectDelay } from "@/lib/record-events";

export function RecordUpdates({
  org,
  mode,
}: {
  org: string;
  mode: "OPERATIONAL" | "SIMULATION";
}) {
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
    const seen = new Set<string>();
    const refresh = () => {
      if (refreshTimer || stopped) return;
      refreshTimer = setTimeout(() => {
        refreshTimer = undefined;
        if (!stopped) window.dispatchEvent(new Event("hydro:record-refresh"));
      }, 250);
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
                refresh();
                setStatus("Refreshing authorized records");
              } else if (frame.event === "record_changed") {
                const data = frame.data as {
                  id?: unknown;
                  workspace_mode?: unknown;
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
                  refresh();
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
    const poll = setInterval(refresh, 30000);
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
    <p className="help" role="status">
      {status}. Record connectivity does not establish physical sensor
      freshness.
    </p>
  );
}
