"""TDD tests for plan comparison functionality.

Compare multiple plans and rank by geometric mean.
Tests written BEFORE implementation following TDD principles.
"""

import pytest


class TestComparePlansExists:
    """Test that comparison functions exist."""

    def test_compare_function_exists(self):
        """compare_plans function should exist."""
        from src.insurance.compare import compare_plans
        assert callable(compare_plans)

    def test_result_dataclass_exists(self):
        """PlanComparisonResult should exist."""
        from src.insurance.compare import PlanComparisonResult
        assert PlanComparisonResult is not None


class TestComparePlans:
    """Test plan comparison functionality."""

    def test_compare_returns_list_of_results(
        self, 
        gold_ppo_plan, 
        platinum_ppo_plan,
        typical_couple_income,
        typical_baseline_spend
    ):
        """compare_plans should return a list of PlanComparisonResult."""
        from src.insurance.compare import compare_plans, PlanComparisonResult
        
        results = compare_plans(
            plans=[gold_ppo_plan, platinum_ppo_plan],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
        )
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, PlanComparisonResult) for r in results)

    def test_results_sorted_by_gm(
        self, 
        gold_ppo_plan, 
        platinum_ppo_plan,
        kaiser_gold_hmo,
        typical_couple_income,
        typical_baseline_spend
    ):
        """Results should be sorted by geometric mean (best first)."""
        from src.insurance.compare import compare_plans
        
        results = compare_plans(
            plans=[gold_ppo_plan, platinum_ppo_plan, kaiser_gold_hmo],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
        )
        
        gms = [r.geometric_mean for r in results]
        assert gms == sorted(gms, reverse=True), "Results should be sorted by GM descending"

    def test_result_contains_plan_name(
        self, 
        gold_ppo_plan,
        typical_couple_income,
        typical_baseline_spend
    ):
        """Result should contain the plan name."""
        from src.insurance.compare import compare_plans
        
        results = compare_plans(
            plans=[gold_ppo_plan],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
        )
        
        assert results[0].plan_name == gold_ppo_plan.name

    def test_result_contains_key_metrics(
        self, 
        gold_ppo_plan,
        typical_couple_income,
        typical_baseline_spend
    ):
        """Result should contain annual_premium, oop_max, and geometric_mean."""
        from src.insurance.compare import compare_plans
        
        results = compare_plans(
            plans=[gold_ppo_plan],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
        )
        
        r = results[0]
        assert hasattr(r, "plan_name")
        assert hasattr(r, "annual_premium")
        assert hasattr(r, "in_network_oop_max")
        assert hasattr(r, "geometric_mean")
        assert hasattr(r, "expected_log_wealth")


class TestCompareWithAddons:
    """Test comparison with dental/vision add-ons."""

    def test_compare_with_dental_vision(
        self, 
        gold_ppo_plan, 
        platinum_ppo_plan,
        basic_dental,
        basic_vision,
        typical_couple_income,
        typical_baseline_spend
    ):
        """Should be able to compare plans with dental/vision add-ons."""
        from src.insurance.compare import compare_plans
        
        results = compare_plans(
            plans=[gold_ppo_plan, platinum_ppo_plan],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
            dental=basic_dental,
            vision=basic_vision,
        )
        
        assert len(results) == 2

    def test_addons_reflected_in_total_premium(
        self, 
        gold_ppo_plan,
        basic_dental,
        basic_vision,
        typical_couple_income,
        typical_baseline_spend
    ):
        """Total premium in result should include add-on costs."""
        from src.insurance.compare import compare_plans
        
        results = compare_plans(
            plans=[gold_ppo_plan],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
            dental=basic_dental,
            vision=basic_vision,
        )
        
        expected_total = gold_ppo_plan.annual_premium + basic_dental.annual_premium + basic_vision.annual_premium
        assert results[0].total_annual_premium == expected_total


class TestComparisonTable:
    """Test comparison table formatting."""

    def test_format_table_exists(self):
        """format_comparison_table function should exist."""
        from src.insurance.compare import format_comparison_table
        assert callable(format_comparison_table)

    def test_format_table_returns_string(
        self, 
        gold_ppo_plan, 
        platinum_ppo_plan,
        typical_couple_income,
        typical_baseline_spend
    ):
        """Should return a formatted string table."""
        from src.insurance.compare import compare_plans, format_comparison_table
        
        results = compare_plans(
            plans=[gold_ppo_plan, platinum_ppo_plan],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
        )
        
        table = format_comparison_table(results)
        
        assert isinstance(table, str)
        assert "Gold" in table or "Blue Shield" in table  # Should contain plan names

    def test_format_table_is_markdown(
        self, 
        gold_ppo_plan, 
        platinum_ppo_plan,
        typical_couple_income,
        typical_baseline_spend
    ):
        """Table should be markdown formatted."""
        from src.insurance.compare import compare_plans, format_comparison_table
        
        results = compare_plans(
            plans=[gold_ppo_plan, platinum_ppo_plan],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
        )
        
        table = format_comparison_table(results)
        
        # Markdown tables have | and - characters
        assert "|" in table
        assert "-" in table


class TestScenarioBreakdown:
    """Test per-scenario wealth breakdown."""

    def test_result_contains_scenario_breakdown(
        self, 
        gold_ppo_plan,
        typical_couple_income,
        typical_baseline_spend
    ):
        """Result should contain per-scenario wealth values."""
        from src.insurance.compare import compare_plans
        
        results = compare_plans(
            plans=[gold_ppo_plan],
            annual_income=typical_couple_income,
            annual_baseline_spend=typical_baseline_spend,
        )
        
        r = results[0]
        assert hasattr(r, "scenario_wealth")
        assert isinstance(r.scenario_wealth, dict)
        assert "no_use" in r.scenario_wealth
        assert "cat_in_network" in r.scenario_wealth
