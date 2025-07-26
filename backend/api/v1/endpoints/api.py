from fastapi import FastAPI, File, UploadFile, Request, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
import shutil
import os
from extraction import hybrid_ocr_pymupdf
from cleaning import clean_and_chunk_document
import pickle
import faiss
from embedding import embed_chunks, store_embeddings  # if you defined them in vectorstore.py
from rag_pipeline import retrieve_chunks, generate_answer, llm, memory
import re
from sentence_transformers import SentenceTransformer

router = APIRouter()


class QueryRequest(BaseModel):
    req: str

async def process_pdf():
    # Save uploaded PDF to disk
    file_path = "G:/BanglaPDF_RAG/BanglaPDF_RAG/backend/HSC26-Bangla1st-Paper.pdf"

    # Step 1: Extract and merge text using OCR + PyMuPDF
    merged_output = hybrid_ocr_pymupdf(file_path)
    merged_text = "".join(merged_output)

    # Step 2: Clean and chunk the merged text
    chunked_cleaned_text = clean_and_chunk_document(merged_text)
    embeddings = embed_chunks(chunked_cleaned_text)
    index, chunk_refs = store_embeddings(chunked_cleaned_text, embeddings)
    # Save FAISS index
    faiss.write_index(index, "bengali_index.faiss")
    # Save chunks (metadata)
    with open("bengali_chunks.pkl", "wb") as f:
        pickle.dump(chunk_refs, f)
        


@router.post("/rag-query")
async def rag_query(body: QueryRequest):
    query = body.req
    model = SentenceTransformer("intfloat/multilingual-e5-small")  # Good Bengali support
    index = faiss.read_index("bengali_index.faiss")
    with open("bengali_chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    relevant_chunks, _ = retrieve_chunks(query, model, index, chunks)
    answer = generate_answer(query, relevant_chunks, llm, memory)
    history = memory.load_memory_variables({})["conversation_history"]
    formatted_history = []
    for i in range(0, len(history), 2):
        formatted_history.append({
            "question": history[i].content if i < len(history) else "",
            "answer": history[i+1].content if i+1 < len(history) else ""
        })
    return {"query": query, "answer": answer, "history": formatted_history}
