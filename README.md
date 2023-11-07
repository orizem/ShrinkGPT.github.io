# ShrinkGPT.github.io
AI Shrink chat bot with GPT


# Virtual Environment
1) create a virtual environment
    * python -m virtualenv venv
2) Activate the environment
    * venv\Scripts\activate
3) To deactivate
    * deactivate

# Install Environment
pip install -r requirements.txt


# Docker
1) cd flask_shrink_gpt
2) docker build -t flask_shrink_gpt .
3) docker run -dp 127.0.0.1:3000:3000 flask_shrink_gpt