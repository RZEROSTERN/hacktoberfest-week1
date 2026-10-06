from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

Confidence = Literal["high", "medium", "low"]


class DocumentAnalysis(BaseModel):
    """Structured result the model must return for a document photo.

    Field names are English; every free-text value is user-facing, in the response language
    the prompt asks for (Spanish or English).
    """

    document_type: str = Field(
        description="Kind of document, in the response language, "
        "e.g. 'Recibo de luz' in Spanish or 'Electricity bill' in English."
    )
    issuer: str | None = Field(description="Who sent it, exactly as printed. Null if not visible.")
    deadline: date | None = Field(
        description="Payment or response due date as YYYY-MM-DD. Null if none is printed."
    )
    amount_due: float | None = Field(
        description="Total amount to pay in MXN, exactly as printed. Null if none is printed."
    )
    required_actions: list[str] = Field(
        description="Short, simple steps, in the response language, for what she needs to do. "
        "Empty if none."
    )
    is_suspicious: bool = Field(
        description="True if it looks like fraud or phishing (asks for personal data or "
        "passwords, suspicious urgency, strange links, sender mismatch)."
    )
    fraud_reason: str | None = Field(
        description="If suspicious, why, in plain words in the response language. Null otherwise."
    )
    confidence: Confidence = Field(
        description="'low' if the photo is blurry, cut off or hard to read, or you are unsure."
    )
    explanation: str = Field(
        description="Warm, plain explanation in the response language, in 2-4 short sentences, "
        "no jargon."
    )


class DocumentRead(DocumentAnalysis):
    """API response: the analysis plus its history id (null when it was not saved)."""

    id: int | None
    created_at: datetime | None


class VoiceAnswer(BaseModel):
    """Structured answer the model must return for a spoken question."""

    answer: str = Field(
        description="Warm, plain answer in the response language, in 1-4 short sentences, "
        "no jargon."
    )
    confidence: Confidence = Field(
        description="'low' if the question is unclear or the answer is not in the document."
    )


class VoiceAnswerRead(VoiceAnswer):
    question: str
    document_id: int | None
