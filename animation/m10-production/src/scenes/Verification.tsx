import { useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, colors, ease } from "../components/Design";

export function VerificationScene({
  outcomes = false,
}: {
  outcomes?: boolean;
}) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Frame
      section="HYDRO-VERIFY / INDEPENDENT EVIDENCE"
      title={
        outcomes
          ? "Model outcomes.\nOperational limits."
          : "A visit is complete.\nIs the repair effective?"
      }
      subtitle={
        outcomes
          ? "Modeled examples are not physical repair certification."
          : "Comparable before-and-after observations require matching supply conditions, valid instruments and suitable timestamps."
      }
      label="SIMULATED OUTCOME EXAMPLES · NO OPERATIONAL REPAIR CERTIFICATION"
    >
      <div style={{ position: "absolute", left: 780, top: 240, width: 1050 }}>
        {outcomes ? (
          <div style={{ display: "flex", gap: 18 }}>
            {[
              ["PASSED", colors.teal],
              ["FAILED", colors.red],
              ["NOT VERIFIABLE", colors.muted],
            ].map(([s, c], i) => (
              <div
                key={s}
                style={{
                  flex: 1,
                  height: 210,
                  padding: "32px 24px",
                  background: "#112f40",
                  borderTop: `5px solid ${c}`,
                  opacity: ease(f, i * 20, i * 20 + 25),
                }}
              >
                <div
                  style={{ fontSize: 18, letterSpacing: 2, color: "#b7ced6" }}
                >
                  MODELED
                </div>
                <div
                  style={{
                    fontSize: 29,
                    fontWeight: 600,
                    color: c,
                    marginTop: 35,
                  }}
                >
                  {s}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <svg width="1050" height="310">
            {["BEFORE", "AFTER"].map((s, i) => (
              <g key={s} transform={`translate(${i * 530},0)`}>
                <text x="45" y="35" fill="#cce3e8" fontSize="29">
                  {s}
                </text>
                <path
                  d="M40 65 V260 H490"
                  fill="none"
                  stroke="#5b7885"
                  strokeWidth="2"
                />
                <path
                  d={Array.from(
                    { length: 85 },
                    (_, k) =>
                      `${k ? "L" : "M"}${50 + k * 5},${130 + i * 40 + Math.sin(k * 0.2) * 12}`,
                  ).join(" ")}
                  fill="none"
                  stroke={i ? colors.teal : colors.cyan}
                  strokeWidth="4"
                />
              </g>
            ))}
          </svg>
        )}
        <div
          style={{
            marginTop: 65,
            padding: 30,
            border: `2px solid ${colors.amber}`,
            background: "#182f3a",
            opacity: ease(f, fps * 2, fps * 3),
          }}
        >
          <div style={{ fontSize: 23, color: "#b7ced6" }}>
            ACTUAL MANUAL-ONLY OPERATIONAL RECORD
          </div>
          <div
            style={{
              fontSize: 49,
              color: colors.amber,
              marginTop: 16,
              fontWeight: 650,
            }}
          >
            NOT_VERIFIABLE
          </div>
        </div>
        <p
          style={{
            fontSize: 27,
            color: "#b7ced6",
            lineHeight: 1.5,
            marginTop: 30,
          }}
        >
          Work completion, resident satisfaction and measured repair
          effectiveness answer different questions.
        </p>
      </div>
    </Frame>
  );
}
