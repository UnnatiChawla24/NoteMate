# 📄 NoteMate — RAG Based PDF Q&A and Summarization App

NoteMate is a Retrieval Augmented Generation (RAG) based web application that allows users to upload any PDF document and either ask questions about it or get a complete summary — all powered by GPT-3.5-turbo.

---

## 🚀 Features

- **PDF Q&A** — Upload any PDF and ask questions. Get accurate answers strictly based on the PDF content
- **PDF Summarization** — Get a complete bullet point summary of the entire PDF
- **OCR Support** — Handles scanned PDFs with no selectable text using Pytesseract
- **Downloadable Summary** — Download the generated summary as a TXT or PDF file
- **Text to Speech** — Listen to answers and summaries using the browser's built in Web Speech API
- **Answer Caching** — Repeated questions are answered instantly without extra API calls
- **Login System** — Basic username and password authentication
- **Multiple UI Themes** — Choose from 5 themes: Classic Light, Classic Dark, Midnight Neon, Desert Sand, Ocean Breeze
- **Documentation** — Full project documentation hosted on Netlify

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend / UI | Streamlit |
| LLM | OpenAI GPT-3.5-turbo |
| Embeddings | OpenAI Embeddings |
| Vector Database | FAISS (Facebook AI Similarity Search) |
| RAG Framework | LangChain |
| PDF Text Extraction | PyPDF2 |
| OCR (Scanned PDFs) | Pytesseract + pdf2image |
| PDF Generation | ReportLab |
| Text to Speech | Browser Web Speech Synthesis API |

---

## 🧠 How It Works — RAG Pipeline

```
User uploads PDF
       ↓
Check if PDF has selectable text
       ↓
  Yes → PyPDF2 extracts text
  No  → OCR via Pytesseract extracts text
       ↓
Text split into chunks (size=300, overlap=50)
using RecursiveCharacterTextSplitter
       ↓
Each chunk converted into embedding vector
using OpenAI Embeddings
       ↓
Embedding vectors stored in FAISS vector store
       ↓
User types a question
       ↓
Question converted into embedding vector
       ↓
Similarity search performed against FAISS
       ↓
Top relevant chunks retrieved
       ↓
Retrieved chunks + user query sent to GPT-3.5-turbo
via a strict prompt template
       ↓
Final answer generated and displayed to user ✅
```

---

## 📝 Summarization — Refine Chain

For summarization, LangChain's **refine chain** is used. Since GPT-3.5-turbo has a maximum token limit, the entire PDF cannot be sent at once. The refine chain processes chunks one by one:

1. First chunk → LLM generates initial summary
2. Second chunk + existing summary → LLM updates the summary
3. Third chunk + updated summary → LLM refines further
4. This continues for every chunk until all chunks are processed

The result is one complete, coherent, non-repetitive summary covering the entire PDF. ✅

---

## ⚡ Smart Caching with Session State

To avoid repeated expensive API calls, the following are cached in Streamlit session state:

| Cached Data | Benefit |
|---|---|
| Extracted PDF text | Avoids re-running PyPDF2 or OCR |
| PDF chunks | Avoids re-chunking on every interaction |
| FAISS vector store | Avoids repeated OpenAI Embedding API calls |
| Per-question answers | Same question answered instantly without API call |
| PDF summary | Avoids re-running entire summarization chain |

---

## 🔧 How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/UnnatiChawla24/NoteMate.git
cd NoteMate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Install Tesseract OCR** (for scanned PDF support)
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Update the path in `main.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**4. Install Poppler** (for pdf2image)
- Download from: https://github.com/oschwartz10612/poppler-windows/releases
- Update the path in `main.py`:
```python
poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"
```

**5. Add your OpenAI API Key**

Create a `.streamlit/secrets.toml` file:
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

**6. Run the app**
```bash
streamlit run main.py
```

---

## ⚠️ Known Limitations and Future Improvements

This project implements **Naive RAG.** The following improvements are planned for version 2:

- **Hybrid Search** — Combine semantic search with keyword search for better retrieval accuracy especially for exact identifiers like product codes
- **Reranking** — Add a reranker model to rescore and filter retrieved chunks for higher precision
- **Query Rewriting** — Add an LLM based query rewriting step to handle vague or poorly written user queries
- **RAGAS Evaluation** — Integrate RAGAS framework to automatically evaluate pipeline performance using metrics like faithfulness, answer relevancy, context precision, and context recall
- **Multi-format Support** — Extend support beyond PDFs to Word documents, Excel files, and plain text files
- **MMR Retrieval** — Implement Maximal Marginal Relevance to avoid retrieving redundant chunks

---

## 📁 Project Structure

```
NoteMate/
│
├── main.py              # Core RAG pipeline and Streamlit UI
├── audio_helpers.py     # Text to speech using Web Speech API
├── pdf_analyzer.py      # Detects if PDF has selectable text
├── pdf_generator.py     # Generates downloadable PDF summary using ReportLab
├── themess.py           # UI theme definitions and application
├── requirements.txt     # Project dependencies
├── favicon.ico          # App favicon
├── .gitignore           # Git ignore rules
└── Documentations/
    └── index.html       # Project documentation page
```

---

## 👩‍💻 Author

**Unnati Chawla**
BSc Computer Science Graduate
[GitHub](https://github.com/UnnatiChawla24)
