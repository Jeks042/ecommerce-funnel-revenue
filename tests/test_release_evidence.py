"""Reject gaps or unexplained changes in the source-backed release receipt."""
import copy
import sys
import unittest
from pathlib import Path
from check_release_evidence import check, read, RECEIPT
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from render_release_checks import render


class ReleaseEvidenceTests(unittest.TestCase):
    def test_accepted_release(self):
        self.assertEqual(check()['models_reconciled'], 8)

    def rejected(self, change):
        receipt = copy.deepcopy(read(RECEIPT))
        change(receipt)
        with self.assertRaises((AssertionError, KeyError, ValueError)):
            check(receipt)

    def test_missing_model(self):
        self.rejected(lambda r: r['models'].pop())

    def test_changed_model_fingerprint(self):
        self.rejected(lambda r: r['models'][0].update(content_checksum='0'))

    def test_reused_native_job(self):
        self.rejected(lambda r: r['runs'][1].update(job_reference_sha256=r['runs'][0]['job_reference_sha256']))

    def test_cached_result_cannot_pass_fresh_gate(self):
        self.rejected(lambda r: r['runs'][0].update(processed_display='0 B (results cached)'))

    def test_scan_limit(self):
        self.rejected(lambda r: r['runs'][0].update(validator_estimate_display='3.1 GB'))

    def test_no_extra_approximate_exceptions(self):
        self.rejected(lambda r: r['comparisons'][2]['reviewed_approximate_diagnostics'][0].update(path='session_checks/keyed_sessions'))

    def test_changed_fresh_result_digest(self):
        self.rejected(lambda r: r['comparisons'][3].update(fresh_canonical_sha256='0'*64))

    def test_configuration_cannot_escape_private(self):
        with self.assertRaises(ValueError):
            render('example-project', 'ecommerce_v1_ci', Path(__file__).parent / 'public-config')
        with self.assertRaises(ValueError):
            render('example-project', 'unrelated', Path(__file__).resolve().parents[1] / 'private/release-test')


if __name__ == '__main__':
    unittest.main()
