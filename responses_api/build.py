from dotenv import load_dotenv
from openai import OpenAI
import intermediary_interpreter
import diffusion_build

load_dotenv()
client = OpenAI()

res1 = client.responses.create(
  model="gpt-5",
  instructions="""You are a storyteller that generates decision based adventures that have continuous dual branching paths.
                  Upon receiving user input, you will generate a context providing story that you will output to the user. Along with each contextual helper, you will provide two paths for the user to follow on thir adventure (i.e. walk into a dark, eerie forest or through a deep, damp swamp). To walk down either of these paths, you will also provide the user with two LeetCode problems, one for each path. 
                  When the user picks a problem, you will generate another story and problem based on whether they've solved it or not,
                  And the genre of the leetcode problem.""",
  input="Prompt the user to choose what type of coding problem they'd like to tackle first and give examples of all common problem types (arrays, queue, dp, trees, graphs, etc)"
)

print(res1.output_text)
# Call the intermediary to generate a prompt for the artist
art_prompt = intermediary_interpreter.receive_input(res1.output_text)
print(art_prompt)
# Call the artist
diffusion_build.generate_image(art_prompt)

while input("Continue? (Y/N): ") == "Y":
  user_text = input("Choose your leetcode problem: ")
  res2 = client.responses.create(
      model="gpt-5",
      instructions="""You are a storyteller that generates decision based adventures that have continuous dual branching paths.
                  Upon receiving user input, you generate a story along with two LeetCode problems, one for each path.
                  When the user picks a problem, you will generate another story and problem based on whether they've solved it or not,
                  And the genre of the leetcode problem.""",
      previous_response_id=res1.id,
      store=True,
      input=user_text
  )
  res1 = res2
  print(res2.output_text)
  





#print(res2.output_text)
