# chatgpt.py

# TO RUN THE FILE IN CMD: python website\utils\chatgpt.py

import os
import sys

from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# LOCAL IMPORTS
# from ..config.config import config

# os.environ["OPENAI_API_KEY"] = config.read("GPT", "API_KEY")
os.environ["OPENAI_API_KEY"] = "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"

query = """You are an expert psychologyst ai chatbot that help people in need for therapy 
but can't afford it, there for you are helping them using the method of psycho analysis of 
zigmond froid, and using the loaded directory."""

loader = DirectoryLoader(r"C:\Users\redkn\Final project AI\ShrinkGPT.github.io\website\static\gpt", glob="*.txt")
index = VectorstoreIndexCreator().from_loaders([loader])

print(index.query(query, llm=ChatOpenAI()))