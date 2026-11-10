import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyse_funnel import admitted,rate,comparable


class FunnelAnalysisTests(unittest.TestCase):
    def test_reporting_thresholds(self):
        self.assertTrue(admitted(30,500))
        for s,n in [(30,499),(29,500),(471,500)]:self.assertFalse(admitted(s,n))

    def test_unknown_zero_denominator(self):
        self.assertIsNone(rate(0,0))
        with self.assertRaises(ValueError):rate(11,10)

    def test_date_mix_can_reverse_a_crude_difference(self):
        a=[{'visit_date':'1','s':720,'n':900},{'visit_date':'2','s':20,'n':100}]
        b=[{'visit_date':'1','s':90,'n':100},{'visit_date':'2','s':270,'n':900}]
        r=comparable(a,b,'s','n')
        self.assertLess(r['crude_gap_pp'],0)
        self.assertAlmostEqual(r['standardized_gap_pp'],10)
        self.assertEqual(r['common_dates'],['1','2'])

    def test_common_date_coverage_and_sparse_retained_groups(self):
        a=[{'visit_date':'1','s':40,'n':500},{'visit_date':'2','s':1,'n':10}]
        b=[{'visit_date':'2','s':50,'n':600}]
        r=comparable(a,b,'s','n')
        self.assertIsNotNone(r['crude_rates'])
        self.assertIsNone(r['standardized_rates'])
        self.assertEqual(r['common_counts'][0]['denominator'],10)

    def test_duplicate_daily_cells_rejected(self):
        r={'visit_date':'1','s':40,'n':500}
        with self.assertRaises(ValueError):comparable([r,r],[r],'s','n')

    def test_leave_one_date_out_is_recomputed(self):
        a=[{'visit_date':str(i),'s':100,'n':1000} for i in range(3)]
        b=[{'visit_date':str(i),'s':100+20*i,'n':1000} for i in range(3)]
        r=comparable(a,b,'s','n')
        self.assertEqual(r['admissible_omissions'],3)
        self.assertAlmostEqual(r['leave_one_day_out_gap_pp'][0],1)
        self.assertAlmostEqual(r['leave_one_day_out_gap_pp'][1],3)


if __name__=='__main__':unittest.main()
