import pytest

from eventide_python import stream_name


def test_compose_requires_category() -> None:
    with pytest.raises(stream_name.StreamNameError):
        stream_name.compose(None)


def test_compose_basic() -> None:
    assert stream_name.compose("account", stream_id="123") == "account-123"


def test_compose_with_type() -> None:
    assert (
        stream_name.compose("account", stream_id="123", type="command")
        == "account:command-123"
    )


def test_compose_with_types() -> None:
    assert (
        stream_name.compose("account", stream_id="123", types=["command", "initiated"])
        == "account:command+initiated-123"
    )


def test_compose_with_cardinal_id() -> None:
    assert stream_name.compose("order", cardinal_id="ABC", stream_id="123") == "order-ABC+123"


def test_split_and_getters() -> None:
    name = "order:command+initiated-ABC+123"
    assert stream_name.get_category(name) == "order:command+initiated"
    assert stream_name.get_id(name) == "ABC+123"
    assert stream_name.get_cardinal_id(name) == "ABC"
    assert stream_name.get_entity_name(name) == "order"
    assert stream_name.get_types(name) == ["command", "initiated"]


def test_is_category() -> None:
    assert stream_name.is_category("order")
    assert not stream_name.is_category("order-123")
