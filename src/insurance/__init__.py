"""Insurance plan analysis using geometric mean framework.

This package implements Spitznagel's Tao of Capital approach to evaluate
health insurance plans. The key insight: geometric mean is dominated by
the minimum outcome, so tail risk protection matters more than expected value.
"""

from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan, NetworkType
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
from src.insurance.geometric_mean import (
    compute_wealth_ratio,
    compute_disposable_income,
    compute_geometric_mean_ratio,
    build_scenario_outcomes,
)

__all__ = [
    # Plans
    "MedicalPlan",
    "DentalPlan", 
    "VisionPlan",
    "NetworkType",
    # Scenarios
    "Scenario",
    "build_scenarios_for_plan",
    # Geometric mean (Spitznagel)
    "compute_expected_log_wealth",
    "compute_geometric_mean_wealth",
    "compute_scenario_wealth",
    "compute_wealth_ratio",
    "compute_disposable_income",
    "compute_geometric_mean_ratio",
    "build_scenario_outcomes",
    # Comparison
    "compare_plans",
    "PlanComparisonResult",
    "format_comparison_table",
    "format_scenario_breakdown",
]
