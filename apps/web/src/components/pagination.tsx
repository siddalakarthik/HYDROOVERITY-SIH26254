"use client";
import { useState } from "react";
import { type Page } from "@/lib/api";
import { useResource, Freshness } from "./ui";

export function usePage<T>(base: string | null) {
  const [navigation, setNavigation] = useState<{
    base: string | null;
    cursors: string[];
  }>({ base, cursors: [] });
  const cursors = navigation.base === base ? navigation.cursors : [];
  const cursor = cursors.at(-1);
  const resource = useResource<Page<T>>(
    base
      ? `${base}${base.includes("?") ? "&" : "?"}limit=50${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`
      : null,
  );
  return {
    ...resource,
    previous: () => setNavigation({ base, cursors: cursors.slice(0, -1) }),
    next: () => {
      if (resource.data?.next_cursor)
        setNavigation({
          base,
          cursors: [...cursors, resource.data.next_cursor],
        });
    },
    hasPrevious: cursors.length > 0,
    page: cursors.length + 1,
  };
}
export function Pager<T>({
  data,
  hasPrevious,
  previous,
  next,
  page,
}: {
  data?: Page<T>;
  hasPrevious: boolean;
  previous: () => void;
  next: () => void;
  page: number;
}) {
  if (!data) return null;
  return (
    <>
      <Freshness at={data.as_of} />
      <div className="actions" aria-label="Pagination">
        <button
          className="button secondary"
          disabled={!hasPrevious}
          onClick={previous}
        >
          Previous page
        </button>
        <span className="meta">
          Page {page} · {data.items.length} records on this page
        </span>
        <button
          className="button secondary"
          disabled={!data.next_cursor}
          onClick={next}
        >
          Next page
        </button>
      </div>
    </>
  );
}
