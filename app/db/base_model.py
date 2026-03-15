from typing import ClassVar

from sqlalchemy.orm import DeclarativeBase, declared_attr


class BaseDBModel(DeclarativeBase):
    """
    Base database model
    """

    __abstract__ = True

    @declared_attr.directive # type: str adding to ignore mypy error
    def __tablename__(cls) -> str:
        return cls.__name__.lower()