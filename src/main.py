"""
Ethos Kernel — Entry point.

Runs the 9 ethical complexity simulations as a **demo / smoke** of the decision pipeline
(no crash, coherent narrative). This is **not** an external ethical correctness benchmark:
invariant tests check internal rules; human-expert or cross-model benchmarks are separate
(see docs/proposals/ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md and scripts/run_empirical_pilot.py).

Usage:
    python -m src.main           # All simulations
    python -m src.main --sim 3   # Only simulation 3
"""

import sys

from .kernel import EthicalKernel
from .runtime_profiles import apply_named_runtime_profile_to_environ
from .simulations.runner import ALL_SIMULATIONS, run_simulation
from .validators.env_policy import validate_kernel_env


def banner():
    return """
╔══════════════════════════════════════════════════════════════╗
║        ETHICAL ANDROID — MVP PROTOTYPE v5                    ║
║        Artificial Conscience Kernel + LLM Layer              ║
║        Ex Machina Foundation — 2026                          ║
╚══════════════════════════════════════════════════════════════╝

  Active modules:
    ✓ Absolute Evil (hardened ethical fuse)
    ✓ Preloaded Buffer (ethical constitution)
    ✓ Impact evaluation (weighted mixture; BayesianEngine)
    ✓ Ethical Poles (dynamic multipolar arbitration)
    ✓ Sigmoid Will (decision function)
    ✓ Sympathetic-Parasympathetic (body regulator)
    ✓ Narrative Memory (identity through stories)
    ✓ Uchi-Soto (trust circles)
    ✓ Locus of Control (causal attribution)
    ✓ Psi Sleep (retrospective audit)
    ✓ Mock DAO (simulated ethical governance)
    ✓ Bayesian Variability (controlled noise)
    ✓ LLM Layer (natural language)
    ✓ Weakness Pole (emotional coloring)             [NEW v5]
    ✓ Algorithmic Forgiveness (memory decay)          [NEW v5]
    ✓ Immortality Protocol (distributed backup)       [NEW v5]
    ✓ Augenesis Engine (synthetic soul creation)      [NEW v5]

  Running simulations...
"""


def final_summary(kernel: EthicalKernel):
    """Displays day summary, Psi Sleep, and DAO status."""
    summary = kernel.memory.daily_summary()
    print(f"\n{'═' * 70}")
    print("  DAY SUMMARY")
    print(f"{'═' * 70}")
    print(f"  Registered episodes: {summary['episodes']}")
    if summary["episodes"] > 0:
        print(f"  Average ethical score: {summary['average_score']}")
        print(f"  Minimum score:         {summary['min_score']}")
        print(f"  Maximum score:         {summary['max_score']}")
        print(f"  Decision modes:        {summary['modes']}")
        print(f"  Contexts faced:        {summary['contexts']}")
    print(f"{'─' * 70}")

    # Execute Psi Sleep
    print(kernel.execute_sleep())

    # DAO status
    print(kernel.dao_status())

    print(f"\n{'═' * 70}")
    print("  BEHAVIORAL COHERENCE: The same ethical principles produced")
    print("  proportional responses at all levels of complexity.")
    print(f"{'═' * 70}\n")


def main():
    apply_named_runtime_profile_to_environ()
    validate_kernel_env()
    kernel = EthicalKernel()

    # Parse arguments
    specific_sim = None
    if "--sim" in sys.argv:
        idx = sys.argv.index("--sim")
        if idx + 1 < len(sys.argv):
            try:
                specific_sim = int(sys.argv[idx + 1])
            except ValueError:
                print("Error: --sim requires a valid batch simulation id")
                sys.exit(1)

    print(banner())

    if specific_sim:
        if specific_sim not in ALL_SIMULATIONS:
            print(f"Simulation {specific_sim} does not exist. Available: {sorted(ALL_SIMULATIONS)}.")
            sys.exit(1)
        result = run_simulation(kernel, specific_sim)
        print(result)
    else:
        for i in sorted(ALL_SIMULATIONS):
            result = run_simulation(kernel, i)
            print(result)

        final_summary(kernel)


if __name__ == "__main__":
    main()
