# build.py
from __future__ import annotations

from dotenv import load_dotenv
from openai import OpenAI

# Your existing modules; leave them as-is
import responses_api.intermediary_interpreter
import responses_api.diffusion_build

load_dotenv()
client = OpenAI()


INTRO_INSTRUCTIONS = (
    "You are a storyteller for a choose-your-own-adventure about coding.\n"
    "Write an intro scene themed around the given TOPIC and end by inviting the player to choose a path.\n"
    "Do NOT invent coding problems here; later screens will attach specific problems."
)

CONTINUE_INSTRUCTIONS = (
    "You are a storyteller that generates decision-based adventures with continuous dual branching.\n"
    "Given the player's input, continue the narrative and end with two clear path options.\n"
    "Do NOT invent coding problems; the app will attach them separately."
)

def start_story(topic: str, *, generate_art: bool = False) -> dict:
    res = client.responses.create(
        model="gpt-5",
        instructions=INTRO_INSTRUCTIONS,
        input=f"TOPIC: {topic}. Write ~120–200 words."
    )

    story_text = getattr(res, "output_text", "")
    # conversation is optional; fall back to response id
    conversation_id = getattr(getattr(res, "conversation", None), "id", None) or getattr(res, "id", None)
    response_id = getattr(res, "id", None)

    # (Optional) image generation – keep wrapped so errors don’t break the request
    if generate_art and story_text:
        try:
            try:
                # package-relative if inside module
                from . import intermediary_interpreter, diffusion_build
            except Exception:
                import intermediary_interpreter, diffusion_build
            art_prompt = intermediary_interpreter.receive_input(story_text)
            diffusion_build.generate_image(art_prompt)
        except Exception:
            pass

    return {
        "story_text": story_text,
        "conversation_id": conversation_id,   # may be None
        "response_id": response_id,           # always present
    }

def continue_story(conversation_id: str | None = None,
                   response_id: str | None = None,
                   user_input: str = "") -> dict:
    kwargs = {}
    # prefer conversation when available; otherwise chain off the previous response id
    if conversation_id:
        kwargs["conversation"] = conversation_id
    elif response_id:
        kwargs["previous_response_id"] = response_id

    res = client.responses.create(
        model="gpt-5",
        instructions=CONTINUE_INSTRUCTIONS,
        input=user_input or "Continue.",
        **kwargs
    )

    return {
        "story_text": getattr(res, "output_text", ""),
        "conversation_id": getattr(getattr(res, "conversation", None), "id", None) or getattr(res, "id", None),
        "response_id": getattr(res, "id", None),
    }

if __name__ == "__main__":
    print(start_story("Arrays & Hashing"))