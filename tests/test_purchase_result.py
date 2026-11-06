"""Reject evidence corruption independently of warehouse execution."""
import copy
import json
from pathlib import Path
import unittest

from check_purchase_result import validate


class PurchaseEvidenceValidation(unittest.TestCase):
    def setUp(self):
        path=Path(__file__).resolve().parents[1]/'reports/evidence/purchase-reconciliation-20261106.json'
        self.result=json.loads(path.read_text(encoding='utf-8'))

    def test_observed_output_reconciles(self):
        self.assertTrue(all(validate(self.result).values()))

    def test_join_inflated_bucket_is_rejected(self):
        changed=copy.deepcopy(self.result)
        changed['diagnostic_buckets'][0]['purchase_events']+=1
        with self.assertRaises(ValueError): validate(changed)

    def test_missing_identifier_events_cannot_disappear(self):
        changed=copy.deepcopy(self.result)
        changed['purchase_checks']['unusable_id_events']-=1
        with self.assertRaises(ValueError): validate(changed)

    def test_conflict_overlap_cannot_be_double_counted(self):
        changed=copy.deepcopy(self.result)
        changed['transaction_checks']['union_conflict_groups']=30
        with self.assertRaises(ValueError): validate(changed)

    def test_positive_negative_differences_must_reconcile(self):
        changed=copy.deepcopy(self.result)
        changed['purchase_checks']['native_item_mismatch_events']-=1
        with self.assertRaises(ValueError): validate(changed)


if __name__ == '__main__':
    unittest.main()
