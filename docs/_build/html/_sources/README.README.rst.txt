======
README
======

Getting Started 🚀
==================

Setting Up Your Virtual Environment
------------------------------------

1. **Create a Virtual Environment:**

   - Run ``python -m virtualenv venv`` to set up a virtual environment.

2. **Activate the Environment:**

   - Use ``venv\Scripts\activate`` to activate the virtual environment.

3. **Deactivate:**

   - When you're done, simply run ``deactivate`` to exit the virtual environment.

Install Dependencies 📦
------------------------

- Upgrade pip with ``python -m pip install --upgrade pip``.
- Install project dependencies with ``python -m pip install -r requirements.txt``.
- Create a `.env` file with::

    OPENAI_API_KEY="OPENAI-API-KEY"
    D_ID_API_KEY="D-ID-API-KEY"

Docker Support 🐳
=================

1. Run ``docker build -t shrink-io-app .``
2. Run ``docker run -p 5000:5000 shrink-io-app``

Documentation with Sphinx 📚✨
==============================

Our documentation is powered by Sphinx and is essential for understanding and contributing to the project. Follow these steps to keep it up-to-date:

1. Navigate to the project root folder (ShrinkGPT.github.io).
2. If not already present, create a `docs` folder in the project root.
3. Run ``sphinx-apidoc -F -P -T -o docs .`` to generate initial documentation.
   - To include a new module, add an `__init__.py` file to the folder.
4. Change to the `docs` directory (``cd docs``).
5. Update the HTML documentation with ``make html``.

Deploy Flask Docker App to Google Cloud ☁️
==========================================

This guide provides step-by-step instructions on how to deploy a Docker image of a Flask web application to Google Cloud using Cloud Run.

Prerequisites
-------------

1. Google Cloud account and project.
2. Docker image of your Flask web application.
3. gcloud CLI installed and configured.

Step 1: Set Up Google Cloud Project
-----------------------------------

1. **Log in to `Google Cloud Console <https://console.cloud.google.com/>`_.**
2. **Create a new project** (or select an existing one):
   - Click on the project dropdown at the top and select "New Project."
   - Give your project a name and wait for it to be created.

Step 2: Enable Required APIs
----------------------------

1. **Enable Cloud Run**:
   - In the search bar, type "Cloud Run" and open it.
   - Click **Enable Cloud Run API**.
2. **Enable Cloud Build**:
   - Search for "Cloud Build" and enable it the same way.

Step 3: Configure gcloud CLI
----------------------------

1. Open a terminal and configure your project::

    gcloud auth login  # Log in to your Google account
    gcloud config set project [PROJECT_ID]  # Replace with your project ID
    gcloud auth configure-docker  # Configure Docker to use Google Cloud

Step 4: Push Docker Image to Google Container Registry (GCR)
------------------------------------------------------------

1. **Tag your Docker image**::

    docker tag [IMAGE_NAME] gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG]

    Replace:
    - `IMAGE_NAME`: Name of your local Docker image.
    - `PROJECT_ID`: Your Google Cloud project ID.
    - `TAG`: Optional version tag (e.g., `v1`).

2. **Push your image to GCR**::

    docker push gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG]

Step 5: Deploy to Cloud Run
---------------------------

1. **Deploy your container image**::

    gcloud run deploy [SERVICE_NAME] \
    --image gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG] \
    --platform managed \
    --region [REGION] \
    --allow-unauthenticated

    Replace:
    - `SERVICE_NAME`: The name of your Cloud Run service.
    - `REGION`: Google Cloud region (e.g., `us-central1`).

2. **Wait for the deployment to finish**. Once done, you'll get a URL where your Flask app is deployed.

Step 6: Test and Share
----------------------

- Copy the URL from the Cloud Run output.
- Share the URL with others to access your Flask app!

Feel free to explore, contribute, and let ShrinkGPT guide you on your virtual therapy journey! 🌈✨