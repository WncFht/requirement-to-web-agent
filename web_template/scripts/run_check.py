"""Capture command logs and derive scenario coverage from execution events."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def read_cases(path, expected):
    results = {case: {'status': 'not_run'} for case in expected}
    started = set()
    errors = []
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            event = json.loads(line)
            case, status = event['case'], event['status']
            if case not in results:
                raise ValueError(f'undeclared case: {case}')
            if status == 'started' and case not in started:
                started.add(case)
            elif (status in {'passed', 'failed', 'blocked'} and case in started
                  and results[case]['status'] == 'not_run'):
                results[case] = {'status': status}
                if event.get('error'):
                    results[case]['error'] = event['error']
            else:
                raise ValueError(f'invalid case transition: {case} -> {status}')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(str(exc))
    return results, errors


def save_record(record):
    ledger = Path('.agent/checks.jsonl')
    with ledger.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')
    # Latest execution wins, including a new attempt that never completes.
    coverage = {}
    for line in ledger.read_text(encoding='utf-8').splitlines():
        check = json.loads(line)
        for case, result in check.get('case_results', {}).items():
            coverage[case] = {**result, 'check_id': check['check_id'], 'check_status': check['status']}
    Path('.agent/coverage.json').write_text(json.dumps(coverage, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', help='command-only check, e.g. build or backend')
    mode.add_argument('--case', action='append', dest='cases', help='expected executed scenario ID; repeat for groups')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a check command is required after --')
    if args.cases and len(set(args.cases)) != len(args.cases):
        parser.error('case IDs must be unique')
    folder = Path('.agent/checks')
    folder.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='check-', suffix='.log', dir=folder)
    log_path = Path(name).resolve()
    record = {
        'check_id': log_path.stem,
        'check': args.check,
        'case_results': {case: {'status': 'not_run'} for case in args.cases or []},
        'started_at': datetime.now(timezone.utc).isoformat(),
        'cwd': str(Path.cwd()),
        'command': command,
        'log': str(log_path),
        'status': 'started',
    }

    events = log_path.with_suffix('.cases.jsonl')
    events.touch()
    record['events'] = str(events)
    env = {**os.environ, 'ARC_CHECK_RESULTS': str(events)}
    with os.fdopen(fd, 'wb') as log:
        save_record(record)
        try:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=env)
            code = result.returncode if result.returncode >= 0 else 128 - result.returncode
        except OSError as exc:
            log.write(f'Unable to start check: {exc}\n'.encode())
            code = 127
    record['command_exit_code'] = code
    results, errors = read_cases(events, args.cases or [])
    record['case_results'] = results
    if errors:
        record['event_errors'] = errors
        # Invalid evidence cannot certify coverage, even when the command succeeds.
        for value in results.values():
            if value['status'] == 'passed':
                value.update(status='not_run', error='Invalid scenario event stream')
    if errors or any(value['status'] != 'passed' for value in results.values()):
        code = code or 1
    record.update(status='passed' if code == 0 else 'failed', exit_code=code,
                  finished_at=datetime.now(timezone.utc).isoformat())
    save_record(record)
    with log_path.open('rb') as log:
        while chunk := log.read(65536):
            sys.stdout.buffer.write(chunk)
    sys.stdout.flush()
    print('\n<check_record>' + json.dumps(record, ensure_ascii=False) + '</check_record>', flush=True)
    return code


if __name__ == '__main__':
    sys.exit(main())
