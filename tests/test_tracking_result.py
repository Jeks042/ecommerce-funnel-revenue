"""Reject inconsistent published evidence; no credentials or source execution."""
import json
from pathlib import Path
import unittest

from check_tracking_result import check

ROOT=Path(__file__).resolve().parents[1]


class TrackingEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.result=json.loads((ROOT/'reports/evidence/tracking-timing-20261106.json').read_text())

    def test_published_evidence_reconciles(self):
        self.assertGreaterEqual(len(check(self.result)),58)

    def test_rejects_dropped_date_device_row(self):
        self.result['daily_device_coverage'].pop()
        with self.assertRaisesRegex(ValueError,'daily event partition'):
            check(self.result)

    def test_rejects_strict_chain_larger_than_tie_sensitivity(self):
        row=next(x for x in self.result['scope_sensitivity'] if x['scope']=='all_keyed')
        row['strict_cart_sessions']=row['tied_cart_sessions']+1
        with self.assertRaisesRegex(ValueError,'strict/tied sensitivity'):
            check(self.result)

    def test_rejects_dropped_missing_start_group(self):
        self.result['session_checks']['without_start']-=1
        with self.assertRaisesRegex(ValueError,'start partition'):
            check(self.result)

    def test_rejects_double_counted_boundary_exclusion(self):
        self.result['session_checks']['edge_sessions']+=1
        with self.assertRaisesRegex(ValueError,'edge partition'):
            check(self.result)

    def test_rejects_unsupported_ordering_field_count(self):
        row=self.result['ordering_field_coverage'][0]
        row['previous_positive']=row['events']+1
        with self.assertRaisesRegex(ValueError,'ordering field bounds'):
            check(self.result)


if __name__=='__main__':
    unittest.main()
