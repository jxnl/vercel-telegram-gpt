from dotenv import load_dotenv

load_dotenv()

import os
import openai

openai.api_key = os.getenv("OPENAI_TOKEN", None)


def respond(msg):
    """
    Generate a response to a user-provided message

    Args:
        msg (str): The message to respond to

    Returns:
        response (str): The response to the user-provided message
    """

    if openai.api_key is None:
        response = (
            "OpenAI API Key not found. Please set the OPENAI_TOKEN environment variable"
        )
        return response

    # Generate a prompt based on the user-provided message, feel free to change this.
    prompt = f"""
    You are an assistant telegram bot that helps people with their daily tasks and answers their questions.
    You are currently chatting with a user. 

    user: 
    {msg}
    
    response:
    """

    gpt3_session = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.8,
        max_tokens=2024,
        n=1,
    )

    # Generate a response to the user-provided message
    response = gpt3_session.choices[0].text
    return response
