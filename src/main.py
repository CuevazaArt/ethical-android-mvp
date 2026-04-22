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


def banner():
    from .utils.terminal_colors import Term

    b_color = Term.B_CYAN + Term.BOLD
    v_color = Term.B_WHITE
    return f"""
{Term.color("╔══════════════════════════════════════════════════════════════╗", b_color)}
{Term.color("║", b_color)}        {Term.color("ETHICAL ANDROID — MVP PROTOTYPE v5", b_color)}                    {Term.color("║", b_color)}
{Term.color("║", b_color)}        {Term.color("Artificial Conscience Kernel + LLM Layer", v_color)}              {Term.color("║", b_color)}
{Term.color("║", b_color)}        {Term.color("Ex Machina Foundation — 2026", Term.DIM)}                          {Term.color("║", b_color)}
{Term.color("╚══════════════════════════════════════════════════════════════╝", b_color)}

  {Term.color("Active modules:", Term.BOLD + Term.CYAN)}
    {Term.color("✓", Term.GREEN)} Absolute Evil (hardened ethical fuse)
    {Term.color("✓", Term.GREEN)} Preloaded Buffer (ethical constitution)
    {Term.color("✓", Term.GREEN)} Impact evaluation (weighted mixture; BayesianEngine)
    {Term.color("✓", Term.GREEN)} Ethical Poles (dynamic multipolar arbitration)
    {Term.color("✓", Term.GREEN)} Sigmoid Will (decision function)
    {Term.color("✓", Term.GREEN)} Sympathetic-Parasympathetic (body regulator)
    {Term.color("✓", Term.GREEN)} Narrative Memory (identity through stories)
    {Term.color("✓", Term.GREEN)} Uchi-Soto (trust circles)
    {Term.color("✓", Term.GREEN)} Locus of Control (causal attribution)
    {Term.color("✓", Term.GREEN)} Psi Sleep (retrospective audit)
    {Term.color("✓", Term.GREEN)} Mock DAO (simulated ethical governance)
    {Term.color("✓", Term.GREEN)} Bayesian Variability (controlled noise)
    {Term.color("✓", Term.GREEN)} LLM Layer (natural language)
    {Term.color("✓", Term.GREEN)} Weakness Pole (emotional coloring)             {Term.color("[NEW v5]", Term.B_YELLOW)}
    {Term.color("✓", Term.GREEN)} Algorithmic Forgiveness (memory decay)          {Term.color("[NEW v5]", Term.B_YELLOW)}
    {Term.color("✓", Term.GREEN)} Immortality Protocol (distributed backup)       {Term.color("[NEW v5]", Term.B_YELLOW)}

  {Term.color("Running simulations...", Term.ITALIC + Term.DIM)}
"""


def final_summary(kernel: EthicalKernel):
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
    print(f"  {Term.color(kernel.execute_sleep(), Term.ITALIC + Term.DIM)}")

    # DAO status
    print(Term.subheader("DAO Governance Ledger"))
    print(f"  {kernel.dao_status()}")

    print(Term.color("\n" + "═" * 70, Term.CYAN))
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
    print(Term.color("═" * 70 + "\n", Term.CYAN))


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
            print(
                f"Simulation {specific_sim} does not exist. Available: {sorted(ALL_SIMULATIONS)}."
            )
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
