# chatgpt.py

import os
import sys

from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# LOCAL IMPORTS
from ..config.config import config

# PROJECT IMPORTS
from config import WEBSITE_PATH

os.environ["OPENAI_API_KEY"] = config.read("GPT", "API_KEY")

query = sys.argv[1]

loader = DirectoryLoader(rf"{WEBSITE_PATH}\static\gpt", glob="*.txt")
index = VectorstoreIndexCreator().from_loaders([loader])

print(index.query(query, llm=ChatOpenAI()))
