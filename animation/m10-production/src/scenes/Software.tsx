import { Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, colors, ease } from "../components/Design";

type Props = {
  asset: string;
  title: string;
  note: string;
  mobile?: boolean;
  science?: boolean;
  scrollPixels?: number;
  startScrollPixels?: number;
};
export function SoftwareScene({
  asset,
  title,
  note,
  mobile = false,
  science = false,
  scrollPixels = 0,
  startScrollPixels = 0,
}: Props) {
  const f = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <Frame
      section={
        science
          ? "SCIENTIFIC WORKSPACE / SIMULATION"
          : "ACTUAL SOFTWARE / SYNTHETIC TEST CAPTURE"
      }
      title={title}
      subtitle={note}
      label={
        science
          ? "SIMULATION · STORED SYNTHETIC RECORDING, NOT LIVE HARDWARE"
          : "AUTHENTIC DEVELOPMENT CAPTURE · SYNTHETIC ACCOUNTS AND RECORDS"
      }
    >
      <div
        style={{
          position: "absolute",
          left: mobile ? 1080 : 720,
          top: 155,
          width: mobile ? 470 : 1120,
          height: 770,
          borderRadius: mobile ? 34 : 15,
          background: "#e9eef3",
          overflow: "hidden",
          border: "8px solid #315364",
          boxShadow: "0 25px 85px #0006",
          opacity: ease(f, 0, 25),
          translate: `0 ${22 * (1 - ease(f, 0, 25))}px`,
        }}
      >
        <div
          style={{
            height: 40,
            background: "#102a3a",
            color: "#b5d2df",
            fontSize: 19,
            padding: "8px 16px",
            boxSizing: "border-box",
          }}
        >
          HYDROOVERITY · private development
        </div>
        <Img
          src={staticFile(`captures/${asset}`)}
          style={{
            width: "100%",
            height: "auto",
            display: "block",
            translate: `0 ${-startScrollPixels - scrollPixels * ease(f, Math.min(fps, durationInFrames * 0.15), durationInFrames * 0.85)}px`,
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          left: 88,
          top: 760,
          width: 530,
          borderTop: `2px solid ${colors.cyan}`,
          paddingTop: 24,
          fontSize: 25,
          color: "#a9c5d1",
          lineHeight: 1.5,
          opacity: ease(f, fps * 2, fps * 3),
        }}
      >
        Recorded software behavior.
        <br />
        Conceptual overlays do not create backend evidence.
      </div>
    </Frame>
  );
}
