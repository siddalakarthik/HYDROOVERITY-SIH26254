import Link from "next/link";
import Image from "next/image";
import { ArrowRight, FileText, ShieldCheck } from "lucide-react";
import { PublicShell } from "@/components/shells";
import { Architecture } from "@/components/architecture";
import { Notice, Heading } from "@/components/ui";
import { PublicStatus, UtilityLookup } from "./public-data";

export function Home() {
  return (
    <PublicShell home>
      <section id="mission" className="mission">
        <div>
          <p className="eyebrow">Water infrastructure · Proposed system</p>
          <h1>
            Find the leak.
            <br />
            Understand the evidence.
            <br />
            Verify the repair.
          </h1>
          <p className="lede">
            Bring observations, investigation and maintenance into one
            accountable record.
          </p>
          <div className="actions">
            <Link className="button" href="/how-it-works">
              How it works
              <ArrowRight size={17} aria-hidden="true" />
            </Link>
            <Link className="button secondary" href="/report">
              Report a water issue
            </Link>
          </div>
        </div>
        <section id="status" className="project-state">
          <h2>
            Project status <span>(development stage)</span>
          </h2>
          <dl>
            <div>
              <dt>Backend foundation</dt>
              <dd>Implemented</dd>
            </div>
            <div>
              <dt>Scientific models</dt>
              <dd>Simulation only</dd>
            </div>
            <div>
              <dt>Hardware designs</dt>
              <dd>Digital only</dd>
            </div>
            <div>
              <dt>Physical validation</dt>
              <dd className="caution">Pending</dd>
            </div>
          </dl>
          <p>
            This is a proposed system in development. Hardware connection and
            field validation remain pending.
          </p>
        </section>
      </section>
      <section id="evidence" className="evidence-section">
        <h2>Evidence before conclusions</h2>
        <p>
          Independent observations support an investigation. Their quality and
          limits govern what can be concluded about a leak or its repair.
        </p>
        <Architecture />
      </section>
      <section id="residents" className="two-stories">
        <article>
          <FileText aria-hidden="true" />
          <div>
            <h2>A report starts an investigation.</h2>
            <p>
              Describe an unusual flow, wet area or service problem. Follow your
              own report through your utility.
            </p>
            <Link href="/report">
              Start a report
              <ArrowRight size={16} aria-hidden="true" />
            </Link>
          </div>
        </article>
        <article>
          <ShieldCheck aria-hidden="true" />
          <div>
            <h2>A completed task is not proof of repair.</h2>
            <p>
              Independent evidence must support the conclusion. An outcome may
              remain not verifiable.
            </p>
            <Link href="/benefits-and-limitations">
              Read benefits and limitations
              <ArrowRight size={16} aria-hidden="true" />
            </Link>
          </div>
        </article>
      </section>
      <Notice tone="warning">
        <strong>Hardware validation pending.</strong> Simulation and digital
        design do not establish field performance.
      </Notice>
    </PublicShell>
  );
}
const editorial: Record<
  string,
  { title: string; lead: string; sections: [string, string][]; image?: string }
> = {
  "/solution": {
    title: "One evidence chain. Accountable decisions.",
    lead: "HYDROOVERITY proposes a practical link between hydraulic context, local wetness, eligible-span acoustics and maintenance records.",
    sections: [
      [
        "Observe the context",
        "HYDRO-WATCH uses pressure and flow to qualify supply state. GUARD-5 investigates wetness at exposed joints. HYDRO-EAR investigates suitable surveyed spans.",
      ],
      [
        "Qualify before acting",
        "Observations retain their source, quality, faults and competing explanations. A wet collar or hydraulic imbalance alone does not prove a leak.",
      ],
      [
        "Investigate, repair, review",
        "Authorized teams can review reports, create incidents, assign work and record repairs. Independent review separates work completion from demonstrated effectiveness.",
      ],
    ],
  },
  "/how-it-works": {
    title: "From concern to a defensible outcome",
    lead: "A clear process for residents and utility teams, with room for uncertainty at every step.",
    sections: [
      [
        "1 · Report or observe",
        "A resident signs in to an enabled utility and describes the problem in a rough area. No precise home coordinates are required.",
      ],
      [
        "2 · Review the concern",
        "A supervisor reviews the report and may link it to an operational incident. A report is a concern, not a confirmed sensor detection.",
      ],
      [
        "3 · Assign and investigate",
        "A supervisor assigns a work order. The current technician can accept it, record findings and submit a repair receipt while online.",
      ],
      [
        "4 · Review independently",
        "An independent authorized reviewer assesses the evidence. Current manual records cannot establish comparable measured performance; verification remains NOT_VERIFIABLE.",
      ],
      [
        "5 · Keep the history",
        "Public-safe updates remain separate from private investigation notes. New evidence can reopen an investigation without erasing earlier decisions.",
      ],
    ],
  },
  "/solution/guard5": {
    title: "GUARD-5: five channels, different jobs",
    lead: "A proposed removable, non-pressure-bearing collar for an accessible exposed joint. Digital geometry has been checked; physical collector performance remains unverified.",
    image: "guard5.png",
    sections: [
      [
        "COLLAR_A · COLLAR_B · COLLAR_C",
        "Three independent protected collection pockets are intended to observe local water arrival. Manufactured separation and crosstalk still require physical tests.",
      ],
      [
        "COLLAR_EXT",
        "An environmental wetness reference. Rain, condensation and external splashing remain competing explanations.",
      ],
      [
        "COLLAR_BYPASS",
        "A separate collection-bypass witness. It is distinct from protected pocket B and the environmental reference.",
      ],
      [
        "What this cannot yet prove",
        "Digital fit is not physical fit. Wetness does not establish its source, and dryness does not establish the absence of a leak. M05 simulation results include unfavorable collector comparisons; no stronger physical performance is claimed.",
      ],
    ],
  },
  "/solution/acoustics": {
    title: "A qualified interval, not a crack pin",
    lead: "HYDRO-EAR proposes two matched pipe-contact pickups sampled by one physical stereo clock on a suitable surveyed span.",
    image: "ear.svg",
    sections: [
      [
        "One physical common clock",
        "Both acoustic channels must share the sampling clock. Two independently timed recorders do not satisfy this architecture.",
      ],
      [
        "An eligible path",
        "Pressure, accessible endpoints, known topology, surveyed length and wave-speed uncertainty determine whether a result can be interpreted.",
      ],
      [
        "Abstention is a valid result",
        "Weak plastic-pipe signals, branches, unknown wave speed, multiple sources and pump vibration may leave the result unresolved. A noise peak does not locate a leak.",
      ],
      [
        "Current status",
        "Scientific results are simulation-only. A complete physically validated acoustic recorder and field firmware do not exist, and live acquisition is not enabled in this website.",
      ],
    ],
  },
  "/benefits-and-limitations": {
    title: "Useful evidence includes its limits",
    lead: "The intended benefit is better-directed investigation and accountable maintenance. Measured water savings or field detection performance have not been established.",
    sections: [
      [
        "Intended value",
        "Combine the reason for an investigation, task ownership, repair receipts and independent review in one history. Support resident reporting without exposing internal topology.",
      ],
      [
        "Scientific limits",
        "Low pressure, uncertain demand, unknown wave speed, branches, rain and condensation can prevent diagnosis. Simplified simulations do not validate physical hardware.",
      ],
      [
        "Engineering limits",
        "CadQuery geometry is digitally checked, not physically fit-tested. KiCad files are connectivity drafts; native ERC was not executed. GUARD-5 physical collection remains unverified.",
      ],
      [
        "Cost and procurement",
        "The 41 BOM prices are estimates, not quotations. The proposed total is ₹59,870 within a ₹60,000 ceiling, leaving only ₹130 residual margin—a procurement risk. The proposed pressure-sensor range is poorly suited to sensitive low-pressure measurements.",
      ],
      [
        "Honest outcomes",
        "No physical or field trials, validated accuracy, battery life, deployment coverage or verified savings are claimed. M05 unfavorable GUARD-5 simulation results remain unchanged.",
      ],
    ],
  },
  "/contact": {
    title: "Contact the project",
    lead: "Project contact intake is not enabled in the current backend.",
    sections: [
      [
        "Water service issues",
        "Use the reporting entry to choose an enabled utility and sign in. A service complaint is separate from contacting Team TARK.",
      ],
      [
        "Project enquiries",
        "No externally delivered contact form or approved public contact address is available here. This page does not accept or claim to send messages.",
      ],
    ],
  },
  "/privacy": {
    title: "Privacy in the current development application",
    lead: "This is a private development system. These statements describe the implemented scope and are not a privacy certification.",
    sections: [
      [
        "Accounts and reports",
        "The backend stores account identity, session verifiers, utility membership and submitted records. Citizens can access their own reports; authorized supervisors review utility reports.",
      ],
      [
        "Browser storage",
        "The frontend does not persist passwords, session tokens, report drafts or internal geometry in localStorage or sessionStorage. Private responses are not service-worker cached. Unsaved input is lost when you leave a page.",
      ],
      [
        "Authentication delivery",
        "Verification, invitation and recovery tokens are delivered only to private local development files. External email delivery is not implemented.",
      ],
      [
        "Maps and services",
        "The default network view uses authorized geometry with a blank local MapLibre style. No third-party basemap, geocoder, analytics tracker or external font is required.",
      ],
      [
        "Before public use",
        "Retention operations, external delivery, shared rate limiting, legal review and production operations require further review. Public deployment remains disabled.",
      ],
    ],
  },
  "/terms": {
    title: "Project-use information",
    lead: "HYDROOVERITY is a development project by Team TARK for SIH26254. This text is not a final legally reviewed service agreement.",
    sections: [
      [
        "Authorized development use",
        "Use only your authorized account and utility workspace. The application does not authorize physical infrastructure actuation or unsafe work.",
      ],
      [
        "Evidence and judgement",
        "Digital designs and simulations do not establish real-world sensor performance. Human review and appropriate physical validation remain necessary.",
      ],
      [
        "Availability",
        "This private local application has no production availability promise. Do not rely on it as an emergency or real-time monitoring service.",
      ],
    ],
  },
};
export function PublicPage({ path }: { path: string }) {
  if (path === "/project-status")
    return (
      <PublicShell>
        <Heading
          eyebrow="Engineering status"
          title="What exists. What remains to be proven."
        >
          Software, simulation and physical evidence are different categories.
        </Heading>
        <PublicStatus />
      </PublicShell>
    );
  if (path === "/report")
    return (
      <PublicShell>
        <Heading eyebrow="For residents" title="Report a water issue">
          Start with your utility. Your reports stay private to your account and
          authorized utility reviewers.
        </Heading>
        <UtilityLookup />
      </PublicShell>
    );
  const page = editorial[path];
  if (!page) return null;
  return (
    <PublicShell>
      <Heading eyebrow="HYDROOVERITY · Team TARK" title={page.title}>
        {page.lead}
      </Heading>
      {path === "/solution" && <Architecture />}
      {page.image && (
        <figure className="engineering-plate">
          <Image
            src={`/engineering/${page.image}`}
            alt={page.title}
            width={2560}
            height={1440}
            unoptimized
          />
          <figcaption>
            Reviewed M08 digital engineering reference · PROPOSED DESIGN / NOT
            PHYSICALLY TESTED
          </figcaption>
        </figure>
      )}
      <div className="editorial-sections">
        {page.sections.map(([title, body]) => (
          <section key={title}>
            <h2>{title}</h2>
            <p>{body}</p>
          </section>
        ))}
      </div>
      <div className="actions">
        <Link className="button secondary" href="/how-it-works">
          How the process works
          <ArrowRight size={16} aria-hidden="true" />
        </Link>
        <Link href="/report">Report a water issue</Link>
      </div>
    </PublicShell>
  );
}
