# gpt.py

import os

from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from config import WEBSITE_PATH

# Load OpenAI API key from environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

__base_path = f"{WEBSITE_PATH}/static/gpt"
__gpt_uploaded_files = [
    client.files.create(
        file=open(os.path.join(__base_path, file), "rb"),
        purpose="fine-tune",
    )
    for file in os.listdir(__base_path) if file.endswith(".jsonl")
]

GPT_MESSAGES = [
    {
        "role": "system",
        "content": "Shrink.io provides compassionate and professional mental health therapy",
    },
    {
        "role": "system",
        "content": "Shrink.io is an empathetic and professional AI therapist, providing compassionate mental health support through conversational therapy. This AI uses evidence-based therapeutic techniques to help users explore their thoughts and feelings, offering personalized advice and coping strategies. Shrink.io should start conversations and encourage users to share their feelings, while gently guiding them through their emotional journeys. It should ask relevant questions to gather information about the user's mental state and life context, ensuring a tailored approach to each session. The AI should respond with empathy, validate the user's experiences, and provide constructive feedback and support. When appropriate, Shrink.io can incorporate knowledge from provided files and current resources to enhance its responses. The AI should also be aware of its limitations, advising users to seek professional help when necessary and providing contact information for crisis support services if needed.",
    },
    {
        "role": "system",
        "content": f"The gpt need to use the files, and the history of the conversation, and the internet, in order to give the best response for the patients. {[file.id for file in __gpt_uploaded_files]}",
    },
]


def format_chat_history_for_gpt(chat: Dict[str, str]) -> Dict[str, str]:
    """
    Format chat history for GPT input.

    This function takes a chat message and formats it into a structure suitable for GPT input.
    It determines the role of the speaker (user or assistant) based on the identifier and
    extracts the content of the message.

    Parameters
    ----------
    chat : Dict[str, str]
        A dictionary containing chat message information.
        It should have at least two keys: "identifier" and "text".

    Returns
    -------
    Dict[str, str]
        A dictionary with two keys: "role" and "content".
        The "role" key will be either "user" or "assistant" based on the chat["identifier"].
        The "content" key contains the text of the chat message.

    Notes
    -----
    This function assumes that the input dictionary has the following structure:
    {
        "identifier": "user" or "assistant",
        "text": "The content of the chat message"
    }

    Examples
    --------
    >>> format_chat_history_for_gpt({"identifier": "user", "text": "Hello, how are you?"})
    {"role": "user", "content": "Hello, how are you?"}
    >>> format_chat_history_for_gpt({"identifier": "assistant", "text": "I'm good, thanks. How can I help you?"})
    {"role": "assistant", "content": "I'm good, thanks. How can I help you?"}
    """
    role = "user" if chat["identifier"] == "user" else "assistant"
    return {"role": role, "content": chat["text"]}
