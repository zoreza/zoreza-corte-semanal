"""Config schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ConfigItem(BaseModel):
    key: str
    value: str

    model_config = {"from_attributes": True}


class ConfigUpdate(BaseModel):
    value: str
