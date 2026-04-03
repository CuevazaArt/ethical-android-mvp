"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { useMemo, useRef } from "react";
import {
  Mesh,
  MeshStandardMaterial,
  Object3D,
  PointLight,
  SphereGeometry,
  TorusGeometry,
} from "three";
import type { InstancedMesh as InstancedMeshType, MeshStandardMaterial as MeshStdMat } from "three";

const dummy = new Object3D();

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
    <mesh ref={ref}>
      <icosahedronGeometry args={[1.15, 1]} />
      <meshStandardMaterial
        color="#86efac"
        wireframe
        emissive="#14532d"
        emissiveIntensity={0.65}
        metalness={0.15}
        roughness={0.4}
      />
    </mesh>
  );
}

function OuterLatticeShell() {
  const ref = useRef<Mesh>(null);
  useFrame((state) => {
    const m = ref.current;
    if (!m) return;
    const t = state.clock.elapsedTime;
    m.rotation.x = -t * 0.07;
    m.rotation.y = -t * 0.11;
    m.rotation.z = t * 0.04;
  });
  return (
    <mesh ref={ref} scale={1.52}>
      <icosahedronGeometry args={[1, 0]} />
      <meshStandardMaterial
        color="#4ade80"
        wireframe
        emissive="#052e16"
        emissiveIntensity={0.35}
        metalness={0.1}
        roughness={0.55}
        transparent
        opacity={0.42}
        depthWrite={false}
      />
    </mesh>
  );
}

function InnerCore() {
  const meshRef = useRef<Mesh>(null);
  const matRef = useRef<MeshStdMat>(null);
  useFrame((state) => {
    const m = meshRef.current;
    if (!m) return;
    const t = state.clock.elapsedTime;
    m.rotation.x = -t * 0.08;
    m.rotation.z = t * 0.1;
    const mat = matRef.current;
    if (mat) {
      const pulse = 0.42 + Math.sin(t * 1.6) * 0.14;
      mat.emissiveIntensity = pulse;
    }
  });
  return (
    <mesh ref={meshRef} scale={0.42}>
      <icosahedronGeometry args={[1, 0]} />
      <meshStandardMaterial
        ref={matRef}
        color="#fdba74"
        emissive="#c2410c"
        emissiveIntensity={0.5}
        metalness={0.45}
        roughness={0.28}
        transparent
        opacity={0.9}
      />
    </mesh>
  );
}

type OrbitCfg = {
  phase: number;
  radius: number;
  speed: number;
  tilt: number;
  wobble: number;
  spin: number;
};

function buildOrbitConfig(count: number, radiusFn: (ring: number, i: number) => number): OrbitCfg[] {
  const rings = 5;
  const perRing = Math.ceil(count / rings);
  return Array.from({ length: count }, (_, i) => {
    const ring = i % rings;
    const idx = Math.floor(i / rings);
    return {
      phase: (idx / perRing) * Math.PI * 2,
      radius: radiusFn(ring, i),
      speed: 0.2 + ring * 0.055 + (i % 3) * 0.025,
      tilt: (ring / rings) * Math.PI * 0.9,
      wobble: 0.1 + (i % 7) * 0.018,
      spin: (i % 5) * 0.17,
    };
  });
}

function OrbitalParticleField({ count = 88 }: { count?: number }) {
  const ref = useRef<InstancedMeshType>(null);
  const { geometry, material } = useMemo(() => {
    return {
      geometry: new SphereGeometry(1, 14, 14),
      material: new MeshStandardMaterial({
        color: "#ecfdf5",
        emissive: "#059669",
        emissiveIntensity: 0.95,
        metalness: 0.42,
        roughness: 0.3,
      }),
    };
  }, []);
  const cfg = useMemo(
    () => buildOrbitConfig(count, (ring) => 1.2 + ring * 0.13),
    [count],
  );

  useFrame((state) => {
    const mesh = ref.current;
    if (!mesh) return;
    const t = state.clock.elapsedTime;
    for (let i = 0; i < count; i++) {
      const c = cfg[i];
      const angle = c.phase + t * c.speed;
      const r = c.radius + Math.sin(t * 0.55 + c.spin) * 0.055;
      const x = Math.cos(angle) * r;
      let z = Math.sin(angle) * r;
      let y = Math.sin(angle * 2 + i * 0.18) * c.wobble;
      const cosT = Math.cos(c.tilt);
      const sinT = Math.sin(c.tilt);
      const zp = z * cosT - y * sinT;
      const yp = z * sinT + y * cosT;
      z = zp;
      y = yp;
      dummy.position.set(x, y, z);
      dummy.scale.setScalar(0.02 + (i % 6) * 0.004);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  });

  return <instancedMesh ref={ref} args={[geometry, material, count]} />;
}

function InnerDataMotes({ count = 26 }: { count?: number }) {
  const ref = useRef<InstancedMeshType>(null);
  const { geometry, material } = useMemo(() => {
    return {
      geometry: new SphereGeometry(1, 10, 10),
      material: new MeshStandardMaterial({
        color: "#ffedd5",
        emissive: "#ea580c",
        emissiveIntensity: 0.85,
        metalness: 0.35,
        roughness: 0.35,
      }),
    };
  }, []);
  const cfg = useMemo(
    () => buildOrbitConfig(count, (ring) => 0.62 + ring * 0.05),
    [count],
  );

  useFrame((state) => {
    const mesh = ref.current;
    if (!mesh) return;
    const t = state.clock.elapsedTime;
    for (let i = 0; i < count; i++) {
      const c = cfg[i];
      const angle = c.phase - t * (c.speed * 1.35);
      const r = c.radius + Math.sin(t * 1.1 + i) * 0.035;
      let x = Math.cos(angle) * r;
      const z = Math.sin(angle) * r;
      let y = Math.sin(angle * 3 + c.spin) * c.wobble * 0.85;
      const tilt = c.tilt * 0.65;
      const cosT = Math.cos(tilt);
      const sinT = Math.sin(tilt);
      const xp = x * cosT - y * sinT;
      const yp = x * sinT + y * cosT;
      x = xp;
      y = yp;
      dummy.position.set(x, y, z);
      dummy.scale.setScalar(0.012 + (i % 4) * 0.003);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  });

  return <instancedMesh ref={ref} args={[geometry, material, count]} />;
}

function AccretionRings() {
  const g1 = useMemo(() => new TorusGeometry(1.68, 0.014, 8, 160), []);
  const g2 = useMemo(() => new TorusGeometry(1.88, 0.011, 8, 128), []);
  const g3 = useMemo(() => new TorusGeometry(1.42, 0.009, 8, 96), []);
  const matA = useMemo(
    () =>
      new MeshStandardMaterial({
        color: "#fde68a",
        emissive: "#b45309",
        emissiveIntensity: 0.45,
        metalness: 0.5,
        roughness: 0.35,
        transparent: true,
        opacity: 0.55,
      }),
    [],
  );
  const matB = useMemo(
    () =>
      new MeshStandardMaterial({
        color: "#6ee7b7",
        emissive: "#065f46",
        emissiveIntensity: 0.35,
        metalness: 0.25,
        roughness: 0.45,
        transparent: true,
        opacity: 0.35,
        depthWrite: false,
      }),
    [],
  );

  const r1 = useRef<Mesh>(null);
  const r2 = useRef<Mesh>(null);
  const r3 = useRef<Mesh>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    const a = r1.current;
    const b = r2.current;
    const c = r3.current;
    if (a) {
      a.rotation.x = Math.PI / 2.35 + Math.sin(t * 0.08) * 0.06;
      a.rotation.y = t * 0.09;
    }
    if (b) {
      b.rotation.x = Math.PI / 2.9;
      b.rotation.z = -t * 0.12;
    }
    if (c) {
      c.rotation.x = Math.PI / 2.15;
      c.rotation.y = t * 0.15;
      c.rotation.z = Math.sin(t * 0.2) * 0.12;
    }
  });

  return (
    <group>
      <mesh ref={r1} geometry={g1} material={matA} />
      <mesh ref={r2} geometry={g2} material={matB} />
      <mesh ref={r3} geometry={g3} material={matB} />
    </group>
  );
}

function DynamicRimLight() {
  const ref = useRef<PointLight>(null);
  useFrame((state) => {
    const L = ref.current;
    if (!L) return;
    const t = state.clock.elapsedTime;
    L.position.set(Math.sin(t * 0.45) * 3.2, 1.4 + Math.sin(t * 0.31) * 0.6, Math.cos(t * 0.38) * 2.8);
    L.intensity = 1.25 + Math.sin(t * 2.1) * 0.25;
  });
  return <pointLight ref={ref} distance={14} decay={2} color="#fed7aa" />;
}

function SceneContent() {
  return (
    <Float speed={1.65} rotationIntensity={0.22} floatIntensity={0.42}>
      <group>
        <OuterLatticeShell />
        <AccretionRings />
        <OrbitalParticleField count={88} />
        <InnerDataMotes count={26} />
        <EthicalLattice />
        <InnerCore />
      </group>
    </Float>
  );
}

export default function HeroCanvas() {
  return (
    <div className="pointer-events-none absolute inset-0 h-full min-h-[420px] w-full md:min-h-0">
      <Canvas
        camera={{ position: [0, 0, 4.35], fov: 42 }}
        gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.28} />
        <pointLight position={[5, 4, 6]} intensity={1.45} color="#fef3c7" />
        <pointLight position={[-4, -2, 4]} intensity={1} color="#bbf7d0" />
        <DynamicRimLight />
        <SceneContent />
      </Canvas>
    </div>
  );
}
