import { useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, colors, ease } from "../components/Design";

export function FieldScene({ tests = false }: { tests?: boolean }) {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const tasks = tests
    ? [
        "WEAK COLLECTION",
        "RAIN / BLOCKAGE",
        "CALIBRATION",
        "ACOUSTIC AUDIBILITY",
        "COMMON CLOCK",
        "SAFE POWER",
        "COMPARABLE REPAIR EVIDENCE",
      ]
    : [
        "AUTHORIZE",
        "ISOLATE / DEPRESSURIZE",
        "INSPECT",
        "APPROVED REPAIR",
        "RESTORE",
        "OBSERVE",
      ];
  const step = Math.min(
    tasks.length - 1,
    Math.floor((f / Math.max(1, durationInFrames)) * tasks.length),
  );
  return (
    <Frame
      section={
        tests
          ? "FUTURE PHYSICAL VALIDATION"
          : "ILLUSTRATIVE FUTURE FIELD WORKFLOW"
      }
      title={
        tests
          ? "The next tests\nare physical."
          : "Qualified people.\nApproved procedures."
      }
      subtitle={
        tests
          ? "Digital geometry and simulated signals cannot establish physical collection, audibility or repair performance."
          : "The utility controls field work. HYDROOVERITY does not operate valves or physically repair the pipe."
      }
      label="CONCEPTUAL FUTURE SCENE · NO PHYSICAL EXPERIMENT OR REPAIR HAS BEEN PERFORMED"
    >
      <svg
        width="1920"
        height="1080"
        style={{ position: "absolute", inset: 0 }}
      >
        <path d="M780 710 H1550" stroke="#718e9c" strokeWidth="65" />
        <path
          d="M780 700 H1550"
          stroke="#b0d0da"
          strokeWidth="5"
          opacity=".6"
        />
        <rect x="1240" y="655" width="82" height="110" rx="10" fill="#537589" />
        <path
          d="M1260 670 V750 M1302 670 V750"
          stroke="#a0c1cd"
          strokeWidth="5"
        />
        {step < 3 &&
          Array.from({ length: 14 }, (_, i) => (
            <circle
              key={i}
              cx={1280 + Math.sin(i) * 8}
              cy={758 + ((f * 2 + i * 7) % 92)}
              r="3"
              fill={colors.cyan}
              opacity=".6"
            />
          ))}
        <path d="M1600 707 H1800" stroke="#345261" strokeWidth="10" />
        <g transform="translate(1690 460)">
          <circle cx="0" cy="0" r="38" fill="#9fb7c4" />
          <path d="M-44 0 Q-44 -60 0 -60 Q44 -60 44 0Z" fill={colors.amber} />
          <path d="M-32 50 H32 L50 150 H-50Z" fill="#236b83" />
          <path
            d="M-26 150 L-35 235 M26 150 L35 235"
            stroke="#7c9ba9"
            strokeWidth="23"
          />
          <path d="M-32 65 L-90 135" stroke="#7c9ba9" strokeWidth="17" />
        </g>
        <rect x="810" y="285" width="940" height="100" rx="16" fill="#143446" />
        <text
          x="1280"
          y="347"
          textAnchor="middle"
          fill={colors.cyan}
          fontSize="34"
        >
          {tasks[step]}
        </text>
        <text
          x="1250"
          y="885"
          textAnchor="middle"
          fill={colors.amber}
          fontSize="28"
          opacity={ease(f, 20, 50)}
        >
          {tests
            ? "FUTURE TEST REQUIREMENT"
            : "QUALIFIED UTILITY CREW · NO AUTOMATIC ACTUATION"}
        </text>
      </svg>
    </Frame>
  );
}
