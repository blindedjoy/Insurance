"""Healthcare outcome scenarios for geometric mean calculation.

Scenarios represent possible healthcare states over a year.
We use EQUAL WEIGHTING across scenarios (Spitznagel approach)
rather than probability-weighted expectations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.insurance.plans import MedicalPlan


@dataclass
class Scenario:
    """A possible healthcare outcome scenario.
    
    Represents one possible outcome for the year. The probability field
    is for reference/documentation only - actual calculation uses equal
    weighting (Spitznagel's approach).
    
    Attributes:
        name: Scenario identifier
        probability: Reference probability (not used in calculation)
        medical_oop: Out-of-pocket medical costs for this scenario
        extra_oon: Additional out-of-network costs (e.g., post-stabilization)
    
    Example:
        >>> catastrophe = Scenario(
        ...     name="cat_in_network",
        ...     probability=0.03,
        ...     medical_oop=17_400.0,
        ... )
    """
    
    name: str
    probability: float  # Reference only - we use equal weighting
    medical_oop: float
    extra_oon: float = 0.0
    
    @property
    def total_oop(self) -> float:
        """Total out-of-pocket including extra OON costs."""
        return self.medical_oop + self.extra_oon


# Default scenario probabilities (for reference - not used in calculation)
DEFAULT_PROBABILITIES = {
    "no_use": 0.70,
    "minor_use": 0.25,
    "cat_in_network": 0.03,
    "cat_oon_emergency": 0.02,
}


def build_scenarios_for_plan(plan: MedicalPlan) -> List[Scenario]:
    """Build scenario list with plan-specific OOP values.
    
    Creates the four standard scenarios with OOP values derived from
    the plan's cost-sharing structure:
    
    1. no_use: $0 medical OOP (healthy year)
    2. minor_use: plan.expected_minor_oop (typical usage)
    3. cat_in_network: plan.in_network_oop_max (catastrophe in-network)
    4. cat_oon_emergency: OOP max + post-stabilization exposure
    
    Args:
        plan: Medical plan to build scenarios for
        
    Returns:
        List of 4 Scenario objects with plan-specific values
        
    Example:
        >>> scenarios = build_scenarios_for_plan(gold_ppo)
        >>> for s in scenarios:
        ...     print(f"{s.name}: ${s.total_oop:,.0f}")
    """
    scenarios = []
    
    # Scenario 1: No healthcare use (healthy year)
    scenarios.append(Scenario(
        name="no_use",
        probability=DEFAULT_PROBABILITIES["no_use"],
        medical_oop=0.0,
        extra_oon=0.0,
    ))
    
    # Scenario 2: Minor use (typical year - checkups, minor issues)
    scenarios.append(Scenario(
        name="minor_use",
        probability=DEFAULT_PROBABILITIES["minor_use"],
        medical_oop=plan.expected_minor_oop,
        extra_oon=0.0,
    ))
    
    # Scenario 3: Catastrophic event, in-network (surgery, hospitalization)
    scenarios.append(Scenario(
        name="cat_in_network",
        probability=DEFAULT_PROBABILITIES["cat_in_network"],
        medical_oop=plan.in_network_oop_max,
        extra_oon=0.0,
    ))
    
    # Scenario 4: Catastrophic event, out-of-network (Colorado accident)
    # Emergency portion treated as in-network (No Surprises Act)
    # Post-stabilization may not be covered
    if plan.oon_emergency_treated_as_in_network:
        emergency_oop = plan.in_network_oop_max
    else:
        # Would need separate OON OOP max - rare on exchange plans
        emergency_oop = plan.in_network_oop_max * 2  # Conservative estimate
    
    if plan.post_stabilization_oon_covered:
        post_stab_extra = 0.0
    else:
        post_stab_extra = plan.post_stabilization_exposure
    
    scenarios.append(Scenario(
        name="cat_oon_emergency",
        probability=DEFAULT_PROBABILITIES["cat_oon_emergency"],
        medical_oop=emergency_oop,
        extra_oon=post_stab_extra,
    ))
    
    return scenarios
