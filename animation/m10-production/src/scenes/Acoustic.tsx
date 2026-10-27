import { useCurrentFrame } from "remotion";
import { Frame, colors } from "../components/Design";

export function AcousticScene({
  unresolved = false,
}: {
  unresolved?: boolean;
}) {
  const f = useCurrentFrame();
  const waveform = (y: number, delay: number) =>
    Array.from(
      { length: 180 },
      (_, i) =>
        `${i ? "L" : "M"}${800 + i * 5},${y + Math.sin(i * 0.29 - f * 0.04 - delay) * Math.sin(i * 0.043) * 27}`,
    ).join(" ");
  return (
    <Frame
      section="03 / HYDRO-EAR"
      title={"One clock.\nA bounded answer."}
      subtitle="Two pipe-contact pickups feed one stereo ADC. Uncertain evidence can remain unresolved."
      label="PROPOSED COMMON-CLOCK ARCHITECTURE · CONCEPTUAL SIGNAL ILLUSTRATION"
    >
      <svg
        width="1920"
        height="1080"
        style={{ position: "absolute", inset: 0 }}
      >
        <defs>
          <linearGradient id="pipe">
            <stop stopColor="#22495b" />
            <stop offset=".5" stopColor="#8bafb8" />
            <stop offset="1" stopColor="#22495b" />
          </linearGradient>
        </defs>
        <rect
          x="780"
          y="255"
          width="1000"
          height="60"
          rx="28"
          fill="url(#pipe)"
        />
        {[850, 1700].map((x, i) => (
          <g key={x}>
            <rect
              x={x}
              y="228"
              width="40"
              height="105"
              rx="5"
              fill={colors.cyan}
            />
            <text
              x={x + 20}
              y="204"
              textAnchor="middle"
              fill={colors.white}
              fontSize="27"
            >
              Pickup {i + 1}
            </text>
          </g>
        ))}
        <path
          d="M870 335 V400 H1150 V540 M1720 335 V400 H1450 V540"
          fill="none"
          stroke={colors.cyan}
          strokeWidth="4"
        />
        <rect
          x="1040"
          y="440"
          width="180"
          height="70"
          rx="12"
          fill="#153849"
          stroke="#39cbe9"
        />
        <text x="1130" y="485" textAnchor="middle" fill="white" fontSize="25">
          AFE 1
        </text>
        <rect
          x="1390"
          y="440"
          width="180"
          height="70"
          rx="12"
          fill="#153849"
          stroke="#39cbe9"
        />
        <text x="1480" y="485" textAnchor="middle" fill="white" fontSize="25">
          AFE 2
        </text>
        <rect
          x="1040"
          y="540"
          width="530"
          height="130"
          rx="16"
          fill="#0e3345"
          stroke="#36c6e9"
          strokeWidth="3"
        />
        <text x="1305" y="590" textAnchor="middle" fill="white" fontSize="31">
          ONE PHYSICAL STEREO ADC
        </text>
        <text
          x="1305"
          y="635"
          textAnchor="middle"
          fill={colors.cyan}
          fontSize="25"
        >
          L + R · common sampling clock
        </text>
        <path
          d={waveform(760, 0)}
          fill="none"
          stroke={colors.cyan}
          strokeWidth="3"
        />
        <path
          d={waveform(840, 0.8)}
          fill="none"
          stroke="#7ea5f5"
          strokeWidth="3"
        />
        {!unresolved && (
          <rect
            x="1200"
            y="275"
            width="190"
            height="20"
            rx="10"
            fill={colors.amber}
          />
        )}
        <text
          x="1295"
          y="365"
          textAnchor="middle"
          fill={colors.amber}
          fontSize="24"
        >
          {unresolved
            ? "LOCATION UNRESOLVED"
            : "Candidate interval, not an exact hole"}
        </text>
      </svg>
    </Frame>
  );
}
