import { useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, colors, ease } from "../components/Design";

export function DispatchScene({
  concurrency = false,
}: {
  concurrency?: boolean;
}) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = ease(f, fps, fps * 3);
  return (
    <Frame
      section="M07-B / SCHEDULING INTEGRITY"
      title={
        concurrency
          ? "One technician.\nOne valid reservation."
          : "Request a visit.\nConfirm deliberately."
      }
      subtitle={
        concurrency
          ? "Atomic database rules protect confirmed technician time. A competing request receives a conflict."
          : "Availability exists only after authorized utility configuration. A resident request does not reserve time."
      }
      label="CONCEPTUAL VIEW OF CODE-TESTED RULES · NO PRODUCTION AVAILABILITY CLAIM"
    >
      <svg
        width="1920"
        height="1080"
        style={{ position: "absolute", inset: 0 }}
      >
        <rect
          x="1040"
          y="260"
          width="630"
          height="520"
          rx="20"
          fill="#112f40"
          stroke="#315769"
          strokeWidth="2"
        />
        <text x="1355" y="325" fill="#d0e1e8" fontSize="31" textAnchor="middle">
          CONFIGURED TECHNICIAN CAPACITY
        </text>
        {[0, 1, 2, 3].map((i) => (
          <path key={i} d={`M1080 ${380 + i * 80} H1630`} stroke="#315769" />
        ))}
        <rect
          x="1090"
          y="460"
          width="520"
          height="70"
          rx="8"
          fill={progress > 0.7 ? "#137d89" : "#526675"}
          opacity=".8"
        />
        <text x="1350" y="505" textAnchor="middle" fill="white" fontSize="27">
          {progress > 0.7
            ? "ONE CONFIRMED BOOKING"
            : "ELIGIBILITY + CURRENT POLICY CHECK"}
        </text>
        <g transform={`translate(${740 + progress * 250},400)`}>
          <rect width="230" height="85" rx="10" fill="#2d94b2" />
          <text x="115" y="52" fill="white" textAnchor="middle" fontSize="27">
            REQUEST A
          </text>
        </g>
        {concurrency && (
          <g transform={`translate(${740 + progress * 150},630)`}>
            <rect width="230" height="85" rx="10" fill="#745846" />
            <text x="115" y="52" fill="white" textAnchor="middle" fontSize="27">
              REQUEST B
            </text>
          </g>
        )}
        {concurrency && (
          <text
            x="1370"
            y="690"
            textAnchor="middle"
            fill={colors.amber}
            fontSize="27"
            opacity={progress}
          >
            CONFLICT · no second reservation
          </text>
        )}
      </svg>
    </Frame>
  );
}
