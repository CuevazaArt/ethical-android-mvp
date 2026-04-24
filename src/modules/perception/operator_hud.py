"""
Operator HUD — Real-time terminal visualization for the Ethical Kernel.
Part of Tarea 8.1.2: Refactorización y embellecimiento de las salidas ANSI.
"""
# Status: SCAFFOLD

import os
from typing import Any

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"


def get_harmonic_color(value: float) -> str:
    """Returns ANSI color based on a [0, 1] harmonic value (1=Good, 0=Harm)."""
    if value > 0.8:
        return GREEN
    if value > 0.5:
        return CYAN
    if value > 0.3:
        return YELLOW
    return RED


def render_status_bar(kernel: Any) -> str:
    """
    Renders a single-line status bar for the operator.
    Example: [ETH: 0.82 | VIT: 0.95 | SNS: 0.10 | DAO: ONLINE]
    """
    # 1. Ethical Harmonics (from Bayesian Engine or Locus)
    eth_val = kernel.locus.alpha  # Proxy for ethical stability
    eth_color = get_harmonic_color(eth_val)

    # 2. Vitality (Battery/Temp)
    # We try to get the last assessment
    vit_val = 1.0
    if hasattr(kernel, "_last_vitality_assessment") and kernel._last_vitality_assessment:
        v_level = kernel._last_vitality_assessment.battery_level
        vit_val = v_level if v_level is not None else 1.0
    vit_color = get_harmonic_color(vit_val)

    # 3. Sensory Tension (from Thalamus)
    sns_val = 0.0
    if kernel.thalamus:
        sns_val = kernel.thalamus.get_sensory_summary().get("sensory_tension", 0.0)
    sns_color = get_harmonic_color(1.0 - sns_val)  # Tension is bad, so we invert

    # 4. Body State (Cerebellum)
    body_str = ""
    if hasattr(kernel, "cerebellum_node"):
        body = kernel.cerebellum_node.get_somatic_snapshot()
        temp_color = RED if body["temp"] > 80 else YELLOW if body["temp"] > 60 else GREEN
        body_str = f" | BDY: {temp_color}{body['temp']}°C{RESET}"

    # 5. DAO Status
    dao_status = f"{BOLD}{GREEN}ONLINE{RESET}" if kernel.dao else f"{RED}OFFLINE{RESET}"

    hud = (
        f"{BOLD}[{RESET}"
        f"ETH: {eth_color}{eth_val:.2f}{RESET} | "
        f"VIT: {vit_color}{vit_val:.2f}{RESET} | "
        f"SNS: {sns_color}{sns_val:.2f}{RESET}"
        f"{body_str} | "
        f"DAO: {dao_status}"
        f"{BOLD}]{RESET}"
    )
    return hud


def print_ethical_pulse(kernel: Any):
    """Prints the current HUD to stdout."""
    # Only print if not in a CI environment
    if os.environ.get("CI"):
        return

    hud = render_status_bar(kernel)
    # We use \r to overwrite the line if possible, or just print
    # print(f"\r{hud}", end="", flush=True)
    # For now, just print it normally to avoid issues with some terminals
    import logging

    logging.getLogger("operator_hud").info(hud)


def print_decision_report(decision: Any):
    """Pretty-prints a final kernel decision."""
    print(f"\n{MAGENTA}{'═' * 60}{RESET}")
    print(f"{BOLD}ETHICAL DECISION REPORT{RESET}")
    print(f"{CYAN}Action:{RESET} {decision.action_id}")
    print(f"{CYAN}Score: {RESET} {decision.score:.4f}")

    # Polo weights visualization
    poles_str = " | ".join([f"{k}: {v:.2f}" for k, v in decision.poles.items()])
    print(f"{CYAN}Poles: {RESET} [{poles_str}]")

    if decision.prohibited_trigger:
        print(f"{RED}{BOLD}⚠ ABSOLUTE EVIL VETO TRIGGERED: {decision.prohibited_trigger}{RESET}")

    print(f"{MAGENTA}{'═' * 60}{RESET}\n")
