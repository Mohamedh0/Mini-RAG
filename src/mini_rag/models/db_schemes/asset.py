from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from bson.objectid import ObjectId
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    WithJsonSchema,
)


def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(str, return_type=str, when_used="json"),
    WithJsonSchema({"type": "string"}),
]


class Asset(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    asset_project_id: PyObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: Optional[int] = Field(default=None, ge=0)
    asset_config: Optional[dict] = Field(default=None)
    asset_pushed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("asset_project_id", 1)],
                "name": "asset_project_id_index_1",
                "unique": False,
            },
            {
                "key": [("asset_project_id", 1), ("asset_name", 1)],
                "name": "asset_project_id_name_index_1",
                "unique": True,
            },
        ]
