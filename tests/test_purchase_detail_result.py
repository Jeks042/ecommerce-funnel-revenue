"""Evidence-integrity regression checks; no credentials or warehouse scan."""
import json
from pathlib import Path
import unittest

from check_purchase_detail_result import check

ROOT = Path(__file__).resolve().parents[1]


class PurchaseDetailEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.result = json.loads((ROOT/'reports/evidence/purchase-detail-diagnostics-20261106.json').read_text())

    def test_published_evidence_reconciles(self):
        self.assertGreaterEqual(len(check(self.result)),21)

    def test_rejects_double_counted_identifier(self):
        self.result['diagnostic_buckets'][0]['id_groups'] += 1
        with self.assertRaisesRegex(ValueError,'group partition'):
            check(self.result)

    def test_rejects_broader_agreeing_population(self):
        self.result['group_checks']['native_item_agree_candidates'] = self.result['group_checks']['native_complete_candidates']+1
        with self.assertRaisesRegex(ValueError,'nested candidate'):
            check(self.result)

    def test_rejects_dropped_device_date(self):
        self.result['coverage_by_date_device'].pop()
        with self.assertRaisesRegex(ValueError,'date/device event coverage'):
            check(self.result)

    def test_rejects_field_count_assigned_to_wrong_bucket(self):
        row = self.result['field_differences_by_bucket'][0]
        row['differing_id_groups'] += 1
        with self.assertRaises(ValueError):
            check(self.result)

    def test_rejects_invented_amount(self):
        self.result['group_checks']['diagnostic_native_amount'] = float('inf')
        with self.assertRaisesRegex(ValueError,'finite nonnegative'):
            check(self.result)


if __name__ == '__main__':
    unittest.main()
