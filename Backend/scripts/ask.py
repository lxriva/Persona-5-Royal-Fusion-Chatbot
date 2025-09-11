import os, sys
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
emb = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-3-small")
vs = FAISS.load_local("vectorstore", emb, allow_dangerous_deserialization=True)
retriever = vs.as_retriever(k=6)

prompt = ChatPromptTemplate.from_template(
"""You are a concise Persona 5 Royal fusion guide.
Use the context to answer with *correct Royal* recipes/pairs. If multiple options, list all of them.
Question: {question}

Context (notes):
{context}

Answer in 4–6 lines, unless there are multiple options, then use as many lines as needed to cover all the options."""
)

def answer(q: str):
    docs = retriever.get_relevant_documents(q)
    context = "\n\n".join(d.page_content[:900] for d in docs)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    msg = prompt.format_messages(question=q, context=context)
    print(llm.invoke(msg).content)

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How do I fuse Yoshitsune?"
    answer(question)
