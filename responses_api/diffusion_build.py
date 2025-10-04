import replicate
from dotenv import load_dotenv

load_dotenv()

def generate_image(input_text):

    output = replicate.run(
        "ideogram-ai/ideogram-v3-turbo",
        input={"prompt": input_text}
    )

    # To access the file URL:
    #print(output[0].url())
    #=> "http://example.com"

    # To write the file to disk:
    with open("./responses_api/diffusion_images/my-image.png", "wb") as file:
        file.write(output.read())

