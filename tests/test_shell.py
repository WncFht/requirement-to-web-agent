import os
import shlex
import sys
import time
from pathlib import Path

import pytest
from minisweagent.environments.local import LocalEnvironment
from minisweagent.exceptions import Submitted

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'web_template/scripts/run_check.py'


def execute(tmp_path, command, **kwargs):
    return LocalEnvironment(cwd=str(tmp_path)).execute({'command': command}, **kwargs)


def test_bash_syntax_pipeline_and_quoting(tmp_path):
    result = execute(tmp_path, "a=('space value' 'quote\"'); printf '%s\\n' \"${a[0]}\" \"${a[1]}\"")
    assert result['returncode'] == 0
    assert result['output'] == 'space value\nquote"\n'
    result = execute(tmp_path, "bash -c 'exit 7' | cat")
    assert result['returncode'] == 7
    # Wrapping must preserve literal $, backticks and multiline commands.
    result = execute(tmp_path, "cat <<'EOF'\n$(touch must-not-exist) `echo literal`\nEOF")
    assert '$(touch must-not-exist) `echo literal`' in result['output']
    assert not (tmp_path / 'must-not-exist').exists()


@pytest.mark.parametrize('code', [0, 7])
def test_runner_log_status_and_spaces(tmp_path, code):
    log = tmp_path / 'logs with spaces/check.log'
    child = f'import sys; print("stdout"); print("stderr", file=sys.stderr); sys.exit({code})'
    command = shlex.join([sys.executable, str(RUNNER), '--log', str(log), '--', sys.executable, '-c', child])
    result = execute(tmp_path, command)
    assert result['returncode'] == code
    assert 'stdout' in result['output'] and 'stderr' in result['output']
    assert log.read_text() == result['output']


def test_runner_preserves_failed_pipeline(tmp_path):
    command = shlex.join([sys.executable, str(RUNNER), '--log', str(tmp_path / 'check.log'), '--', 'bash', '-o', 'pipefail', '-c', 'exit 9 | cat'])
    assert execute(tmp_path, command)['returncode'] == 9


def test_later_success_can_still_mask_failure(tmp_path):
    # Document the shell boundary: pipefail is not errexit or a submission gate.
    assert execute(tmp_path, 'false; echo done')['returncode'] == 0


def test_submission_marker_still_works(tmp_path):
    with pytest.raises(Submitted):
        execute(tmp_path, 'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT')


@pytest.mark.skipif(os.name != 'posix', reason='POSIX process groups')
def test_timeout_kills_runner_and_descendants(tmp_path):
    sentinel = tmp_path / 'orphan-survived'
    child = 'import time; from pathlib import Path; time.sleep(1.5); Path(' + repr(str(sentinel)) + ').write_text("alive")'
    command = shlex.join([sys.executable, str(RUNNER), '--log', str(tmp_path / 'timeout.log'), '--', sys.executable, '-c', child])
    result = execute(tmp_path, command, timeout=1)
    assert result['returncode'] == -1
    assert result['extra']['exception_type'] == 'TimeoutExpired'
    time.sleep(0.8)
    assert not sentinel.exists()


@pytest.mark.skipif(os.name != 'posix', reason='POSIX background processes')
def test_background_output_handle_does_not_delay_shell_result(tmp_path):
    import signal

    started = time.monotonic()
    result = execute(tmp_path, 'sleep 30 & echo $! > child.pid; echo ready', timeout=2)
    child = int((tmp_path / 'child.pid').read_text())
    try:
        assert result['returncode'] == 0
        assert result['output'] == 'ready\n'
        assert time.monotonic() - started < 1.5
        # Normal completion does not terminate a deliberately backgrounded service.
        os.kill(child, 0)
    finally:
        try:
            os.kill(child, signal.SIGKILL)
        except ProcessLookupError:
            pass


def test_output_is_bounded_but_full_log_is_retained(tmp_path):
    env = LocalEnvironment(cwd=str(tmp_path), output_limit=128)
    code = 'import sys; sys.stdout.write("a" * 1000000 + "TAIL")'
    result = env.execute({'command': shlex.join([sys.executable, '-c', code])})
    assert result['returncode'] == 0
    assert len(result['output'].encode()) == 128
    assert result['output'].endswith('TAIL')
    assert result['output_truncated'] is True
    assert result['output_bytes'] == 1000004
    assert Path(result['log_path']).read_text() == 'a' * 1000000 + 'TAIL'


def test_shell_calls_start_in_project_root_without_persistent_state(tmp_path):
    env = LocalEnvironment(cwd=str(tmp_path))
    (tmp_path / 'nested').mkdir()
    assert env.execute({'command': 'cd nested; export ONLY_THIS_CALL=value'})['returncode'] == 0
    result = env.execute({'command': 'pwd; printf "%s" "${ONLY_THIS_CALL-unset}"'})
    assert result['output'].splitlines() == [str(tmp_path.resolve()), 'unset']
