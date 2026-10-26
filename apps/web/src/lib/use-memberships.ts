"use client";
import { useEffect, useState } from "react";
import { api, ApiError, clearPrivateState, type Model, type Page } from "./api";

// A failed network/limit check is not evidence of revoked membership. Keep the
// last loaded view explicitly qualified; every mutation still needs server ACL.
export function useMemberships() {
  const [state, setState] = useState<{
    data?: Model<"MembershipView">[];
    error?: unknown;
    warning?: string;
    loading: boolean;
  }>({ loading: true });
  useEffect(() => {
    const controller = new AbortController();
    let signature = "";
    let inFlight = false;
    let retryAt = 0;
    let retry: ReturnType<typeof setTimeout> | undefined;
    const clear = () => {
      controller.abort();
      clearTimeout(retry);
      setState({
        loading: false,
        error: new ApiError(
          401,
          "SESSION_CHANGED",
          "Session or membership changed. Sign in to reload current access.",
        ),
      });
    };
    const load = async () => {
      if (controller.signal.aborted || inFlight || Date.now() < retryAt) return;
      inFlight = true;
      try {
        if (signature) await api("/me", { signal: controller.signal });
        const items: Model<"MembershipView">[] = [];
        let cursor: string | null = null;
        do {
          const response: {
            data: Page<Model<"MembershipView">>;
            etag: string | null;
          } = await api(
            `/me/memberships?limit=100${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`,
            { signal: controller.signal },
          );
          items.push(...response.data.items);
          cursor = response.data.next_cursor;
        } while (cursor);
        if (controller.signal.aborted) return;
        const current = JSON.stringify(items);
        if (signature && current !== signature) {
          clearPrivateState();
          return;
        }
        signature = current;
        setState({ data: items, loading: false });
      } catch (error) {
        if (controller.signal.aborted) return;
        if (
          error instanceof ApiError &&
          [401, 403, 404].includes(error.status)
        ) {
          clearPrivateState();
          return;
        }
        const transient =
          error instanceof ApiError &&
          (error.status === 0 || error.status === 429 || error.status >= 500);
        if (transient) {
          const seconds = error.status === 429 ? Number(error.retryAfter) : 0;
          const delay =
            Number.isFinite(seconds) && seconds > 0
              ? Math.max(1000, seconds * 1000)
              : 30000;
          retryAt = Date.now() + delay;
          clearTimeout(retry);
          retry = setTimeout(() => void load(), delay);
          setState((previous) =>
            previous.data
              ? {
                  ...previous,
                  warning:
                    "Membership recheck interrupted. Showing last loaded access; the server checks every action.",
                  loading: false,
                }
              : { error, loading: false },
          );
        } else setState({ error, loading: false });
      } finally {
        inFlight = false;
      }
    };
    window.addEventListener("hydro:scope-cleared", clear);
    window.addEventListener("focus", load);
    void load();
    const timer = setInterval(() => void load(), 30000);
    const onPageShow = (e: PageTransitionEvent) => {
      if (e.persisted) window.location.reload();
    };
    window.addEventListener("pageshow", onPageShow);
    return () => {
      controller.abort();
      clearTimeout(retry);
      clearInterval(timer);
      window.removeEventListener("hydro:scope-cleared", clear);
      window.removeEventListener("focus", load);
      window.removeEventListener("pageshow", onPageShow);
    };
  }, []);
  return state;
}
