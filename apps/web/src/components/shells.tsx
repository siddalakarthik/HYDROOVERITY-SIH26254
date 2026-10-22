"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef, useState, type ReactNode } from "react";
import { Menu, X, ArrowUpRight, Droplets } from "lucide-react";

export function Wordmark() {
  return (
    <Link href="/" className="wordmark" aria-label="HYDROOVERITY home">
      HYDROOVERITY<span>Evidence before conclusions</span>
    </Link>
  );
}
export function PublicShell({
  children,
  home = false,
}: {
  children: ReactNode;
  home?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const menuButton = useRef<HTMLButtonElement>(null);
  const path = usePathname();
  return (
    <>
      <header className="site-header">
        <Wordmark />
        <button
          ref={menuButton}
          type="button"
          className="icon-button menu-toggle"
          aria-expanded={open}
          aria-controls="public-nav"
          aria-label={open ? "Close navigation" : "Open navigation"}
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
        <nav
          id="public-nav"
          aria-label="Main navigation"
          className={open ? "public-nav open" : "public-nav"}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              setOpen(false);
              menuButton.current?.focus();
            }
          }}
        >
          <Link
            href="/solution"
            aria-current={path === "/solution" ? "page" : undefined}
          >
            Solution
          </Link>
          <Link
            href="/how-it-works"
            aria-current={path === "/how-it-works" ? "page" : undefined}
          >
            How it works
          </Link>
          <Link
            href="/project-status"
            aria-current={path === "/project-status" ? "page" : undefined}
          >
            Project status
          </Link>
          <Link href="/login">Sign in</Link>
          <Link className="button" href="/report">
            Report a water issue
            <ArrowUpRight size={16} aria-hidden="true" />
          </Link>
        </nav>
      </header>
      <div className={home ? "public-frame home-frame" : "public-frame"}>
        {home && (
          <aside className="editorial-index" aria-label="On this page">
            <a href="#mission">The mission</a>
            <a href="#evidence">The evidence chain</a>
            <a href="#status">Current status</a>
            <a href="#residents">For residents</a>
            <div className="index-note">
              <Droplets aria-hidden="true" />
              <strong>Team TARK</strong>
              <span>SIH26254</span>
              <p>
                Investigating water loss with evidence and accountable
                maintenance.
              </p>
            </div>
          </aside>
        )}
        <main
          id="main"
          className={home ? "public-main home-main" : "public-main"}
        >
          {children}
        </main>
      </div>
      <footer className="site-footer">
        <span>HYDROOVERITY · Team TARK · SIH26254</span>
        <nav aria-label="Footer">
          <Link href="/benefits-and-limitations">Benefits and limitations</Link>
          <Link href="/contact">Contact</Link>
          <Link href="/privacy">Privacy</Link>
          <Link href="/terms">Terms</Link>
        </nav>
      </footer>
    </>
  );
}
