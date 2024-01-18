from shift.domain.shift import Shift

EmployeeSlot = tuple[int, str]


def get_key(employee_id: int, shift: Shift) -> EmployeeSlot:
    return (employee_id, str(shift))
