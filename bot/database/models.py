"""Experimental over-engineered models for mongo database which/might help with code quality and readability
Reason:
    mongodb syntax is ugly af. however this might actually a bad idea :].

Agg*: models for aggregation
Upd*: models for updates
Flt*: models for filters
Pipe*: models for pipelines

instead of having '$' character at begining it will be replaced with '*_'."""

from typing import Any

from pydantic import BaseModel, Field


class DefaultDump(BaseModel):
    """This Override model_dump default parameters"""

    def model_dump(self, **kwargs: Any) -> dict[Any, Any]:  # noqa: ANN401
        return super().model_dump(by_alias=True, **kwargs)


class PipeMatch(DefaultDump):
    match: dict[str | int, str | int] = Field(..., serialization_alias="$match")


class FltId(DefaultDump):
    id_: int | str = Field(..., alias="_id")


class UpdSet(DefaultDump):
    set_: dict[str, int | str] = Field(..., serialization_alias="$set", alias="_set")
