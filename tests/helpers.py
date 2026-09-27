"""Test helpers.

``todo`` marks a test whose target function is still a stub. It xfails only on
NotImplementedError; once the function is implemented the test must pass and the
strict XPASS forces the developer to delete the marker. Wrong implementations fail.
"""

import pytest

todo = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="stub — implement per CODE SPEC")
