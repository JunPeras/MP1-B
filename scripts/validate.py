#!/usr/bin/env python
"""
Validation script to run all linting and formatting checks.
Usage: python scripts/validate.py
"""
import subprocess
import sys
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

PROJECT_ROOT = Path(__file__).parent.parent
PYTHON_DIRS = ["api", "core"]


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{YELLOW}Running: {description}...{RESET}")
    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, text=True)
        print(f"{GREEN}✓ {description} passed{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}✗ {description} failed{RESET}")
        print(e)
        return False


def main():
    """Run all validation checks."""
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Starting Code Quality Checks{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")

    results = {}

    # Check imports with isort
    results["isort"] = run_command(
        ["isort", "--check-only", "--diff"] + PYTHON_DIRS,
        "isort (import sorting)"
    )

    # Check formatting with black
    results["black"] = run_command(
        ["black", "--check", "--diff"] + PYTHON_DIRS,
        "black (code formatting)"
    )

    # Check with flake8
    results["flake8"] = run_command(
        ["flake8"] + PYTHON_DIRS,
        "flake8 (linting)"
    )

    # Check with mypy
    results["mypy"] = run_command(
        ["mypy"] + PYTHON_DIRS,
        "mypy (type checking)"
    )

    # Print summary
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Validation Summary{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, status in results.items():
        status_text = f"{GREEN}PASS{RESET}" if status else f"{RED}FAIL{RESET}"
        print(f"{check:.<20} {status_text}")

    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print(f"{GREEN}All checks passed!{RESET}")
        return 0
    else:
        print(f"{RED}Some checks failed. Fix errors and try again.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
