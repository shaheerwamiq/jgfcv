# Screenshot Mapping

Both source PDFs embed screenshots as raster images. Text extraction recovered the typed notes and captions, but **not the pixel contents of the screenshots themselves**. Below, every screenshot is mapped to its page, the surrounding note text, its inferred content, and where that concept lives in this repository.

> **Assumption flag:** rows marked *(inferred)* are educated inferences from the caption/surrounding notes, not verified image contents.

## Full_Stack.pdf (9 screenshots)

| # | Label | Surrounding notes | Inferred content | Used in this repo |
| --- | --- | --- | --- | --- |
| 1 | Full Stack1 | chat_history, chat_template, reusable message templates | *(inferred)* Code: `ChatPromptTemplate` + message history example | `src/memory/chat_history.py`, agent prompts |
| 2 | Full Stack2 | "Structured response" | *(inferred)* Code: structured output / `with_structured_output` demo | `src/chains/parsers.py` |
| 3 | Full Stack3 | StrOutputParser, chains, "output of one input to other" | *(inferred)* Code: `prompt \| model \| StrOutputParser()` | `src/chains/sequential.py` |
| 4 | Full Stack4 | PydanticOutputParser, "parser works based on schema" | *(inferred)* Code: Pydantic schema + parser format instructions | `src/chains/parsers.py` |
| 5 | Full Stack5 | Sequential + Conditional chains, RunnableBranch/RunnableLambda | *(inferred)* Code: branch on classification result | `src/chains/conditional.py` |
| 6 | Full Stack6 | Parallel chains, RunnableParallel | *(inferred)* Code: parallel branch dict | `src/chains/parallel.py` |
| 7 | Full Stack7 | HuggingFaceEmbeddings, cosine_similarity via sklearn | *(inferred)* Code: embed texts, compute similarity matrix | `src/llm/embeddings.py` (Gemini instead of HF — see KB 04) |
| 8 | Full Stack8 | RAG: TextLoader, RecursiveCharacterTextSplitter, FAISS, RetrievalQA | *(inferred)* Code: full RAG pipeline assembly | `src/rag/pipeline.py` |
| 9 | Full Stack9 | (end of document, no caption text) | *(inferred)* RAG continuation — retriever usage or QA output | `src/rag/pipeline.py` |

## AI_compressed.pdf (21 screenshots)

The first page lists the tool ecosystem (fully covered in `docs/knowledge-base/10-ecosystem-tooling.md`). Screenshots AI1–AI21 follow with no individual captions.

| # | Label | Inferred content | Assumption level |
| --- | --- | --- | --- |
| 1–21 | AI1 … AI21 | *(inferred)* Screenshots of tool websites/docs/code for the listed ecosystem: pypdf, pymupdf, chromadb, faiss-cpu, sentence-transformers, pageindex.ai, deepagents, tavily, uv, guardrails, litellm, Valkey, fastmcp, nemoguardrails/Colang, logfire, langsmith, langchain/langgraph, pydantic | High — no caption text per image; mapping is by the page-1 tool list order |

## What could be improved in the source notes
1. Caption each screenshot with the tool/concept name so notes survive text extraction.
2. Include the code from screenshots as text (copy-paste, not images) — searchable and runnable.
3. Fix typos that break imports if copied (`langchain_hugginface` → `langchain_huggingface`, `RetrivalQA` → `RetrievalQA`, `impirt` → `import`, `FIAS` → `FAISS`).
4. Note versions: LangChain moves fast; `from langchain.output_parser import ...` paths have since moved to `langchain_core.output_parsers`.
