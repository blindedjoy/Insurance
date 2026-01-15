"""TDD tests for geometric mean / expected log-wealth calculation.

This is the core of the Spitznagel approach:
- Geometric mean is dominated by the minimum outcome
- A single catastrophic outcome (W → 0) drives GM → 0
- This naturally penalizes high-variance downside strategies

Tests written BEFORE implementation following TDD principles.
"""

import pytest
import math


class TestExpectedLogWealthExists:
    """Test that the main calculation function exists."""

    def test_function_exists(self):
        """compute_expected_log_wealth should exist."""
        from src.insurance.geometric_mean import compute_expected_log_wealth
        assert callable(compute_expected_log_wealth)

    def test_returns_float(self, gold_ppo_plan, default_scenarios, typical_couple_income, typical_baseline_spend):
        """Should return a float value."""
        from src.insurance.geometric_mean import compute_expected_log_wealth
        
        result = compute_expected_log_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        assert isinstance(result, float)


class TestExpectedLogWealthMath:
    """Test the mathematical properties of expected log-wealth."""

    def test_no_cost_scenario_gives_zero_log(self, typical_couple_income, typical_baseline_spend):
        """If no costs at all, relative wealth = 1, log = 0."""
        from src.insurance.geometric_mean import compute_scenario_wealth, compute_wealth_ratio
        from src.insurance.plans import MedicalPlan
        from src.insurance.scenarios import Scenario
        
        # Create a hypothetical free plan
        free_plan = MedicalPlan(
            name="Free",
            annual_premium=0.0,
            in_network_oop_max=0.0,
            expected_minor_oop=0.0,
        )
        
        no_cost_scenario = Scenario("no_cost", 1.0, medical_oop=0.0)
        
        # Using new ratio function
        disposable = typical_couple_income - typical_baseline_spend
        ratio = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=0.0,
            scenario_oop=0.0,
        )
        
        assert ratio == 1.0  # No spending = ratio of 1

    def test_higher_oop_means_lower_wealth(self, typical_couple_income, typical_baseline_spend):
        """Higher OOP should result in lower remaining wealth."""
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        disposable = typical_couple_income - typical_baseline_spend
        
        ratio_low = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=24_000,
            scenario_oop=1_000,
        )
        
        ratio_high = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=24_000,
            scenario_oop=20_000,
        )
        
        assert ratio_high < ratio_low

    def test_catastrophic_loss_dominates_gm(self, gold_ppo_plan, typical_couple_income, typical_baseline_spend):
        """A near-total loss scenario should dramatically reduce GM."""
        from src.insurance.geometric_mean import compute_expected_log_wealth
        from src.insurance.scenarios import Scenario
        
        # Normal scenarios
        normal_scenarios = [
            Scenario("good", 0.9, medical_oop=0.0),
            Scenario("ok", 0.1, medical_oop=500.0),
        ]
        
        # Scenarios with catastrophic loss
        disaster_scenarios = [
            Scenario("good", 0.9, medical_oop=0.0),
            Scenario("disaster", 0.1, medical_oop=100_000.0),  # Massive OOP
        ]
        
        gm_normal = compute_expected_log_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=normal_scenarios,
        )
        
        gm_disaster = compute_expected_log_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=disaster_scenarios,
        )
        
        # Disaster should significantly reduce expected log-wealth
        assert gm_disaster < gm_normal


class TestGeometricMeanWealth:
    """Test the geometric mean wealth calculation."""

    def test_gm_function_exists(self):
        """compute_geometric_mean_wealth should exist."""
        from src.insurance.geometric_mean import compute_geometric_mean_wealth
        assert callable(compute_geometric_mean_wealth)

    def test_gm_is_exp_of_expected_log(self, gold_ppo_plan, default_scenarios, typical_couple_income, typical_baseline_spend):
        """GM = exp(E[log(W)]) × disposable."""
        from src.insurance.geometric_mean import (
            compute_expected_log_wealth,
            compute_geometric_mean_wealth,
        )
        
        expected_log = compute_expected_log_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        gm = compute_geometric_mean_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        # GM should equal exp(expected_log) scaled by disposable income
        disposable = typical_couple_income - typical_baseline_spend
        expected_gm = math.exp(expected_log) * disposable
        
        assert abs(gm - expected_gm) < 0.01  # Allow small floating point error


class TestPlatinumVsGoldGM:
    """Test the key comparison: does Platinum improve GM over Gold?
    
    Research finding (2026): PPO Platinum premium is so high ($36,936 vs $27,168)
    that it's NOT better than Gold PPO even in catastrophe. But Kaiser Platinum
    IS better than Kaiser Gold (only $1,368 premium delta vs $8,400 OOP savings).
    """

    def test_kaiser_platinum_better_in_catastrophic_scenario(
        self, 
        kaiser_gold_hmo, 
        kaiser_platinum_hmo, 
        typical_couple_income, 
        typical_baseline_spend
    ):
        """Kaiser Platinum preserves more wealth in catastrophic scenarios.
        
        Kaiser premium delta: $1,368 ($19,824 - $18,456)
        Kaiser OOP delta: $8,400 ($18,400 - $10,000)
        Net savings in catastrophe: $7,032
        """
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        disposable = typical_couple_income - typical_baseline_spend
        
        # Catastrophic scenario - hit OOP max
        gold_ratio = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=kaiser_gold_hmo.annual_premium,
            scenario_oop=kaiser_gold_hmo.in_network_oop_max,
        )
        
        plat_ratio = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=kaiser_platinum_hmo.annual_premium,
            scenario_oop=kaiser_platinum_hmo.in_network_oop_max,
        )
        
        # Kaiser Platinum: $1,368 more premium, $8,400 less OOP max
        # Net effect: platinum preserves $7,032 more wealth in catastrophe
        assert plat_ratio > gold_ratio
    
    def test_ppo_platinum_not_better_in_catastrophic_scenario(
        self, 
        gold_ppo_plan, 
        platinum_ppo_plan, 
        typical_couple_income, 
        typical_baseline_spend
    ):
        """PPO Platinum does NOT preserve more wealth - premium too high!
        
        PPO premium delta: $9,768 ($36,936 - $27,168)
        PPO OOP delta: $8,400 ($18,400 - $10,000)
        Net LOSS in catastrophe: $1,368
        
        Research finding: Both ChatGPT and Opus said PPO Platinum hard to justify.
        """
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        disposable = typical_couple_income - typical_baseline_spend
        
        gold_ratio = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=gold_ppo_plan.annual_premium,
            scenario_oop=gold_ppo_plan.in_network_oop_max,
        )
        
        plat_ratio = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=platinum_ppo_plan.annual_premium,
            scenario_oop=platinum_ppo_plan.in_network_oop_max,
        )
        
        # PPO Platinum: $9,768 more premium, only $8,400 less OOP max
        # Net effect: Gold PPO is actually BETTER even in catastrophe!
        assert gold_ratio > plat_ratio

    def test_gold_better_in_no_use_scenario(
        self, 
        gold_ppo_plan, 
        platinum_ppo_plan, 
        typical_couple_income, 
        typical_baseline_spend
    ):
        """Gold should preserve more wealth when no healthcare used."""
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        disposable = typical_couple_income - typical_baseline_spend
        
        # No use scenario - only premium cost
        gold_ratio = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=gold_ppo_plan.annual_premium,
            scenario_oop=0.0,
        )
        
        plat_ratio = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=platinum_ppo_plan.annual_premium,
            scenario_oop=0.0,
        )
        
        # Gold has lower premium, so more wealth preserved
        assert gold_ratio > plat_ratio


class TestDentalVisionAddons:
    """Test that dental/vision add-ons are properly included."""

    def test_addons_increase_premium_cost(
        self, 
        gold_ppo_plan, 
        basic_dental, 
        basic_vision,
        default_scenarios,
        typical_couple_income, 
        typical_baseline_spend
    ):
        """Adding dental/vision should increase total cost."""
        from src.insurance.geometric_mean import compute_expected_log_wealth
        
        # Without addons
        log_wealth_no_addons = compute_expected_log_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        # With addons
        log_wealth_with_addons = compute_expected_log_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
            dental=basic_dental,
            vision=basic_vision,
        )
        
        # More premium = lower expected log-wealth
        assert log_wealth_with_addons < log_wealth_no_addons


class TestEqualWeighting:
    """Test that scenarios use equal weighting (Spitznagel approach)."""

    def test_equal_weighting_ignores_probability(
        self, 
        gold_ppo_plan, 
        typical_couple_income, 
        typical_baseline_spend
    ):
        """Expected log should use equal weights, not probabilities."""
        from src.insurance.geometric_mean import compute_expected_log_wealth
        from src.insurance.scenarios import Scenario
        
        # Two scenario sets with different probabilities but same outcomes
        scenarios_v1 = [
            Scenario("a", 0.9, medical_oop=0.0),
            Scenario("b", 0.1, medical_oop=10_000.0),
        ]
        
        scenarios_v2 = [
            Scenario("a", 0.1, medical_oop=0.0),  # Different probability
            Scenario("b", 0.9, medical_oop=10_000.0),  # Different probability
        ]
        
        # With equal weighting, results should be the same
        log_v1 = compute_expected_log_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=scenarios_v1,
        )
        
        log_v2 = compute_expected_log_wealth(
            after_tax_income=typical_couple_income,
            baseline_spend=typical_baseline_spend,
            plan=gold_ppo_plan,
            scenarios=scenarios_v2,
        )
        
        # Equal weighting means probability doesn't matter
        assert log_v1 == log_v2
