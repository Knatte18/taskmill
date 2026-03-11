#!/usr/bin/env python3
"""Set the finished: timestamp in a plan file's YAML frontmatter."""

import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print('Usage: plan_finish.py <plan-file>', file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f'File not found: {sys.argv[1]}', file=sys.stderr)
        sys.exit(1)

    lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)

    if not lines or lines[0].rstrip('\n') != '---':
        print('No YAML frontmatter found.', file=sys.stderr)
        sys.exit(1)

    closing_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip('\n') == '---':
            closing_idx = i
            break

    if closing_idx is None:
        print('Unclosed YAML frontmatter.', file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    finished_line = f'finished: {now}\n'

    existing_idx = None
    for i in range(1, closing_idx):
        if lines[i].startswith('finished:'):
            existing_idx = i
            break

    if existing_idx is not None:
        lines[existing_idx] = finished_line
    else:
        lines.insert(closing_idx, finished_line)

    file_path.write_text(''.join(lines), encoding='utf-8')
    print(finished_line.rstrip('\n'))


if __name__ == '__main__':
    main()
