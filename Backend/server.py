# backend/server.py
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --- Paths & init ---
BASE_DIR = Path(__file__).parent              # .../backend
VSTORE_DIR = BASE_DIR / "vectorstore"         # expects index.faiss + index.pkl here

load_dotenv()

# CORS: allow your Pages domain; fallback "*" for quick local tests
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Embeddings + VectorStore
emb = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="text-embedding-3-small",
)
vs = FAISS.load_local(str(VSTORE_DIR), emb, allow_dangerous_deserialization=True)
retriever = vs.as_retriever(k=6)

prompt = ChatPromptTemplate.from_template(
    """You are a concise Persona 5 Royal fusion guide.
Use the context to answer with *correct Royal* recipes/pairs. If multiple options, list all of them.

Context:
{context}

Question: {question}

Answer in 4–6 lines, unless there are multiple options, then use as many lines as needed to cover all the options."""
)

class AskBody(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask")
async def ask(body: AskBody):
    docs = retriever.get_relevant_documents(body.question)
    context = "\n\n".join(d.page_content[:900] for d in docs)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    msg = prompt.format_messages(question=body.question, context=context)
    answer = llm.invoke(msg).content
    return {"answer": answer}
