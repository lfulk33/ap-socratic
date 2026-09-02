import anthropic
from config import ANTHROPIC_API_KEY

MODEL = "claude-sonnet-5"

# The conversation is resent in full on every turn, so input grows quadratically: by turn
# 30 the opening exchange has been paid for thirty times. Caching the stable prefix costs
# a tenth of fresh input and is what makes Sonnet cheaper here than uncached Haiku was.
# One breakpoint, on the end of the history, so it covers the system prompt and every
# prior turn together — the system prompt alone (~625 tokens) is under the cache minimum.
CACHE = {"type": "ephemeral"}


def _cached_prefix(messages):
    """Mark the end of the stable prefix. Returns a new list; inputs are not mutated."""
    if not messages:
        return messages
    out = [dict(m) for m in messages]
    tail = out[-1]
    if isinstance(tail["content"], str):
        tail["content"] = [{"type": "text", "text": tail["content"], "cache_control": CACHE}]
    return out


def _text(msg):
    """The first text block. Sonnet returns thinking blocks ahead of the answer, so
    content[0] is not reliably the reply -- indexing it blindly crashes the request."""
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            return block.text
    return ""


def _log_usage(msg, where):
    u = getattr(msg, "usage", None)
    if u is None:
        return
    print(f"[{where}] in={getattr(u, 'input_tokens', 0)} "
          f"cache_write={getattr(u, 'cache_creation_input_tokens', 0)} "
          f"cache_read={getattr(u, 'cache_read_input_tokens', 0)} "
          f"out={getattr(u, 'output_tokens', 0)}", flush=True)

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
        final = stream.get_final_message()
        _log_usage(final, "open")
        reply = _text(final)

    history = [
        {"role": "user", "content": OPENING_INSTRUCTION},
        {"role": "assistant", "content": reply},
    ]
    return reply, history


def send_message(unit: dict, history: list[dict], user_message: str) -> str:
    # Cache everything up to and including the last stored turn; the new message is the
    # only fresh input. The breakpoint moves forward each turn, so the cache keeps up.
    messages = _cached_prefix(history) + [{"role": "user", "content": user_message}]

    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=build_system_prompt(unit),
        messages=messages,
    ) as stream:
        final = stream.get_final_message()
        _log_usage(final, "turn")
        return _text(final)
