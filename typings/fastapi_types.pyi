from typing import TypeVar, Sequence, Type
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

ModelT = TypeVar("ModelT", bound=DeclarativeBase)
SchemaT = TypeVar("SchemaT", bound=BaseModel)

def convert_sequence(
    models: Sequence[ModelT], schema_cls: Type[SchemaT]
) -> Sequence[SchemaT]: ...
