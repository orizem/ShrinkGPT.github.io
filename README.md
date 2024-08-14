<div style="background:linear-gradient(to bottom, #f0f8ff, #c7e3ff); padding:20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); color: #444; width:40%; transition: box-shadow 0.3s;">

# <span style="color:#3366ff; text-shadow: 1px 1px 3px #ddd;">ShrinkGPT - Your Virtual AI Shrink 🤖🧠</span>

Welcome to ShrinkGPT, your personal AI chatbot psychologist! This project combines the power of GPT with an intuitive chatbot interface to provide you with a unique and interactive therapy experience.

## <span style="color:#ff9900; text-shadow: 1px 1px 2px #ddd;">Getting Started 🚀</span>

### <span style="color:#ffcc00; text-shadow: 1px 1px 2px #ddd;">Setting Up Your Virtual Environment</span>

1. **Create a Virtual Environment:**

   - Run `python -m virtualenv venv` to set up a virtual environment.

2. **Activate the Environment:**

   - Use `venv\Scripts\activate` to activate the virtual environment.

3. **Deactivate:**
   - When you're done, simply run `deactivate` to exit the virtual environment.

### <span style="color:#ffcc00; text-shadow: 3px 3px 3px #ddd;">Install Dependencies 📦</span>

- Upgrade pip with `python -m pip install --upgrade pip`.
- Install project dependencies with `python -m pip install -r requirements.txt`.
- Create a .env file with OPENAI_API_KEY="OPENAI-API-KEY" and D_ID_API_KEY="D-ID-API-KEY"

## <span style="color:#ff9900; text-shadow: 1px 1px 2px #ddd;">Docker Support 🐳</span>

<!-- Uncomment the following lines to enable Docker support for your project. -->
<!-- ```bash
1. cd website
2. docker build -t website .
3. docker run -dp 127.0.0.1:3000:3000 website
``` -->

## <span style="color:#ff9900;">Documentation with Sphinx 📚✨</span>

Our documentation is powered by Sphinx and is essential for understanding and contributing to the project. Follow these steps to keep it up-to-date:

1. Navigate to the project root folder (ShrinkGPT.github.io).
2. If not already present, create a 'docs' folder in the project root.
3. Run `sphinx-apidoc -F -P -T -o docs .` to generate initial documentation.
   - To include a new module, add an `__init__.py` file to the folder.
4. Change to the 'docs' directory (`cd docs`).
5. Update the HTML documentation with `make html`.

Feel free to explore, contribute, and let ShrinkGPT guide you on your virtual therapy journey! 🌈✨

</div>
