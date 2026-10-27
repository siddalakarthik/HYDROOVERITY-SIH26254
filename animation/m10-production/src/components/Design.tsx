import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const colors = {
  bg: "#071623",
  surface: "#102A3A",
  cyan: "#36C6E9",
  teal: "#19B4A2",
  white: "#F5FAFD",
  amber: "#F5B64A",
  red: "#E66A68",
  muted: "#9CAFB9",
};
export const ease = (f: number, a: number, b: number) => {
  const x = Math.max(0, Math.min(1, (f - a) / (b - a)));
  return x * x * (3 - 2 * x);
};
export function Frame({
  children,
  label = "ILLUSTRATIVE ENGINEERING SCENE",
  section = "HYDROOVERITY",
  title,
  subtitle,
}: {
  children: React.ReactNode;
  label?: string;
  section?: string;
  title?: string;
  subtitle?: string;
}) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        background: colors.bg,
        color: colors.white,
        fontFamily: "Segoe UI, Arial, sans-serif",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at 72% 45%, #123c4e 0%, #071623 68%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.12,
          backgroundImage:
            "linear-gradient(#72acbc22 1px,transparent 1px),linear-gradient(90deg,#72acbc22 1px,transparent 1px)",
          backgroundSize: "100px 100px",
        }}
      />
      {children}
      <div
        style={{
          position: "absolute",
          left: 88,
          top: 56,
          fontSize: 22,
          letterSpacing: 5,
          fontWeight: 600,
          color: colors.cyan,
        }}
      >
        {section}
      </div>
      {title && (
        <div
          style={{
            position: "absolute",
            left: 88,
            top: 210,
            width: 600,
            opacity: ease(f, 0, fps * 0.6),
            translate: `0 ${interpolate(ease(f, 0, fps * 0.6), [0, 1], [20, 0])}px`,
          }}
        >
          <div
            style={{
              width: 58,
              height: 5,
              background: colors.cyan,
              marginBottom: 32,
            }}
          />
          <h1
            style={{
              fontSize: 76,
              lineHeight: 1.07,
              letterSpacing: -3,
              fontWeight: 650,
              margin: 0,
              whiteSpace: "pre-line",
            }}
          >
            {title}
          </h1>
          {subtitle && (
            <p
              style={{
                fontSize: 30,
                lineHeight: 1.45,
                color: "#b6cbd5",
                maxWidth: 550,
                marginTop: 30,
              }}
            >
              {subtitle}
            </p>
          )}
        </div>
      )}
      <div
        style={{
          position: "absolute",
          left: 88,
          bottom: 46,
          color: colors.amber,
          fontSize: 20,
          letterSpacing: 1.5,
          maxWidth: 1500,
        }}
      >
        {label}
      </div>
      <div
        style={{
          position: "absolute",
          right: 88,
          bottom: 46,
          fontSize: 19,
          color: "#9eb2bf",
        }}
      >
        TARK · SIH26254
      </div>
    </AbsoluteFill>
  );
}
export function Pill({
  text,
  x,
  y,
  color = colors.cyan,
}: {
  text: string;
  x: number;
  y: number;
  color?: string;
}) {
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        borderLeft: `4px solid ${color}`,
        padding: "12px 20px",
        background: "#071623db",
        fontSize: 25,
        color,
        whiteSpace: "nowrap",
      }}
    >
      {text}
    </div>
  );
}
