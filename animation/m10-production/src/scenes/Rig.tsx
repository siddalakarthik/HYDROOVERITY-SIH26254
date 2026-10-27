import { useMemo } from "react";
import * as THREE from "three";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Studio3D } from "../components/Engineering3D";
import { Frame, colors } from "../components/Design";

function Link({
  a,
  b,
  color = "#8fb2c4",
  radius = 1.6,
}: {
  a: [number, number, number];
  b: [number, number, number];
  color?: string;
  radius?: number;
}) {
  const { mid, q, length } = useMemo(() => {
    const av = new THREE.Vector3(...a),
      bv = new THREE.Vector3(...b);
    const d = bv.clone().sub(av);
    return {
      mid: av.clone().add(bv).multiplyScalar(0.5),
      q: new THREE.Quaternion().setFromUnitVectors(
        new THREE.Vector3(0, 1, 0),
        d.clone().normalize(),
      ),
      length: d.length(),
    };
  }, [a, b]);
  return (
    <mesh position={mid} quaternion={q}>
      <cylinderGeometry args={[radius, radius, length, 12]} />
      <meshStandardMaterial color={color} metalness={0.25} roughness={0.45} />
    </mesh>
  );
}
export function RigScene() {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Frame
      section="M08 / PROPOSED DIGITAL TEST RIG"
      title={"A complete loop.\nA testable design."}
      subtitle="12 m instrumented span, 12 m supply/return allowance, three joints and two controlled leak stations."
      label="DIGITAL DESIGN / NOT PHYSICALLY VALIDATED · PRESSURE TESTING NOT AUTHORIZED"
    >
      <div
        style={{
          position: "absolute",
          left: 520,
          top: 130,
          width: 1350,
          height: 850,
        }}
      >
        <Studio3D camera={[930, 700, 1150]}>
          <group
            position={[-550, 0, 0]}
            rotation={[0, 0.09 * Math.sin((f / fps) * 0.15), 0]}
          >
            <Link a={[0, 0, 0]} b={[1200, 0, 0]} />
            <Link a={[1200, 0, 0]} b={[1200, 0, 80]} />
            <Link a={[1200, 0, 80]} b={[0, 0, 80]} />
            <Link a={[0, 0, 80]} b={[-35, 0, 35]} />
            <Link a={[-35, 0, 35]} b={[0, 0, 0]} />
            <mesh position={[-35, 15, 35]}>
              <boxGeometry args={[50, 30, 50]} />
              <meshStandardMaterial color="#34778e" transparent opacity={0.8} />
            </mesh>
            <mesh
              position={[45, 0, 0]}
              rotation={[Math.PI / 2, 0, Math.PI / 2]}
            >
              <cylinderGeometry args={[12, 12, 35, 24]} />
              <meshStandardMaterial color="#d9a65c" />
            </mesh>
            {[300, 600, 900].map((x) => (
              <mesh key={x} position={[x, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
                <torusGeometry args={[3.3, 1.4, 10, 24]} />
                <meshStandardMaterial
                  color={x === 600 ? colors.cyan : "#afb8ba"}
                />
              </mesh>
            ))}
            {[600, 900].map((x) => (
              <Link
                key={x}
                a={[x, 0, 0]}
                b={[x, 0, -40]}
                color={colors.amber}
              />
            ))}
            <Link a={[80, 0, 0]} b={[80, 0, 50]} color={colors.amber} />
            <Link a={[80, 0, 50]} b={[-35, 0, 50]} color={colors.amber} />
            <Link a={[-35, 0, 50]} b={[-35, 0, 35]} color={colors.amber} />
            <Link a={[95, 0, 0]} b={[95, 0, -50]} color={colors.red} />
            <Link a={[95, 0, -50]} b={[-35, 0, -50]} color={colors.red} />
            <Link a={[-35, 0, -50]} b={[-35, 0, 35]} color={colors.red} />
            {/* Symbols follow the reviewed P&ID; their display size and station offsets are illustrative. */}
            {[
              { x: 160, z: 0 },
              { x: 160, z: 80 },
            ].map(({ x, z }) => (
              <group key={z}>
                <Link a={[x, 0, z]} b={[x, 25, z]} color={colors.cyan} />
                <mesh position={[x, 30, z]}>
                  <sphereGeometry args={[7, 16, 12]} />
                  <meshStandardMaterial color={colors.cyan} />
                </mesh>
                <mesh position={[x + 35, 0, z]}>
                  <boxGeometry args={[15, 12, 12]} />
                  <meshStandardMaterial color={colors.teal} />
                </mesh>
              </group>
            ))}
            <mesh position={[20, 0, 0]}>
              <boxGeometry args={[12, 9, 9]} />
              <meshStandardMaterial color="#b5c7cb" />
            </mesh>
            <mesh position={[1170, 0, 80]}>
              <boxGeometry args={[9, 15, 9]} />
              <meshStandardMaterial color={colors.amber} />
            </mesh>
            {[0, 1200].map((x) => (
              <mesh key={x} position={[x, 6, 0]}>
                <boxGeometry args={[11, 9, 11]} />
                <meshStandardMaterial color="#a898db" />
              </mesh>
            ))}
            {Array.from({ length: 35 }, (_, i) => {
              const x = ((i / 35 + f * 0.0006) % 1) * 1200;
              return (
                <group key={i}>
                  <mesh position={[x, 3, 0]}>
                    <sphereGeometry args={[2.5, 8, 6]} />
                    <meshBasicMaterial color={colors.cyan} />
                  </mesh>
                  <mesh position={[1200 - x, 3, 80]}>
                    <sphereGeometry args={[2.5, 8, 6]} />
                    <meshBasicMaterial color={colors.teal} />
                  </mesh>
                </group>
              );
            })}
          </group>
        </Studio3D>
      </div>
      <div
        style={{
          position: "absolute",
          left: 750,
          top: 190,
          color: "#bed6df",
          fontSize: 27,
        }}
      >
        SUPPLY → 12 m SPAN → FULL RETURN → RESERVOIR
      </div>
      <div
        style={{
          position: "absolute",
          left: 750,
          top: 720,
          fontSize: 25,
          lineHeight: 1.55,
          color: "#bdd2dc",
        }}
      >
        Joint positions: 3 / 6 / 9 m · GUARD-5: 6 m<br />
        Acoustic endpoints: 0 / 12 m · Reservoir: 75 L<br />
        Pressure + bulk flow at supply and return · Contained leak cups
        <br />
        <span style={{ color: colors.amber }}>Bypass</span> +{" "}
        <span style={{ color: colors.red }}>
          unisolatable mechanical relief
        </span>{" "}
        return to reservoir
        <br />
        Dry electrical zone: isolated 24 V supply, DC stop and fuses
        <br />
        <span style={{ fontSize: 21 }}>
          Schematic apparatus sizes / offsets; no operating pressure approved.
        </span>
      </div>
    </Frame>
  );
}
