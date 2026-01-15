"""Tests to cover missing code paths and increase coverage.

These tests target specific uncovered lines identified by coverage analysis.
"""

import pytest

from src.insurance.plans import MedicalPlan, NetworkType
from src.insurance.scenarios import Scenario, build_scenarios_for_plan
from src.insurance.geometric_mean import (
    compute_wealth_ratio,
    compute_geometric_mean_ratio,
    compute_disposable_income,
    build_scenario_outcomes,
)
from src.insurance.compare import (
    compare_plans,
    format_scenario_breakdown,
    PlanComparisonResult,
)
from src.insurance.data import KAISER_GOLD_HMO, DELTA_DENTAL, VSP_VISION


class TestCompareWithTaxRate:
    """Tests for compare_plans with tax_rate parameter (lines 85-90)."""

    def test_compare_with_gross_income_and_tax_rate(self):
        """compare_plans should accept gross_income with tax_rate."""
        plans = [KAISER_GOLD_HMO]
        
        results = compare_plans(
            plans=plans,
            annual_income=275_000,  # Gross income
            annual_baseline_spend=68_000,
            tax_rate=0.326,  # This triggers the uncovered branch
        )
        
        assert len(results) == 1
        assert results[0].plan_name == "Kaiser Gold HMO"
        assert results[0].geometric_mean > 0

    def test_compare_tax_rate_affects_result(self):
        """Higher tax rate should reduce geometric mean."""
        plans = [KAISER_GOLD_HMO]
        
        # Low tax rate
        results_low_tax = compare_plans(
            plans=plans,
            annual_income=275_000,
            annual_baseline_spend=68_000,
            tax_rate=0.20,
        )
        
        # High tax rate
        results_high_tax = compare_plans(
            plans=plans,
            annual_income=275_000,
            annual_baseline_spend=68_000,
            tax_rate=0.40,
        )
        
        # Higher tax = less disposable = lower GM
        assert results_low_tax[0].geometric_mean > results_high_tax[0].geometric_mean


class TestFormatScenarioBreakdown:
    """Tests for format_scenario_breakdown function (lines 202-214)."""

    def test_format_scenario_breakdown_exists(self):
        """format_scenario_breakdown should be importable."""
        from src.insurance.compare import format_scenario_breakdown
        assert callable(format_scenario_breakdown)

    def test_format_scenario_breakdown_returns_markdown(self):
        """format_scenario_breakdown should return markdown table."""
        result = PlanComparisonResult(
            plan_name="Test Plan",
            annual_premium=20_000,
            total_annual_premium=21_000,
            in_network_oop_max=10_000,
            expected_log_wealth=-0.5,
            geometric_mean=50_000,
            scenario_wealth={"no_use": 80_000, "catastrophe": 50_000},
            scenario_ratios={"no_use": 0.8, "catastrophe": 0.5},
        )
        
        markdown = format_scenario_breakdown(result)
        
        # Should be a markdown string
        assert isinstance(markdown, str)
        assert "Test Plan" in markdown
        assert "| Scenario | Wealth | Ratio |" in markdown
        assert "no_use" in markdown
        assert "catastrophe" in markdown

    def test_format_scenario_breakdown_formats_correctly(self):
        """format_scenario_breakdown should format numbers correctly."""
        result = PlanComparisonResult(
            plan_name="Kaiser Platinum HMO",
            annual_premium=19_824,
            total_annual_premium=20_924,
            in_network_oop_max=10_000,
            expected_log_wealth=-0.44,
            geometric_mean=86_283,
            scenario_wealth={"no_use": 96_176, "cat": 69_676},
            scenario_ratios={"no_use": 0.82, "cat": 0.59},
        )
        
        markdown = format_scenario_breakdown(result)
        
        # Check formatting
        assert "$96,176" in markdown
        assert "$69,676" in markdown
        assert "82.0%" in markdown
        assert "59.0%" in markdown


class TestDisposableIncomeEdgeCases:
    """Tests for edge cases in compute_disposable_income."""

    def test_disposable_income_zero(self):
        """Zero disposable should return 0."""
        disposable = compute_disposable_income(
            after_tax_income=80_000,
            baseline_spend=80_000,
        )
        assert disposable == 0.0

    def test_disposable_income_negative(self):
        """Negative disposable (spend > income) should return negative."""
        disposable = compute_disposable_income(
            after_tax_income=50_000,
            baseline_spend=80_000,
        )
        assert disposable == -30_000

    def test_disposable_from_gross_only(self):
        """Using gross_income without after_tax_income."""
        disposable = compute_disposable_income(
            gross_income=100_000,
            tax_rate=0.30,
            baseline_spend=50_000,
        )
        # 100,000 * 0.70 - 50,000 = 70,000 - 50,000 = 20,000
        assert disposable == 20_000

    def test_disposable_no_income_provided(self):
        """If no income provided, should return -baseline_spend."""
        disposable = compute_disposable_income(
            baseline_spend=50_000,
        )
        # No income = 0 - 50,000 = -50,000
        assert disposable == -50_000


class TestWealthRatioEdgeCases:
    """Tests for edge cases in compute_wealth_ratio."""

    def test_wealth_ratio_zero_disposable(self):
        """Zero disposable should return 0."""
        ratio = compute_wealth_ratio(
            disposable_income=0,
            total_premium=10_000,
            scenario_oop=5_000,
        )
        assert ratio == 0.0

    def test_wealth_ratio_negative_disposable(self):
        """Negative disposable should return 0."""
        ratio = compute_wealth_ratio(
            disposable_income=-10_000,
            total_premium=5_000,
            scenario_oop=2_000,
        )
        assert ratio == 0.0


class TestGeometricMeanEdgeCases:
    """Tests for edge cases in compute_geometric_mean_ratio."""

    def test_gm_empty_list(self):
        """Empty list should return 0."""
        gm = compute_geometric_mean_ratio([])
        assert gm == 0.0

    def test_gm_single_value(self):
        """Single value GM should equal that value."""
        gm = compute_geometric_mean_ratio([0.75])
        assert gm == 0.75

    def test_gm_negative_value(self):
        """Negative value should return 0 (invalid ratio)."""
        gm = compute_geometric_mean_ratio([0.8, -0.2, 0.7])
        assert gm == 0.0


class TestOONEmergencyNotInNetwork:
    """Tests for oon_emergency_treated_as_in_network=False branch (line 113)."""

    def test_oon_emergency_not_treated_as_in_network(self):
        """Plans with OON emergency NOT treated as in-network should double OOP estimate."""
        plan = MedicalPlan(
            name="Weird Plan",
            annual_premium=20_000,
            in_network_oop_max=10_000,
            network_type=NetworkType.PPO,
            deductible=0,
            expected_minor_oop=300,
            oon_emergency_treated_as_in_network=False,  # Triggers line 113
            post_stabilization_oon_covered=False,
            post_stabilization_exposure=15_000,
            oon_deductible=5_000,
            oon_oop_max=25_000,
            oon_coinsurance=0.5,
            ground_ambulance_exposure=1_500,
        )
        
        scenarios = build_scenarios_for_plan(plan)
        
        # Find the OON emergency scenario
        oon_scenario = next(s for s in scenarios if s.name == "cat_oon_emergency")
        
        # Should use 2x the in-network OOP max (conservative estimate)
        # medical_oop = 10,000 * 2 = 20,000
        assert oon_scenario.medical_oop == 20_000


class TestBuildScenarioOutcomesEdgeCases:
    """Tests for build_scenario_outcomes edge cases."""

    def test_build_outcomes_with_dental_vision(self):
        """build_scenario_outcomes should include dental/vision OOP."""
        from src.insurance.data import KAISER_PLATINUM_HMO
        
        scenarios = build_scenarios_for_plan(KAISER_PLATINUM_HMO)
        
        outcomes = build_scenario_outcomes(
            disposable_income=100_000,
            plan=KAISER_PLATINUM_HMO,
            scenarios=scenarios,
            dental=DELTA_DENTAL,
            vision=VSP_VISION,
        )
        
        assert len(outcomes) == 4
        # All outcomes should be ratios (0-1)
        for ratio in outcomes:
            assert 0 <= ratio <= 1

    def test_build_outcomes_no_addons(self):
        """build_scenario_outcomes should work without dental/vision."""
        from src.insurance.data import KAISER_GOLD_HMO
        
        scenarios = build_scenarios_for_plan(KAISER_GOLD_HMO)
        
        outcomes = build_scenario_outcomes(
            disposable_income=100_000,
            plan=KAISER_GOLD_HMO,
            scenarios=scenarios,
        )
        
        assert len(outcomes) == 4
