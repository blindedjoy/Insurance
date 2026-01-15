"""Plan comparison utilities.

Compare multiple insurance plans and rank by geometric mean.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan, total_annual_premium
from src.insurance.scenarios import Scenario, build_scenarios_for_plan
from src.insurance.geometric_mean import (
    compute_expected_log_wealth,
    compute_geometric_mean_wealth,
    compute_wealth_ratio,
    compute_disposable_income,
    build_scenario_outcomes,
)


@dataclass
class PlanComparisonResult:
    """Result of comparing a single plan.
    
    Contains all relevant metrics for ranking and display.
    
    Attributes:
        plan_name: Name of the medical plan
        annual_premium: Medical plan annual premium
        total_annual_premium: Total premium including dental/vision
        in_network_oop_max: Maximum in-network out-of-pocket
        expected_log_wealth: E[log(W/W₀)] - the optimization target
        geometric_mean: GM wealth in dollars
        scenario_wealth: Per-scenario wealth breakdown (in dollars)
        scenario_ratios: Per-scenario wealth ratios (0-1 scale)
    """
    
    plan_name: str
    annual_premium: float
    total_annual_premium: float
    in_network_oop_max: float
    expected_log_wealth: float
    geometric_mean: float
    scenario_wealth: Dict[str, float] = field(default_factory=dict)
    scenario_ratios: Dict[str, float] = field(default_factory=dict)


def compare_plans(
    plans: List[MedicalPlan],
    annual_income: float,
    annual_baseline_spend: float,
    dental: Optional[DentalPlan] = None,
    vision: Optional[VisionPlan] = None,
    scenarios: Optional[List[Scenario]] = None,
    tax_rate: Optional[float] = None,
) -> List[PlanComparisonResult]:
    """Compare multiple plans and rank by geometric mean.
    
    Args:
        plans: List of medical plans to compare
        annual_income: Gross annual income (or after-tax if tax_rate=None)
        annual_baseline_spend: Fixed non-health spending
        dental: Optional dental add-on (applied to all plans)
        vision: Optional vision add-on (applied to all plans)
        scenarios: Custom scenarios (if None, builds from each plan)
        tax_rate: Optional tax rate (if provided, annual_income is gross)
        
    Returns:
        List of PlanComparisonResult sorted by geometric mean (best first)
        
    Example:
        >>> results = compare_plans(
        ...     plans=[gold_ppo, platinum_ppo, kaiser_hmo],
        ...     annual_income=180_000,  # after-tax
        ...     annual_baseline_spend=80_000,
        ... )
        >>> for r in results:
        ...     print(f"{r.plan_name}: GM=${r.geometric_mean:,.0f}")
    """
    results = []
    
    # Compute disposable income once
    if tax_rate is not None:
        disposable = compute_disposable_income(
            gross_income=annual_income,
            tax_rate=tax_rate,
            baseline_spend=annual_baseline_spend,
        )
        after_tax = annual_income * (1 - tax_rate)
    else:
        # Assume annual_income is already after-tax
        disposable = annual_income - annual_baseline_spend
        after_tax = annual_income
    
    for plan in plans:
        # Build scenarios for this plan (or use custom)
        plan_scenarios = scenarios if scenarios else build_scenarios_for_plan(plan)
        
        # Compute metrics using new API
        expected_log = compute_expected_log_wealth(
            plan=plan,
            scenarios=plan_scenarios,
            baseline_spend=annual_baseline_spend,
            after_tax_income=after_tax,
            dental=dental,
            vision=vision,
        )
        
        gm = compute_geometric_mean_wealth(
            plan=plan,
            scenarios=plan_scenarios,
            baseline_spend=annual_baseline_spend,
            after_tax_income=after_tax,
            dental=dental,
            vision=vision,
        )
        
        # Compute total premium
        total_premium = total_annual_premium(plan, dental, vision)
        
        # Compute add-on OOP
        addon_oop = 0.0
        if dental:
            addon_oop += dental.expected_oop
        if vision:
            addon_oop += vision.expected_oop
        
        # Per-scenario wealth breakdown (dollars AND ratios)
        scenario_wealth = {}
        scenario_ratios = {}
        for s in plan_scenarios:
            total_oop = s.total_oop + addon_oop
            
            # Dollar wealth
            wealth = disposable - total_premium - total_oop
            scenario_wealth[s.name] = wealth
            
            # Ratio (0-1)
            ratio = compute_wealth_ratio(
                disposable_income=disposable,
                total_premium=total_premium,
                scenario_oop=total_oop,
            )
            scenario_ratios[s.name] = ratio
        
        results.append(PlanComparisonResult(
            plan_name=plan.name,
            annual_premium=plan.annual_premium,
            total_annual_premium=total_premium,
            in_network_oop_max=plan.in_network_oop_max,
            expected_log_wealth=expected_log,
            geometric_mean=gm,
            scenario_wealth=scenario_wealth,
            scenario_ratios=scenario_ratios,
        ))
    
    # Sort by geometric mean (best first)
    results.sort(key=lambda r: r.geometric_mean, reverse=True)
    
    return results


def format_comparison_table(results: List[PlanComparisonResult]) -> str:
    """Format comparison results as a markdown table.
    
    Args:
        results: List of PlanComparisonResult objects
        
    Returns:
        Markdown table string
        
    Example:
        >>> table = format_comparison_table(results)
        >>> print(table)
    """
    lines = [
        "| Rank | Plan | Premium | OOP Max | GM Wealth | E[log(W)] |",
        "|------|------|---------|---------|-----------|-----------|",
    ]
    
    for i, r in enumerate(results, 1):
        premium = f"${r.total_annual_premium:,.0f}"
        oop_max = f"${r.in_network_oop_max:,.0f}"
        gm = f"${r.geometric_mean:,.0f}"
        log_w = f"{r.expected_log_wealth:.4f}"
        
        lines.append(f"| {i} | {r.plan_name} | {premium} | {oop_max} | {gm} | {log_w} |")
    
    return "\n".join(lines)


def format_scenario_breakdown(result: PlanComparisonResult) -> str:
    """Format per-scenario wealth breakdown as a markdown table.
    
    Args:
        result: Single PlanComparisonResult
        
    Returns:
        Markdown table string showing wealth in each scenario
    """
    lines = [
        f"### {result.plan_name} - Scenario Breakdown",
        "",
        "| Scenario | Wealth | Ratio |",
        "|----------|--------|-------|",
    ]
    
    for name in result.scenario_wealth:
        wealth = result.scenario_wealth[name]
        ratio = result.scenario_ratios.get(name, 0)
        lines.append(f"| {name} | ${wealth:,.0f} | {ratio:.1%} |")
    
    return "\n".join(lines)
