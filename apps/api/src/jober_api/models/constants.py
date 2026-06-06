from enum import StrEnum

from sqlalchemy import Enum as SAEnum

ENUM_LEN = 32


def str_enum_column(enum_cls: type[StrEnum]) -> SAEnum:
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=ENUM_LEN,
        values_callable=lambda obj: [member.value for member in obj],
    )
