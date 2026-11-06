"""Validate aggregate reconciliation and optional warehouse-fixture expectations."""
from pathlib import Path
import argparse
import json


def validate(result, expected=None):
    p, t = result['purchase_checks'], result['transaction_checks']
    buckets = result['diagnostic_buckets']
    checks = {
        'identifier_partition': p['null_id_events'] + p['blank_id_events'] + p['placeholder_id_events'] == p['unusable_id_events'],
        'event_partition': (t['events_with_nonplaceholder_id'] or 0) + p['unusable_id_events'] == p['purchase_events'],
        'group_partition': sum(b['id_groups'] for b in buckets) == t['nonplaceholder_id_groups'],
        'bucket_event_partition': sum(b['purchase_events'] for b in buckets) == (t['events_with_nonplaceholder_id'] or 0),
        'conflict_overlap': t['identity_conflict_groups'] + t['summary_conflict_groups'] - t['overlapping_conflict_groups'] == t['union_conflict_groups'],
        'difference_partition': p['native_above_item_events'] + p['native_below_item_events'] == p['native_item_mismatch_events'],
        'monetary_population': p['native_item_mismatch_events'] <= p['comparable_native_item_events'] <= p['purchase_events'],
        'tax_match_population': p['mismatches_matching_observed_tax'] <= p['native_item_mismatch_events'],
        'unique_buckets': len({b['diagnostic_bucket'] for b in buckets}) == len(buckets),
        'nonnegative_counts': all(v is None or (isinstance(v,int) and not isinstance(v,bool) and v>=0) for section in (p,t) for v in section.values()),
    }
    if expected:
        for key, value in expected.items():
            if key != 'buckets':
                observed = p[key] if key in p else t[key]
                checks['fixture_'+key] = observed == value
        observed_buckets = {b['diagnostic_bucket']:[b['id_groups'],b['purchase_events']] for b in buckets}
        checks['fixture_bucket_set'] = observed_buckets == {k:list(v) for k,v in expected['buckets'].items()}
    failed=[key for key, passed in checks.items() if not passed]
    if failed:
        raise ValueError('Failed reconciliation checks: '+', '.join(failed))
    return checks


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result',type=Path)
    parser.add_argument('--expected',type=Path)
    args=parser.parse_args()
    expected=json.loads(args.expected.read_text(encoding='utf-8')) if args.expected else None
    checks=validate(json.loads(args.result.read_text(encoding='utf-8')),expected)
    print(f'{len(checks)} aggregate/fixture checks passed.')
