from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    runtime_checkable,
)
from pydantic import BaseModel
from sqlalchemy import select, and_, or_, desc, asc, Select
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# Custom types for filter operations
FilterOperator = Literal["eq", "ne", "gt", "lt", "gte", "lte", "like", "ilike", "in"]
FilterCondition = Dict[str, Union[str, int, bool, List[Any]]]
SortOrder = Literal["asc", "desc"]
OrderBy = List[Tuple[str, SortOrder]]


@runtime_checkable
class DataTransformer(Protocol):
    """Protocol for objects that can be transformed into dicts for DB operations"""

    def create_update_dict(self) -> Dict[str, Any]:
        """
        Transform the object into a dictionary suitable for database operations.

        Returns:
            Dict containing transformed data for database operations.
        """
        ...


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def _process_schema_data(
        self, schema: Union[CreateSchemaType, UpdateSchemaType], is_update: bool = False
    ) -> Dict[str, Any]:
        """
        Process schema data for database operations.

        Args:
            schema: Pydantic model instance
            is_update: Whether this is an update operation

        Returns:
            Dict of processed data
        """
        if hasattr(schema, "create_update_dict"):
            try:
                return schema.create_update_dict()  # type: ignore
            except Exception:
                pass  # Fallback to default behavior if method fails

        # Default behavior using model_dump
        if is_update:
            return schema.model_dump(exclude_unset=True)
        return schema.model_dump()

    def _build_query(
        self,
        filter_params: Optional[Dict[str, Any]] = None,
        or_filter_params: Optional[Dict[str, Any]] = None,
        order_by: Optional[OrderBy] = None,
    ) -> Select:
        """
        Build SQLAlchemy query with filters and ordering.

        Args:
            filter_params: Dictionary of AND filter conditions
            or_filter_params: Dictionary of OR filter conditions
            order_by: List of field names and sort orders

        Returns:
            SQLAlchemy Select object
        """
        query = select(self.model)

        # Add AND conditions
        if filter_params:
            and_conditions = []
            for field, value in filter_params.items():
                if hasattr(self.model, field):
                    model_attr = cast(InstrumentedAttribute, getattr(self.model, field))
                    if isinstance(value, list):
                        and_conditions.append(model_attr.in_(value))
                    else:
                        and_conditions.append(model_attr == value)
            if and_conditions:
                query = query.where(and_(*and_conditions))

        # Add OR conditions
        if or_filter_params:
            or_conditions = []
            for field, value in or_filter_params.items():
                if hasattr(self.model, field):
                    model_attr = cast(InstrumentedAttribute, getattr(self.model, field))
                    if isinstance(value, list):
                        or_conditions.append(model_attr.in_(value))
                    else:
                        or_conditions.append(model_attr == value)
            if or_conditions:
                query = query.where(or_(*or_conditions))

        # Add ordering
        if order_by:
            for field_name, order in order_by:
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    query = query.order_by(
                        desc(field) if order == "desc" else asc(field)
                    )

        return query

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Optional model instance
        """
        try:
            return db.get(self.model, id)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    def get_by_filter(
        self,
        db: Session,
        *,
        filter_params: Dict[str, Any],
        or_filter_params: Optional[Dict[str, Any]] = None,
    ) -> Optional[ModelType]:
        """
        Get a single record by filter conditions.

        Args:
            db: Database session
            filter_params: AND filter conditions
            or_filter_params: OR filter conditions

        Returns:
            Optional model instance
        """
        try:
            query = self._build_query(filter_params, or_filter_params)
            return db.execute(query).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filter_params: Optional[Dict[str, Any]] = None,
        or_filter_params: Optional[Dict[str, Any]] = None,
        order_by: Optional[OrderBy] = None,
    ) -> Sequence[ModelType]:
        """
        Get multiple records with pagination, filtering, and sorting.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filter_params: AND filter conditions
            or_filter_params: OR filter conditions
            order_by: Sorting configuration

        Returns:
            Sequence of model instances
        """
        try:
            query = self._build_query(filter_params, or_filter_params, order_by)
            result = db.execute(query.offset(skip).limit(limit))
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        try:
            create_data = self._process_schema_data(obj_in, is_update=False)
            db_obj = self.model(**create_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """Update an existing record."""
        try:
            update_data = self._process_schema_data(obj_in, is_update=True)
            for field in update_data:
                setattr(db_obj, field, update_data[field])
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Delete a record."""
        try:
            obj = db.get(self.model, id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
