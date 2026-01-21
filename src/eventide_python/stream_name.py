from __future__ import annotations

ID_SEPARATOR = "-"
COMPOUND_ID_SEPARATOR = "+"
CATEGORY_TYPE_SEPARATOR = ":"
COMPOUND_TYPE_SEPARATOR = "+"


class StreamNameError(ValueError):
    pass


def compose(
    category: str | None,
    stream_id: str | list[str] | None = None,
    *,
    cardinal_id: str | None = None,
    id: str | list[str] | None = None,
    ids: list[str] | None = None,
    type: str | list[str] | None = None,
    types: list[str] | None = None,
) -> str:
    if category is None:
        raise StreamNameError("Category must not be omitted from stream name")

    stream_name = category

    type_list: list[str] = []
    type_list.extend(_to_list(type))
    type_list.extend(_to_list(types))
    type_part = COMPOUND_TYPE_SEPARATOR.join(type_list)

    if type_part:
        stream_name = f"{stream_name}{CATEGORY_TYPE_SEPARATOR}{type_part}"

    id_list: list[str] = []
    if cardinal_id is not None:
        id_list.append(cardinal_id)
    id_list.extend(_to_list(stream_id))
    id_list.extend(_to_list(id))
    id_list.extend(_to_list(ids))

    if id_list:
        id_part = compound_id(id_list)
        stream_name = f"{stream_name}{ID_SEPARATOR}{id_part}"

    return stream_name


def split(stream_name: str) -> tuple[str, str | None]:
    parts = stream_name.split(ID_SEPARATOR, 1)
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]


def get_id(stream_name: str) -> str | None:
    return split(stream_name)[1]


def parse_ids(stream_name: str) -> list[str]:
    ids = get_id(stream_name)
    if ids is None:
        return []
    return parse_compound_id(ids)


def get_cardinal_id(stream_name: str) -> str | None:
    ids = parse_ids(stream_name)
    return ids[0] if ids else None


def get_category(stream_name: str) -> str:
    return split(stream_name)[0]


def is_category(stream_name: str) -> bool:
    return ID_SEPARATOR not in stream_name


def get_category_type(stream_name: str) -> str | None:
    if CATEGORY_TYPE_SEPARATOR not in stream_name:
        return None
    category = get_category(stream_name)
    return category.split(CATEGORY_TYPE_SEPARATOR, 1)[1]


def get_types(stream_name: str) -> list[str]:
    type_list = get_category_type(stream_name)
    if type_list is None:
        return []
    return type_list.split(COMPOUND_TYPE_SEPARATOR)


def get_entity_name(stream_name: str) -> str:
    return get_category(stream_name).split(CATEGORY_TYPE_SEPARATOR, 1)[0]


def compound_id(ids: list[str]) -> str:
    if not ids:
        raise StreamNameError("IDs must not be omitted")
    return COMPOUND_ID_SEPARATOR.join(ids)


def parse_compound_id(value: str) -> list[str]:
    if value is None:
        raise StreamNameError("ID must not be omitted")
    return value.split(COMPOUND_ID_SEPARATOR)


def _to_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
