#!/usr/bin/env python3
"""Demo: Compare health insurance plans using Spitznagel's geometric mean approach."""

from src.insurance import (
    MedicalPlan, DentalPlan, VisionPlan,
    compare_plans, format_comparison_table
)

# Define plans from your Covered California research
gold_ppo = MedicalPlan(
    name="Blue Shield Gold 80 PPO",
    annual_premium=24_000,  # ~$2000/month couple
    in_network_oop_max=17_400,
    deductible=0,
    expected_minor_oop=400,
)

platinum_ppo = MedicalPlan(
    name="Blue Shield Platinum 90 PPO",
    annual_premium=30_000,  # Higher premium
    in_network_oop_max=8_700,  # Lower OOP max
    deductible=0,
    expected_minor_oop=300,
)

kaiser_gold = MedicalPlan(
    name="Kaiser Gold HMO",
    annual_premium=18_000,
    in_network_oop_max=8_700,
    deductible=0,
    expected_minor_oop=350,
)

blue_shield_trio = MedicalPlan(
    name="Blue Shield Gold Trio HMO",
    annual_premium=21_000,
    in_network_oop_max=8_700,
    deductible=0,
    expected_minor_oop=400,
)

# Add-ons
dental = DentalPlan(name="Delta Dental", annual_premium=800, expected_oop=200)
vision = VisionPlan(name="VSP Vision", annual_premium=300, expected_oop=50)

# Compare plans (Spitznagel geometric mean approach)
results = compare_plans(
    plans=[gold_ppo, platinum_ppo, kaiser_gold, blue_shield_trio],
    annual_income=240_000,
    annual_baseline_spend=120_000,
    dental=dental,
    vision=vision,
)

print("\n=== Health Insurance Plan Comparison (Geometric Mean Ranking) ===\n")
print(format_comparison_table(results))
print(f"\n🏆 Winner: {results[0].plan_name}")
print(f"\n--- Key Insight (Spitznagel / Tao of Capital) ---")
print("The geometric mean naturally penalizes high-variance downside.")
print("Plans with lower OOP max protect better in catastrophic scenarios,")
print("which dominates the geometric mean calculation.")
print("\n--- Scenario Breakdown for Winner ---")
for name, wealth in results[0].scenario_wealth.items():
    print(f"  {name}: ${wealth:,.0f}")
