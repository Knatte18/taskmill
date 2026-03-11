#!/usr/bin/env python3
"""Mark a task as planned and link its plan file."""

import argparse
import re
import sys
from pathlib import Path

import filelock

from task_subbullet import upsert_subbullet

CHECKBOX_RE = re.compile(r'^(\s*)- \[(.)\] ')
LOCK_PATH = Path('.llm/backlog.lock')


def find_task_by_name(lines, name):
    """Find a top-level task by name (case-insensitive substring match)."""
    name_lower = name.lower()
    for i, line in enumerate(lines):
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        if len(match.group(1)) > 0:
            continue  # skip sub-bullets
        if name_lower in line.lower():
            return i
    return None


def main():
    parser = argparse.ArgumentParser(description='Mark a task as planned with a plan file link')
    parser.add_argument('file', help='Path to the backlog file')
    parser.add_argument('task_name', help='Task name (case-insensitive substring match)')
    parser.add_argument('plan_path', help='Path to the plan file')
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f'File not found: {args.file}', file=sys.stderr)
        sys.exit(1)

    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock = filelock.FileLock(LOCK_PATH, timeout=5)

    try:
        lock.acquire()
        lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)

        idx = find_task_by_name(lines, args.task_name)
        if idx is None:
            print(f'Task not found: {args.task_name}', file=sys.stderr)
            sys.exit(1)

        # Change state to [p] (any single-character state)
        lines[idx] = re.sub(r'^(\s*- \[).(\])', r'\1p\2', lines[idx])

        # Add or update plan sub-bullet
        upsert_subbullet(lines, idx, 'plan', args.plan_path)

        file_path.write_text(''.join(lines), encoding='utf-8')
        print(lines[idx].rstrip('\n'))
    finally:
        lock.release()


if __name__ == '__main__':
    main()
