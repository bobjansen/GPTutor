"""Access the GPT API"""
import openai
import app_globals

openai.api_key = app_globals.app_settings["openai_key"]


def choose_model():
    """Select the model to use"""
    return "gpt-3.5-turbo"


def get_completion(messages):
    """Get the completion given the messages"""
    # Strip out metadata added on our side.
    messages = [
        {"role": message["role"], "content": message["content"]} for message in messages
    ]
    response = openai.ChatCompletion.create(
        model=choose_model(), messages=messages, n=1
    )
    return response.choices[0]
