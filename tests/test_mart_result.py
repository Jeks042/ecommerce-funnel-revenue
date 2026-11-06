from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import prepare_measurement_fixture
from check_mart_result import check

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from render_marts import render


class MartEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((ROOT/'reports/evidence/marts-fixture-20261106.json').read_text())

    def test_native_fixture_evidence(self):
        check(self.r)

    def test_fixture_runs_in_a_fresh_checkout(self):
        private=(ROOT/'private').resolve();private.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='fixture-clean-',dir=private) as folder:
            fresh=Path(folder).resolve()
            self.assertTrue(fresh.is_relative_to(private))
            (fresh/'sql').mkdir()
            (fresh/'sql/07_measurement_gate.sql').write_bytes((ROOT/'sql/07_measurement_gate.sql').read_bytes())
            self.assertFalse((fresh/'private').exists())
            with patch.object(prepare_measurement_fixture,'ROOT',fresh):
                prepare_measurement_fixture.prepare()
            self.assertTrue((fresh/'private/measurement_fixture.sql').is_file())

    def test_dropped_item_occurrence_is_rejected(self):
        next(x for x in self.r['fingerprints'] if x['model']=='fact_transaction_items')['row_count']-=1
        with self.assertRaises(AssertionError):check(self.r)

    def test_unkeyed_events_cannot_disappear(self):
        self.r['source']['unkeyed_events']=0
        with self.assertRaises(AssertionError):check(self.r)

    def test_failed_native_assertion_is_rejected(self):
        self.r['checks'][0]['passed']=False
        with self.assertRaises(AssertionError):check(self.r)

    def test_purchase_exclusion_cannot_disappear(self):
        self.r['purchase_coverage'][0]['missing_id_events']=0
        with self.assertRaises(AssertionError):check(self.r)

    def test_duplicate_scope_is_rejected(self):
        self.r['scopes'].append(deepcopy(self.r['scopes'][0]))
        with self.assertRaises(AssertionError):check(self.r)

    def test_project_sql_injection_is_rejected(self):
        with self.assertRaises(ValueError):render('example-project`; DROP TABLE x','ecommerce_v1_test',ROOT/'private/ci-render')

    def test_unrelated_dataset_is_rejected(self):
        with self.assertRaises(ValueError):render('example-project','user_work',ROOT/'private/ci-render')

    def test_private_configuration_cannot_be_written_to_public_docs(self):
        with self.assertRaises(ValueError):render('example-project','ecommerce_v1_test',ROOT/'docs')


if __name__=='__main__':
    unittest.main()
