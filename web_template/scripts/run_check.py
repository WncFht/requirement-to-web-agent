"""Capture a check's combined log without losing its exit status."""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', required=True, type=Path)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a check command is required after --')
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open('wb') as log:
        try:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            code = result.returncode
            if code < 0:
                code = 128 - code
        except OSError as exc:
            log.write(f'Unable to start check: {exc}\n'.encode())
            code = 127
    with args.log.open('rb') as log:
        while chunk := log.read(65536):
            sys.stdout.buffer.write(chunk)
    sys.stdout.flush()
    return code


if __name__ == '__main__':
    sys.exit(main())
