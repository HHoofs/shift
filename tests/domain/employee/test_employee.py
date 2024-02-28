from shift.domain.employee.employee import Employee


def test_employee_repr():
    employee = Employee("employee_1", 40)
    employee.id = 1
    assert str(employee) == "employee_1"
