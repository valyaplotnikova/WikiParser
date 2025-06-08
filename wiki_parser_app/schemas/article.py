from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ArticleSchema(BaseModel):
    id: UUID
    title: str
    url: str
    summary: Optional[str]
    content: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ParseRequestSchema(BaseModel):
    url: str


class ArticleResponseSchema(BaseModel):
    id: UUID
    url: str
    title: str


class ArticleSummarySchema(BaseModel):
    id: UUID
    summary: Optional[str]
