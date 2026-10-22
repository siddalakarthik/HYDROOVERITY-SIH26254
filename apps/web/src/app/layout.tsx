import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "HYDROOVERITY · Evidence before conclusions",
    template: "%s · HYDROOVERITY",
  },
  description:
    "A proposed evidence-qualified water-infrastructure investigation and maintenance system. Team TARK · SIH26254.",
  robots: { index: false, follow: false },
};
export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  await headers(); // Per-request CSP nonce; no static private-page cache.
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        {children}
      </body>
    </html>
  );
}
