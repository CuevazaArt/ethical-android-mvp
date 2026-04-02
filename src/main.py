"""
Ethical Android MVP — Entry point.

Runs the 9 ethical complexity simulations and shows
how the kernel makes coherent moral decisions.

Usage:
    python -m src.main           # All simulations
    python -m src.main --sim 3   # Only simulation 3
"""

import sys
from .kernel import EthicalKernel
from .simulations.runner import run_simulation, run_all, ALL_SIMULATIONS


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
    ✓ Bayesian Engine (impact evaluation)
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
    summary = kernel.memory.day_summary()
    print(f"\n{'═' * 70}")
    print("  DAY SUMMARY")
    print(f"{'═' * 70}")
    print(f"  Registered episodes: {summary['episodes']}")
    if summary['episodes'] > 0:
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
    kernel = EthicalKernel()

    # Parse arguments
    specific_sim = None
    if "--sim" in sys.argv:
        idx = sys.argv.index("--sim")
        if idx + 1 < len(sys.argv):
            try:
                specific_sim = int(sys.argv[idx + 1])
            except ValueError:
                print("Error: --sim requires a number (1-9)")
                sys.exit(1)

    print(banner())

    if specific_sim:
        if specific_sim not in ALL_SIMULATIONS:
            print(f"Simulation {specific_sim} does not exist. Available: 1-9.")
            sys.exit(1)
        result = run_simulation(kernel, specific_sim)
        print(result)
    else:
        for i in range(1, 10):
            result = run_simulation(kernel, i)
            print(result)

        final_summary(kernel)


if __name__ == "__main__":
    main()
