"""Languages the API can answer in, and every fixed phrase it writes itself.

The model follows the requested language through its prompt; this module covers the text the
server produces without the model (fallback answers, calendar reminders). Spanish is the
default because it is the app's primary audience.
"""

from dataclasses import dataclass
from typing import Literal

Lang = Literal["es", "en"]
DEFAULT_LANG: Lang = "es"


@dataclass(frozen=True)
class Language:
    # Prompt fragments: how the model should write, and extra guidance for document photos.
    style: str
    analysis_note: str
    # Fallbacks used when the model fails or the audio is silent.
    unreadable_type: str
    unreadable_action: str
    unreadable_explanation: str
    unanswered: str
    not_heard: str
    # Calendar reminder (.ics) text.
    reminder_summary: str
    reminder_amount: str
    reminder_tomorrow: str
    reminder_in_days: str
    reminder_filename: str


LANGUAGES: dict[Lang, Language] = {
    "es": Language(
        style='warm, simple Mexican Spanish ("usted")',
        analysis_note="",
        unreadable_type="No se pudo leer",
        unreadable_action="Tome otra foto con buena luz, con la hoja completa y sin moverse.",
        unreadable_explanation=(
            "No pude leer bien este papel. ¿Me ayuda tomando otra foto? "
            "Ponga la hoja sobre una mesa, con buena luz y que se vea completa."
        ),
        unanswered=(
            "Perdón, no pude contestar en este momento. ¿Me lo pregunta otra vez en un ratito?"
        ),
        not_heard="No le escuché bien. ¿Me lo puede repetir un poco más cerca del teléfono?",
        reminder_summary="Vence: {document_type}",
        reminder_amount="Monto: ${amount:,.2f} MXN",
        reminder_tomorrow="mañana",
        reminder_in_days="en {days} días",
        reminder_filename="recordatorio-{id}.ics",
    ),
    "en": Language(
        style="warm, plain English",
        analysis_note=(
            " Keep the names of institutions and the document's own title as printed "
            '(for example CFE, SAT, "Recibo de luz") and add a short English translation '
            "in parentheses where it helps."
        ),
        unreadable_type="Could not be read",
        unreadable_action=(
            "Take another photo in good light, with the whole page showing and held still."
        ),
        unreadable_explanation=(
            "I couldn't read this paper well. Could you take another photo? "
            "Lay the page on a table, in good light, with the whole page showing."
        ),
        unanswered="Sorry, I couldn't answer right now. Could you ask me again in a little while?",
        not_heard="I didn't hear you well. Could you say it again, a bit closer to the phone?",
        reminder_summary="Due: {document_type}",
        reminder_amount="Amount: ${amount:,.2f} MXN",
        reminder_tomorrow="tomorrow",
        reminder_in_days="in {days} days",
        reminder_filename="reminder-{id}.ics",
    ),
}
