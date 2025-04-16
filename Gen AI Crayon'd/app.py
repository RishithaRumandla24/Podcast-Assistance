from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid
import google.generativeai as genai
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# Initialize Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
generation_model = genai.GenerativeModel('gemini-1.5-pro')
embedding_model = genai.GenerativeModel('embedding-001')

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_or_create_user_id():
    """Get or create a user ID for the session"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

def get_embeddings(text):
    """Get embeddings from Gemini embedding model"""
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"  # or "retrieval_query" based on use case
    )
    return result["embedding"]

def store_memory(user_id, content, memory_type):
    """Store memory in Supabase vector database"""
    embedding = get_embeddings(content)
    
    timestamp = datetime.now().isoformat()
    
    # Insert into vector database
    data = {
        "user_id": user_id,
        "content": content,
        "embedding": embedding,
        "memory_type": memory_type,
        "created_at": timestamp
    }
    
    supabase.table("podcast_memories").insert(data).execute()

def retrieve_memories(user_id, query, limit=5):
    """Retrieve relevant memories from Supabase vector database"""
    query_embedding = get_embeddings(query)
    
    # Search for similar memories
    result = supabase.rpc(
        "match_memories",
        {
            "query_embedding": query_embedding,
            "match_threshold": 0.7,
            "match_count": limit,
            "user_id_filter": user_id
        }
    ).execute()
    
    if result.data:
        return result.data
    return []

def generate_podcast_ideas(theme, previous_episodes=None):
    """Tool to generate podcast episode ideas"""
    context = f"Theme: {theme}\n"
    if previous_episodes:
        context += f"Previous episodes: {previous_episodes}\n"
    
    prompt = f"""
    {context}
    Generate 3 unique and engaging podcast episode ideas related to this theme.
    For each idea, provide:
    1. A catchy title
    2. A brief description (2-3 sentences)
    3. 1-2 potential guest types or specific topics to explore
    """
    
    response = generation_model.generate_content(prompt)
    return response.text

def create_podcast_script(title, outline=None, duration=None):
    """Tool to create a podcast script template"""
    context = f"Episode Title: {title}\n"
    if outline:
        context += f"Outline: {outline}\n"
    if duration:
        context += f"Target Duration: {duration} minutes\n"
    
    prompt = f"""
    {context}
    Create a podcast script template with the following sections:
    1. Introduction (greeting, episode overview)
    2. Main content sections (3-4 key topics)
    3. Transition phrases between sections
    4. Conclusion and call to action
    
    Make the script conversational and engaging.
    """
    
    response = generation_model.generate_content(prompt)
    return response.text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_id = get_or_create_user_id()
    user_message = request.json.get('message', '')
    
    # Retrieve relevant memories
    memories = retrieve_memories(user_id, user_message)
    memory_context = ""
    
    if memories:
        memory_context = "Relevant information from previous conversations:\n"
        for memory in memories:
            memory_context += f"- {memory['content']}\n"
    
    # Process command for specific tools
    response_text = ""
    memory_type = "general"
    
    if user_message.lower().startswith("generate ideas:"):
        theme = user_message[len("generate ideas:"):].strip()
        previous_episodes = None
        
        # Look for previous episode memories
        episode_memories = [m for m in memories if m['memory_type'] == 'episode']
        if episode_memories:
            previous_episodes = "; ".join([m['content'] for m in episode_memories[:3]])
        
        response_text = generate_podcast_ideas(theme, previous_episodes)
        
        # Store the podcast theme as memory
        store_memory(user_id, f"Podcast theme: {theme}", "theme")
        memory_type = "theme"
        
    elif user_message.lower().startswith("create script:"):
        script_details = user_message[len("create script:"):].strip()
        title = script_details
        outline = None
        duration = None
        
        if ":" in script_details:
            parts = script_details.split(":")
            title = parts[0].strip()
            if len(parts) > 1:
                outline = parts[1].strip()
            if len(parts) > 2 and "min" in parts[2]:
                duration = parts[2].strip()
        
        response_text = create_podcast_script(title, outline, duration)
        
        # Store the episode as memory
        store_memory(user_id, f"Created episode: {title}", "episode")
        memory_type = "episode"
        
    else:
        # General conversation
        prompt = f"""
        You are a Podcast Research & Script Writing Assistant. 
        
        {memory_context}
        
        User message: {user_message}
        
        Provide helpful and relevant assistance for podcast creators. Focus on helping with research, 
        content creation, and script writing. If the user hasn't shared their podcast theme or details yet, 
        ask them about it.
        """
        
        response = generation_model.generate_content(prompt)
        response_text = response.text
        
        # Store the general conversation as memory
        if len(user_message) > 10:  # Only store substantial messages
            store_memory(user_id, user_message, memory_type)
    
    # Store assistant's response as memory if it contains useful information
    if len(response_text) > 50:  # Only store substantial responses
        store_memory(user_id, f"Assistant provided: {response_text[:200]}...", memory_type)
    
    return jsonify({"response": response_text})

if __name__== '__main__':
    app.run(debug=True)