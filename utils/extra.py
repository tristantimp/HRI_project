import os
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]


def request_to_chatgpt(prompt, history):
    with open("prompts/initial_prompt.txt", "r") as file:
        content = file.read()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": content + history},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()