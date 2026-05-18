import sys
import pytest

with open("pytest_log.txt", "w") as f:
    sys.stdout = f
    sys.stderr = f
    pytest.main(["tests/", "-v"])
