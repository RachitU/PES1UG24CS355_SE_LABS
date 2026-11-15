"""Print-order helpers, hardened against invalid input (Lab 7).

Every function validates its input and returns ``None`` when the input is
invalid, instead of raising. Valid input behaves exactly as before.
"""
import math


def parse_order(text):
    """Parse ``"size:copies"`` into ``(SIZE, copies)``.

    Returns None if ``text`` is not a string, does not contain exactly one
    ``:``, has an empty size, or ``copies`` is not a non-negative integer.
    """
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    size = parts[0].strip()
    if not size:
        return None
    try:
        copies = int(parts[1])
    except ValueError:
        return None
    if copies < 0:
        return None
    return size.upper(), copies


def file_size_average(sizes_csv):
    """Average (floor) of comma-separated non-negative integer file sizes.

    Returns None for non-strings, empty/blank/non-integer entries
    (e.g. ``""``, ``"1,,3"``, ``"1,2,"``, ``"one,two"``) or negative sizes.
    """
    if not isinstance(sizes_csv, str):
        return None
    try:
        values = [int(item) for item in sizes_csv.split(',')]
    except ValueError:
        return None
    if any(value < 0 for value in values):
        return None
    return sum(values) // len(values)


def payable_amount(text):
    """Payable amount for ``"amount|discount"``: amount * 1.18 - discount, min 0.

    Returns None for non-strings, anything that is not exactly two numbers
    separated by one ``|``, negative values, or non-finite values
    (``nan``, ``inf``, ``1e999``) including a result that overflows.
    """
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    try:
        amount = float(parts[0])
        discount = float(parts[1])
    except ValueError:
        return None
    if not (math.isfinite(amount) and math.isfinite(discount)):
        return None
    if amount < 0 or discount < 0:
        return None
    total = amount * 1.18 - discount
    if not math.isfinite(total):
        return None
    return total if total > 0 else 0


def _show(label, result):
    print(label, "Invalid input" if result is None else result)


def main():
    print("==== Running parse_order ====")
    user_input = input("Enter print size:copies (e.g. 4x6:25): ")
    _show("Size and Copies:", parse_order(user_input))

    print("\n==== Running file_size_average ====")
    user_input = input("Enter file sizes in MB as CSV (e.g. 4,8,12): ")
    _show("Average File Size:", file_size_average(user_input))

    print("\n==== Running payable_amount ====")
    user_input = input("Enter amount|discount (e.g. 450|50): ")
    _show("Payable Amount:", payable_amount(user_input))


if __name__ == "__main__":
    main()
