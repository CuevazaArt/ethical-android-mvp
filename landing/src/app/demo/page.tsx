import Link from "next/link";

export default function DemoPage() {
  return (
    <div className="flex h-dvh flex-col bg-[#050508]">
      <header className="flex shrink-0 items-center justify-between border-b border-white/[0.08] px-4 py-3 md:px-5">
        <Link
          href="/"
          className="text-sm font-medium text-violet-300 transition hover:text-white"
        >
          ← Back
        </Link>
        <span className="text-xs text-zinc-500">Ethical Android — dashboard</span>
      </header>

      <section
        aria-labelledby="demo-intro-heading"
        lang="es"
        className="shrink-0 border-b border-white/[0.06] bg-[#07070c] px-4 py-4 md:px-5 md:py-5"
      >
        <h1
          id="demo-intro-heading"
          className="text-base font-semibold tracking-tight text-zinc-100 md:text-lg"
        >
          Qué estás viendo
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-zinc-400">
          Este panel recorre <strong className="font-medium text-zinc-300">situaciones inventadas</strong>{" "}
          — del día a día, con tensión o riesgo — como si pasaras tarjetas de{" "}
          <strong className="font-medium text-zinc-300">cuentos éticos</strong> ante un
          &ldquo;androide&rdquo; de investigación. Cada escena nueva pregunta cómo ese prototipo
          valoraría distintas respuestas. Los{" "}
          <strong className="font-medium text-zinc-300">números junto a cada acción</strong> son
          pistas sencillas de <em className="text-zinc-400">mejor o peor según este simulador</em>;
          lo que mide riesgo, calma o vulnerabilidad indica{" "}
          <strong className="font-medium text-zinc-300">qué tan cargado está el momento ficticio</strong>{" "}
          para el modelo — no es un juicio sobre ti.{" "}
          <span className="text-zinc-500">
            Nada de esto es consejo médico, legal ni para la vida real; el valor es que cualquier
            persona pueda <strong className="font-medium text-zinc-400">mirar dentro de una ética de máquina transparente</strong>, sin
            fórmulas ni tecnicismos.
          </span>
        </p>
      </section>

      <iframe
        src="/dashboard.html"
        title="Ethical Android interactive dashboard"
        className="min-h-0 w-full flex-1 border-0 bg-black"
      />
    </div>
  );
}
