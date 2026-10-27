import { useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, Pill, ease } from "../components/Design";
import { Flow, Studio3D, Tube } from "../components/Engineering3D";

export function PipelineScene() {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const leak = ease(f, fps * 2, fps * 4);
  return (
    <Frame
      section="01 / THE HIDDEN PROBLEM"
      title={"A small leak.\nA bigger question."}
      subtitle="Water where it should not be is an observation. Its source still needs investigation."
      label="ILLUSTRATIVE LEAK SCENARIO · NOT A PHYSICAL EXPERIMENT"
    >
      <div
        style={{
          position: "absolute",
          left: 530,
          top: 90,
          width: 1390,
          height: 900,
        }}
      >
        <Studio3D camera={[230, 150, 290]}>
          <group rotation={[0, Math.PI / 2 + 0.2, 0]}>
            <Tube length={330} />
            <Flow length={330} />
            <mesh>
              <torusGeometry args={[18.5, 3, 16, 48]} />
              <meshStandardMaterial
                color="#758d9e"
                roughness={0.32}
                metalness={0.6}
              />
            </mesh>
            {Array.from({ length: 28 }, (_, i) => {
              const p = (f * 0.017 + i / 28) % 1;
              return (
                <mesh
                  key={i}
                  position={[((i % 3) - 1) * 1.2, -18 - p * p * 65, p * 3]}
                  scale={[1, 1 + p * 2, 1]}
                  visible={leak > 0.2}
                >
                  <sphereGeometry args={[0.7 + leak * 0.5, 8, 6]} />
                  <meshBasicMaterial
                    color="#36c6e9"
                    transparent
                    opacity={(1 - p) * leak}
                  />
                </mesh>
              );
            })}
          </group>
        </Studio3D>
      </div>
      <Pill text="PIPE WALL / INTERNAL FLOW" x={980} y={255} />
      <Pill text="SUSPICION ≠ CONFIRMATION" x={1100} y={810} color="#F5B64A" />
    </Frame>
  );
}
