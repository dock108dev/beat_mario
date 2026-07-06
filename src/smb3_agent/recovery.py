from __future__ import annotations

from dataclasses import dataclass

from smb3_agent.goals import GoalContract


SUPPORTED_SCENARIOS = {"life_lost", "wrong_map_node"}


class RecoveryError(ValueError):
    pass


@dataclass(frozen=True)
class RecoveryDecision:
    scenario: str
    goal: str
    decision: str
    action: str
    reason: str

    def to_text(self) -> str:
        return "\n".join(
            [
                f"scenario={self.scenario}",
                f"goal={self.goal}",
                f"decision={self.decision}",
                f"action={self.action}",
                f"reason={self.reason}",
            ]
        )


def simulate_recovery(contract: GoalContract, scenario: str) -> RecoveryDecision:
    if scenario not in SUPPORTED_SCENARIOS:
        raise RecoveryError(f"Unsupported recovery scenario: {scenario}")

    policy = contract.recovery_policy.get(scenario)
    if policy is None:
        return RecoveryDecision(
            scenario=scenario,
            goal=contract.id,
            decision="stop",
            action="capture_artifacts_and_stop",
            reason=f"No recovery policy is configured for {scenario}.",
        )

    action = str(policy.get("action"))
    if scenario == "life_lost":
        if policy.get("continue_if_contract_allows") is True:
            return RecoveryDecision(
                scenario=scenario,
                goal=contract.id,
                decision="continue_next_life",
                action=action,
                reason="Goal policy explicitly allows continuing after life loss when the route can be reclassified.",
            )
        return RecoveryDecision(
            scenario=scenario,
            goal=contract.id,
            decision="stop",
            action=action,
            reason="Goal policy does not allow continuing after life loss.",
        )

    if scenario == "wrong_map_node":
        if action == "correct_known_state_or_stop" and contract.constraints.get("allow_bridge_steps") is True:
            return RecoveryDecision(
                scenario=scenario,
                goal=contract.id,
                decision="correct_known_state",
                action=action,
                reason="Goal permits bridge/correction steps, so a known map correction is allowed instead of silent drift.",
            )
        return RecoveryDecision(
            scenario=scenario,
            goal=contract.id,
            decision="stop",
            action=action,
            reason="Bridge/correction steps are not allowed by the goal contract.",
        )

    raise RecoveryError(f"Unsupported recovery scenario: {scenario}")

