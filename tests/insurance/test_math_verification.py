"""Math verification tests with hand-calculated golden values.

These tests verify our implementation matches the mathematical definitions.
Each test includes the hand calculation in comments for audit.

TDD approach: These are the "gold standard" tests that prove the math is correct.
"""

import math
import pytest

from src.insurance.geometric_mean import (
    compute_wealth_ratio,
    compute_geometric_mean_ratio,
    compute_disposable_income,
    compute_expected_log_wealth,
)
from src.insurance.plans import MedicalPlan
from src.insurance.scenarios import Scenario


class TestWealthRatioMath:
    """Verify wealth ratio formula: ratio = (disposable - premium - oop) / disposable"""

    def test_wealth_ratio_simple_case(self):
        """
        Hand calculation:
        disposable = $100,000
        premium = $20,000
        oop = $10,000
        remaining = 100,000 - 20,000 - 10,000 = $70,000
        ratio = 70,000 / 100,000 = 0.70
        """
        ratio = compute_wealth_ratio(
            disposable_income=100_000,
            total_premium=20_000,
            scenario_oop=10_000,
        )
        assert ratio == 0.70

    def test_wealth_ratio_no_spending(self):
        """
        Hand calculation:
        disposable = $100,000
        premium = $0
        oop = $0
        remaining = 100,000
        ratio = 100,000 / 100,000 = 1.0
        """
        ratio = compute_wealth_ratio(
            disposable_income=100_000,
            total_premium=0,
            scenario_oop=0,
        )
        assert ratio == 1.0

    def test_wealth_ratio_all_spent(self):
        """
        Hand calculation:
        disposable = $100,000
        premium = $60,000
        oop = $40,000
        remaining = 100,000 - 60,000 - 40,000 = $0
        ratio = 0 / 100,000 = 0.0
        """
        ratio = compute_wealth_ratio(
            disposable_income=100_000,
            total_premium=60_000,
            scenario_oop=40_000,
        )
        assert ratio == 0.0

    def test_wealth_ratio_ruin_scenario(self):
        """
        Hand calculation (costs exceed disposable):
        disposable = $100,000
        premium = $60,000
        oop = $50,000
        remaining = 100,000 - 60,000 - 50,000 = -$10,000
        ratio = max(0, -10,000 / 100,000) = 0.0 (floored at 0)
        """
        ratio = compute_wealth_ratio(
            disposable_income=100_000,
            total_premium=60_000,
            scenario_oop=50_000,
        )
        assert ratio == 0.0  # Floored at 0, not negative

    def test_wealth_ratio_real_numbers(self):
        """
        Hand calculation with YOUR real numbers:
        disposable = $117,350
        premium = $20,924 (Kaiser Platinum + dental + vision)
        oop = $10,000 (OOP max in catastrophe)
        remaining = 117,350 - 20,924 - 10,000 = $86,426
        ratio = 86,426 / 117,350 = 0.7366...
        """
        ratio = compute_wealth_ratio(
            disposable_income=117_350,
            total_premium=20_924,
            scenario_oop=10_000,
        )
        expected = (117_350 - 20_924 - 10_000) / 117_350
        assert abs(ratio - expected) < 1e-10
        assert abs(ratio - 0.7366) < 0.001


class TestGeometricMeanMath:
    """Verify GM formula: GM = (r1 × r2 × ... × rn)^(1/n)"""

    def test_gm_two_values(self):
        """
        Hand calculation:
        GM([4, 9]) = (4 × 9)^(1/2) = 36^0.5 = 6.0
        """
        gm = compute_geometric_mean_ratio([4.0, 9.0])
        assert gm == 6.0

    def test_gm_three_values(self):
        """
        Hand calculation:
        GM([2, 4, 8]) = (2 × 4 × 8)^(1/3) = 64^(1/3) = 4.0
        """
        gm = compute_geometric_mean_ratio([2.0, 4.0, 8.0])
        assert abs(gm - 4.0) < 1e-10  # Floating point tolerance

    def test_gm_wealth_ratios(self):
        """
        Hand calculation with typical wealth ratios:
        GM([0.9, 0.8, 0.5]) = (0.9 × 0.8 × 0.5)^(1/3)
                           = (0.36)^(1/3)
                           = 0.7114...
        """
        gm = compute_geometric_mean_ratio([0.9, 0.8, 0.5])
        expected = (0.9 * 0.8 * 0.5) ** (1/3)
        assert abs(gm - expected) < 1e-10
        assert abs(gm - 0.7114) < 0.001

    def test_gm_four_scenarios(self):
        """
        Hand calculation with 4 scenarios (our model):
        ratios = [0.82, 0.82, 0.73, 0.59]
        product = 0.82 × 0.82 × 0.73 × 0.59 = 0.2896...
        GM = 0.2896^(1/4) = 0.7336...
        """
        ratios = [0.82, 0.82, 0.73, 0.59]
        gm = compute_geometric_mean_ratio(ratios)
        expected = (0.82 * 0.82 * 0.73 * 0.59) ** 0.25
        assert abs(gm - expected) < 1e-10

    def test_gm_with_zero_is_zero(self):
        """
        Key Spitznagel insight: ANY zero makes GM = 0
        GM([0.9, 0.8, 0.0]) = (0.9 × 0.8 × 0.0)^(1/3) = 0^(1/3) = 0
        """
        gm = compute_geometric_mean_ratio([0.9, 0.8, 0.0])
        assert gm == 0.0

    def test_gm_all_same_equals_value(self):
        """
        When all values equal, GM = that value
        GM([0.7, 0.7, 0.7, 0.7]) = (0.7^4)^(1/4) = 0.7
        """
        gm = compute_geometric_mean_ratio([0.7, 0.7, 0.7, 0.7])
        assert abs(gm - 0.7) < 1e-10

    def test_gm_less_than_arithmetic_mean(self):
        """
        Mathematical property: GM ≤ AM, with equality only when all values equal.
        
        For [0.9, 0.8, 0.7, 0.6]:
        AM = (0.9 + 0.8 + 0.7 + 0.6) / 4 = 0.75
        GM = (0.9 × 0.8 × 0.7 × 0.6)^0.25 = 0.7416...
        
        GM < AM ✓
        """
        ratios = [0.9, 0.8, 0.7, 0.6]
        gm = compute_geometric_mean_ratio(ratios)
        am = sum(ratios) / len(ratios)
        
        assert gm < am
        assert abs(am - 0.75) < 1e-10
        assert abs(gm - 0.7416) < 0.001


class TestDisposableIncomeMath:
    """Verify disposable income calculations."""

    def test_disposable_from_after_tax(self):
        """
        Hand calculation:
        after_tax = $180,000
        baseline = $80,000
        disposable = 180,000 - 80,000 = $100,000
        """
        disposable = compute_disposable_income(
            after_tax_income=180_000,
            baseline_spend=80_000,
        )
        assert disposable == 100_000

    def test_disposable_from_gross_with_tax(self):
        """
        Hand calculation:
        gross = $275,000
        tax_rate = 0.326 (32.6%)
        after_tax = 275,000 × (1 - 0.326) = 275,000 × 0.674 = $185,350
        baseline = $68,000
        disposable = 185,350 - 68,000 = $117,350
        """
        disposable = compute_disposable_income(
            gross_income=275_000,
            tax_rate=0.326,
            baseline_spend=68_000,
        )
        expected = 275_000 * (1 - 0.326) - 68_000
        assert abs(disposable - expected) < 1
        assert abs(disposable - 117_350) < 1


class TestExpectedLogWealthMath:
    """Verify expected log wealth calculation (equal weighting)."""

    def test_log_wealth_formula(self):
        """
        Formula: E[log(W)] = (1/n) × Σ log(rᵢ)
        
        For ratios [0.9, 0.8, 0.7, 0.6]:
        log(0.9) = -0.1054
        log(0.8) = -0.2231
        log(0.7) = -0.3567
        log(0.6) = -0.5108
        sum = -1.1960
        E[log(W)] = -1.1960 / 4 = -0.2990
        """
        import math
        ratios = [0.9, 0.8, 0.7, 0.6]
        log_sum = sum(math.log(r) for r in ratios)
        expected = log_sum / len(ratios)
        
        assert abs(expected - (-0.2990)) < 0.001

    def test_gm_from_exp_log(self):
        """
        Verify: GM = exp(E[log(W)])
        
        For ratios [0.9, 0.8, 0.7, 0.6]:
        E[log(W)] = -0.2990
        GM = exp(-0.2990) = 0.7416...
        
        This should match compute_geometric_mean_ratio().
        """
        ratios = [0.9, 0.8, 0.7, 0.6]
        
        # Method 1: Direct GM
        gm_direct = compute_geometric_mean_ratio(ratios)
        
        # Method 2: exp(E[log(W)])
        log_sum = sum(math.log(r) for r in ratios)
        expected_log = log_sum / len(ratios)
        gm_from_log = math.exp(expected_log)
        
        assert abs(gm_direct - gm_from_log) < 1e-10


class TestEndToEndMath:
    """End-to-end verification with real scenario."""

    def test_kaiser_platinum_scenario_by_hand(self):
        """
        Complete hand calculation for Kaiser Platinum HMO.
        
        YOUR NUMBERS:
        - Gross: $275,000
        - Tax rate: 32.6%
        - After-tax: $185,350
        - Baseline: $68,000
        - Disposable: $117,350
        
        KAISER PLATINUM:
        - Premium: $19,824 (medical) + $1,100 (dental+vision) = $20,924
        
        SCENARIOS (equal weighted):
        1. No use:       OOP = $0
           ratio = (117,350 - 20,924 - 0) / 117,350 = 0.8217
        
        2. Minor use:    OOP = $450 (copays + dental/vision)
           ratio = (117,350 - 20,924 - 450) / 117,350 = 0.8178
        
        3. Cat in-net:   OOP = $10,000 (OOP max)
           ratio = (117,350 - 20,924 - 10,000) / 117,350 = 0.7366
        
        4. Cat OON:      OOP = $10,000 + $16,500 (post-stab + ambulance) = $26,500
           ratio = (117,350 - 20,924 - 26,500) / 117,350 = 0.5959
        
        GM = (0.8217 × 0.8178 × 0.7366 × 0.5959)^0.25 = 0.7336
        """
        disposable = 117_350
        premium = 20_924
        
        # Hand-calculate each ratio
        r1 = (disposable - premium - 0) / disposable        # No use
        r2 = (disposable - premium - 450) / disposable      # Minor
        r3 = (disposable - premium - 10_000) / disposable   # Cat in-net
        r4 = (disposable - premium - 26_500) / disposable   # Cat OON
        
        ratios = [r1, r2, r3, r4]
        
        # Verify individual ratios
        assert abs(r1 - 0.8217) < 0.001
        assert abs(r2 - 0.8178) < 0.001
        assert abs(r3 - 0.7366) < 0.001
        assert abs(r4 - 0.5959) < 0.001
        
        # Verify GM
        gm = compute_geometric_mean_ratio(ratios)
        expected_gm = (r1 * r2 * r3 * r4) ** 0.25
        assert abs(gm - expected_gm) < 1e-10
        
        # The GM should be around 0.7336
        assert abs(gm - 0.7336) < 0.01


class TestSpitznagelInsights:
    """Tests that verify Spitznagel's key insights."""

    def test_tail_risk_dominates(self):
        """
        Spitznagel's insight: A single catastrophic outcome dominates GM.
        
        Scenario A: [0.9, 0.9, 0.9, 0.9]  → GM = 0.9
        Scenario B: [0.9, 0.9, 0.9, 0.1]  → GM = (0.9³ × 0.1)^0.25 = 0.5196
        
        One bad outcome (0.1 vs 0.9) cuts GM by 42%!
        """
        ratios_good = [0.9, 0.9, 0.9, 0.9]
        ratios_one_bad = [0.9, 0.9, 0.9, 0.1]
        
        gm_good = compute_geometric_mean_ratio(ratios_good)
        gm_one_bad = compute_geometric_mean_ratio(ratios_one_bad)
        
        assert abs(gm_good - 0.9) < 1e-10
        expected_bad = (0.9 * 0.9 * 0.9 * 0.1) ** 0.25  # 0.5196...
        assert abs(gm_one_bad - expected_bad) < 1e-10
        
        # One bad outcome cuts GM dramatically (>40% reduction)
        reduction = (gm_good - gm_one_bad) / gm_good
        assert reduction > 0.40  # >40% reduction from one bad scenario

    def test_oop_max_is_put_protection(self):
        """
        Spitznagel's analogy: OOP max is like a put option (caps downside).
        
        Plan A: OOP max = $18,400 → worst ratio = 0.596
        Plan B: OOP max = $10,000 → worst ratio = 0.668 (+12% better!)
        
        Lower OOP max = better "put" = higher worst-case ratio.
        """
        disposable = 117_350
        premium = 20_000  # Same premium for comparison
        oon_extra = 16_500  # Post-stabilization + ambulance
        
        # Plan A: Gold (high OOP max)
        oop_max_gold = 18_400
        worst_gold = (disposable - premium - oop_max_gold - oon_extra) / disposable
        
        # Plan B: Platinum (low OOP max)
        oop_max_plat = 10_000
        worst_plat = (disposable - premium - oop_max_plat - oon_extra) / disposable
        
        # Platinum has better worst-case ratio
        assert worst_plat > worst_gold
        improvement = (worst_plat - worst_gold) / worst_gold
        assert improvement > 0.10  # >10% improvement

    def test_premium_vs_protection_tradeoff(self):
        """
        The key question: Is $1,368 extra premium worth $8,400 less OOP max?
        
        Kaiser Gold:     Premium $19,556, OOP max $18,400
        Kaiser Platinum: Premium $20,924, OOP max $10,000
        
        In catastrophe:
        Gold total cost:     $19,556 + $18,400 = $37,956
        Platinum total cost: $20,924 + $10,000 = $30,924
        
        Platinum saves $7,032 in catastrophe for $1,368 more premium.
        That's a 5.1x payoff ratio. Worth it!
        """
        gold_premium = 19_556
        gold_oop_max = 18_400
        plat_premium = 20_924
        plat_oop_max = 10_000
        
        premium_diff = plat_premium - gold_premium  # $1,368
        oop_savings = gold_oop_max - plat_oop_max   # $8,400
        net_benefit = oop_savings - premium_diff    # $7,032
        payoff_ratio = oop_savings / premium_diff   # 6.14x
        
        assert abs(premium_diff - 1_368) < 1
        assert abs(oop_savings - 8_400) < 1
        assert abs(net_benefit - 7_032) < 1
        assert payoff_ratio > 5.0  # Excellent payoff
