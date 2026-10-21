"use client";
import Link from "next/link";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main id="main" className="public-main">
      <h1>This page could not be loaded</h1>
      <p>
        No action receipt was confirmed. Retry loading the page or return to
        your workspace.
      </p>
      <button className="button" onClick={reset}>
        Retry page
      </button>
      <Link href="/account">My account</Link>
    </main>
  );
}
