"""
Ethos Kernel — Entry point.

Runs the 9 ethical complexity simulations as a **demo / smoke** of the decision pipeline
(no crash, coherent narrative). This is **not** an external ethical correctness benchmark:
invariant tests check internal rules; human-expert or cross-model benchmarks are separate
(see docs/proposals/README.md and scripts/run_empirical_pilot.py).

Usage:
    python -m src.main           # All simulations
    python -m src.main --sim 3   # Only simulation 3
"""

import sys

from .kernel import EthicalKernel
from .runtime_profiles import apply_named_runtime_profile_to_environ
from .simulations.runner import ALL_SIMULATIONS, run_simulation
from .validators.env_policy import validate_kernel_env


def banner() -> str:
    from .utils.terminal_colors import Term

    b_color = Term.B_CYAN + Term.BOLD
    v_color = Term.B_WHITE
    return f"""
+--------------------------------------------------------------+
|        ETHICAL ANDROID — MVP PROTOTYPE v5                    |
|        Artificial Conscience Kernel + LLM Layer              |
|        Ex Machina Foundation — 2026                          |
+--------------------------------------------------------------+

  Active modules:
    [x] Absolute Evil (hardened ethical fuse)
    [x] Preloaded Buffer (ethical constitution)
    [x] Impact evaluation (weighted mixture; BayesianEngine)
    [x] Ethical Poles (dynamic multipolar arbitration)
    [x] Sigmoid Will (decision function)
    [x] Sympathetic-Parasympathetic (body regulator)
    [x] Narrative Memory (identity through stories)
    [x] Uchi-Soto (trust circles)
    [x] Locus of Control (causal attribution)
    [x] Psi Sleep (retrospective audit)
    [x] Mock DAO (simulated ethical governance)
    [x] Bayesian Variability (controlled noise)
    [x] LLM Layer (natural language)
    [x] Weakness Pole (emotional coloring)             [NEW v5]
    [x] Algorithmic Forgiveness (memory decay)          [NEW v5]
    [x] Immortality Protocol (distributed backup)       [NEW v5]

  Running simulations...
"""


async def final_summary(kernel: EthicalKernel) -> None:
    """Displays day summary, Psi Sleep, and DAO status."""
    from .utils.terminal_colors import Term

    summary = kernel.memory.daily_summary()

    print(Term.header("Daily Summary Profile"))
    print(f"  {Term.color('Registered episodes:', Term.CYAN)} {summary['episodes']}")
    if summary["episodes"] > 0:
        print(
            f"  {Term.color('Average ethical score:', Term.CYAN)} {Term.highlight_impact(summary['average_score'])}"
        )
        print(
            f"  {Term.color('Minimum score:', Term.CYAN)}         {Term.highlight_impact(summary['min_score'])}"
        )
        print(
            f"  {Term.color('Maximum score:', Term.CYAN)}         {Term.highlight_impact(summary['max_score'])}"
        )
        print(f"  {Term.color('Decision modes:', Term.CYAN)}        {summary['modes']}")
        print(f"  {Term.color('Contexts faced:', Term.CYAN)}        {summary['contexts']}")

    # Execute Psi Sleep
    print(Term.subheader("Psi Sleep Retrospective"))
    sleep_out = await kernel.execute_sleep()
    print(f"  {Term.color(sleep_out, Term.ITALIC + Term.DIM)}")

    # DAO status
    print(Term.subheader("DAO Governance Ledger"))
    print(f"  {kernel.dao_status()}")

    print(Term.color("\n" + "=" * 70, Term.CYAN))
    print(
        Term.color(
            "  BEHAVIORAL COHERENCE: The same ethical principles produced", Term.BOLD + Term.B_WHITE
        )
    )
    print(
        Term.color(
            "  proportional responses at all levels of complexity.", Term.BOLD + Term.B_WHITE
        )
    )
    print(Term.color("=" * 70 + "\n", Term.CYAN))


def main():
    apply_named_runtime_profile_to_environ()
    
    import asyncio
    asyncio.run(_async_main())

async def _async_main():
    
    # 1. Environment validation
    validate_kernel_env()

    # 2. Kernel initialization
    kernel = EthicalKernel()
    print(banner())

    # 3. Simulation execution
    sim_idx = None
    if "--sim" in sys.argv:
        try:
            sim_idx = int(sys.argv[sys.argv.index("--sim") + 1])
        except (ValueError, IndexError):
            pass

    if sim_idx is not None:
        if sim_idx not in ALL_SIMULATIONS:
            print(
                f"Simulation {sim_idx} does not exist. Available: {sorted(ALL_SIMULATIONS)}."
            )
            sys.exit(1)
        result = run_simulation(kernel, sim_idx)
        print(result)
    else:
        for i in sorted(ALL_SIMULATIONS):
            result = run_simulation(kernel, i)
            print(result)

    await final_summary(kernel)


if __name__ == "__main__":
    main()
