import { Frame } from "../components/Design";
import { GuardModel, Studio3D } from "../components/Engineering3D";

export function GuardScene({
  exploded = true,
  focus = "",
}: {
  exploded?: boolean;
  focus?: string;
}) {
  return (
    <Frame
      section="02 / GUARD-5"
      title={"Five channels.\nDifferent clues."}
      subtitle="A removable, non-pressure-bearing collar for accessible exposed joints."
      label="DIGITAL DESIGN / NOT PHYSICALLY VALIDATED · COLLECTION PERFORMANCE UNVERIFIED"
    >
      <div
        style={{
          position: "absolute",
          left: 570,
          top: 110,
          width: 1350,
          height: 850,
        }}
      >
        <Studio3D>
          <GuardModel exploded={exploded} />
        </Studio3D>
      </div>
      {focus && (
        <div
          style={{
            position: "absolute",
            left: 1110,
            top: 150,
            fontSize: 36,
            color: focus === "EXT" ? "#f5b64a" : "#e66a68",
            background: "#071623cc",
            padding: "14px 24px",
          }}
        >
          {focus === "EXT"
            ? "EXT · environmental water"
            : "BYPASS · uncollected water"}
        </div>
      )}
      <div
        style={{
          position: "absolute",
          left: 88,
          top: 610,
          display: "flex",
          gap: 12,
        }}
      >
        {[
          ["A", "#39cbe9"],
          ["B", "#7ea5f5"],
          ["C", "#19b4a2"],
          ["EXT", "#f5b64a"],
          ["BYPASS", "#e66a68"],
        ].map(([text, color]) => (
          <div
            key={text}
            style={{
              borderTop: `4px solid ${color}`,
              color,
              padding: "16px 16px",
              background: "#102a3a",
              fontSize: 25,
              fontWeight: 600,
            }}
          >
            {text}
          </div>
        ))}
      </div>
      <div
        style={{
          position: "absolute",
          left: 88,
          top: 735,
          width: 560,
          color: "#adc2cc",
          fontSize: 25,
          lineHeight: 1.5,
        }}
      >
        A / B / C · protected collection
        <br />
        EXT · environmental witness
        <br />
        BYPASS · uncollected-water witness
      </div>
    </Frame>
  );
}
