"""Minimal RFC 5545 calendar file for a document deadline. No external dependency."""

from datetime import UTC, datetime, timedelta

from app.i18n import DEFAULT_LANG, LANGUAGES, Lang
from app.models import Document

REMINDER_DAYS_BEFORE = (3, 1)


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    """Fold content lines longer than 75 octets, as RFC 5545 requires."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line
    parts: list[str] = []
    current = ""
    for char in line:
        limit = 75 if not parts else 74  # continuation lines start with a space
        if len((current + char).encode("utf-8")) > limit:
            parts.append(current)
            current = char
        else:
            current += char
    parts.append(current)
    return "\r\n ".join(parts)


def build_reminder(document: Document, lang: Lang = DEFAULT_LANG) -> str:
    if document.deadline is None:
        raise ValueError("document has no deadline")

    language = LANGUAGES[lang]
    start = document.deadline
    summary = language.reminder_summary.format(document_type=document.document_type)
    details = [document.explanation]
    if document.amount_due is not None:
        details.append(language.reminder_amount.format(amount=document.amount_due))
    details += [f"- {step}" for step in document.required_actions]

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//Paperwork Translator//{lang.upper()}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:document-{document.id}@paperwork-translator",
        f"DTSTAMP:{datetime.now(UTC):%Y%m%dT%H%M%SZ}",
        f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
        f"DTEND;VALUE=DATE:{start + timedelta(days=1):%Y%m%d}",
        f"SUMMARY:{_escape(summary)}",
        f"DESCRIPTION:{_escape(chr(10).join(details))}",
    ]
    for days in REMINDER_DAYS_BEFORE:
        when = (
            language.reminder_tomorrow if days == 1 else language.reminder_in_days.format(days=days)
        )
        lines += [
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{_escape(f'{summary} {when}')}",
            f"TRIGGER:-P{days}D",
            "END:VALARM",
        ]
    lines += ["END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"
