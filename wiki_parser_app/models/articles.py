import uuid
from typing import Optional, List

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from wiki_parser_app.db.database import Base


class Article(Base):
    title: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(512), unique=True)
    content: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[int] = mapped_column(default=0)

    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("articles.id"),
        nullable=True
    )

    # Отношения
    parent: Mapped[Optional["Article"]] = relationship(
        "Article",
        remote_side=[id],
        back_populates="children"
    )
    children: Mapped[List["Article"]] = relationship(
        "Article",
        back_populates="parent"
    )
    summary_rel: Mapped[Optional["Summary"]] = relationship(
        "Summary",
        back_populates="article",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Summary(Base):
    article_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("articles.id"),
        primary_key=True
    )
    content: Mapped[str] = mapped_column(Text)

    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="summary_rel"
    )
