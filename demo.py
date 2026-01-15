#!/usr/bin/env python3
"""Demo: Compare health insurance plans using Spitznagel's geometric mean approach.

Wealth ratios (Spitznagel / Tao of Capital):
- 1.0 = kept all disposable income (no health spending)
- 0.9 = kept 90% (spent 10% on health)
- 0.0 = total loss (all gone to health costs)

The geometric mean is dominated by the MINIMUM outcome.
Any near-zero outcome (catastrophe) drives GM toward zero.
"""

from src.insurance import compare_plans, format_comparison_table
from src.insurance.data import (
    # Plans (Single Source of Truth)
    KAISER_GOLD_HMO,
    KAISER_PLATINUM_HMO,
    BLUE_SHIELD_TRIO_GOLD_HMO,
    BLUE_SHIELD_TRIO_PLATINUM_HMO,
    BLUE_SHIELD_GOLD_PPO,
    BLUE_SHIELD_PLATINUM_PPO,
    ALL_PLANS,
    # Add-ons
    DELTA_DENTAL,
    VSP_VISION,
    # Financial defaults
    DEFAULT_GROSS_INCOME,
    DEFAULT_TAX_RATE,
    DEFAULT_BASELINE_SPEND,
    DEFAULT_AFTER_TAX,
    DEFAULT_DISPOSABLE,
)
from src.insurance.scenarios import build_scenarios_for_plan
from src.insurance.geometric_mean import compute_wealth_ratio, compute_geometric_mean_ratio

# =============================================================================
# FINANCIAL PARAMETERS (from data.py - customize there if needed)
# =============================================================================

GROSS_INCOME = DEFAULT_GROSS_INCOME  # $240,000
TAX_RATE = DEFAULT_TAX_RATE  # 32%
AFTER_TAX_INCOME = DEFAULT_AFTER_TAX  # $163,200
BASELINE_SPEND = DEFAULT_BASELINE_SPEND  # $130,000 (realistic SF)
DISPOSABLE = DEFAULT_DISPOSABLE  # $33,200

# Add-ons
dental = DELTA_DENTAL
vision = VSP_VISION

# =============================================================================
# DEMO: FINANCIAL SETUP
# =============================================================================

print("\n" + "="*70)
print("SPITZNAGEL WEALTH RATIO DEMO")
print("="*70)

print(f"\nFinancial Setup:")
print(f"  Gross Income:     ${GROSS_INCOME:,}")
print(f"  Tax Rate:         {TAX_RATE:.0%}")
print(f"  After-Tax Income: ${AFTER_TAX_INCOME:,.0f}")
print(f"  Baseline Spend:   ${BASELINE_SPEND:,} (SF realistic)")
print(f"  Disposable:       ${DISPOSABLE:,.0f}  ← This is '1.0' on the ratio scale")

# =============================================================================
# DEMO: PLAN SCENARIOS (using shared build_scenarios_for_plan)
# =============================================================================

def demo_plan_scenarios(plan, dental, vision) -> tuple[list[float], float]:
    """Show wealth ratios for a plan using shared scenario builder."""
    scenarios = build_scenarios_for_plan(plan)
    total_premium = plan.annual_premium + dental.annual_premium + vision.annual_premium
    addon_oop = dental.expected_oop + vision.expected_oop
    
    print(f"\n--- {plan.name} ---")
    print(f"  Premium: ${total_premium:,.0f}/year")
    print(f"  OOP Max: ${plan.in_network_oop_max:,.0f} (couple)")
    
    ratios = []
    for s in scenarios:
        total_oop = s.total_oop + addon_oop
        ratio = compute_wealth_ratio(
            disposable_income=DISPOSABLE,
            total_premium=total_premium,
            scenario_oop=total_oop,
        )
        ratios.append(ratio)
        remaining = ratio * DISPOSABLE
        print(f"  {s.name:30s} ({s.probability:.0%}): {ratio:.2%} (${remaining:,.0f})")
    
    gm = compute_geometric_mean_ratio(ratios)
    print(f"\n  Geometric Mean Ratio: {gm:.2%}")
    print(f"  GM Wealth:            ${gm * DISPOSABLE:,.0f}")
    return ratios, gm

# =============================================================================
# GOLD vs PLATINUM COMPARISON
# =============================================================================

print("\n" + "="*70)
print("GOLD vs PLATINUM COMPARISON (Kaiser)")
print("="*70)

kaiser_gold_ratios, kaiser_gold_gm = demo_plan_scenarios(KAISER_GOLD_HMO, dental, vision)
kaiser_plat_ratios, kaiser_plat_gm = demo_plan_scenarios(KAISER_PLATINUM_HMO, dental, vision)

print("\n" + "-"*70)
print("KEY INSIGHT: Kaiser Platinum IS worth it")
print("-"*70)
premium_diff = KAISER_PLATINUM_HMO.annual_premium - KAISER_GOLD_HMO.annual_premium
oop_savings = KAISER_GOLD_HMO.in_network_oop_max - KAISER_PLATINUM_HMO.in_network_oop_max
print(f"  Premium difference: ${premium_diff:,.0f}/year")
print(f"  OOP max savings:    ${oop_savings:,.0f} in catastrophe")
print(f"  Net benefit:        ${oop_savings - premium_diff:,.0f} in worst case")
print(f"\n  Gold GM:     {kaiser_gold_gm:.2%}")
print(f"  Platinum GM: {kaiser_plat_gm:.2%}")
if kaiser_plat_gm > kaiser_gold_gm:
    print(f"  ✅ Platinum wins by {(kaiser_plat_gm - kaiser_gold_gm)*100:.2f} percentage points")
else:
    print(f"  ⚠️  Gold wins - catastrophe not likely enough to justify premium")

# =============================================================================
# FULL PLAN COMPARISON (All 6 Plans)
# =============================================================================

print("\n" + "="*70)
print("FULL PLAN COMPARISON (Geometric Mean Ranking)")
print("="*70)

results = compare_plans(
    plans=ALL_PLANS,
    annual_income=AFTER_TAX_INCOME,
    annual_baseline_spend=BASELINE_SPEND,
    dental=dental,
    vision=vision,
)

print(f"\n{format_comparison_table(results)}")

print(f"\n🏆 Winner: {results[0].plan_name}")

print(f"\n--- Winner's Scenario Ratios ---")
for name, ratio in results[0].scenario_ratios.items():
    print(f"  {name:25s}: {ratio:.1%}")

print(f"\n" + "="*70)
print("KEY INSIGHTS (Spitznagel / Tao of Capital)")
print("="*70)
print("""
1. GEOMETRIC MEAN IS DOMINATED BY THE MINIMUM
   Any near-zero outcome (catastrophe) drives GM toward zero.
   This is why downside protection matters more than expected value.

2. PLATINUM WINS FOR KAISER (but NOT for PPO)
   - Kaiser: +$1,368 premium → -$8,400 OOP max = +$7,032 net benefit
   - PPO:    +$9,768 premium → -$8,400 OOP max = -$1,368 net LOSS

3. AVOID PPO (both research sources agree)
   - $8,712/year premium penalty vs Kaiser Gold
   - OON coverage has gaps (50% coinsurance, $5.5k deductible)
   - Not worth it for occasional travel risk

4. HMO TRAVEL RISK IS OVERBLOWN
   - Emergency: Protected by No Surprises Act
   - Kaiser has 1,100+ doctors in Colorado
   - Blue Shield has BlueCard national network
   - Post-stabilization exposure: ~$15k expected (manageable)

5. THE INSURANCE "PUT"
   OOP maximum = your strike price (caps downside loss)
   Lower OOP max = better put protection = higher geometric mean
""")
