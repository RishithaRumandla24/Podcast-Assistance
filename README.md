🎙️ Podcast Assistant – Your AI-Powered Podcast Creation Sidekick
Welcome to Podcast Assistant, a smart web app built with Flask that helps podcast creators like you come up with episode ideas, write engaging scripts, and keep track of your creative process — all with the help of Google Gemini AI and a memory system powered by Supabase vector embeddings.

🚀 What It Can Do
🧠 Smart Conversations – Ask anything and get relevant, AI-generated responses using Gemini.

💡 Idea Generator – Share your podcast theme, and the assistant will pitch unique episode ideas.

✍️ Script Builder – Automatically generate a structured, conversational script for your next episode.

📚 Context Awareness – Remembers your past inputs to provide more personalized and relevant responses.

🔐 User Tracking – Each user session is stored using a unique ID so your data stays consistent and separate.

📌 Embedding Magic – Uses text embeddings to understand and store context intelligently.

🛠️ Tech Stack

Layer	Tech Used
Backend	Flask (Python)
AI Models	Google Gemini (Generative + Embedding)
Database	Supabase (Postgres + RPC + Vector Search)
Environment	python-dotenv for secure config management
Sessions	Flask's built-in session handling with UUID
📁 Project Overview
bash
Copy
Edit
podcast-assistant/
├── app.py                # Main Flask application logic
├── templates/
│   └── index.html        # Basic front-end UI
├── .env                  # Environment variables (not committed)
├── requirements.txt      # Python dependencies
🧠 How It Works
🧍 User Session
Each visitor gets a unique ID (UUID) stored in their session. This makes sure each user's data stays private and consistent across their interactions.

🧾 Memory Storage & Retrieval
Text inputs from users are converted into vector embeddings using Gemini’s embedding-001 model.

These embeddings, along with user messages, are saved in a podcast_memories table in Supabase.

An RPC function named match_memories retrieves the most relevant past memories to help with continuity and smarter responses.

💬 Chat Commands
You can talk to the assistant using natural language, or use special commands for more specific tasks:

generate ideas: [theme]
Generate 3 unique podcast episode ideas based on the theme. Each comes with a title, short description, and guest/topic suggestions.

create script: [title]: [optional outline]: [optional duration in min]
Build a ready-to-use podcast script that includes intro, key talking points, transitions, and a wrap-up.

General Chat
Not sure what you want? Just ask! The assistant can help brainstorm, plan, and polish content based on your ongoing conversation.

🌐 API Endpoints
/
Renders the home page (index.html)

/chat (POST)
Accepts a JSON body with a message field.

Processes the message, looks up relevant memories, runs the appropriate logic or AI tool, and returns a response.

🧪 Sample API Use
Request:
{
  "message": "generate ideas: space exploration"
}
Response:
{
  "response": "1. 'Beyond the Stars' – Dive into the future of space travel..."
}
