import pytest

from shift.domain.utils.model import Model


def test_entity():
    model = Model()
    assert model.entity == "Model"


def test_repr():
    model = Model()
    model.id = 1
    assert repr(model) == "Model(id=1)"


def test_id():
    model = Model()
    with pytest.raises(AttributeError):
        model.id

    model.id = 1
    assert model.id == 1
