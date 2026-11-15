"""Lab 7 - Fuzz tests (Hypothesis) for photo_print_order.py

Run:
    pytest test_photo_print_order.py
    python -m pytest test_photo_print_order.py
"""
import math

import pytest
from hypothesis import given, strategies as st

from photo_print_order import parse_order, file_size_average, payable_amount


# --------------------------------------------------------------------------
# 1. "Must never crash" properties - arbitrary text and None for every function
# --------------------------------------------------------------------------
@given(st.text() | st.none())
def test_parse_order_no_crash(s):
    try:
        parse_order(s)
    except Exception as e:
        assert False, f"parse_order crashed with: {e!r}"


@given(st.text() | st.none())
def test_file_size_average_no_crash(s):
    try:
        file_size_average(s)
    except Exception as e:
        assert False, f"file_size_average crashed with: {e!r}"


@given(st.text() | st.none())
def test_payable_amount_no_crash(s):
    try:
        payable_amount(s)
    except Exception as e:
        assert False, f"payable_amount crashed with: {e!r}"


# --------------------------------------------------------------------------
# 2. Non-text junk must not crash either (ints, lists, bytes, ...)
# --------------------------------------------------------------------------
junk = st.one_of(st.integers(), st.floats(), st.binary(), st.lists(st.integers()))


@given(junk)
def test_all_functions_survive_non_string_input(x):
    for fn in (parse_order, file_size_average, payable_amount):
        try:
            fn(x)
        except Exception as e:
            assert False, f"{fn.__name__} crashed on {x!r} with: {e!r}"


# --------------------------------------------------------------------------
# 3. Correctness properties - valid input must still give the right answer
# --------------------------------------------------------------------------
size_text = st.text(
    alphabet=st.characters(blacklist_characters=":", blacklist_categories=("Cs",)),
    min_size=1,
).filter(lambda t: t.strip() != "")


@given(size_text, st.integers(min_value=0, max_value=10**9))
def test_parse_order_round_trip(size, copies):
    assert parse_order(f"{size}:{copies}") == (size.strip().upper(), copies)


@given(st.lists(st.integers(min_value=0, max_value=10**6), min_size=1))
def test_file_size_average_is_within_min_and_max(values):
    result = file_size_average(",".join(map(str, values)))
    assert min(values) <= result <= max(values)


@given(
    st.floats(min_value=0, max_value=1e12, allow_nan=False),
    st.floats(min_value=0, max_value=1e12, allow_nan=False),
)
def test_payable_amount_is_finite_and_never_negative(amount, discount):
    result = payable_amount(f"{amount!r}|{discount!r}")
    assert result is not None
    assert math.isfinite(result)
    assert result >= 0


# --------------------------------------------------------------------------
# 4. Known edge cases found by fuzzing / from the lab handout
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "bad", [None, "", "   ", "4x6", ":5", "4x6:", "4x6:abc", "4x6:1:2", "4x6:-1", "4x6:2.5"]
)
def test_parse_order_rejects_invalid(bad):
    assert parse_order(bad) is None


@pytest.mark.parametrize(
    "bad", [None, "", " ", "1,,3", "one,two", "1,2,", ",", "4,-8", "1.5,2"]
)
def test_file_size_average_rejects_invalid(bad):
    assert file_size_average(bad) is None


@pytest.mark.parametrize(
    "bad",
    [None, "", "450", "450|", "|50", "a|b", "1|2|3", "nan|0", "0|nan", "inf|0",
     "0|inf", "-5|0", "5|-1", "1e999|0", "1.7e308|0"],
)
def test_payable_amount_rejects_invalid(bad):
    assert payable_amount(bad) is None


def test_valid_examples_from_the_program_prompts():
    assert parse_order("4x6:25") == ("4X6", 25)
    assert parse_order("  8x10 : 3 ") == ("8X10", 3)
    assert file_size_average("4,8,12") == 8
    assert payable_amount("450|50") == pytest.approx(450 * 1.18 - 50)
    assert payable_amount("10|500") == 0  # discount larger than total -> floor at 0
