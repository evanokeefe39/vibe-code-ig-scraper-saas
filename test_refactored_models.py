#!/usr/bin/env python3
"""
Basic syntax validation for Django models after refactoring.
This doesn't run Django but checks for basic Python syntax errors.
"""

import ast
import sys

def check_syntax(file_path):
    """Check Python syntax of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse the AST
        ast.parse(source)
        print(f"✓ Syntax check passed for {file_path}")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking {file_path}: {e}")
        return False

if __name__ == "__main__":
    files_to_check = [
        "core/models.py",
        "core/migrations/0007_refactor_source_output_mapping.py"
    ]

    all_passed = True
    for file_path in files_to_check:
        if not check_syntax(file_path):
            all_passed = False

    if all_passed:
        print("\n✓ All syntax checks passed!")
        sys.exit(0)
    else:
        print("\n✗ Some syntax checks failed!")
        sys.exit(1)