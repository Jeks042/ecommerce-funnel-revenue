import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/plotting'))
from report_data import coverage_data,scenario_data
from check_report_evidence import check


def read(name):return json.loads((ROOT/'reports/evidence'/name).read_text(encoding='utf-8'))


class ReportEvidenceTests(unittest.TestCase):
    def test_published_report_reconciles(self):
        self.assertTrue(check()['report_chart_data_reproduced'])

    def test_missing_device_date_is_not_filled_with_zero(self):
        d=read('tracking-timing-20261106.json');d['daily_device_coverage'].pop()
        with self.assertRaisesRegex(ValueError,'92 dates'):coverage_data(d)

    def test_duplicate_device_date_rejected(self):
        d=read('tracking-timing-20261106.json');d['daily_device_coverage'].append(copy.deepcopy(d['daily_device_coverage'][0]))
        with self.assertRaisesRegex(ValueError,'92 dates'):coverage_data(d)

    def test_unknown_count_remains_unavailable(self):
        d=read('tracking-timing-20261106.json');d['daily_device_coverage'][0]['cart_events']=None
        with self.assertRaisesRegex(ValueError,'invalid event'):coverage_data(d)

    def test_missing_or_duplicate_scenario_rejected(self):
        for duplicate in [False,True]:
            d=read('opportunity-analysis-20261110.json')
            if duplicate:d['scenarios'].append(copy.deepcopy(d['scenarios'][0]))
            else:d['scenarios'].pop()
            with self.assertRaisesRegex(ValueError,'15 distinct'):scenario_data(d)

    def test_labels_use_explicit_decimal_rounding(self):
        d=scenario_data(read('opportunity-analysis-20261110.json'))
        self.assertEqual(d['rows'][2]['additional_carts_display'],'136.45')
        self.assertEqual(d['rows'][3]['completion_display'],['0.00','24.90','49.80'])
