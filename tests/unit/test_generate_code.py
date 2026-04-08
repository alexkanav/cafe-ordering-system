import pytest
import string

from utils.coupons import generate_coupon_code


@pytest.mark.parametrize("length", [0, 1, 5, 10, 20])
def test_generate_coupon_code__valid_length(length):
    code = generate_coupon_code(length)
    assert len(code) == length
    assert all(c in string.ascii_uppercase + string.digits for c in code)
