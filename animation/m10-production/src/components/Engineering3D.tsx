import React, { Suspense, useMemo, useEffect, useState } from "react";
import { ThreeCanvas } from "@remotion/three";
import { useLoader, useThree } from "@react-three/fiber";
import * as THREE from "three";
import {
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  delayRender,
  continueRender,
} from "remotion";
import { ease } from "./Design";

export function Studio3D({
  children,
  camera = [250, 160, 310],
}: {
  children: React.ReactNode;
  camera?: [number, number, number];
}) {
  const width = 1350;
  const height = 850;
  const [ready] = useState(() =>
    delayRender("Load and commit reviewed CAD scene"),
  );
  return (
    <ThreeCanvas
      width={width}
      height={height}
      camera={{ position: camera, fov: 36, near: 1, far: 2000 }}
      onCreated={({ camera: cam }) => cam.lookAt(0, 0, 0)}
      gl={{ antialias: true, alpha: true }}
    >
      <ambientLight intensity={1.4} />
      <directionalLight
        position={[80, 200, 180]}
        intensity={3.4}
        color="#bfeeff"
      />
      <directionalLight
        position={[-150, 90, -150]}
        intensity={3}
        color="#36c6e9"
      />
      <directionalLight
        position={[50, -70, 150]}
        intensity={0.8}
        color="#f5b64a"
      />
      <Suspense fallback={null}>
        {children}
        <Ready handle={ready} />
      </Suspense>
    </ThreeCanvas>
  );
}
function Ready({ handle }: { handle: number }) {
  const { advance } = useThree();
  useEffect(() => {
    advance(0);
    continueRender(handle);
  }, [handle, advance]);
  return null;
}
export function Tube({
  length = 260,
  radius = 16,
  opacity = 0.32,
}: {
  length?: number;
  radius?: number;
  opacity?: number;
}) {
  const geo = useMemo(() => {
    const shape = new THREE.Shape();
    shape.absarc(0, 0, radius, 0, Math.PI * 2, false);
    const hole = new THREE.Path();
    hole.absarc(0, 0, radius - 2, 0, Math.PI * 2, true);
    shape.holes.push(hole);
    const g = new THREE.ExtrudeGeometry(shape, {
      depth: length,
      bevelEnabled: false,
      curveSegments: 48,
    });
    g.translate(0, 0, -length / 2);
    return g;
  }, [length, radius]);
  return (
    <mesh geometry={geo}>
      <meshStandardMaterial
        color="#afc9d5"
        metalness={0.4}
        roughness={0.28}
        transparent
        opacity={opacity}
        depthWrite={false}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}
export function Flow({
  length = 260,
  radius = 12,
  speed = 1,
}: {
  length?: number;
  radius?: number;
  speed?: number;
}) {
  const f = useCurrentFrame();
  return (
    <group>
      {Array.from({ length: 42 }, (_, i) => {
        const phase = (i / 42 + f * 0.0015 * speed) % 1;
        const angle = i * 2.39996;
        const r = radius * Math.sqrt(((i % 7) + 1) / 8);
        return (
          <mesh
            key={i}
            position={[
              Math.cos(angle) * r,
              Math.sin(angle) * r,
              (phase - 0.5) * length,
            ]}
            scale={[0.65, 0.65, 2.8]}
          >
            <sphereGeometry args={[1.2, 8, 6]} />
            <meshBasicMaterial
              color="#54d9f5"
              transparent
              opacity={0.3 + 0.6 * Math.sin(phase * Math.PI)}
            />
          </mesh>
        );
      })}
    </group>
  );
}
type MeshData = { positions: number[]; indices: number[] };
function CadPart({ name, explode }: { name: string; explode: number }) {
  const raw = useLoader(
    THREE.FileLoader,
    staticFile(`cad/${name}.json`),
  ) as string;
  const geo = useMemo(() => {
    const data = JSON.parse(raw) as MeshData;
    const g = new THREE.BufferGeometry();
    g.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(data.positions, 3),
    );
    g.setIndex(data.indices);
    g.computeVertexNormals();
    return g;
  }, [raw]);
  const channel = name.includes("BYPASS")
    ? "BYPASS"
    : name.includes("EXT")
      ? "EXT"
      : name.match(/_(A|B|C)(_|$)/)?.[1];
  const tint = channel
    ? {
        A: "#39cbe9",
        B: "#7ea5f5",
        C: "#19b4a2",
        EXT: "#f5b64a",
        BYPASS: "#e66a68",
      }[channel]
    : "#879caa";
  const shell = name.startsWith("shell");
  const electrode = name.startsWith("electrode");
  const translation: [number, number, number] =
    name === "shell_upper"
      ? [0, explode * 65, 0]
      : name === "shell_lower"
        ? [0, -explode * 65, 0]
        : name.includes("EXT")
          ? [explode * 20, 0, 0]
          : name.includes("BYPASS")
            ? [0, -explode * 20, 0]
            : [0, 0, 0];
  return (
    <mesh geometry={geo} position={translation}>
      <meshStandardMaterial
        color={electrode ? "#d9bd75" : tint}
        metalness={electrode ? 0.75 : 0.18}
        roughness={shell ? 0.32 : 0.46}
      />
    </mesh>
  );
}
export function GuardModel({ exploded = true }: { exploded?: boolean }) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const raw = useLoader(
    THREE.FileLoader,
    staticFile("cad/manifest.json"),
  ) as string;
  const manifest = JSON.parse(raw) as { parts: { name: string }[] };
  const explode = exploded
    ? ease(f, fps * 1, fps * 3) * (1 - ease(f, fps * 7, fps * 9))
    : 0;
  return (
    <group rotation={[0, 0.25 + Math.sin((f / fps) * 0.12) * 0.16, 0]}>
      <Tube length={250} opacity={0.23} />
      <Flow length={250} />
      {manifest.parts.map((p) => (
        <CadPart key={p.name} name={p.name} explode={explode} />
      ))}
    </group>
  );
}
