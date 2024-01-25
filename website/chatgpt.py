# chatgpt.py

import os
import sys
import gpt_constants

from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

os.environ["OPENAI_API_KEY"] = gpt_constants.APIKEY

query = sys.argv[1]

loader = DirectoryLoader("static\gpt", glob="*.txt")
index = VectorstoreIndexCreator().from_loaders([loader])

print(index.query(query, llm=ChatOpenAI()))