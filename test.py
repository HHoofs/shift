from datetime import date
from shift.domain.shift import Day, Period, Shift, shift_range


if __name__ == "__main__":
    shifts = shift_range(
        Shift(Period.evening, Day(date(2002, 2, 2))),
        Shift(Period.morning, Day(date(2002, 2, 3))),
        inclusive=False,
    )

    for shift in shifts:
        print(shift)
