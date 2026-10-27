import { useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, colors, ease } from "../components/Design";

export function EvidenceScene({
  kind = "guard",
}: {
  kind?: "guard" | "ear" | "software" | "budget";
}) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = ease(f, 15, fps * 3);
  const title =
    kind === "guard"
      ? "Our own results\nexpose weaknesses."
      : kind === "ear"
        ? "Accepted does\nnot mean certain."
        : kind === "budget"
          ? "₹59,870 estimated.\n₹130 of headroom."
          : "Software evidence.\nNot sensor accuracy.";
  return (
    <Frame
      section={
        kind === "budget"
          ? "FEASIBILITY / ESTIMATES"
          : kind === "software"
            ? "VERIFIED SOFTWARE BASELINE"
            : "M05 / SIMULATED BENCHMARK"
      }
      title={title}
      subtitle={
        kind === "guard"
          ? "The nominal comparison was unfavorable to GUARD-5. Physical collection behavior remains unverified."
          : kind === "ear"
            ? "Unresolved cases and accepted intervals that miss modeled truth remain in the denominator."
            : kind === "budget"
              ? "41 estimated BOM prices. No supplier quotations. The residual margin is a procurement risk."
              : "Accepted main 886bf01. Private-development software with explicit deployment gates."
      }
      label={
        kind === "budget"
          ? "ESTIMATED_NOT_QUOTED · MATERIALS CEILING ₹60,000"
          : kind === "software"
            ? "CODE-TESTED SOFTWARE · NO PHYSICAL OR FIELD PERFORMANCE CLAIM"
            : "SIMULATION ONLY · SOURCE: REVIEWED M05 REFERENCE SUMMARY"
      }
    >
      <div style={{ position: "absolute", left: 790, top: 240, width: 1010 }}>
        {kind === "guard" ? (
          <>
            {[
              ["GUARD-5", 0.7142857142857143, colors.amber],
              ["Simple pad", 0.7777777777777778, "#83a1b2"],
              ["Multizone baseline", 0.8235294117647058, colors.cyan],
            ].map(([name, value, color]) => (
              <div key={String(name)} style={{ marginBottom: 42 }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: 29,
                    marginBottom: 16,
                  }}
                >
                  <span>{name}</span>
                  <strong>{Number(value).toFixed(3)}</strong>
                </div>
                <div style={{ height: 53, background: "#153342" }}>
                  <div
                    style={{
                      height: "100%",
                      width: `${Number(value) * progress * 100}%`,
                      background: String(color),
                    }}
                  />
                </div>
              </div>
            ))}
            <div style={{ fontSize: 25, color: "#b8cad3" }}>
              F1 score · common zero baseline · 168 nominal cases per method
            </div>
          </>
        ) : kind === "ear" ? (
          <>
            <div style={{ fontSize: 75, fontWeight: 650 }}>
              264{" "}
              <span style={{ fontSize: 30, fontWeight: 400, color: "#bdd1dc" }}>
                eligible synthetic captures
              </span>
            </div>
            <div style={{ display: "flex", height: 110, margin: "38px 0" }}>
              <div
                style={{
                  width: `${(190 / 264) * 100}%`,
                  background: "#218ca6",
                  padding: 24,
                  fontSize: 29,
                }}
              >
                190 accepted
              </div>
              <div
                style={{
                  flex: 1,
                  background: "#617883",
                  padding: 24,
                  fontSize: 29,
                }}
              >
                74 unresolved
              </div>
            </div>
            <div
              style={{
                borderLeft: `5px solid ${colors.red}`,
                padding: 30,
                background: "#2a2930",
                fontSize: 33,
                lineHeight: 1.4,
                color: "#efb0a9",
              }}
            >
              20 accepted candidate intervals excluded the modeled truth.
            </div>
            <div style={{ fontSize: 26, color: "#b8cad3", marginTop: 30 }}>
              Engineering bounds, not calibrated confidence intervals.
            </div>
          </>
        ) : kind === "software" ? (
          <>
            <div style={{ display: "flex", gap: 24 }}>
              {[
                ["119", "registered API operations"],
                ["57", "migrated tables"],
                ["4", "passing CI jobs"],
              ].map(([n, label]) => (
                <div
                  key={n}
                  style={{
                    flex: 1,
                    borderTop: "4px solid #36c6e9",
                    background: "#112f40",
                    padding: "32px 24px",
                  }}
                >
                  <div style={{ fontSize: 84, fontWeight: 650 }}>{n}</div>
                  <div
                    style={{ fontSize: 27, lineHeight: 1.3, color: "#c5d8df" }}
                  >
                    {label}
                  </div>
                </div>
              ))}
            </div>
            <div
              style={{
                fontSize: 27,
                lineHeight: 1.6,
                marginTop: 55,
                color: "#b7ced6",
              }}
            >
              M07 retains deferred scope.
              <br />
              Offline, secure media and public deployment remain gated.
              <br />
              No physical sensor or repair certification follows.
            </div>
          </>
        ) : (
          <>
            <div style={{ fontSize: 27, color: "#c5d8df" }}>
              PLANNING CEILING
            </div>
            <div style={{ fontSize: 84, fontWeight: 650 }}>₹60,000</div>
            <div
              style={{
                height: 65,
                background: "#34464f",
                marginTop: 40,
                display: "flex",
              }}
            >
              <div
                style={{
                  width: `${(54870 / 60000) * 100 * progress}%`,
                  background: colors.cyan,
                }}
              />
              <div
                style={{
                  width: `${(5000 / 60000) * 100 * progress}%`,
                  background: "#5d8193",
                }}
              />
            </div>
            <div
              style={{ display: "flex", gap: 55, fontSize: 28, marginTop: 25 }}
            >
              <span>₹54,870 materials</span>
              <span>₹5,000 contingency</span>
            </div>
            <div style={{ color: colors.amber, fontSize: 38, marginTop: 60 }}>
              Residual estimated margin: ₹130
            </div>
            <div
              style={{
                fontSize: 27,
                lineHeight: 1.5,
                color: "#c5d8df",
                marginTop: 24,
              }}
            >
              Prices, suitability and physical performance require procurement
              and engineering review.
            </div>
          </>
        )}
      </div>
    </Frame>
  );
}
