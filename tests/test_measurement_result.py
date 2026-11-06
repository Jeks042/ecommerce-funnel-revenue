from copy import deepcopy
import json
from pathlib import Path
import unittest
from check_measurement_result import check


class MeasurementEvidenceTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        self.result=json.loads((root/'reports/evidence/measurement-fixture-20261106.json').read_text())

    def test_fixture_is_consistent(self):
        check(self.result)

    def test_dropped_candidate_link_is_rejected(self):
        self.result['linkage']['linked_candidate_transactions']-=1
        with self.assertRaises(AssertionError):check(self.result)

    def test_missing_purchase_not_hidden_as_zero(self):
        self.result['linkage']['missing_id_events']=0
        with self.assertRaises(AssertionError):check(self.result)

    def test_replay_cannot_inflate_strict_completion(self):
        self.result['scopes'][0]['strict_candidate_sessions']=100
        with self.assertRaises(AssertionError):check(self.result)

    def test_duplicate_scope_cannot_inflate_totals(self):
        self.result['scopes'].append(deepcopy(self.result['scopes'][0]))
        with self.assertRaises(AssertionError):check(self.result)


if __name__=='__main__':
    unittest.main()
