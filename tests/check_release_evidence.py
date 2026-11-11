"""Verify the fresh-run receipt without warehouse credentials or raw records."""
import copy
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = 'reports/evidence/release-receipt-20261111.json'
APPROX_FIELDS = {'median_observed_span_seconds', 'p95_observed_span_seconds'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def check(receipt=None):
    r = read(RECEIPT) if receipt is None else copy.deepcopy(receipt)
    assert r['contract_version'] == 1
    assert (r['source_start'], r['source_end'], r['analysis_month']) == ('20201101', '20210131', '202012')
    prior = {v['model']: v for v in read('reports/evidence/marts-reproduction-20261106.json')['models']}
    models = {v['model']: v for v in r['models']}
    assert len(models) == len(r['models']) == 8 and models.keys() == prior.keys(), 'Incomplete model coverage'
    for name, v in models.items():
        assert int(v['row_count']) == int(prior[name]['row_count']), 'Model row count changed'
        assert v['content_checksum'] == prior[name]['content_checksum'], 'Model fingerprint changed'
    jobs = {v['key']: v for v in r['runs']}
    expected = {f'{i:02d}_{v["model"]}' for i, v in enumerate(r['models'], 1)}
    expected |= {'09_mart_validation', '10_inventory', '11_source_coverage', '12_funnel_profile', '13_reverse_funnel'}
    assert jobs.keys() == expected and len(r['runs']) == 13
    assert len({v['job_reference_sha256'] for v in r['runs']}) == 13, 'Duplicate execution reference'
    for job in jobs.values():
        assert job['status'] == 'SUCCESS' and job['location'] == 'US'
        assert job['started_utc'].startswith(r['release_date']) and job['ended_utc'] >= job['started_utc']
        assert job['processed_display'] != '0 B' and 'cached' not in job['processed_display'].lower()
        size, unit = job['validator_estimate_display'].split()
        assert float(size.replace(',', '')) * 1024 ** ['B', 'KB', 'MB', 'GB', 'TB'].index(unit) <= 3 * 1024 ** 3
        for field in ['job_reference_sha256', 'rendered_sql_sha256', 'result_canonical_sha256']:
            assert re.fullmatch('[0-9a-f]{64}', job[field])
    for i, model in enumerate(r['models'], 1):
        assert digest(canonical(model)) == jobs[f'{i:02d}_{model["model"]}']['result_canonical_sha256']
    comparisons = {c['key']: c for c in r['comparisons']}
    assert len(comparisons) == len(r['comparisons']) == 5
    assert comparisons.keys() == {k for k in expected if int(k[:2]) >= 9}
    for key, c in comparisons.items():
        baseline = read(c['accepted_file'])
        assert digest((ROOT / c['accepted_file']).read_bytes()) == c['accepted_file_sha256']
        assert digest(canonical(baseline)) == c['accepted_canonical_sha256']
        fresh = copy.deepcopy(baseline)
        if key == '11_source_coverage':
            fresh = read('reports/evidence/release-source-coverage-20261111.json')
            a, b = copy.deepcopy(fresh), copy.deepcopy(baseline)
            changes = c['reviewed_approximate_diagnostics']
            assert len(changes) == 2 and {d['path'] for d in changes} == {'session_checks/' + f for f in APPROX_FIELDS}
            for d in changes:
                field = d['path'].split('/')[1]
                assert a['session_checks'].pop(field) == d['fresh']
                assert b['session_checks'].pop(field) == d['accepted']
                assert all(type(d[x]) in (int, float) and math.isfinite(d[x]) and d[x] >= 0 for x in ['fresh', 'accepted'])
            assert a == b, 'Exact coverage evidence changed'
        else:
            assert not c['reviewed_approximate_diagnostics']
        if key == '12_funnel_profile':
            keyed = {v['model']: v for v in fresh['input_fingerprints']}
            order = c['fresh_input_fingerprint_order']
            assert len(order) == len(set(order)) == 3 and set(order) == keyed.keys()
            fresh['input_fingerprints'] = [keyed[name] for name in order]
        else:
            assert not c['fresh_input_fingerprint_order']
        assert digest(canonical(fresh)) == c['fresh_canonical_sha256'] == jobs[key]['result_canonical_sha256']
        assert c['exact_json_match'] == (fresh == baseline) and c['all_exact_fields_match']
    clean = r['clean_checkout']
    assert clean['checkout_clean_after_reproduction'] and clean['fresh_virtual_environment']
    assert clean['tests_passed'] == 57 and clean['rendered_figure_files'] == 8
    assert clean['summary_and_scenarios_regenerated_without_tracked_changes'] and clean['all_eight_rendered_asset_bytes_match'] and clean['chart_data_validated']
    assert r['checks'] == {'mart_source_checks': 995, 'funnel_source_and_reverse_checks': 4682, 'model_count': 8, 'fresh_native_jobs': 13, 'direct_source_rereads': 2}
    for path, expected_hash in r['code_sha256'].items():
        assert digest((ROOT / path).read_bytes()) == expected_hash, 'Release checker or renderer changed: ' + path
    assert set(r['code_sha256']) == {'src/render_release_checks.py', 'tests/check_release_evidence.py', 'tests/test_release_evidence.py'}
    return {'fresh_jobs': 13, 'models_reconciled': 8, 'mart_checks': 995, 'funnel_checks': 4682, 'reviewed_approximate_diagnostics': 2}


if __name__ == '__main__':
    print(check())
