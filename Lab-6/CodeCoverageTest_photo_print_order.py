"""Lab 6 - Code (line) coverage tests for photo_print_order.py

Run:
    coverage run -m pytest CodeCoverageTest_photo_print_order.py
    coverage report -m
"""
import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status


# ---------------------------------------------------------------- extra_print_charge
def test_within_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_unknown_print_size_raises():
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("12x18", 10, "matte", False)


def test_negative_copies_raises():
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -1, "matte", False)


def test_member_gets_five_extra_included_prints():
    # 4x6: 20 included + 5 member bonus = 25; 30 copies -> 5 extra * 4 (matte)
    assert extra_print_charge("4x6", 30, "matte", True) == 20


def test_non_matte_finish_uses_higher_rate():
    # 4x6: 20 included; 25 copies -> 5 extra * 7 (glossy)
    assert extra_print_charge("4x6", 25, "glossy", False) == 35


def test_bulk_surcharge_for_canvas():
    # 4x6: 20 included; 100 copies -> 80 extra, rate 7 + 2 + 5 = 14
    assert extra_print_charge("4x6", 100, "canvas", False) == 80 * 14


# ---------------------------------------------------------------- order_valid
def test_order_valid():
    assert order_valid(10, 100, False) is True


def test_rush_order_within_limit():
    assert order_valid(10, 50, True) is True


def test_oversized_file_rejected():
    assert order_valid(30, 10, False) is False


# ---------------------------------------------------------------- dispatch_status
def test_dispatch_on_time_unframed_domestic():
    assert dispatch_status(12, False, False) == "on_time"


def test_dispatch_tight_framed():
    # framed cutoff = 24, tight window is 18 <= h < 24
    assert dispatch_status(20, True, False) == "tight"


def test_dispatch_missed_international():
    # unframed international cutoff = 36, tight starts at 30
    assert dispatch_status(5, False, True) == "missed"
