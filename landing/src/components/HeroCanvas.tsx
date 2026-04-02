"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { useRef } from "react";
import type { Mesh } from "three";

function EthicalLattice() {
  const ref = useRef<Mesh>(null);
  useFrame((state) => {
    const m = ref.current;
    if (!m) return;
    const t = state.clock.elapsedTime;
    m.rotation.x = t * 0.12;
    m.rotation.y = t * 0.2;
  });
  return (
    <Float speed={1.8} rotationIntensity={0.25} floatIntensity={0.45}>
      <mesh ref={ref}>
        <icosahedronGeometry args={[1.15, 1]} />
        <meshStandardMaterial
          color="#5b8def"
          wireframe
          emissive="#1e3a6e"
          emissiveIntensity={0.55}
          metalness={0.2}
          roughness={0.35}
        />
      </mesh>
    </Float>
  );
}

function InnerCore() {
  const ref = useRef<Mesh>(null);
  useFrame((state) => {
    const m = ref.current;
    if (!m) return;
    const t = state.clock.elapsedTime;
    m.rotation.x = -t * 0.08;
    m.rotation.z = t * 0.1;
  });
  return (
    <mesh ref={ref} scale={0.42}>
      <icosahedronGeometry args={[1, 0]} />
      <meshStandardMaterial
        color="#c4b5fd"
        emissive="#6d28d9"
        emissiveIntensity={0.35}
        metalness={0.6}
        roughness={0.25}
        transparent
        opacity={0.85}
      />
    </mesh>
  );
}

export default function HeroCanvas() {
  return (
    <div className="pointer-events-none absolute inset-0 h-full min-h-[420px] w-full md:min-h-0">
      <Canvas
        camera={{ position: [0, 0, 4.2], fov: 42 }}
        gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.35} />
        <pointLight position={[5, 4, 6]} intensity={1.8} color="#93c5fd" />
        <pointLight position={[-4, -2, 4]} intensity={0.9} color="#c4b5fd" />
        <EthicalLattice />
        <InnerCore />
      </Canvas>
    </div>
  );
}
