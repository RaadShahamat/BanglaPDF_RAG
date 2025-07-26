import faiss
import pickle
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
hf_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"]= hf_key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import numpy as np
from langdetect import detect

# Load vector index
index = faiss.read_index("G:/BanglaPDF_RAG/BanglaPDF_RAG/backend/bengali_index.faiss")

# Load chunk metadata
with open("G:/BanglaPDF_RAG/BanglaPDF_RAG/backend/bengali_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)



def retrieve_chunks(query, model, index, chunks, top_k=5):
    """
    Retrieve top-k relevant chunks for a query.
    Args:
        query (str): User query (English or Bengali).
        model: SentenceTransformer model.
        index: FAISS index.
        chunks (list): List of text chunks.
        top_k (int): Number of chunks to retrieve.
    Returns:
        tuple: (relevant chunks, similarity scores)
    """
    query_embedding = model.encode([query], convert_to_numpy=True)[0]
    distances, indices = index.search(np.array([query_embedding]), top_k)
    return [chunks[i] for i in indices[0]], distances[0]

memory = ConversationBufferMemory(
    memory_key="conversation_history",
    return_messages=True
)

llm = genai.GenerativeModel("gemini-2.0-flash")

def generate_answer(query, chunks, llm, memory):
    """
    Generate an answer using the language model.
    Args:
        query (str): User query.
        chunks (list): Retrieved chunks.
        llm: Language model pipeline.
        memory: ConversationBufferMemory for short-term memory.
    Returns:
        str: Generated answer.
    """
    context = "\n".join(chunks)
    conversation_history = memory.load_memory_variables({}).get("conversation_history", "")

    # Detect language of the query
    detected_lang = detect(query)

    # Choose language-specific instruction
    if detected_lang == "bn":
        lang_instruction = "উত্তরটি প্রশ্নের ভাষায় দিন (বাংলা)।"
    else:
        lang_instruction = "Answer in the same language as the question (English)."

    prompt = f"""
    You are a knowledgeable and helpful AI teacher. A student has asked you a question.

    Carefully read the provided context from a study resource (PDF). Understand what the student is really trying to ask. If the question is relevant to the provided context, then:

    1. Think deeply and clarify the answer in your own words.
    2. Reply clearly and concisely in the same language the question was asked in (English or Bengali).
    3. Do not make the answer unnecessarily long — focus on being correct, not detailed.
    4. reply in the same language as the question.

    If the question is not related to the given context, politely reply that the question is outside the topic.

    ---
    Context:
    {context}

    Question:
    {query}

    Conversation History (for continuity):
    {conversation_history}

    Instructions:
    - Always answer in the question's language.
    - Avoid repeating the context unless needed.
    - Be helpful, concise, and relevant.
    """

    if llm:
        response = llm.generate_content(prompt).text
    else:
        response = f"Placeholder answer for query: {query}\nContext: {context}"

    # Save to short-term memory
    memory.save_context({"input": query}, {"output": response})

    return response