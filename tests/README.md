# Purchase-reconciliation validation

`prepare_purchase_fixture.py` replaces the public-source reference in the actual reconciliation SQL with eleven synthetic events. It retains the production extraction, grouping and classification logic. The generated query reads literal fixtures only; the validated scan estimate is zero bytes.

Run `python tests/prepare_purchase_fixture.py` from the repository root. Open the resulting ignored `private/purchase_fixture.sql` in BigQuery, validate it, and execute. Save the returned inner `audit_json` object privately. Check it with `python tests/check_purchase_result.py private/fixture-result.json --expected private/purchase_fixture_expected.json`.

The fixtures cover repeated identical financial records, multi-item purchases without event multiplication, identity conflicts, changed monetary summaries, missing purchase value, missing transaction ID, an observed tax difference, and changed individual item values that preserve the same total. Expected values are declared independently from the production classification logic.

For real-data results, run `python tests/check_purchase_result.py reports/evidence/purchase-reconciliation-20261106.json`. This checks reconciliation, not whether records are genuine commercial orders or whether the source is suitable for every proposed measure.

The native fixture run passed thirteen scalar expectations and four bucket expectations on 5 November 2026. See the purchase-reconciliation receipt for query hashes and execution evidence. No credentialed execution runs automatically on GitHub pushes.

Run the credential-free validator regression checks with `python -m unittest discover -s tests -p "test_*.py"`. These check that corrupted bucket counts, dropped missing-ID events, double-counted conflict groups and inconsistent monetary-difference counts are rejected. They complement the native SQL fixture; they do not replace warehouse execution.
