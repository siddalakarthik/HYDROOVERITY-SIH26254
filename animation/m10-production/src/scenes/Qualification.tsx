import { useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, colors, ease } from "../components/Design";

export function QualificationScene({
  mode = "supply",
}: {
  mode?: "supply" | "rain" | "watch" | "patterns";
}) {
  const f = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = f / fps;
  const states = ["OFF", "FILLING", "STEADY", "DRAINING", "UNKNOWN"];
  const active = Math.min(
    4,
    Math.floor((f / Math.max(1, durationInFrames)) * 5),
  );
  const patterns = ["A", "B", "C", "EXT", "BYPASS"];
  const title =
    mode === "rain"
      ? "Same symptom.\nDifferent causes."
      : mode === "watch"
        ? "Context before\nconclusion."
        : mode === "patterns"
          ? "Wetness is evidence.\nIts source is a question."
          : "Supply changes\nthe interpretation.";
  return (
    <Frame
      section={
        mode === "patterns"
          ? "GUARD-5 / REASONING"
          : "HYDRO-WATCH / QUALIFIED EVIDENCE"
      }
      title={title}
      subtitle={
        mode === "rain"
          ? "A leak, rainfall and normal supply changes can produce ambiguous observations."
          : mode === "patterns"
            ? "Protected, external and bypass observations stay distinct. Missing health remains UNKNOWN."
            : "Pressure, flow, supply state, sensor health and observation age belong together."
      }
      label="ILLUSTRATIVE PATTERNS · NO LIVE PHYSICAL MEASUREMENTS"
    >
      {mode === "rain" ? (
        <svg
          width="1920"
          height="1080"
          style={{ position: "absolute", inset: 0 }}
        >
          {["PIPE LEAK", "RAINFALL", "FILLING / DEMAND"].map((s, i) => (
            <g key={s} transform={`translate(${750 + i * 355},280)`}>
              <rect width="310" height="480" rx="20" fill="#102a3a" />
              <text
                x="155"
                y="60"
                fill="white"
                textAnchor="middle"
                fontSize="26"
              >
                {s}
              </text>
              <path d="M30 280 H280" stroke="#6d9ba9" strokeWidth="32" />
              {Array.from({ length: 12 }, (_, k) => (
                <line
                  key={k}
                  x1={i === 0 ? 150 : 35 + k * 21}
                  y1={i === 0 ? 290 : 100 + ((f * 4 + k * 11) % 130)}
                  x2={i === 0 ? 150 + k * 3 : 30 + k * 21}
                  y2={
                    i === 0
                      ? 300 + ((f * 3 + k * 9) % 65)
                      : 120 + ((f * 4 + k * 11) % 130)
                  }
                  stroke={colors.cyan}
                  strokeWidth="3"
                  opacity={i === 2 ? 0.2 : 0.8}
                />
              ))}
              <ellipse
                cx="155"
                cy="370"
                rx={80 + Math.sin(t) * 8}
                ry="20"
                fill="#2399bd"
                opacity=".6"
              />
              <text
                x="155"
                y="440"
                textAnchor="middle"
                fill={colors.amber}
                fontSize="27"
              >
                INVESTIGATE
              </text>
            </g>
          ))}
        </svg>
      ) : (
        <div style={{ position: "absolute", left: 760, top: 230, width: 1050 }}>
          <div style={{ display: "flex", gap: 12 }}>
            {(mode === "patterns" ? patterns : states).map((s, i) => (
              <div
                key={s}
                style={{
                  flex: 1,
                  padding: "22px 6px",
                  fontSize: 25,
                  textAlign: "center",
                  borderTop: `4px solid ${i === active ? colors.cyan : "#405865"}`,
                  background: i === active ? "#16485b" : "#102a3a",
                  color: i === active ? "white" : "#9fb5bf",
                }}
              >
                {s}
              </div>
            ))}
          </div>
          <svg width="1050" height="420" viewBox="0 0 1050 420">
            <path
              d="M35 30 V330 H1030"
              fill="none"
              stroke="#526b78"
              strokeWidth="2"
            />
            {[90, 170, 250].map((y) => (
              <path
                key={y}
                d={`M35 ${y} H1030`}
                stroke="#34505d"
                strokeDasharray="4 8"
              />
            ))}
            <path
              d={Array.from(
                { length: 190 },
                (_, i) =>
                  `${i ? "L" : "M"}${35 + i * 5},${220 - Math.sin(i * 0.035) * 45 - Math.sin(i * 0.18) * 12}`,
              ).join(" ")}
              fill="none"
              stroke={colors.cyan}
              strokeWidth="4"
              strokeDasharray="1200"
              strokeDashoffset={1200 * (1 - ease(f, 15, 150))}
            />
            <rect x="535" y="30" width="95" height="300" fill="#071623" />
            <text
              x="582"
              y="365"
              textAnchor="middle"
              fill={colors.amber}
              fontSize="24"
            >
              GAP
            </text>
            <text x="50" y="400" fill="#a9c1cd" fontSize="23">
              Conceptual trace · no physical units or measured values claimed
            </text>
          </svg>
          <div
            style={{
              fontSize: 31,
              color: active === 4 ? "#bbc7cf" : colors.amber,
              borderLeft: `4px solid ${colors.amber}`,
              padding: "20px 24px",
              background: "#112f40",
            }}
          >
            {mode === "patterns"
              ? [
                  "A · protected-path wetness",
                  "B · protected-path wetness",
                  "C · protected-path wetness",
                  "EXT · environmental exposure",
                  "BYPASS · collection bypass",
                ][active]
              : active === 4
                ? "UNKNOWN is not a healthy state"
                : "Qualified suspicion → investigation, not proof"}
          </div>
        </div>
      )}
    </Frame>
  );
}
