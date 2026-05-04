#!/usr/bin/env python3
"""
Fix frontend TypeScript files encoding issues
"""

from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix encoding issues in a file"""
    try:
        # Read with latin-1 to get raw bytes
        with open(filepath, 'rb') as f:
            raw = f.read()

        # Try to decode as GB18030 (Chinese Windows encoding)
        try:
            content = raw.decode('gb18030')
        except:
            # If that fails, use UTF-8
            content = raw.decode('utf-8', errors='replace')

        # Remove replacement characters
        content = content.replace('\ufffd', '')

        # Fix common garbled patterns
        replacements = [
            ('âœ?', '✓'),
            ('âœ", '✗'),
            ('ðÿ', ''),
            ('â', ''),
            ('ï¸', ''),
            ('_"', '"'),
            ('_"', '"'),
        ]

        for old, new in replacements:
            content = content.replace(old, new)

        # Write back as UTF-8
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False


def main():
    root = Path(__file__).parent / 'desktop'
    ts_files = list(root.glob('src/**/*.tsx')) + list(root.glob('src/**/*.ts'))

    print(f"Fixing {len(ts_files)} TypeScript files...")

    for f in ts_files:
        if fix_file(f):
            print(f"  OK: {f.name}")


if __name__ == '__main__':
    main()
