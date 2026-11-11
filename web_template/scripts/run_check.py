"""Capture each check in a unique log and retain its execution status."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True, action='append', dest='cases')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a check command is required after --')
    folder = Path('.agent/checks')
    folder.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='check-', suffix='.log', dir=folder)
    log_path = Path(name).resolve()
    record = {
        'check_id': log_path.stem,
        'cases': args.cases,
        'started_at': datetime.now(timezone.utc).isoformat(),
        'cwd': str(Path.cwd()),
        'command': command,
        'log': str(log_path),
        'status': 'started',
    }

    def save_record():
        with Path('.agent/checks.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')

    with os.fdopen(fd, 'wb') as log:
        save_record()
        try:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            code = result.returncode if result.returncode >= 0 else 128 - result.returncode
        except OSError as exc:
            log.write(f'Unable to start check: {exc}\n'.encode())
            code = 127
    record.update(status='passed' if code == 0 else 'failed', exit_code=code,
                  finished_at=datetime.now(timezone.utc).isoformat())
    save_record()
    with log_path.open('rb') as log:
        while chunk := log.read(65536):
            sys.stdout.buffer.write(chunk)
    sys.stdout.flush()
    print('\n<check_record>' + json.dumps(record, ensure_ascii=False) + '</check_record>', flush=True)
    return code


if __name__ == '__main__':
    sys.exit(main())
