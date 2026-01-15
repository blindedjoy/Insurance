"""TDD tests for wealth ratio calculation (Spitznagel approach).

The wealth ratio should be:
- 1.0 = kept all disposable income (no health spending)
- 0.9 = kept 90% (spent 10% on health)
- 0.0 = total loss (all disposable income gone to health)

This matches how austrian-trading computes outcomes for put protection:
- Outcomes are ratios (0-1)
- GM = (product of ratios) ^ (1/n)
- log(GM) → -∞ as any ratio → 0

Tests written BEFORE implementation following TDD principles.
"""

import pytest
import math


class TestWealthRatioCalculation:
    """Test that wealth is computed as a ratio (0-1 scale)."""

    def test_compute_wealth_ratio_exists(self):
        """compute_wealth_ratio function should exist."""
        from src.insurance.geometric_mean import compute_wealth_ratio
        assert callable(compute_wealth_ratio)

    def test_no_health_spending_returns_one(self):
        """If no premium and no OOP, wealth ratio should be 1.0."""
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        ratio = compute_wealth_ratio(
            disposable_income=100_000,
            total_premium=0,
            scenario_oop=0,
        )
        
        assert ratio == 1.0

    def test_spending_reduces_ratio(self):
        """Health spending should reduce wealth ratio below 1.0."""
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        # Spend $10k on health out of $100k disposable
        ratio = compute_wealth_ratio(
            disposable_income=100_000,
            total_premium=8_000,
            scenario_oop=2_000,
        )
        
        # Should be 0.9 (kept 90%)
        assert ratio == 0.9

    def test_ratio_is_fraction_of_disposable(self):
        """Ratio = (disposable - premium - oop) / disposable."""
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        disposable = 120_000
        premium = 24_000
        oop = 6_000
        
        ratio = compute_wealth_ratio(
            disposable_income=disposable,
            total_premium=premium,
            scenario_oop=oop,
        )
        
        expected = (disposable - premium - oop) / disposable
        assert ratio == expected
        assert ratio == 0.75  # 90k / 120k

    def test_ratio_cannot_exceed_one(self):
        """Wealth ratio should never exceed 1.0."""
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        ratio = compute_wealth_ratio(
            disposable_income=100_000,
            total_premium=0,
            scenario_oop=0,
        )
        
        assert ratio <= 1.0

    def test_ratio_floors_at_zero(self):
        """If costs exceed disposable, ratio should be 0 (not negative)."""
        from src.insurance.geometric_mean import compute_wealth_ratio
        
        ratio = compute_wealth_ratio(
            disposable_income=50_000,
            total_premium=30_000,
            scenario_oop=30_000,  # Total 60k > 50k disposable
        )
        
        assert ratio == 0.0


class TestAfterTaxIncome:
    """Test tax handling for disposable income calculation."""

    def test_compute_disposable_income_exists(self):
        """compute_disposable_income function should exist."""
        from src.insurance.geometric_mean import compute_disposable_income
        assert callable(compute_disposable_income)

    def test_disposable_from_after_tax_income(self):
        """Should compute disposable from after-tax income directly."""
        from src.insurance.geometric_mean import compute_disposable_income
        
        # After-tax income minus baseline spending
        disposable = compute_disposable_income(
            after_tax_income=180_000,
            baseline_spend=80_000,
        )
        
        assert disposable == 100_000

    def test_disposable_from_gross_with_tax_rate(self):
        """Should compute disposable from gross income with tax rate."""
        from src.insurance.geometric_mean import compute_disposable_income
        
        # Gross 240k, 25% tax = 180k after tax, minus 80k baseline = 100k
        disposable = compute_disposable_income(
            gross_income=240_000,
            tax_rate=0.25,
            baseline_spend=80_000,
        )
        
        assert disposable == 100_000

    def test_after_tax_takes_precedence(self):
        """If both after_tax and gross provided, after_tax should win."""
        from src.insurance.geometric_mean import compute_disposable_income
        
        disposable = compute_disposable_income(
            after_tax_income=180_000,  # This should be used
            gross_income=500_000,  # This should be ignored
            tax_rate=0.50,
            baseline_spend=80_000,
        )
        
        assert disposable == 100_000  # 180k - 80k, not 250k - 80k


class TestGeometricMeanRatio:
    """Test that GM is computed on ratios (0-1) per Spitznagel."""

    def test_gm_of_ones_is_one(self):
        """GM of all 1.0 ratios should be 1.0."""
        from src.insurance.geometric_mean import compute_geometric_mean_ratio
        
        ratios = [1.0, 1.0, 1.0, 1.0]
        gm = compute_geometric_mean_ratio(ratios)
        
        assert gm == 1.0

    def test_gm_with_zero_is_zero(self):
        """Any zero ratio should make GM = 0 (Spitznagel's key insight)."""
        from src.insurance.geometric_mean import compute_geometric_mean_ratio
        
        ratios = [1.0, 0.9, 0.8, 0.0]  # One catastrophic outcome
        gm = compute_geometric_mean_ratio(ratios)
        
        assert gm == 0.0

    def test_gm_is_nth_root_of_product(self):
        """GM = (r1 × r2 × ... × rn) ^ (1/n)."""
        from src.insurance.geometric_mean import compute_geometric_mean_ratio
        
        ratios = [0.9, 0.8, 0.7, 0.6]
        gm = compute_geometric_mean_ratio(ratios)
        
        product = 0.9 * 0.8 * 0.7 * 0.6
        expected = product ** (1/4)
        
        assert abs(gm - expected) < 1e-10

    def test_gm_less_than_arithmetic_mean(self):
        """GM should always be ≤ arithmetic mean (AM-GM inequality)."""
        from src.insurance.geometric_mean import compute_geometric_mean_ratio
        
        ratios = [1.0, 0.9, 0.5, 0.3]
        gm = compute_geometric_mean_ratio(ratios)
        am = sum(ratios) / len(ratios)
        
        assert gm < am


class TestExpectedLogWealthRefactored:
    """Test the refactored expected log-wealth calculation."""

    def test_uses_disposable_income(self, gold_ppo_plan, default_scenarios):
        """Should use disposable income (after-tax - baseline)."""
        from src.insurance.geometric_mean import compute_expected_log_wealth
        
        # Using after_tax_income parameter
        log_wealth = compute_expected_log_wealth(
            after_tax_income=180_000,
            baseline_spend=80_000,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        assert isinstance(log_wealth, float)
        assert log_wealth < 0  # Should be negative (we're spending money)

    def test_supports_gross_income_with_tax_rate(self, gold_ppo_plan, default_scenarios):
        """Should support gross income with tax rate estimation."""
        from src.insurance.geometric_mean import compute_expected_log_wealth
        
        # These should give same result
        log_v1 = compute_expected_log_wealth(
            after_tax_income=180_000,
            baseline_spend=80_000,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        log_v2 = compute_expected_log_wealth(
            gross_income=240_000,
            tax_rate=0.25,
            baseline_spend=80_000,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        assert abs(log_v1 - log_v2) < 1e-10

    def test_catastrophe_dominates_log_wealth(self, gold_ppo_plan):
        """High OOP max (tail risk) should severely hurt log-wealth."""
        from src.insurance.geometric_mean import compute_expected_log_wealth
        from src.insurance.scenarios import Scenario
        
        # Scenarios with moderate loss
        mild_scenarios = [
            Scenario("no_use", 0.7, 0),
            Scenario("minor", 0.3, 1_000),
        ]
        
        # Scenarios with catastrophic loss
        severe_scenarios = [
            Scenario("no_use", 0.7, 0),
            Scenario("catastrophe", 0.3, 50_000),  # Huge OOP
        ]
        
        log_mild = compute_expected_log_wealth(
            after_tax_income=180_000,
            baseline_spend=80_000,
            plan=gold_ppo_plan,
            scenarios=mild_scenarios,
        )
        
        log_severe = compute_expected_log_wealth(
            after_tax_income=180_000,
            baseline_spend=80_000,
            plan=gold_ppo_plan,
            scenarios=severe_scenarios,
        )
        
        # Severe should be much worse
        assert log_severe < log_mild


class TestScenarioOutcomesAsRatios:
    """Test that scenario outcomes are computed as ratios."""

    def test_build_scenario_outcomes_exists(self):
        """build_scenario_outcomes function should exist."""
        from src.insurance.geometric_mean import build_scenario_outcomes
        assert callable(build_scenario_outcomes)

    def test_outcomes_are_ratios(self, gold_ppo_plan, default_scenarios):
        """Each outcome should be a ratio between 0 and 1."""
        from src.insurance.geometric_mean import build_scenario_outcomes
        
        outcomes = build_scenario_outcomes(
            disposable_income=100_000,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        for outcome in outcomes:
            assert 0 <= outcome <= 1.0, f"Outcome {outcome} not in [0, 1]"

    def test_no_use_scenario_highest_ratio(self, gold_ppo_plan, default_scenarios):
        """No use scenario should have highest ratio (only premium cost)."""
        from src.insurance.geometric_mean import build_scenario_outcomes
        
        outcomes = build_scenario_outcomes(
            disposable_income=100_000,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        # First scenario (no_use) should be highest
        assert outcomes[0] == max(outcomes)

    def test_catastrophe_scenario_lowest_ratio(self, gold_ppo_plan, default_scenarios):
        """Catastrophe scenario should have lowest ratio."""
        from src.insurance.geometric_mean import build_scenario_outcomes
        
        outcomes = build_scenario_outcomes(
            disposable_income=100_000,
            plan=gold_ppo_plan,
            scenarios=default_scenarios,
        )
        
        # OON catastrophe (last scenario) should be lowest
        assert outcomes[-1] == min(outcomes)
