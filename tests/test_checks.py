"""Check the boundary between a successful process and executed assertions."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'web_template/scripts/run_check.py'
HELPER = ROOT / 'web_template/scripts/scenario.cjs'


def run_cases(tmp_path, cases, command):
    args = [sys.executable, str(RUNNER)]
    for case in cases:
        args += ['--case', case]
    result = subprocess.run([*args, '--', *command], cwd=tmp_path, capture_output=True, text=True, timeout=15)
    records = [json.loads(line) for line in (tmp_path / '.agent/checks.jsonl').read_text().splitlines()]
    coverage = json.loads((tmp_path / '.agent/coverage.json').read_text())
    return result, records[-1], coverage


def events_command(events):
    script = ('import os; from pathlib import Path; '
              f'Path(os.environ["ARC_CHECK_RESULTS"]).write_text({events!r})')
    return [sys.executable, '-c', script]


@pytest.mark.parametrize('events', [
    '',
    '{broken json}\n',
    '[]\n',
    '{"case":"a","status":"passed"}\n',
    '{"case":"a","status":"started"}\n{"case":"a","status":"failed"}\n',
    '{"case":"a","status":"started"}\n{"case":"a","status":"blocked"}\n',
    '{"case":"other","status":"started"}\n',
    '{"case":"a","status":"started"}\n' * 2,
    '{"case":"a","status":"started"}\n{"case":"a","status":"passed"}\n'
    '{"case":"a","status":"failed"}\n',
])
def test_successful_command_cannot_certify_missing_or_invalid_evidence(tmp_path, events):
    result, record, coverage = run_cases(tmp_path, ['a'], events_command(events))
    assert result.returncode == 1
    assert record['command_exit_code'] == 0
    assert record['status'] == 'failed'
    assert coverage['a']['status'] != 'passed'


def test_group_only_certifies_completed_cases_and_retry_invalidates_old_pass(tmp_path):
    events = '{"case":"a","status":"started"}\n{"case":"a","status":"passed"}\n'
    result, record, coverage = run_cases(tmp_path, ['a', 'b'], events_command(events))
    assert result.returncode == 1
    assert coverage['a']['status'] == 'passed'
    assert coverage['b']['status'] == 'not_run'
    previous_id = record['check_id']
    result, record, coverage = run_cases(tmp_path, ['a'], events_command(''))
    assert result.returncode == 1
    assert coverage['a']['status'] == 'not_run'
    assert coverage['a']['check_id'] != previous_id


@pytest.mark.skipif(not shutil.which('node'), reason='Node required for browser scenario helper')
def test_helper_records_assertion_failure_blocked_setup_and_independent_success(tmp_path):
    script = """
const { scenario } = require(process.argv[1]);
const assert = require('node:assert/strict');
(async () => {
  await scenario('failed', async () => { await Promise.resolve(); assert.equal(1, 2); });
  await scenario('blocked', async () => { require('node:fs').writeFileSync('unexpected-assertions', 'ran'); },
    async () => { throw new Error('setup unavailable'); });
  await scenario('passed', async () => { await Promise.resolve(); assert.equal(1, 1); });
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    result, record, coverage = run_cases(tmp_path, ['failed', 'blocked', 'passed'],
                                         [shutil.which('node'), '-e', script, str(HELPER)])
    assert result.returncode == 1
    assert {case: value['status'] for case, value in coverage.items()} == {
        'failed': 'failed', 'blocked': 'blocked', 'passed': 'passed',
    }
    assert 'setup unavailable' in coverage['blocked']['error']
    assert not (tmp_path / 'unexpected-assertions').exists()
    assert record['command_exit_code'] == 1


@pytest.mark.skipif(not shutil.which('node'), reason='Node required for browser scenario helper')
def test_helper_success_records_awaited_cases(tmp_path):
    script = """
const { scenario } = require(process.argv[1]);
(async () => {
  let ready = false;
  await scenario('a', async () => { if (!ready) throw new Error('setup not awaited'); },
    async () => { await new Promise(resolve => setTimeout(resolve, 10)); ready = true; });
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    result, record, coverage = run_cases(tmp_path, ['a'], [shutil.which('node'), '-e', script, str(HELPER)])
    assert result.returncode == 0
    assert record['status'] == coverage['a']['status'] == 'passed'
