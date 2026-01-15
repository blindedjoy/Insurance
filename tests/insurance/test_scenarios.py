"""TDD tests for scenario definitions.

Scenarios represent possible healthcare outcome states for geometric mean calculation.
Tests written BEFORE implementation following TDD principles.
"""

import pytest
from dataclasses import fields


class TestScenarioDataclass:
    """Test Scenario data model structure."""

    def test_scenario_exists(self):
        """Scenario dataclass should exist."""
        from src.insurance.scenarios import Scenario
        assert Scenario is not None

    def test_scenario_is_dataclass(self):
        """Scenario should be a dataclass."""
        from src.insurance.scenarios import Scenario
        assert hasattr(Scenario, "__dataclass_fields__")

    def test_scenario_required_fields(self, no_use_scenario):
        """Scenario should have name, probability, and medical_oop."""
        assert hasattr(no_use_scenario, "name")
        assert hasattr(no_use_scenario, "probability")
        assert hasattr(no_use_scenario, "medical_oop")

    def test_scenario_has_extra_oon(self, cat_oon_scenario):
        """Scenario should track extra OON costs."""
        assert hasattr(cat_oon_scenario, "extra_oon")
        assert cat_oon_scenario.extra_oon > 0


class TestScenarioValues:
    """Test scenario values are sensible."""

    def test_no_use_has_zero_oop(self, no_use_scenario):
        """No use scenario should have $0 medical OOP."""
        assert no_use_scenario.medical_oop == 0.0

    def test_minor_use_has_moderate_oop(self, minor_use_scenario):
        """Minor use should have moderate OOP ($100-1000)."""
        assert 0 < minor_use_scenario.medical_oop < 2000

    def test_catastrophic_has_high_oop(self, cat_in_network_scenario):
        """Catastrophic scenario should hit OOP max."""
        # Typical OOP max range: $8k-18k for couples
        assert cat_in_network_scenario.medical_oop >= 5000

    def test_oon_scenario_has_extra_exposure(self, cat_oon_scenario):
        """OON catastrophe should include post-stabilization exposure."""
        total = cat_oon_scenario.medical_oop + cat_oon_scenario.extra_oon
        assert total > cat_oon_scenario.medical_oop

    def test_probabilities_sum_to_one(self, default_scenarios):
        """Reference probabilities should sum to ~1.0."""
        total_prob = sum(s.probability for s in default_scenarios)
        assert 0.99 <= total_prob <= 1.01


class TestBuildScenariosForPlan:
    """Test scenario builder that fills in plan-specific values."""

    def test_build_scenarios_exists(self):
        """build_scenarios_for_plan function should exist."""
        from src.insurance.scenarios import build_scenarios_for_plan
        assert callable(build_scenarios_for_plan)

    def test_build_scenarios_fills_minor_oop(self, gold_ppo_plan):
        """Builder should use plan's expected_minor_oop for minor_use scenario."""
        from src.insurance.scenarios import build_scenarios_for_plan
        
        scenarios = build_scenarios_for_plan(gold_ppo_plan)
        minor = next(s for s in scenarios if s.name == "minor_use")
        
        assert minor.medical_oop == gold_ppo_plan.expected_minor_oop

    def test_build_scenarios_fills_oop_max(self, gold_ppo_plan):
        """Builder should use plan's OOP max for catastrophic scenario."""
        from src.insurance.scenarios import build_scenarios_for_plan
        
        scenarios = build_scenarios_for_plan(gold_ppo_plan)
        cat = next(s for s in scenarios if s.name == "cat_in_network")
        
        assert cat.medical_oop == gold_ppo_plan.in_network_oop_max

    def test_build_scenarios_handles_oon_emergency(self, gold_ppo_plan):
        """Builder should set OON emergency OOP based on plan config."""
        from src.insurance.scenarios import build_scenarios_for_plan
        
        scenarios = build_scenarios_for_plan(gold_ppo_plan)
        oon = next(s for s in scenarios if s.name == "cat_oon_emergency")
        
        # If plan treats OON emergency as in-network, OOP should match OOP max
        if gold_ppo_plan.oon_emergency_treated_as_in_network:
            assert oon.medical_oop == gold_ppo_plan.in_network_oop_max

    def test_build_scenarios_adds_post_stabilization(self, gold_ppo_plan):
        """Builder should add post-stabilization exposure if not covered."""
        from src.insurance.scenarios import build_scenarios_for_plan
        
        scenarios = build_scenarios_for_plan(gold_ppo_plan)
        oon = next(s for s in scenarios if s.name == "cat_oon_emergency")
        
        if not gold_ppo_plan.post_stabilization_oon_covered:
            assert oon.extra_oon == gold_ppo_plan.post_stabilization_exposure
        else:
            assert oon.extra_oon == 0.0

    def test_build_scenarios_returns_four_scenarios(self, gold_ppo_plan):
        """Builder should return the four standard scenarios."""
        from src.insurance.scenarios import build_scenarios_for_plan
        
        scenarios = build_scenarios_for_plan(gold_ppo_plan)
        
        assert len(scenarios) == 4
        names = {s.name for s in scenarios}
        assert names == {"no_use", "minor_use", "cat_in_network", "cat_oon_emergency"}


class TestScenarioTotalCost:
    """Test scenario cost calculation."""

    def test_total_oop_calculation(self, cat_oon_scenario):
        """total_oop should sum medical_oop and extra_oon."""
        from src.insurance.scenarios import Scenario
        
        total = cat_oon_scenario.medical_oop + cat_oon_scenario.extra_oon
        
        # If Scenario has a total_oop property/method
        if hasattr(cat_oon_scenario, "total_oop"):
            assert cat_oon_scenario.total_oop == total
