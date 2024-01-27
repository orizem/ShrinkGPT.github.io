# chatgpt.py

import os
import sys

from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# LOCAL IMPORTS
from ..config.config import config

os.environ["OPENAI_API_KEY"] = config.read("GPT", "APIKEY")

query = sys.argv[1]

loader = DirectoryLoader("static\gpt", glob="*.txt")
index = VectorstoreIndexCreator().from_loaders([loader])

print(index.query(query, llm=ChatOpenAI()))