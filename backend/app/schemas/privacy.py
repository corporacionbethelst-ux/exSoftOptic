from __future__ import annotations

from pydantic import BaseModel, Field


class SubjectAnonymizeRequest(BaseModel):
    confirmation: str = Field(..., pattern="^ANONYMIZE$")
    reason: str = Field(..., min_length=10, max_length=500)


class SubjectAnonymizeResponse(BaseModel):
    cliente_id: str
    anonymized_at: str
    patients_anonymized: int
    prescriptions_redacted: int
    appointments_redacted: int
    reminders_redacted: int
