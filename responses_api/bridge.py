from openai import OpenAI
import os
import responses_api.intermediary_interpreter
import responses_api.diffusion_build

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key) if api_key else None

def path_bridge(input_text):
    if client is None:
        # Return different creative paths based on input
        if "approach A" in input_text or "systematic" in input_text:
            return "Path of Ancient Wisdom"
        else:
            return "Path of Digital Dragons"
    
    try:
        res1 = client.responses.create(
            model="gpt-5",
            instructions="""
                        You are a creative bridge between backend and frontend.
                        Return exactly ONE short, epic title in the format: Path of {EpicNounOrPhrase}
                        Examples: Path of Shadow Stealth, Path of Crystal Towers, Path of Dragon's Lair, Path of Mystic Forests, Path of Ancient Temples, Path of Digital Battles
                        Make it sound like a unique fantasy adventure! Keep it short and exciting.
                        No quotes. No trailing period. Maximum 4 words.
                        """,
            input=input_text
        )
        return res1.output_text
    except Exception as e:
        return "Path of Mystical Mastery"

def description_former_bridge(input_text):
    if client is None:
        return "Master the time-tested algorithms of legendary coders. Follow systematic approaches that have stood the test of time. Build your foundation with proven techniques and disciplined practice."
    
    try:
        res1 = client.responses.create(
            model="gpt-5",
            instructions="""You are a creative bridge between backend and frontend. Create a BRIEF, exciting description of the FIRST path choice (maximum 3 sentences). 
            Make it sound like an epic adventure - stealth mission, puzzle expedition, rescue mission, or grand battle. 
            Use coding metaphors and make it exciting. Keep it short and punchy!""",
            input=input_text
        )
        return res1.output_text
    except Exception as e:
        return "This mystical path leads through ancient coding temples where systematic wisdom has been preserved for centuries. Follow the time-tested methods of legendary programmers who have mastered the fundamentals through disciplined practice."

def description_latter_bridge(input_text):
    if client is None:
        return "Forge new solutions through creative experimentation. Embrace innovative approaches and bold thinking. Discover uncharted territories where coding magic awaits."
    
    try:
        res1 = client.responses.create(
            model="gpt-5",
            instructions="""You are a creative bridge between backend and frontend. Create a BRIEF, exciting description of the SECOND path choice (maximum 3 sentences). 
            Make it sound like a completely different adventure from the first path - if first was stealth, this could be exploration; if first was battle, this could be puzzle-solving.
            Use coding metaphors and make it exciting. Keep it short and punchy!""",
            input=input_text
        )
        return res1.output_text
    except Exception as e:
        return "This enchanted path winds through uncharted territories where innovative coding magic awaits discovery. Embrace the unknown and forge new solutions through creative experimentation and bold thinking."

def journey_bridge(input_text):
    if client is None:
        return "You stand at the crossroads of an epic coding adventure, where every algorithm is a spell waiting to be mastered and every data structure holds the key to unlocking new realms of computational power."
    
    try:
        res1 = client.responses.create(
            model="gpt-5",
            instructions="""You are a creative bridge between backend and frontend. Transform the broad descriptions into an engaging, fantasy-themed summary of the user's current situation in their coding adventure. Use epic language and coding metaphors.""",
            input=input_text
        )
        return res1.output_text
    except Exception as e:
        return "You stand at the crossroads of an epic coding adventure, where every algorithm is a spell waiting to be mastered and every data structure holds the key to unlocking new realms of computational power."

