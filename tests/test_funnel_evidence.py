import copy
import unittest
from check_funnel_result import check,read


class FunnelEvidenceTests(unittest.TestCase):
    def test_dropped_independent_cell_is_rejected(self):
        r=copy.deepcopy(read('funnel-reverse-fixture-20261110.json'))
        r['daily_independent']=[]
        with self.assertRaisesRegex(AssertionError,'coverage'):
            check(read('funnel-fixture-20261110.json'),r,True)

    def test_non_nested_count_is_rejected(self):
        d=copy.deepcopy(read('funnel-fixture-20261110.json'))
        d['daily_device'][0]['strict_cart_sessions']=100
        with self.assertRaisesRegex(AssertionError,'Nested'):
            check(d,read('funnel-reverse-fixture-20261110.json'),True)

    def test_tampered_independent_count_is_rejected(self):
        r=copy.deepcopy(read('funnel-reverse-fixture-20261110.json'))
        r['daily_independent'][0]['strict_candidate_sessions']+=1
        with self.assertRaisesRegex(AssertionError,'Independent reverse'):
            check(read('funnel-fixture-20261110.json'),r,True)
