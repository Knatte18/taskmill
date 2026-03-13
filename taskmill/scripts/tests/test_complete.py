"""Tests for task_complete.py: completing items including blocked ones."""

import subprocess
import sys
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().parent.parent / 'task_complete.py')


def run_complete(file_path, task_name=None):
    """Run task_complete.py and return (returncode, stdout, stderr)."""
    cmd = [sys.executable, SCRIPT, str(file_path)]
    if task_name:
        cmd.append(task_name)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=file_path.parent)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def test_no_name_completes_incomplete_before_blocked(tmp_path):
    f = tmp_path / 'plan.md'
    f.write_text(
        '- [!] **Blocked step**\n'
        '  - blocked: reason\n'
        '- [ ] **Open step**\n'
    )
    rc, stdout, _ = run_complete(f)
    assert rc == 0
    assert '[ ] **Open step**' in stdout

    content = f.read_text()
    assert '- [x] **Open step**\n' in content
    # Blocked step untouched.
    assert '- [!] **Blocked step**\n' in content


def test_no_name_completes_blocked_when_no_incomplete(tmp_path):
    f = tmp_path / 'plan.md'
    f.write_text(
        '- [x] **Done step**\n'
        '- [!] **Blocked step**\n'
        '  - blocked: reason\n'
    )
    rc, stdout, _ = run_complete(f)
    assert rc == 0
    assert '[!] **Blocked step**' in stdout

    content = f.read_text()
    assert '- [x] **Blocked step**\n' in content


def test_name_targets_blocked_item_directly(tmp_path):
    f = tmp_path / 'plan.md'
    f.write_text(
        '- [ ] **Step A**\n'
        '- [!] **Step B**\n'
        '  - blocked: reason\n'
        '- [ ] **Step C**\n'
    )
    rc, stdout, _ = run_complete(f, task_name='Step B')
    assert rc == 0
    assert '[!] **Step B**' in stdout

    content = f.read_text()
    assert '- [x] **Step B**\n' in content
    # Others untouched.
    assert '- [ ] **Step A**\n' in content
    assert '- [ ] **Step C**\n' in content
