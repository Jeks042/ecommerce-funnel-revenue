"""Validate saved aggregate diagnostics, optionally against independent fixture expectations."""
import argparse
import json
from math import isfinite
from pathlib import Path


def check(result, expected=None):
    p, g = result['population'], result['group_checks']
    buckets, coverage = result['diagnostic_buckets'], result['coverage_by_date_device']
    passed = []

    def require(condition, label):
        if not condition:
            raise ValueError(label)
        passed.append(label)

    require(p['purchase_events'] == p['unusable_id_events']+g['usable_id_events'], 'purchase partition')
    require(sum(b['id_groups'] for b in buckets) == g['id_groups'], 'group partition')
    require(sum(b['purchase_events'] for b in buckets) == g['usable_id_events'], 'event partition')
    require(len({b['diagnostic_bucket'] for b in buckets}) == len(buckets), 'unique buckets')
    require(g['native_item_agree_candidates'] <= g['native_complete_candidates']
            <= g['conservative_id_candidates'] <= g['id_groups'], 'nested candidate populations')
    require(g['conservative_id_candidates'] <= g['conservative_candidate_events']
            <= g['usable_id_events'], 'candidate event bounds')
    require(g['cross_date_identity_or_summary_conflicts'] <= g['cross_date_repeated_groups']
            <= g['repeated_id_groups'] <= g['id_groups'], 'cross-date bounds')
    require(sum(x['purchase_events'] for x in coverage) == p['purchase_events'], 'date/device event coverage')
    require(sum(x['unusable_id_events'] for x in coverage) == p['unusable_id_events'], 'date/device missing coverage')
    require(sum(x['conservative_candidate_events'] for x in coverage)
            == g['conservative_candidate_events'], 'date/device candidate coverage')
    require(all(0 <= x['native_item_agree_candidate_events'] <= x['conservative_candidate_events']
                <= x['purchase_events']-x['unusable_id_events'] for x in coverage), 'row population bounds')
    require(len({(x['source_suffix'],x['device']) for x in coverage}) == len(coverage), 'unique coverage rows')
    require(len({x['field_path'] for x in result['field_differences']}) == len(result['field_differences']), 'unique fields')
    require(all(0 <= x['differing_id_groups'] <= g['repeated_id_groups']
                for x in result['field_differences']), 'field difference bounds')
    bucket_counts = {b['diagnostic_bucket']:b['id_groups'] for b in buckets}
    cross = result['field_differences_by_bucket']
    require(len({(x['diagnostic_bucket'],x['field_path']) for x in cross}) == len(cross), 'unique bucket/field rows')
    require(all(0 < x['differing_id_groups'] <= bucket_counts[x['diagnostic_bucket']] for x in cross), 'bucket/field bounds')
    require(all(sum(x['differing_id_groups'] for x in cross if x['field_path']==f['field_path'])
                == f['differing_id_groups'] for f in result['field_differences']), 'bucket/field reconciliation')
    for key in ('diagnostic_native_amount','diagnostic_agreeing_native_amount'):
        require(g[key] is None or (isfinite(g[key]) and g[key]>=0), 'finite nonnegative '+key)
    for section in (p,g):
        require(all(isinstance(v,int) and not isinstance(v,bool) and v>=0
                    for k,v in section.items() if not k.startswith('diagnostic_')), 'nonnegative counts')
    if expected:
        for section in ('population','group_checks'):
            for key,value in expected[section].items():
                require(result[section][key] == value, 'fixture '+key)
        actual = {b['diagnostic_bucket']:(b['id_groups'],b['purchase_events']) for b in buckets}
        require(actual == {k:tuple(v) for k,v in expected['buckets'].items()}, 'fixture bucket identities')
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('result',type=Path)
    parser.add_argument('--expected',type=Path)
    args = parser.parse_args()
    checks = check(json.loads(args.result.read_text()),
                   json.loads(args.expected.read_text()) if args.expected else None)
    print(f'{len(checks)} aggregate/fixture checks passed.')
