import json
import os

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_username(project_name, metadata):
    formatted_metadata = "\n".join(
        f"{item['trait_type']}:{item['value']}" for item in json.loads(metadata)
    )

    messages = [
        {
            "role": "user",
            "content": f"{formatted_metadata}\nType:{project_name}\n\nGenerate a username for this character provided its attributes. Reply with the username and nothing else.",
        }
    ]
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=5,
        stop=["\n"],
        temperature=1.5,
    )

    # remove quotes
    message = chat_completion.choices[0].message.content.replace('"', "")

    return message


def generate_bio(project_name, username, metadata):
    formatted_metadata = "\n".join(
        f"{item['trait_type']}:{item['value']}" for item in json.loads(metadata)
    )

    messages = [
        {
            "role": "user",
            "content": f"{formatted_metadata}\nType:{project_name}\nUsername:{username}\n\nGenerate a bio in less than 50 characters for this character provided its attributes. Use first person. Plaintext. English only.",
        }
    ]
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=50,
        stop=["\n"],
        temperature=1.4,
    )

    # remove quotes
    message = chat_completion.choices[0].message.content.replace('"', "")

    return message


def generate_tone(bio):
    messages = [
        {
            "role": "user",
            "content": f"{bio}\n\nProvided this bio, what tone does this character have? Respond with adjectives only.",
        }
    ]
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=50,
        stop=["\n"],
        temperature=1.7,
    )

    # remove quotes
    message = chat_completion.choices[0].message.content.replace('"', "")

    return message


async def create_post_from_tone(tone: str):
    messages = [
        {
            "role": "user",
            "content": f"{tone}\n\nUsing this tone, create a post. Keep it under 150 characters.",
        }
    ]
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=50,
        stop=["\n"],
        temperature=1.1,
    )

    # remove quotes
    message = chat_completion.choices[0].message.content.replace('"', "")
    # remove hashtags and the word that follows them
    message = " ".join(
        [word for word in message.split(" ") if not word.startswith("#")]
    )

    return message
