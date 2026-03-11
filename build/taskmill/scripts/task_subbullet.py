#!/usr/bin/env python3
"""Add or update a sub-bullet on a checkbox item."""

import re
import sys
from pathlib import Path
import filelock

CHECKBOX_RE = re.compile(r'^(\s*)- \[(.)\] ')
LOCK_PATH = Path('.llm/backlog.lock')


def find_item_by_index(lines, index):
    """Find the Nth checkbox item (1-based)."""
    count = 0
    for i, line in enumerate(lines):
        if CHECKBOX_RE.match(line):
            count += 1
            if count == index:
                return i
    return None


def find_item_by_name(lines, name):
    """Find a checkbox item by case-insensitive substring match."""
    name_lower = name.lower()
    for i, line in enumerate(lines):
        m = CHECKBOX_RE.match(line)
        if not m:
            continue
        if name_lower in line.lower():
            return i
    return None


def upsert_subbullet(lines, idx, key, value):
    """Add or update a sub-bullet on the item at idx. Returns the sub-bullet line."""
    key_pattern = re.compile(rf'^\s*-\s+{re.escape(key)}:')
    subbullet_line = f'  - {key}: {value}\n'

    sub_start = idx + 1
    sub_end = sub_start
    existing_idx = None

    while sub_end < len(lines):
        line = lines[sub_end]
        if line.strip() == '' or (not line.startswith('  ') and not line.startswith('\t')):
            break
        if key_pattern.match(line):
            existing_idx = sub_end
        sub_end += 1

    if existing_idx is not None:
        lines[existing_idx] = subbullet_line
    else:
        lines.insert(sub_end, subbullet_line)

    return subbullet_line


def main():
    if len(sys.argv) < 4:
        print('Usage: task_subbullet.py <file-path> <identifier> "<key>: <value>"',
              file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    identifier = sys.argv[2]
    kv_string = sys.argv[3]

    if not file_path.exists():
        print(f'File not found: {sys.argv[1]}', file=sys.stderr)
        sys.exit(1)

    colon_pos = kv_string.find(':')
    if colon_pos == -1:
        print('Value must be in "key: value" format.', file=sys.stderr)
        sys.exit(1)

    key = kv_string[:colon_pos].strip()
    value = kv_string[colon_pos + 1:].strip()

    is_backlog = file_path.name == 'backlog.md'

    if is_backlog:
        LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        lock = filelock.FileLock(LOCK_PATH, timeout=5)
    else:
        lock = None

    try:
        if lock:
            lock.acquire()

        lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)

        if identifier.isdigit():
            idx = find_item_by_index(lines, int(identifier))
        else:
            idx = find_item_by_name(lines, identifier)

        if idx is None:
            print(f'Item not found: {identifier}', file=sys.stderr)
            sys.exit(1)

        result = upsert_subbullet(lines, idx, key, value)
        file_path.write_text(''.join(lines), encoding='utf-8')
        print(result.rstrip('\n'))
    finally:
        if lock:
            lock.release()


if __name__ == '__main__':
    main()
