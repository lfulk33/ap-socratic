import anthropic
from config import ANTHROPIC_API_KEY

MODEL = "claude-haiku-4-5"

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def build_system_prompt(unit: dict) -> str:
    big_ideas = ", ".join(unit.get("big_ideas", []))
    essential_questions = "\n".join(f"- {q}" for q in unit["essential_questions"])
    focus_skills = "\n".join(f"- {s}" for s in unit["focus_skills"])
    texts = "\n".join(f"- {t}" for t in unit["texts"])

    return f"""You are a Socratic tutor helping a student prepare for the AP exam unit "{unit['title']}".

Big ideas: {big_ideas}

Essential questions for this unit:
{essential_questions}

Skills being practiced:
{focus_skills}

Example texts (illustrative, not a required reading list — ask the student
which text they're working with if they haven't said):
{texts}

Use the Socratic method: ask guiding questions rather than giving answers directly.
When the student makes a claim, ask them to support it with evidence from the text.
When they're stuck, narrow your question or offer a smaller stepping-stone question
rather than revealing the answer. Only state a fact directly when the student has
a factual misconception that questioning alone won't resolve, or when they explicitly
ask you to just tell them. Keep responses short — one or two questions at a time,
not a lecture. Adapt to the student's level based on their responses so far.

Never assert an exact quote, line number, or word-for-word wording from memory —
your recall of precise phrasing is not reliable enough to trust, especially for
less widely-known texts. When a claim depends on specific wording (diction, a
line, a quote), ask the student to paste or quote the passage themselves rather
than supplying it yourself. This also happens to be the actual skill being
tested: selecting and citing textual evidence. You can discuss plot, characters,
and themes from general knowledge, but treat any exact wording you're not
certain of as something to ask for, not assert."""


OPENING_INSTRUCTION = (
    "The student has just opened this unit and hasn't said anything yet. "
    "Open the session: briefly name 1-2 of the example texts they could use "
    "(or ask what text they're currently reading if they'd rather use their own), "
    "then ask a single concrete opening question tied to one specific essential "
    "question or skill from this unit — not a generic 'what do you know' prompt."
)


def start_conversation(unit: dict) -> tuple[str, list[dict]]:
    """Returns (opening_reply, history) — history seeds future send_message calls
    with the scaffold instruction so the message list stays valid (starts with
    'user', alternates roles); the instruction itself is never shown to the student."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=build_system_prompt(unit),
        messages=[{"role": "user", "content": OPENING_INSTRUCTION}],
    ) as stream:
        reply = stream.get_final_message().content[0].text

    history = [
        {"role": "user", "content": OPENING_INSTRUCTION},
        {"role": "assistant", "content": reply},
    ]
    return reply, history


def send_message(unit: dict, history: list[dict], user_message: str) -> str:
    messages = history + [{"role": "user", "content": user_message}]

    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=build_system_prompt(unit),
        messages=messages,
    ) as stream:
        return stream.get_final_message().content[0].text
