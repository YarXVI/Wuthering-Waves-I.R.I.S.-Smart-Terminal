#!/usr/bin/env python3
"""
Add AGPLv3 license header to source files.
"""
import os
from datetime import datetime

PYTHON_HEADER = '''# I.R.I.S. Smart Terminal
# Copyright (C) 2024 I.R.I.S. Agent
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <https://www.gnu.org/licenses/>.

'''

TYPESCRIPT_HEADER = '''// I.R.I.S. Smart Terminal
// Copyright (C) 2024 I.R.I.S. Agent
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public
// License along with this program.  If not, see
// <https://www.gnu.org/licenses/>.

'''

EXISTING_HEADER_KEYWORDS = ['Copyright', 'AGPL', 'GNU Affero', 'License']

def has_existing_license(content):
    """Check if file already has a license header."""
    for keyword in EXISTING_HEADER_KEYWORDS:
        if keyword in content[:1000]:
            return True
    return False

def add_header_to_file(filepath, header):
    """Add license header to a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if has_existing_license(content):
            print(f"  SKIP (already has license): {filepath}")
            return False

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + content)

        print(f"  ADDED: {filepath}")
        return True
    except Exception as e:
        print(f"  ERROR: {filepath} - {e}")
        return False

def main():
    base_dir = r"e:\agent办公室\工程区\agent-core"

    # Python files
    python_files = [
        os.path.join(base_dir, "launcher.py"),
    ]

    for root, dirs, files in os.walk(os.path.join(base_dir, "agent_core")):
        for f in files:
            if f.endswith('.py'):
                python_files.append(os.path.join(root, f))

    for root, dirs, files in os.walk(os.path.join(base_dir, "server")):
        for f in files:
            if f.endswith('.py'):
                python_files.append(os.path.join(root, f))

    for root, dirs, files in os.walk(os.path.join(base_dir, "tests")):
        for f in files:
            if f.endswith('.py') and not f.startswith('legacy_'):
                python_files.append(os.path.join(root, f))

    # TypeScript files
    ts_files = []
    for root, dirs, files in os.walk(os.path.join(base_dir, "desktop", "src")):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                ts_files.append(os.path.join(root, f))

    print("Adding AGPLv3 headers to Python files...")
    count_py = 0
    for f in python_files:
        if add_header_to_file(f, PYTHON_HEADER):
            count_py += 1

    print(f"\nAdded headers to {count_py} Python files")

    print("\nAdding AGPLv3 headers to TypeScript files...")
    count_ts = 0
    for f in ts_files:
        if add_header_to_file(f, TYPESCRIPT_HEADER):
            count_ts += 1

    print(f"\nAdded headers to {count_ts} TypeScript files")
    print(f"\nTotal: {count_py + count_ts} files updated")

if __name__ == "__main__":
    main()
