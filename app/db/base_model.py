from sqlalchemy.orm import DeclarativeBase, declared_attr


class BaseDBModel(DeclarativeBase):
    """
    Base database model
    """

    @declared_attr.directive # type: str adding to ignore mypy error
    def __tablename__(cls) -> str:
        return cls.__name__.lower()