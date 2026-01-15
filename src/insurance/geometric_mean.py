"""Geometric mean / expected log-wealth calculation.

This is the core of the Spitznagel "Tao of Capital" approach:

1. Geometric mean is dominated by the MINIMUM outcome
2. A single catastrophic outcome (W → 0) drives GM → 0
3. This naturally penalizes high-variance downside strategies

Key insight: Arithmetic mean can mislead. A strategy with high average
returns but occasional catastrophic losses will underperform a more
modest but consistent strategy over time.
"""

from __future__ import annotations

import math
from typing import List, Optional

from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan, total_annual_premium
from src.insurance.scenarios import Scenario, build_scenarios_for_plan


def compute_scenario_wealth(
    annual_income: float,
    annual_baseline_spend: float,
    total_premium: float,
    scenario_oop: float,
) -> float:
    """Compute remaining wealth for a single scenario.
    
    Wealth = Income - Baseline Spend - Premium - OOP
    
    Args:
        annual_income: Gross annual income
        annual_baseline_spend: Fixed non-health spending (rent, food, etc.)
        total_premium: Total insurance premium (medical + dental + vision)
        scenario_oop: Out-of-pocket healthcare costs for this scenario
        
    Returns:
        Remaining wealth after all costs
        
    Example:
        >>> wealth = compute_scenario_wealth(
        ...     annual_income=240_000,
        ...     annual_baseline_spend=120_000,
        ...     total_premium=24_000,
        ...     scenario_oop=5_000,
        ... )
        >>> print(f"Remaining: ${wealth:,.0f}")  # $91,000
    """
    return annual_income - annual_baseline_spend - total_premium - scenario_oop


def compute_expected_log_wealth(
    annual_income: float,
    annual_baseline_spend: float,
    plan: MedicalPlan,
    scenarios: List[Scenario],
    dental: Optional[DentalPlan] = None,
    vision: Optional[VisionPlan] = None,
) -> float:
    """Compute expected log-wealth (geometric mean objective).
    
    Uses EQUAL WEIGHTING across scenarios (Spitznagel approach).
    Probabilities in scenarios are for reference only.
    
    The formula is:
        E[log(W/W₀)] = (1/n) × Σᵢ log(Wᵢ/W₀)
    
    where:
        - Wᵢ = wealth in scenario i
        - W₀ = disposable income (income - baseline)
        - n = number of scenarios
    
    Args:
        annual_income: Gross annual income
        annual_baseline_spend: Fixed non-health spending (rent, food, etc.)
        plan: Medical plan to evaluate
        scenarios: List of possible outcomes
        dental: Optional dental add-on
        vision: Optional vision add-on
        
    Returns:
        Expected log of relative wealth: E[log(W/W₀)]
        
    Example:
        >>> scenarios = build_scenarios_for_plan(gold_ppo)
        >>> log_wealth = compute_expected_log_wealth(
        ...     annual_income=240_000,
        ...     annual_baseline_spend=120_000,
        ...     plan=gold_ppo,
        ...     scenarios=scenarios,
        ... )
    """
    # Compute total premium including add-ons
    premium = total_annual_premium(plan, dental, vision)
    
    # Add expected dental/vision OOP to each scenario
    addon_oop = 0.0
    if dental is not None:
        addon_oop += dental.expected_oop
    if vision is not None:
        addon_oop += vision.expected_oop
    
    # Disposable income (baseline for relative wealth)
    disposable = annual_income - annual_baseline_spend
    if disposable <= 0:
        return float("-inf")
    
    # Compute log-wealth for each scenario (EQUAL WEIGHTING)
    n = len(scenarios)
    if n == 0:
        return 0.0
    
    log_sum = 0.0
    for scenario in scenarios:
        # Total OOP for this scenario
        total_oop = scenario.total_oop + addon_oop
        
        # Remaining wealth
        wealth = compute_scenario_wealth(
            annual_income=annual_income,
            annual_baseline_spend=annual_baseline_spend,
            total_premium=premium,
            scenario_oop=total_oop,
        )
        
        # Relative wealth (fraction of disposable income)
        relative_wealth = wealth / disposable
        
        # Handle edge case: if wealth goes negative or zero
        if relative_wealth <= 0:
            return float("-inf")  # Any zero → GM = 0
        
        log_sum += math.log(relative_wealth)
    
    # Equal-weighted average of log-wealth
    return log_sum / n


def compute_geometric_mean_wealth(
    annual_income: float,
    annual_baseline_spend: float,
    plan: MedicalPlan,
    scenarios: List[Scenario],
    dental: Optional[DentalPlan] = None,
    vision: Optional[VisionPlan] = None,
) -> float:
    """Compute geometric mean wealth across scenarios.
    
    GM = exp(E[log(W/W₀)]) × W₀
    
    This is the dollar value that, if received with certainty,
    would provide the same expected log-utility as the uncertain
    outcomes across scenarios.
    
    Args:
        annual_income: Gross annual income
        annual_baseline_spend: Fixed non-health spending
        plan: Medical plan to evaluate
        scenarios: List of possible outcomes
        dental: Optional dental add-on
        vision: Optional vision add-on
        
    Returns:
        Geometric mean wealth in dollars
        
    Example:
        >>> gm = compute_geometric_mean_wealth(
        ...     annual_income=240_000,
        ...     annual_baseline_spend=120_000,
        ...     plan=gold_ppo,
        ...     scenarios=scenarios,
        ... )
        >>> print(f"GM Wealth: ${gm:,.0f}")
    """
    expected_log = compute_expected_log_wealth(
        annual_income=annual_income,
        annual_baseline_spend=annual_baseline_spend,
        plan=plan,
        scenarios=scenarios,
        dental=dental,
        vision=vision,
    )
    
    # Handle edge case
    if expected_log == float("-inf"):
        return 0.0
    
    # Disposable income as baseline
    disposable = annual_income - annual_baseline_spend
    
    # GM = exp(E[log(W/W₀)]) × W₀
    return math.exp(expected_log) * disposable
