from datetime import UTC, date, datetime

from sqlmodel import JSON, Column, Field, SQLModel


class Document(SQLModel, table=True):
    """Only the extracted structured data is stored; never the image or audio."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    document_type: str
    issuer: str | None = None
    deadline: date | None = Field(default=None, index=True)
    amount_due: float | None = None
    required_actions: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_suspicious: bool = False
    fraud_reason: str | None = None
    confidence: str
    explanation: str
