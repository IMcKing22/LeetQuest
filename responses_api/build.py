# build.py
from __future__ import annotations
import os

from dotenv import load_dotenv
from openai import OpenAI

# Your existing modules; leave them as-is
import responses_api.intermediary_interpreter
import responses_api.diffusion_build

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key) if api_key else None


INTRO_INSTRUCTIONS = (
    "You are a master storyteller creating an epic coding adventure! "
    "Write a captivating intro scene (120-200 words) themed around the given TOPIC. "
    "Create an immersive fantasy/sci-fi setting where the player is a coding hero embarking on a quest. "
    "Use creative metaphors: arrays become treasure chests, algorithms become magical spells, "
    "data structures become ancient artifacts, etc. "
    "End with a dramatic choice between two distinct paths that represent different approaches to the topic. "
    "Make the paths feel like completely different adventures - one could be a stealth mission, "
    "another could be a grand battle, one could be a puzzle-solving expedition, another could be a rescue mission. "
    "Each path should feel unique and exciting! Do NOT mention specific coding problems - focus on the adventure story."
)

CONTINUE_INSTRUCTIONS = (
    "You are a master storyteller continuing an epic coding adventure! "
    "Based on the player's choice, continue the narrative with exciting developments. "
    "Create dramatic scenarios, challenges, and discoveries that relate to coding concepts through creative metaphors. "
    "End with two compelling path options that represent different approaches or strategies. "
    "Keep the adventure engaging and immersive! Do NOT mention specific coding problems - focus on the story."
)

EASY_COMPLETION_INSTRUCTIONS = (
    "You are a master storyteller continuing an epic coding adventure! "
    "The player has just completed their first set of challenges (Easy level). "
    "Write a continuation story (100-150 words) that celebrates their progress and sets up the next phase. "
    "Make it feel like they've gained new powers or unlocked new areas. "
    "The story should build on the previous narrative and create excitement for the Medium challenges ahead. "
    "Use creative metaphors and make it feel like a natural progression in their hero's journey."
)

MEDIUM_COMPLETION_INSTRUCTIONS = (
    "You are a master storyteller continuing an epic coding adventure! "
    "The player has just completed the Medium level challenges and proven their growing mastery. "
    "Write a continuation story (100-150 words) that acknowledges their increased skill and sets up the ultimate challenge. "
    "Make it feel like they're approaching the final boss or the most dangerous part of their quest. "
    "Build tension and excitement for the Hard challenges - this should feel like the climax is approaching. "
    "Use epic language and make it feel like they're becoming a true coding hero."
)

HARD_COMPLETION_INSTRUCTIONS = (
    "You are a master storyteller concluding an epic coding adventure! "
    "The player has just completed the Hard level challenges and achieved mastery! "
    "Write a triumphant conclusion story (120-180 words) that celebrates their complete victory. "
    "Make it feel like they've become a legendary coding hero, unlocked ultimate powers, or saved the digital realm. "
    "This should be an epic finale with celebration, recognition, and a sense of completion. "
    "End with a message about their growth and the new adventures that await them."
)

def start_story(topic: str, *, generate_art: bool = False) -> dict:
    if client is None:
        # Return creative default story when OpenAI client is not available
        story_text = f"""🌟 Welcome to the Realm of {topic}! 🌟

You stand at the entrance of an ancient coding temple, where legendary algorithms are said to be hidden within mystical data structures. The air crackles with computational energy as you prepare to embark on your quest.

Before you lies a grand hall with two shimmering portals, each leading to a different approach for mastering {topic}. The left portal glows with the warm light of systematic learning, while the right portal pulses with the vibrant energy of creative exploration.

Which path will you choose to begin your epic journey?"""
        conversation_id = "default_conversation"
        response_id = "default_response"
    else:
        try:
            res = client.responses.create(
                model="gpt-5",
                instructions=INTRO_INSTRUCTIONS,
                input=f"TOPIC: {topic}. Write ~120–200 words."
            )
            story_text = getattr(res, "output_text", "")
            # conversation is optional; fall back to response id
            conversation_id = getattr(getattr(res, "conversation", None), "id", None) or getattr(res, "id", None)
            response_id = getattr(res, "id", None)
        except Exception as e:
            # Fallback to creative default story if API call fails
            story_text = f"""🌟 Welcome to the Realm of {topic}! 🌟

You stand at the entrance of an ancient coding temple, where legendary algorithms are said to be hidden within mystical data structures. The air crackles with computational energy as you prepare to embark on your quest.

Before you lies a grand hall with two shimmering portals, each leading to a different approach for mastering {topic}. The left portal glows with the warm light of systematic learning, while the right portal pulses with the vibrant energy of creative exploration.

Which path will you choose to begin your epic journey?"""
            conversation_id = "default_conversation"
            response_id = "default_response"

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

    if client is None:
        # Return creative default continuation when OpenAI client is not available
        return {
            "story_text": """⚡ The Adventure Continues! ⚡

Your previous choice has opened new possibilities in this mystical coding realm. The path ahead splits into two intriguing directions, each promising unique challenges and rewards.

To your left, a path of structured mastery beckons with its methodical approach and proven techniques. To your right, a path of creative innovation glimmers with opportunities for breakthrough discoveries.

Which direction calls to your coding spirit?""",
            "conversation_id": conversation_id or "default_conversation",
            "response_id": response_id or "default_response",
        }
    
    try:
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
    except Exception as e:
        # Fallback to creative default continuation if API call fails
        return {
            "story_text": """⚡ The Adventure Continues! ⚡

Your previous choice has opened new possibilities in this mystical coding realm. The path ahead splits into two intriguing directions, each promising unique challenges and rewards.

To your left, a path of structured mastery beckons with its methodical approach and proven techniques. To your right, a path of creative innovation glimmers with opportunities for breakthrough discoveries.

Which direction calls to your coding spirit?""",
            "conversation_id": conversation_id or "default_conversation",
            "response_id": response_id or "default_response",
        }

def continue_story_easy_completion(conversation_id: str | None = None,
                                  response_id: str | None = None,
                                  previous_story: str = "") -> dict:
    """Generate story continuation after completing Easy problems"""
    kwargs = {}
    if conversation_id:
        kwargs["conversation"] = conversation_id
    elif response_id:
        kwargs["previous_response_id"] = response_id

    if client is None:
        return {
            "story_text": """🎉 Easy Challenges Conquered! 🎉
            
Your first victories have unlocked new powers within you! The mystical algorithms you've mastered now flow through your digital veins like liquid light. The realm around you begins to shift and expand, revealing deeper mysteries and more complex challenges.

You can feel your coding abilities growing stronger, and the path ahead now leads to more sophisticated challenges that will test your newfound skills. The Medium level awaits, promising greater rewards and more epic adventures.

Are you ready to ascend to the next level of your coding journey?""",
            "conversation_id": conversation_id or "default_conversation",
            "response_id": response_id or "default_response",
        }
    
    try:
        res = client.responses.create(
            model="gpt-5",
            instructions=EASY_COMPLETION_INSTRUCTIONS,
            input=f"Previous story context: {previous_story[:200]}... Continue the adventure after Easy completion.",
            **kwargs
        )

        return {
            "story_text": getattr(res, "output_text", ""),
            "conversation_id": getattr(getattr(res, "conversation", None), "id", None) or getattr(res, "id", None),
            "response_id": getattr(res, "id", None),
        }
    except Exception as e:
        return {
            "story_text": """🎉 Easy Challenges Conquered! 🎉
            
Your first victories have unlocked new powers within you! The mystical algorithms you've mastered now flow through your digital veins like liquid light. The realm around you begins to shift and expand, revealing deeper mysteries and more complex challenges.

You can feel your coding abilities growing stronger, and the path ahead now leads to more sophisticated challenges that will test your newfound skills. The Medium level awaits, promising greater rewards and more epic adventures.

Are you ready to ascend to the next level of your coding journey?""",
            "conversation_id": conversation_id or "default_conversation",
            "response_id": response_id or "default_response",
        }

def continue_story_medium_completion(conversation_id: str | None = None,
                                   response_id: str | None = None,
                                   previous_story: str = "") -> dict:
    """Generate story continuation after completing Medium problems"""
    kwargs = {}
    if conversation_id:
        kwargs["conversation"] = conversation_id
    elif response_id:
        kwargs["previous_response_id"] = response_id

    if client is None:
        return {
            "story_text": """⚡ Medium Mastery Achieved! ⚡
            
Your growing expertise has transformed you into a formidable coding warrior! The complex algorithms you've conquered now dance at your command, and the digital realm itself seems to recognize your increasing power.

But ahead lies the ultimate challenge - the Hard level. This is where legends are born and true masters are forged. The final trials await, promising the most epic battles and the greatest rewards.

The climax of your adventure approaches. Are you ready to face the ultimate test and become a true coding legend?""",
            "conversation_id": conversation_id or "default_conversation",
            "response_id": response_id or "default_response",
        }
    
    try:
        res = client.responses.create(
            model="gpt-5",
            instructions=MEDIUM_COMPLETION_INSTRUCTIONS,
            input=f"Previous story context: {previous_story[:200]}... Continue the adventure after Medium completion.",
            **kwargs
        )

        return {
            "story_text": getattr(res, "output_text", ""),
            "conversation_id": getattr(getattr(res, "conversation", None), "id", None) or getattr(res, "id", None),
            "response_id": getattr(res, "id", None),
        }
    except Exception as e:
        return {
            "story_text": """⚡ Medium Mastery Achieved! ⚡
            
Your growing expertise has transformed you into a formidable coding warrior! The complex algorithms you've conquered now dance at your command, and the digital realm itself seems to recognize your increasing power.

But ahead lies the ultimate challenge - the Hard level. This is where legends are born and true masters are forged. The final trials await, promising the most epic battles and the greatest rewards.

The climax of your adventure approaches. Are you ready to face the ultimate test and become a true coding legend?""",
            "conversation_id": conversation_id or "default_conversation",
            "response_id": response_id or "default_response",
        }

def continue_story_hard_completion(conversation_id: str | None = None,
                                 response_id: str | None = None,
                                 previous_story: str = "") -> dict:
    """Generate story conclusion after completing Hard problems"""
    kwargs = {}
    if conversation_id:
        kwargs["conversation"] = conversation_id
    elif response_id:
        kwargs["previous_response_id"] = response_id

    if client is None:
        return {
            "story_text": """🏆 LEGENDARY MASTERY ACHIEVED! 🏆
            
You have transcended the realm of ordinary coders and ascended to the pantheon of digital legends! Your complete mastery of these challenges has unlocked the ultimate coding powers within you.

The digital realm now recognizes you as a true hero - algorithms bow to your will, data structures reshape themselves at your command, and the very fabric of code itself flows through your consciousness like liquid starlight.

You have become a coding legend, and new adventures in other realms await your legendary skills. The journey continues, but you are forever changed - a true master of the digital arts!""",
            "conversation_id": conversation_id or "default_conversation",
            "response_id": response_id or "default_response",
        }
    
    try:
        res = client.responses.create(
            model="gpt-5",
            instructions=HARD_COMPLETION_INSTRUCTIONS,
            input=f"Previous story context: {previous_story[:200]}... Conclude the adventure after Hard completion.",
            **kwargs
        )

        return {
            "story_text": getattr(res, "output_text", ""),
            "conversation_id": getattr(getattr(res, "conversation", None), "id", None) or getattr(res, "id", None),
            "response_id": getattr(res, "id", None),
        }
    except Exception as e:
        return {
            "story_text": """🏆 LEGENDARY MASTERY ACHIEVED! 🏆
            
You have transcended the realm of ordinary coders and ascended to the pantheon of digital legends! Your complete mastery of these challenges has unlocked the ultimate coding powers within you.

The digital realm now recognizes you as a true hero - algorithms bow to your will, data structures reshape themselves at your command, and the very fabric of code itself flows through your consciousness like liquid starlight.

You have become a coding legend, and new adventures in other realms await your legendary skills. The journey continues, but you are forever changed - a true master of the digital arts!""",
            "conversation_id": conversation_id or "default_conversation",
            "response_id": response_id or "default_response",
        }

if __name__ == "__main__":
    print(start_story("Arrays & Hashing"))