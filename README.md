OpenAI Chat REST API

This project is a small REST API built with FastAPI that allows users to chat with OpenAI models and keeps the conversation history. It tracks token usage and calculates the total cost for each chat session.

Features:

1) Start a new chat session

2) Send a message to a session

3) Retrieve full chat history with:

- User messages

- Model responses

- Token usage

- Total accumulated cost

4) Simple in-memory storage (or database if configured)

5) Fully documented API with Swagger UI at /docs

Tech Stack:

  - Python 3.10+

  - FastAPI

  - Uvicorn (ASGI server)

  - OpenAI API

  - SQLAlchemy (optional, for database storage)

  - python-dotenv (for environment variables)

Getting Started

Prerequisites:

- Python 3.10 or higher installed

- OpenAI API key (get your key here https://platform.openai.com/account/api-keys)

Installation

1. Clone the repository:

git clone <your-repo-url>
cd <your-project-folder>

2. Create and activate a virtual environment:

python -m venv venv

.\venv\Scripts\Activate.ps1

3. Install dependencies:

pip install --upgrade pip

pip install -r requirements.txt

4. Create .env file in the project root and add your OpenAI API key:

OPENAI_API_KEY=sk-your_actual_api_key_here

5. Running the Server

python -m uvicorn main:app --reload

API Endpoints

All endpoints are documented and can be tested via Swagger UI:

http://127.0.0.1:8000/docs

POST /chat/start – Start a new chat session

POST /chat/{session_id}/message – Send a message to a session

GET /chat/{session_id}/history – Retrieve the full chat history with token usage and total cost
