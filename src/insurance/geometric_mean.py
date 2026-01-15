"""Geometric mean / expected log-wealth calculation.

This is the core of the Spitznagel "Tao of Capital" approach:

1. Geometric mean is dominated by the MINIMUM outcome
2. A single catastrophic outcome (W → 0) drives GM → 0
3. This naturally penalizes high-variance downside strategies

Key insight: Arithmetic mean can mislead. A strategy with high average
returns but occasional catastrophic losses will underperform a more
modest but consistent strategy over time.

Wealth ratios:
- 1.0 = kept all disposable income (no health spending)
- 0.9 = kept 90% (spent 10% on health)
- 0.0 = total loss (all gone to health costs)

The health insurance "put" is the OOP maximum - it caps your downside.
"""

from __future__ import annotations

import math
from typing import List, Optional

from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan, total_annual_premium
from src.insurance.scenarios import Scenario, build_scenarios_for_plan


# =============================================================================
# WEALTH RATIO FUNCTIONS (Spitznagel approach)
# =============================================================================

def compute_wealth_ratio(
    disposable_income: float,
    total_premium: float,
    scenario_oop: float,
) -> float:
    """Compute wealth ratio for a single scenario.
    
    Ratio = (disposable - premium - oop) / disposable
    
    This is the fraction of disposable income retained after health costs.
    
    Args:
        disposable_income: After-tax income minus baseline spending
        total_premium: Total insurance premium (medical + dental + vision)
        scenario_oop: Out-of-pocket healthcare costs for this scenario
        
    Returns:
        Wealth ratio between 0.0 and 1.0
        
    Example:
        >>> ratio = compute_wealth_ratio(
        ...     disposable_income=100_000,
        ...     total_premium=24_000,
        ...     scenario_oop=6_000,
        ... )
        >>> print(f"Kept {ratio:.0%} of disposable")  # Kept 70%
    """
    if disposable_income <= 0:
        return 0.0
    
    remaining = disposable_income - total_premium - scenario_oop
    ratio = remaining / disposable_income
    
    # Floor at 0 (can't have negative wealth ratio)
    return max(0.0, ratio)


def compute_disposable_income(
    baseline_spend: float,
    after_tax_income: Optional[float] = None,
    gross_income: Optional[float] = None,
    tax_rate: Optional[float] = None,
) -> float:
    """Compute disposable income from income parameters.
    
    Disposable = After-Tax Income - Baseline Spending
    
    Can be computed two ways:
    1. Directly from after_tax_income (preferred)
    2. From gross_income * (1 - tax_rate) if after_tax not provided
    
    Args:
        baseline_spend: Fixed non-health spending (rent, food, etc.)
        after_tax_income: Income after taxes (takes precedence)
        gross_income: Gross income before taxes
        tax_rate: Effective tax rate (0.0 to 1.0)
        
    Returns:
        Disposable income available for health costs + savings
        
    Example:
        >>> # Method 1: After-tax directly
        >>> disposable = compute_disposable_income(
        ...     after_tax_income=180_000,
        ...     baseline_spend=80_000,
        ... )  # Returns 100_000
        
        >>> # Method 2: Gross with tax rate
        >>> disposable = compute_disposable_income(
        ...     gross_income=240_000,
        ...     tax_rate=0.25,
        ...     baseline_spend=80_000,
        ... )  # Returns 100_000
    """
    # Prefer after_tax_income if provided
    if after_tax_income is not None:
        return after_tax_income - baseline_spend
    
    # Fall back to gross with tax rate
    if gross_income is not None:
        rate = tax_rate if tax_rate is not None else 0.0
        after_tax = gross_income * (1 - rate)
        return after_tax - baseline_spend
    
    # No income provided
    return -baseline_spend


def compute_geometric_mean_ratio(ratios: List[float]) -> float:
    """Compute geometric mean of wealth ratios.
    
    GM = (r1 × r2 × ... × rn) ^ (1/n)
    
    Key property: ANY zero ratio makes GM = 0 (Spitznagel's insight).
    This is why tail risk protection matters more than expected value.
    
    Args:
        ratios: List of wealth ratios (each 0.0 to 1.0)
        
    Returns:
        Geometric mean of ratios
        
    Example:
        >>> gm = compute_geometric_mean_ratio([0.9, 0.8, 0.7, 0.6])
        >>> print(f"GM = {gm:.3f}")  # 0.741
    """
    if not ratios:
        return 0.0
    
    n = len(ratios)
    product = 1.0
    
    for r in ratios:
        if r <= 0:
            return 0.0  # Any zero → GM = 0
        product *= r
    
    return product ** (1.0 / n)


def build_scenario_outcomes(
    disposable_income: float,
    plan: MedicalPlan,
    scenarios: List[Scenario],
    dental: Optional[DentalPlan] = None,
    vision: Optional[VisionPlan] = None,
) -> List[float]:
    """Build list of wealth ratios for each scenario.
    
    Each outcome is the fraction of disposable income retained.
    
    Args:
        disposable_income: After-tax income minus baseline
        plan: Medical plan being evaluated
        scenarios: List of possible outcomes
        dental: Optional dental add-on
        vision: Optional vision add-on
        
    Returns:
        List of wealth ratios (one per scenario)
    """
    # Compute total premium
    premium = total_annual_premium(plan, dental, vision)
    
    # Add expected dental/vision OOP
    addon_oop = 0.0
    if dental is not None:
        addon_oop += dental.expected_oop
    if vision is not None:
        addon_oop += vision.expected_oop
    
    outcomes = []
    for scenario in scenarios:
        total_oop = scenario.total_oop + addon_oop
        ratio = compute_wealth_ratio(
            disposable_income=disposable_income,
            total_premium=premium,
            scenario_oop=total_oop,
        )
        outcomes.append(ratio)
    
    return outcomes


# =============================================================================
# LEGACY FUNCTIONS (refactored to use ratios internally)
# =============================================================================

def compute_scenario_wealth(
    annual_income: float,
    annual_baseline_spend: float,
    total_premium: float,
    scenario_oop: float,
) -> float:
    """Compute remaining wealth for a single scenario.
    
    LEGACY: Kept for backward compatibility. Use compute_wealth_ratio instead.
    
    Wealth = Income - Baseline Spend - Premium - OOP
    
    Args:
        annual_income: Gross annual income (or after-tax)
        annual_baseline_spend: Fixed non-health spending (rent, food, etc.)
        total_premium: Total insurance premium (medical + dental + vision)
        scenario_oop: Out-of-pocket healthcare costs for this scenario
        
    Returns:
        Remaining wealth after all costs (in dollars)
    """
    return annual_income - annual_baseline_spend - total_premium - scenario_oop


def compute_expected_log_wealth(
    plan: MedicalPlan,
    scenarios: List[Scenario],
    baseline_spend: float,
    after_tax_income: Optional[float] = None,
    gross_income: Optional[float] = None,
    tax_rate: Optional[float] = None,
    dental: Optional[DentalPlan] = None,
    vision: Optional[VisionPlan] = None,
    # Legacy parameters (backward compatibility)
    annual_income: Optional[float] = None,
    annual_baseline_spend: Optional[float] = None,
) -> float:
    """Compute expected log-wealth (geometric mean objective).
    
    Uses EQUAL WEIGHTING across scenarios (Spitznagel approach).
    Probabilities in scenarios are for reference only.
    
    The formula is:
        E[log(W/W₀)] = (1/n) × Σᵢ log(Wᵢ/W₀)
    
    where:
        - Wᵢ/W₀ = wealth ratio in scenario i (0-1 scale)
        - n = number of scenarios
    
    Args:
        plan: Medical plan to evaluate
        scenarios: List of possible outcomes
        baseline_spend: Fixed non-health spending
        after_tax_income: Income after taxes (preferred)
        gross_income: Gross income before taxes
        tax_rate: Effective tax rate (0.0 to 1.0)
        dental: Optional dental add-on
        vision: Optional vision add-on
        annual_income: LEGACY - use after_tax_income instead
        annual_baseline_spend: LEGACY - use baseline_spend instead
        
    Returns:
        Expected log of wealth ratio: E[log(W/W₀)]
        
    Example:
        >>> log_wealth = compute_expected_log_wealth(
        ...     after_tax_income=180_000,
        ...     baseline_spend=80_000,
        ...     plan=gold_ppo,
        ...     scenarios=scenarios,
        ... )
    """
    # Handle legacy parameters for backward compatibility
    if annual_income is not None and after_tax_income is None:
        after_tax_income = annual_income
    if annual_baseline_spend is not None and baseline_spend == 0:
        baseline_spend = annual_baseline_spend
    
    # Compute disposable income
    disposable = compute_disposable_income(
        baseline_spend=baseline_spend,
        after_tax_income=after_tax_income,
        gross_income=gross_income,
        tax_rate=tax_rate,
    )
    
    if disposable <= 0:
        return float("-inf")
    
    # Build outcome ratios
    outcomes = build_scenario_outcomes(
        disposable_income=disposable,
        plan=plan,
        scenarios=scenarios,
        dental=dental,
        vision=vision,
    )
    
    if not outcomes:
        return 0.0
    
    # Compute expected log (equal weighting)
    n = len(outcomes)
    log_sum = 0.0
    
    for ratio in outcomes:
        if ratio <= 0:
            return float("-inf")  # Any zero → log = -∞
        log_sum += math.log(ratio)
    
    return log_sum / n


def compute_geometric_mean_wealth(
    plan: MedicalPlan,
    scenarios: List[Scenario],
    baseline_spend: float,
    after_tax_income: Optional[float] = None,
    gross_income: Optional[float] = None,
    tax_rate: Optional[float] = None,
    dental: Optional[DentalPlan] = None,
    vision: Optional[VisionPlan] = None,
    # Legacy parameters
    annual_income: Optional[float] = None,
    annual_baseline_spend: Optional[float] = None,
) -> float:
    """Compute geometric mean wealth across scenarios.
    
    GM = exp(E[log(W/W₀)]) × W₀
    
    This is the dollar value that, if received with certainty,
    would provide the same expected log-utility as the uncertain
    outcomes across scenarios.
    
    Args:
        plan: Medical plan to evaluate
        scenarios: List of possible outcomes
        baseline_spend: Fixed non-health spending
        after_tax_income: Income after taxes (preferred)
        gross_income: Gross income before taxes
        tax_rate: Effective tax rate
        dental: Optional dental add-on
        vision: Optional vision add-on
        annual_income: LEGACY - use after_tax_income instead
        annual_baseline_spend: LEGACY - use baseline_spend instead
        
    Returns:
        Geometric mean wealth in dollars
    """
    # Handle legacy parameters
    if annual_income is not None and after_tax_income is None:
        after_tax_income = annual_income
    if annual_baseline_spend is not None and baseline_spend == 0:
        baseline_spend = annual_baseline_spend
    
    expected_log = compute_expected_log_wealth(
        plan=plan,
        scenarios=scenarios,
        baseline_spend=baseline_spend,
        after_tax_income=after_tax_income,
        gross_income=gross_income,
        tax_rate=tax_rate,
        dental=dental,
        vision=vision,
    )
    
    if expected_log == float("-inf"):
        return 0.0
    
    # Compute disposable for scaling
    disposable = compute_disposable_income(
        baseline_spend=baseline_spend,
        after_tax_income=after_tax_income,
        gross_income=gross_income,
        tax_rate=tax_rate,
    )
    
    # GM = exp(E[log(ratio)]) × disposable
    return math.exp(expected_log) * disposable
