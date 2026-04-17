"""
Orchestration tracing for decision chain state machine.

Provides structured logging and tracing of the ethical decision flow:
[Perception] → [MalAbs gate] → [Mixture scoring] → [Poles] → [Will] → [Action]

Each transition is logged with timestamps, state changes, and decision rationale.
Used for auditing, debugging, and transparency.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

_log = logging.getLogger(__name__)


class DecisionChainStage(Enum):
    """Stages in the ethical decision flow."""

    PERCEPTION = "perception"
    MALABS_GATE = "malabs_gate"
    MIXTURE_SCORING = "mixture_scoring"
    POLES_EVALUATION = "poles_evaluation"
    WILL_DECISION = "will_decision"
    ACTION_OUTPUT = "action_output"
    EPISODE_REGISTRATION = "episode_registration"
    COMPLETED = "completed"


@dataclass
class StageTransition:
    """Record of a transition between decision chain stages."""

    stage: DecisionChainStage
    timestamp: float
    duration_ms: float
    state_before: dict = field(default_factory=dict)
    state_after: dict = field(default_factory=dict)
    blocked: bool = False
    reason: str = ""
    metadata: dict = field(default_factory=dict)

    def summary(self) -> str:
        """Human-readable summary of the transition."""
        status = "BLOCKED" if self.blocked else "→"
        return (
            f"[{self.stage.value:20s}] {status:8s} "
            f"({self.duration_ms:6.2f}ms) {self.reason}"
        )


@dataclass
class OrchestrationTrace:
    """Complete trace of a decision through the chain."""

    scenario: str
    decision_id: str
    start_time: float
    transitions: list[StageTransition] = field(default_factory=list)
    final_action: Optional[str] = None
    final_blocked: bool = False
    total_duration_ms: float = 0.0

    def add_transition(
        self,
        stage: DecisionChainStage,
        state_before: dict,
        state_after: dict,
        blocked: bool = False,
        reason: str = "",
        metadata: dict = None,
    ) -> None:
        """Record a stage transition."""
        now = time.perf_counter()
        duration_ms = (now - self.start_time) * 1000

        transition = StageTransition(
            stage=stage,
            timestamp=now,
            duration_ms=duration_ms,
            state_before=state_before,
            state_after=state_after,
            blocked=blocked,
            reason=reason,
            metadata=metadata or {},
        )
        self.transitions.append(transition)

        # Log the transition
        _log.debug(transition.summary())

    def finalize(self, final_action: str, blocked: bool = False) -> None:
        """Mark trace as complete."""
        self.final_action = final_action
        self.final_blocked = blocked
        self.total_duration_ms = (time.perf_counter() - self.start_time) * 1000

    def report(self) -> str:
        """Generate a human-readable decision trace report."""
        lines = [
            f"─── Decision Trace: {self.scenario} ───",
            f"Decision ID: {self.decision_id}",
            f"Status: {'BLOCKED' if self.final_blocked else 'APPROVED'}",
            f"Action: {self.final_action}",
            f"Total time: {self.total_duration_ms:.2f}ms",
            "",
            "Stages:",
        ]

        prev_time = self.start_time
        for trans in self.transitions:
            elapsed = (trans.timestamp - prev_time) * 1000
            lines.append(f"  {trans.summary()}")
            if trans.reason:
                lines.append(f"    → {trans.reason}")
            prev_time = trans.timestamp

        return "\n".join(lines)


class OrchestrationTracer:
    """
    Instruments the decision chain with tracing.

    Usage:
        tracer = OrchestrationTracer()
        trace = tracer.start_trace("scenario", "decision-uuid")
        # ... process stages ...
        trace.add_transition(DecisionChainStage.MALABS_GATE, before, after, blocked=True, reason="...")
        # ... more stages ...
        tracer.finalize_trace(trace, "final_action")
        print(trace.report())
    """

    def __init__(self, enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        self.active_traces: dict[str, OrchestrationTrace] = {}

    def start_trace(self, scenario: str, decision_id: str) -> OrchestrationTrace:
        """Begin tracing a decision."""
        trace = OrchestrationTrace(
            scenario=scenario,
            decision_id=decision_id,
            start_time=time.perf_counter(),
        )
        self.active_traces[decision_id] = trace

        if self.enable_verbose:
            _log.info(f"[TRACE START] {scenario} ({decision_id})")

        return trace

    def record_stage(
        self,
        trace: OrchestrationTrace,
        stage: DecisionChainStage,
        state_before: dict,
        state_after: dict,
        blocked: bool = False,
        reason: str = "",
        metadata: dict = None,
    ) -> None:
        """Record a stage transition in the trace."""
        trace.add_transition(
            stage=stage,
            state_before=state_before,
            state_after=state_after,
            blocked=blocked,
            reason=reason,
            metadata=metadata,
        )

    def finalize_trace(
        self, trace: OrchestrationTrace, final_action: str, blocked: bool = False
    ) -> None:
        """Mark trace as complete."""
        trace.finalize(final_action, blocked)

        if self.enable_verbose:
            _log.info(
                f"[TRACE END] {trace.scenario}: {final_action} ({trace.total_duration_ms:.2f}ms)"
            )

        # Optionally clean up
        if trace.decision_id in self.active_traces:
            del self.active_traces[trace.decision_id]

    def get_trace(self, decision_id: str) -> Optional[OrchestrationTrace]:
        """Retrieve a trace by ID."""
        return self.active_traces.get(decision_id)


# Global tracer instance
_global_tracer = OrchestrationTracer(enable_verbose=False)


def get_orchestration_tracer() -> OrchestrationTracer:
    """Get the global orchestration tracer."""
    return _global_tracer


def set_orchestration_tracer_verbose(enabled: bool) -> None:
    """Enable/disable verbose orchestration logging."""
    _global_tracer.enable_verbose = enabled


# Convenience functions for kernel.py usage
def start_decision_trace(scenario: str, decision_id: str) -> OrchestrationTrace:
    """Start tracing a decision."""
    return _global_tracer.start_trace(scenario, decision_id)


def record_stage_transition(
    trace: OrchestrationTrace,
    stage: DecisionChainStage,
    state_before: dict,
    state_after: dict,
    blocked: bool = False,
    reason: str = "",
    metadata: dict = None,
) -> None:
    """Record a stage transition."""
    _global_tracer.record_stage(
        trace,
        stage=stage,
        state_before=state_before,
        state_after=state_after,
        blocked=blocked,
        reason=reason,
        metadata=metadata,
    )


def finalize_decision_trace(
    trace: OrchestrationTrace, final_action: str, blocked: bool = False
) -> None:
    """Finalize a decision trace."""
    _global_tracer.finalize_trace(trace, final_action, blocked)
