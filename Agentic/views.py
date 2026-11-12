from django.shortcuts import render
from django.http import JsonResponse
from pgvector.django import CosineDistance
from .models import CharacterMemory
import requests

def index(request):
    return render(request, 'Agentic/index.html')

def chat_with_character(request):
    user_message = request.POST.get('message', 'Hello')

    # 1. Get the embedding for the user's message
    embed_resp = requests.post("http://localhost:11434/api/embeddings", json={
        "model": "nomic-embed-text",
        "prompt": user_message
    })
    user_vector = embed_resp.json()['embedding']

    # 2. Query Django ORM using Cosine Distance
    similar_lines = CharacterMemory.objects.annotate(
        distance=CosineDistance('embedding', user_vector)
    ).order_by('distance')[:3]

    # 3. Format the retrieved context
    examples = "\n".join([
        f"Someone says: '{line.interlocutor_line}'\nYou reply: '{line.character_response}'"
        for line in similar_lines
    ])

    # 4. Generate the final response using the retrieved context
    prompt = f"""You are playing the role of the character.
    Respond to the user completely in character based on these examples:
    {examples}

    User says: {user_message}
    Your reply:"""

    chat_resp = requests.post("http://localhost:11434/api/generate", json={
        "model": "HammerAI/cydonia-v4.3",  # Or llama3, depending on your setup
        "prompt": prompt,
        "stream": False
    })

    return JsonResponse({"reply": chat_resp.json()['response']})

