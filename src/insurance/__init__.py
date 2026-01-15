"""Insurance plan analysis using geometric mean framework.

This package implements Spitznagel's Tao of Capital approach to evaluate
health insurance plans. The key insight: geometric mean is dominated by
the minimum outcome, so tail risk protection matters more than expected value.
"""

from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan
from src.insurance.scenarios import Scenario, build_scenarios_for_plan
from src.insurance.geometric_mean import (
    compute_expected_log_wealth,
    compute_geometric_mean_wealth,
    compute_scenario_wealth,
)
from src.insurance.compare import (
    compare_plans,
    PlanComparisonResult,
    format_comparison_table,
    format_scenario_breakdown,
)

__all__ = [
    "MedicalPlan",
    "DentalPlan", 
    "VisionPlan",
    "Scenario",
    "build_scenarios_for_plan",
    "compute_expected_log_wealth",
    "compute_geometric_mean_wealth",
    "compute_scenario_wealth",
    "compare_plans",
    "PlanComparisonResult",
    "format_comparison_table",
    "format_scenario_breakdown",
]
