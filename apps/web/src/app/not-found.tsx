import Link from "next/link";
import { PublicShell } from "@/components/shells";
export default function NotFound() {
  return (
    <PublicShell>
      <h1>Page unavailable</h1>
      <p>This route is not available in the current application.</p>
      <Link className="button" href="/">
        Return home
      </Link>
    </PublicShell>
  );
}
