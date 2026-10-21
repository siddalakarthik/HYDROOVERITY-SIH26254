import { notFound } from "next/navigation";
import { PublicPage } from "@/features/public";
import { AuthPage, AccountPage } from "@/features/auth";
import { Workspace } from "@/features/workspace";

const publicRoutes = new Set([
  "solution",
  "how-it-works",
  "solution/guard5",
  "solution/acoustics",
  "benefits-and-limitations",
  "project-status",
  "report",
  "contact",
  "privacy",
  "terms",
]);
const authRoutes = new Set([
  "login",
  "register",
  "forgot-password",
  "reset-password",
  "verify-account",
  "accept-invitation",
]);
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ segments: string[] }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { segments } = await params;
  const route = segments.join("/");
  if (publicRoutes.has(route)) return <PublicPage path={`/${route}`} />;
  if (authRoutes.has(route)) {
    const query = await searchParams;
    const utility =
      typeof query.utility === "string" &&
      /^[a-z0-9-]{1,80}$/.test(query.utility)
        ? query.utility
        : "";
    return (
      <AuthPage
        mode={route}
        utility={utility}
        logoutUnconfirmed={query.logout === "unconfirmed"}
      />
    );
  }
  if (route === "account" || route === "account/sessions")
    return <AccountPage sessions={route.endsWith("sessions")} />;
  if (segments[0] === "app" || segments[0] === "citizen")
    return <Workspace segments={segments} />;
  notFound();
}
