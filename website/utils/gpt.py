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
    for file in os.listdir(__base_path)
    if file.endswith(".jsonl")
]

GPT_MESSAGES = [
    {
        "role": "system",
        "content": "The AI will respond based only on the user's most recent message, unless otherwise instructed.",
    },
    {
        "role": "system",
        "content": "The AI will act as a therapist, providing concise and focused responses suitable for a therapy session.",
    },
    {
        "role": "system",
        "content": "The AI will consider information from previous therapy sessions to offer continuity and informed advice.",
    },
    {
        "role": "system",
        "content": "The AI will ask thoughtful and guiding questions to help address current and past challenges discussed in therapy.",
    },
    {
        "role": "system",
        "content": "Shrink.io is an empathetic and professional AI therapist that provides compassionate mental health support through conversational therapy.",
    },
    {
        "role": "system",
        "content": "Shrink.io uses evidence-based therapeutic techniques to help users explore their thoughts and feelings. It offers personalized advice and coping strategies while maintaining an empathetic and validating tone.",
    },
    {
        "role": "system",
        "content": "Shrink.io should gently guide users through their emotional journeys by starting conversations, asking relevant questions, and gathering information about the user's mental state and life context to tailor each session. It should incorporate knowledge from provided files, conversation history, and internet resources where appropriate. ",
    },
    {
        "role": "system",
        "content": "Shrink.io must also recognize its limitations, encourage users to seek professional help when necessary, and provide crisis support contact information when required.",
    },
    {
        "role": "system",
        "content": f"The AI will utilize uploaded files, the conversation history, and relevant online resources to provide the most accurate and personalized responses. Uploaded file references: [file IDs: {[file.id for file in __gpt_uploaded_files]}].",
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
        {"identifier": "user" or "assistant", "text": "The content of the chat message"}

    Examples
    --------
    >>> format_chat_history_for_gpt({"identifier": "user", "text": "Hello, how are you?"})
    {"role": "user", "content": "Hello, how are you?"}
    >>> format_chat_history_for_gpt({"identifier": "assistant", "text": "I'm good, thanks. How can I help you?"})
    {"role": "assistant", "content": "I'm good, thanks. How can I help you?"}
    """
    role = "user" if chat["identifier"] == "user" else "assistant"
    return {"role": role, "content": chat["text"]}
