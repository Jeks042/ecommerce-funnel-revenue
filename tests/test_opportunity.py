from decimal import Decimal
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from assess_opportunity import planning_power,sample_size,visit_scenario,assess
ROOT=Path(__file__).resolve().parents[1]


class OpportunityTests(unittest.TestCase):
    def test_absolute_points_not_relative_percent(self):
        r=visit_scenario(27289,7874,1437,'0.01','1')
        self.assertEqual(r['additional_cart_visit_equivalents'],'272.890000')
        self.assertEqual(r['additional_qualified_completion_visit_equivalents'],'49.802252')

    def test_no_assumed_downstream_gain(self):
        self.assertEqual(visit_scenario(27289,7874,1437,'.02','0')['additional_qualified_completion_visit_equivalents'],'0.000000')
        for m in ['0','.5','1']:
            self.assertEqual(Decimal(visit_scenario(27289,7874,1437,'0',m)['additional_cart_visit_equivalents']),0)

    def test_downside_is_retained(self):
        r=visit_scenario(27289,7874,1437,'-.01','1')
        self.assertLess(Decimal(r['additional_qualified_completion_visit_equivalents']),0)

    def test_scenarios_respect_feasible_populations(self):
        for values in [(100,10,20,'.01','1'),(100,0,0,'.01','1'),(100,50,20,'.6','1'),
                       (100,50,20,'-.4','0'),(100,50,20,'.01','2'),(100,50,20,'NaN','1')]:
            with self.assertRaises(ValueError):visit_scenario(*values)

    def test_more_power_and_smaller_effect_need_more_visitors(self):
        self.assertGreater(sample_size(.3,.01,.9),sample_size(.3,.01,.8))
        self.assertGreater(sample_size(.3,.005),sample_size(.3,.01))

    def test_two_sided_power_symmetry_and_null(self):
        self.assertAlmostEqual(planning_power(.2,.01,25000),planning_power(.21,-.01,25000),12)
        self.assertAlmostEqual(planning_power(.3,0,1000),.05,12)

    def test_integer_sample_meets_target_and_predecessor_does_not(self):
        n=sample_size(.3,.01)
        self.assertGreaterEqual(planning_power(.3,.01,n),.8)
        self.assertLess(planning_power(.3,.01,n-1),.8)

    def test_invalid_power_inputs(self):
        for p,e,power,alpha in [(0,.01,.8,.05),(.99,.02,.8,.05),(.3,0,.8,.05),(.3,.01,.01,.05),(.3,.01,.8,0)]:
            with self.assertRaises(ValueError):sample_size(p,e,power,alpha)

    def test_independent_statsmodels_reference(self):
        d=json.loads((ROOT/'reports/evidence/power-reference-20261110.json').read_text(encoding='utf-8'))
        for r in d['cases']:
            for nkey,pkey in [('visitors_per_arm','power'),('previous_integer','previous_power')]:
                self.assertAlmostEqual(planning_power(r['baseline'],r['effect'],r[nkey]),r[pkey],12)

    def test_two_distinct_units_and_unavailable_money(self):
        summary=json.loads((ROOT/'reports/evidence/funnel-analysis-20261110.json').read_text(encoding='utf-8'))
        assumptions=json.loads((ROOT/'reports/evidence/scenario-assumptions-v1.json').read_text(encoding='utf-8'))
        d=assess(summary,assumptions)
        self.assertEqual(len(d['scenarios']),15)
        self.assertEqual(len(d['visitor_power_illustrations']),9)
        self.assertIsNone(d['financial_return'])
        self.assertIsNone(d['calendar_duration'])
        self.assertFalse(d['launch_ready'])
