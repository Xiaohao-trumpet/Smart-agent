"""
Test runner script with various options.
"""

import sys
import subprocess


def run_tests(args=None):
    """Run pytest with specified arguments."""
    cmd = ["pytest"]
    
    if args:
        cmd.extend(args)
    else:
        # Default: run all tests with verbose output
        cmd.extend(["-v", "--tb=short"])
    
    print("=" * 60)
    print("Running tests...")
    print("Command:", " ".join(cmd))
    print("=" * 60)
    
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            # Run with coverage
            exit_code = run_tests([
                "--cov=backend",
                "--cov-report=html",
                "--cov-report=term",
                "-v"
            ])
        elif sys.argv[1] == "fast":
            # Run fast tests only
            exit_code = run_tests(["-v", "-m", "not slow"])
        elif sys.argv[1] == "unit":
            # Run unit tests only
            exit_code = run_tests(["-v", "-m", "unit"])
        elif sys.argv[1] == "integration":
            # Run integration tests only
            exit_code = run_tests(["-v", "-m", "integration"])
        else:
            # Pass through arguments
            exit_code = run_tests(sys.argv[1:])
    else:
        # Default run
        exit_code = run_tests()
    
    sys.exit(exit_code)
