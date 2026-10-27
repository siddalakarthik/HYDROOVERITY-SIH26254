import { useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, colors, ease } from "../components/Design";

const flows = {
  architecture: ["HYDRO-WATCH", "GUARD-5", "HYDRO-EAR", "HYDRO-VERIFY"],
  service: [
    "REPORT",
    "TRIAGE",
    "INVESTIGATE",
    "ASSIGN",
    "VISIT",
    "REVIEW",
    "UPDATE",
  ],
  repair: [
    "AUTHORIZE",
    "ISOLATE / DEPRESSURIZE",
    "INSPECT",
    "APPROVED REPAIR",
    "RESTORE",
    "OBSERVE",
  ],
  roles: ["RESIDENT", "SUPERVISOR", "ENGINEER", "TECHNICIAN"],
  gates: [
    "OFFLINE SYNC",
    "SECURE MEDIA",
    "EXTERNAL DELIVERY",
    "PUBLIC DEPLOYMENT",
    "PRIVACY / RETENTION",
    "PHYSICAL QUALIFICATION",
  ],
  booking: ["REQUESTED", "ELIGIBILITY CHECK", "CONFIRMED BOOKING", "VISIT"],
};
type Mode = keyof typeof flows;
export function WorkflowScene({ mode = "service" }: { mode?: Mode }) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const labels = flows[mode];
  const title =
    mode === "architecture"
      ? "One evidence chain. Distinct responsibilities."
      : mode === "repair"
        ? "Future field work requires qualified people."
        : mode === "roles"
          ? "The right information. The right people."
          : mode === "gates"
            ? "Progress with explicit limits."
            : mode === "booking"
              ? "A request is not an appointment."
              : "Every decision stays attached to its evidence.";
  return (
    <Frame
      section="HYDROOVERITY / ACCOUNTABLE WORKFLOW"
      label={
        mode === "repair"
          ? "ILLUSTRATIVE FUTURE FIELD WORKFLOW · NO AUTOMATIC VALVE ACTUATION"
          : mode === "gates"
            ? "CURRENT GATES REMAIN CLOSED · NO PUBLIC OR FIELD DEPLOYMENT"
            : "CONCEPTUAL WORKFLOW · SOFTWARE TESTS USE SYNTHETIC DATA"
      }
    >
      <h1
        style={{
          position: "absolute",
          left: 88,
          top: 155,
          fontSize: 62,
          width: 1600,
          lineHeight: 1.15,
          margin: 0,
          letterSpacing: -2,
        }}
      >
        {title}
      </h1>
      <svg
        width="1920"
        height="1080"
        style={{ position: "absolute", inset: 0 }}
      >
        <path d="M170 540 H1740" stroke="#2c4d60" strokeWidth="3" />
        <path
          d="M170 540 H1740"
          stroke={colors.cyan}
          strokeWidth="4"
          strokeDasharray="1570"
          strokeDashoffset={1570 * (1 - ease(f, 0, fps * 8))}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          left: 88,
          right: 88,
          top: 410,
          display: "flex",
          gap: 24,
        }}
      >
        {labels.map((label, i) => (
          <div
            key={label}
            style={{
              flex: 1,
              minWidth: 0,
              opacity: 0.25 + 0.75 * ease(f, i * fps * 0.6, i * fps * 0.6 + 24),
              translate: `0 ${30 * (1 - ease(f, i * fps * 0.6, i * fps * 0.6 + 24))}px`,
              background: "#112f40",
              borderTop: `4px solid ${mode === "gates" ? colors.amber : colors.cyan}`,
              padding: "32px 18px",
              height: 220,
            }}
          >
            <div
              style={{ fontSize: 18, color: colors.muted, letterSpacing: 2 }}
            >
              0{i + 1}
            </div>
            <div
              style={{
                fontSize: labels.length > 5 ? 25 : 29,
                lineHeight: 1.3,
                fontWeight: 600,
                marginTop: 38,
              }}
            >
              {label}
            </div>
          </div>
        ))}
      </div>
      <div
        style={{
          position: "absolute",
          left: 88,
          top: 760,
          maxWidth: 1560,
          fontSize: 32,
          color: "#b5cdd8",
          lineHeight: 1.5,
        }}
      >
        {mode === "gates"
          ? "Operator policies, consent, encryption, retention and physical evidence still require review."
          : mode === "booking"
            ? "Only real, authorized shifts, skills, service areas, durations and buffers establish eligibility."
            : mode === "roles"
              ? "Private utility notes stay private. Ownership and current roles control access."
              : mode === "architecture"
                ? "Uncertainty must not become certainty simply because systems are connected."
                : mode === "repair"
                  ? "Utility-approved procedures, trained personnel and suitable post-repair observations are required."
                  : "A report, incident, work order, completed visit and independently verified repair are different records."}
      </div>
    </Frame>
  );
}
