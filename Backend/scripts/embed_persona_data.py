import os
import pickle
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

# Load env vars
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Please set OPENAI_API_KEY in your environment or .env file.")

# Load chunks
chunks_dir = "chunks"
documents = []
for entry in sorted(os.listdir(chunks_dir)):
    path = os.path.join(chunks_dir, entry)
    if not os.path.isfile(path) or not entry.lower().endswith(".txt"):
        continue
    with open(path, "r", encoding="utf-8") as f:
        documents.append(Document(page_content=f.read()))

print(f"Loaded {len(documents)} persona text chunks.")

# Embed & save
print("Creating embeddings...")
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
vectorstore = FAISS.from_documents(documents, embedding)
out_dir = "vectorstore"
vectorstore.save_local(out_dir)
print(f"FAISS vector store saved in ./{out_dir}")
