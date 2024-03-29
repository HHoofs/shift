from shift.domain.shifts.shift import Shift

EmployeeSlot = tuple[int, Shift]  # Employee-id, Shift


def get_key(employee_id: int, shift: Shift) -> EmployeeSlot:
    return (employee_id, shift)
