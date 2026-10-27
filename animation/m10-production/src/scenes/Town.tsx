import { useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, colors, ease } from "../components/Design";

export function TownScene({
  intro = false,
  closing = false,
  opening = false,
}: {
  intro?: boolean;
  closing?: boolean;
  opening?: boolean;
}) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const paths = [
    "M150 550 H1750",
    "M450 550 V230",
    "M800 550 V780",
    "M1150 550 V230",
    "M1500 550 V780",
  ];
  return (
    <Frame
      section={
        intro
          ? "TEAM TARK / SMART INDIA HACKATHON 2026"
          : closing
            ? "FUTURE DEVELOPMENT VISION"
            : "01 / AN ORDINARY WATER NETWORK"
      }
      label={
        intro || closing
          ? "SIH26254 · MINISTRY OF JAL SHAKTI"
          : "ILLUSTRATIVE NETWORK · NO REAL VILLAGE OR DEPLOYMENT"
      }
    >
      {opening && (
        <svg
          width="1920"
          height="1080"
          style={{
            position: "absolute",
            inset: 0,
            opacity: 1 - ease(f, 4 * fps, 7.2 * fps),
          }}
        >
          <defs>
            <radialGradient id="drop">
              <stop stopColor="#b6f1ff" />
              <stop offset=".45" stopColor="#34b9da" />
              <stop offset="1" stopColor="#0c455e" />
            </radialGradient>
          </defs>
          <g
            transform={`translate(960 ${390 + Math.sin(t) * 7}) scale(${1 + ease(f, 3 * fps, 7 * fps) * 3})`}
          >
            <path
              d="M0 -120 C-28 -67 -75 -14 -75 35 A75 75 0 0 0 75 35 C75 -14 28 -67 0 -120Z"
              fill="url(#drop)"
              stroke="#7ae2fa"
              strokeWidth="2"
            />
            <path
              d="M-20 -38 Q-62 22 -43 52"
              stroke="#e3fcff"
              strokeWidth="7"
              fill="none"
              opacity=".55"
            />
          </g>
          <text
            x="960"
            y="670"
            textAnchor="middle"
            fill="#d2ecf5"
            fontSize="35"
            letterSpacing="7"
            opacity={ease(f, 2.14 * fps, 2.8 * fps)}
          >
            TEAM TARK
          </text>
        </svg>
      )}
      <svg
        width="1920"
        height="1080"
        style={{
          position: "absolute",
          inset: 0,
          opacity:
            (intro || closing ? 0.5 : 1) *
            (opening ? ease(f, 4 * fps, 7.2 * fps) : 1),
        }}
      >
        <g transform={`translate(0 ${intro || closing ? 230 : 40})`}>
          <path
            d="M120 490 H1800 M390 180 V850 M1090 180 V850"
            stroke="#172f3c"
            strokeWidth="85"
            fill="none"
          />
          <path
            d="M120 490 H1800"
            stroke="#64808a"
            strokeDasharray="20 22"
            strokeWidth="2"
          />
          {paths.map((d, i) => (
            <g key={d}>
              <path d={d} stroke="#234b5d" strokeWidth="23" fill="none" />
              <path
                d={d}
                stroke={colors.cyan}
                strokeWidth="6"
                strokeDasharray="11 70"
                strokeDashoffset={-t * 55 - i * 12}
                fill="none"
              />
            </g>
          ))}
          {[
            { x: 450, y: 230 },
            { x: 800, y: 780 },
            { x: 1150, y: 230 },
            { x: 1500, y: 780 },
          ].map(({ x, y }, i) => (
            <g key={x} transform={`translate(${x - 72},${y - 180})`}>
              <path d="M0 75 L90 30 L180 75 L90 120Z" fill="#487181" />
              <path d="M0 75 V170 L90 218 V120Z" fill="#254858" />
              <path d="M90 120 V218 L180 170 V75Z" fill="#193748" />
              <path
                d="M-10 75 L90 0 L190 75 L90 126Z"
                fill={i === 0 ? "#388093" : "#365b6d"}
              />
              <path
                d="M25 125 V160 L50 173 V137Z M120 137 V173 L149 158 V124Z"
                fill="#7ad1dd"
                opacity=".7"
              />
            </g>
          ))}
          <ellipse cx="160" cy="550" rx="70" ry="30" fill="#306479" />
          <rect x="90" y="370" width="140" height="180" fill="#22485a" />
          <ellipse cx="160" cy="370" rx="70" ry="30" fill="#4e899c" />
          <text
            x="160"
            y="330"
            textAnchor="middle"
            fill="#b7d4df"
            fontSize="27"
          >
            Supply
          </text>
          <circle
            cx="1000"
            cy="550"
            r={24 + Math.sin(t * 2) * 5}
            fill={colors.amber}
            opacity=".25"
          />
          <circle cx="1000" cy="550" r="8" fill={colors.amber} />
        </g>
      </svg>
      {intro || closing ? (
        <div
          style={{
            position: "absolute",
            left: 88,
            top: 170,
            opacity: ease(f, opening ? 7.2 * fps : 0, opening ? 8.1 * fps : 30),
          }}
        >
          <div style={{ fontSize: 105, fontWeight: 700, letterSpacing: -5 }}>
            HYDROOVERITY
          </div>
          <div style={{ fontSize: 35, marginTop: 22, color: "#c1dbe3" }}>
            Find the leak. Understand the evidence. Verify the repair.
          </div>
          <div
            style={{
              fontSize: 25,
              color: colors.cyan,
              letterSpacing: 3,
              marginTop: 40,
            }}
          >
            TEAM TARK · TEAM ID 155480
          </div>
        </div>
      ) : (
        <div
          style={{
            position: "absolute",
            left: 90,
            top: 120,
            fontSize: 57,
            fontWeight: 600,
          }}
        >
          Every connection carries a responsibility.
        </div>
      )}
    </Frame>
  );
}
