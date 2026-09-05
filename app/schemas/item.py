from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(ge=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    # name/price are non-nullable in the domain (unlike description), so unlike a
    # typical partial-update field they must not accept `null` on the wire. The
    # defaults below are placeholders that ItemService.update_item never reads —
    # model_dump(exclude_unset=True) drops any field the client didn't send —
    # they only exist so the field can be omitted without widening its type to
    # allow `None`, which would let a client explicitly null out the column.
    name: str = Field(default="", min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(default=0.0, ge=0)


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def _assume_utc(cls, value: datetime) -> datetime:
        # SQLite has no timezone-aware datetime type, so values read back from it
        # are naive even though the column is declared DateTime(timezone=True).
        return value if value.tzinfo else value.replace(tzinfo=UTC)
