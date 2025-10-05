from openai import OpenAI
import responses_api.intermediary_interpreter
import responses_api.diffusion_build

client = OpenAI()

def path_bridge(input_text):

    res1 = client.responses.create(
        model="gpt-5",
        instructions="""
                    You are a bridge between backend and frontend.
                    Return exactly ONE short title in the format: Path of {NounOrNounPhrase}
                    Examples: Path of Precision, Path of Strategy
                    No quotes. No trailing period.
                    """,
        input=input_text
    )

    return res1.output_text

def description_former_bridge(input_text):

    res1 = client.responses.create(
        model="gpt-5",
        instructions="""You are a bridge between backend and frontend. You will take the broad descriptions that are provided to you and compact them into a few helpfully descriptive sentences about the situation regarding the FORMER path.""",
        input=input_text
    )

    return res1.output_text

def description_latter_bridge(input_text):

    res1 = client.responses.create(
        model="gpt-5",
        instructions="""You are a bridge between backend and frontend. You will take the broad descriptions that are provided to you and compact them into a few helpfully descriptive sentences about the situation regarding the LATTER path.""",
        input=input_text
    )

    return res1.output_text

def journey_bridge(input_text):

    res1 = client.responses.create(
        model="gpt-5",
        instructions="""You are a bridge between backend and frontend. You will take the broad descriptions that are provided to you and format them into a concise paragraph describing the situation that the user is in at large.""",
        input=input_text
    )

    return res1.output_text

