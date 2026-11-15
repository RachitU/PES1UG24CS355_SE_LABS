"""Lab 6 - Branch coverage tests for photo_print_order.py

Every decision is exercised both True and False, with boundary values.

Run:
    coverage run --branch -m pytest BranchCoverageTest_photo_print_order.py
    coverage report -m
"""
import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status


# ---------------------------------------------------------------- extra_print_charge
# Validation branches (size in table / not in table, copies < 0 / >= 0)
def test_unknown_print_size_raises():
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("12x18", 10, "matte", False)


def test_negative_copies_raises():
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -1, "matte", False)


def test_zero_copies_is_free():
    assert extra_print_charge("4x6", 0, "matte", False) == 0


# Membership branch: (member & non-8x10) / (member & 8x10) / (non-member)
def test_non_member_no_bonus():
    # 4x6: 20 included, 25 copies -> 5 extra * 4
    assert extra_print_charge("4x6", 25, "matte", False) == 20


def test_member_bonus_applies_to_4x6():
    # 20 + 5 = 25 included, 30 copies -> 5 extra * 4
    assert extra_print_charge("4x6", 30, "matte", True) == 20


def test_member_bonus_applies_to_5x7():
    # 15 + 5 = 20 included, 25 copies -> 5 extra * 4
    assert extra_print_charge("5x7", 25, "matte", True) == 20


def test_member_bonus_does_not_apply_to_8x10():
    # 8x10: 10 included (no bonus), 15 copies -> 5 extra * 4
    assert extra_print_charge("8x10", 15, "matte", True) == 20


# extra <= 0 branch: below, exactly at, and just above the included amount
def test_below_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_exactly_included_prints():
    assert extra_print_charge("4x6", 20, "glossy", False) == 0


def test_one_over_included_prints():
    assert extra_print_charge("4x6", 21, "matte", False) == 4


# Finish branch: matte / not matte
def test_matte_rate():
    assert extra_print_charge("5x7", 20, "matte", False) == 5 * 4


def test_glossy_rate():
    assert extra_print_charge("5x7", 20, "glossy", False) == 5 * 7


# Bulk surcharge branch: extra > 50 false / true, then canvas true / false
def test_extra_exactly_50_has_no_surcharge():
    # 4x6: 20 included, 70 copies -> extra 50, rate 4
    assert extra_print_charge("4x6", 70, "matte", False) == 50 * 4


def test_extra_51_gets_bulk_surcharge_matte():
    # extra 51, rate 4 + 2 = 6
    assert extra_print_charge("4x6", 71, "matte", False) == 51 * 6


def test_bulk_surcharge_non_canvas_finish():
    # extra 60, glossy -> 7 + 2 = 9, no canvas add-on
    assert extra_print_charge("4x6", 80, "glossy", False) == 60 * 9


def test_bulk_surcharge_canvas_finish():
    # extra 80, canvas -> 7 + 2 + 5 = 14
    assert extra_print_charge("4x6", 100, "canvas", False) == 80 * 14


def test_canvas_without_bulk_has_no_addon():
    # canvas only adds its premium inside the bulk branch
    assert extra_print_charge("4x6", 30, "canvas", False) == 10 * 7


# ---------------------------------------------------------------- order_valid
def test_order_valid():
    assert order_valid(10, 100, False) is True


def test_rush_within_limit():
    assert order_valid(10, 50, True) is True


def test_rush_over_limit():
    assert order_valid(10, 51, True) is False


def test_rush_ignores_file_size():
    assert order_valid(100, 10, True) is True


def test_file_exactly_25mb_allowed():
    assert order_valid(25, 10, False) is True


def test_file_over_25mb_rejected():
    assert order_valid(25.1, 10, False) is False


def test_standard_copies_at_limit():
    assert order_valid(10, 500, False) is True


def test_standard_copies_over_limit():
    assert order_valid(10, 501, False) is False


# ---------------------------------------------------------------- dispatch_status
# cutoff = 12 (unframed) / 24 (framed), +24 if international.
# on_time: h >= cutoff, tight: cutoff-6 <= h < cutoff, missed: h < cutoff-6
@pytest.mark.parametrize(
    "hours, framed, intl, expected",
    [
        # unframed, domestic (cutoff 12)
        (12, False, False, "on_time"),
        (11, False, False, "tight"),
        (6, False, False, "tight"),
        (5, False, False, "missed"),
        # framed, domestic (cutoff 24)
        (24, True, False, "on_time"),
        (23, True, False, "tight"),
        (18, True, False, "tight"),
        (17, True, False, "missed"),
        # unframed, international (cutoff 36)
        (36, False, True, "on_time"),
        (35, False, True, "tight"),
        (30, False, True, "tight"),
        (29, False, True, "missed"),
        # framed, international (cutoff 48)
        (48, True, True, "on_time"),
        (47, True, True, "tight"),
        (42, True, True, "tight"),
        (41, True, True, "missed"),
        # extremes
        (0, False, False, "missed"),
        (1000, True, True, "on_time"),
    ],
)
def test_dispatch_status(hours, framed, intl, expected):
    assert dispatch_status(hours, framed, intl) == expected
