from openai import OpenAI
import os

client = OpenAI()

response = client.responses.create(
  model="gpt-5",
  instructions="""You are a storyteller that generates decision based adventures that have continuous dual branching paths.
                  Upon receiving user input, you` generate a story along with two LeetCode problems, one for each path.
                  When the user picks a problem, you will generate another story and problem based on whether they've solved it or not,
                  And the genre of the leetcode problem.""",
  input="Prompt the user to choose what type of coding problem they'd like to tackle first and give examples of all common problem types (arrays, queue, dp, trees, graphs, etc)"
)

print(response.output_text)
