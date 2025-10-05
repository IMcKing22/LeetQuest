from openai import OpenAI
import os

# Initialize OpenAI client with API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key) if api_key else None

def receive_input(input_response):
    if client is None:
        # Return a default response when OpenAI client is not available
        return "Two contrasting settings: one elegant and refined, the other bold and adventurous. Side by side visual comparison."
    
    try:
        res1 = client.responses.create(
        model="gpt-5",
        instructions="""You are an important intermediary between a storyteller and an artist that takes the settings that the storyteller provides you with and communicates these settings clearly and succinctly to the artist so that they can draw images based on your descriptions. 
                        The content of the input that you receive will always give two distinct settings that the story can go down. Upon receiving said input, you will take both of these settings and output a message to the artist that allows them to draw a clear side by side image of one setting next to the other. Always limit your response to 30 words.""",
        input= input_response
        )
        return res1
    except Exception as e:
        # Return a default response if API call fails
        return "Two contrasting settings: one elegant and refined, the other bold and adventurous. Side by side visual comparison."
