# Cheatsheet: RAG

## Pipeline in 6 lines
```
Load → Split → Embed → Store → Retrieve → Generate
```

## Load
```python
from langchain_community.document_loaders import TextLoader
docs = TextLoader("notes.txt").load()
# PDFs: pypdf (pure python) or pymupdf (faster, better layout)
```

## Split
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # start here, tune per corpus
    chunk_overlap=150,    # prevents cut sentences at boundaries
)
chunks = splitter.split_documents(docs)
```
Recursive = tries `\n\n`, then `\n`, then `" "`, then chars — respects structure.

## Embed + Store (FAISS)
```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

emb = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
store = FAISS.from_documents(chunks, emb)
store.save_local("index/")                       # FAISS is manual-persistence
store = FAISS.load_local("index/", emb, allow_dangerous_deserialization=True)
```

## Retrieve
```python
retriever = store.as_retriever(search_kwargs={"k": 4})
hits = retriever.invoke("What is the refund policy?")
# with scores:
scored = store.similarity_search_with_score(query, k=4)
```

## Generate (grounded, with citations)
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the context. If insufficient, say you don't know.\n"
               "Cite sources as [source:chunk]."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])
context = "\n\n".join(f"[{d.metadata['source']}:{i}] {d.page_content}"
                      for i, d in enumerate(hits))
answer = (prompt | llm | StrOutputParser()).invoke(
    {"context": context, "question": query})
```

## Tuning table
| Symptom | Try |
| --- | --- |
| Answers miss obvious facts | bigger k, smaller chunks, hybrid BM25 |
| Answers vague/diluted | smaller k, bigger chunks, re-ranking |
| Cut-off sentences in context | increase overlap |
| Hallucinated details | stricter system prompt + grounding check |
| Exact terms (IDs, names) missed | hybrid keyword + vector search |

## Store choice
FAISS = in-process/ephemeral · Chroma = embedded persistent · pgvector = already-have-Postgres · managed (Pinecone/Qdrant) = scale/multi-tenant

## Remember
- Retrieval quality is the ceiling — evaluate it separately from generation.
- In-memory FAISS dies on serverless cold starts.
- Store embedding-model name with the index; re-embed when it changes.
