import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Fix for potential library conflicts on some systems

import time
import streamlit as st

# Import LangChain components for document processing and LLM interaction
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain

# Import local modules
from themess import themes, apply_theme
from pdf_generator import create_pdf
from audio_helpers import speech_work
from pdf_analyzer import pdf_contains_text

# OCR dependencies for scanned PDFs
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Path to tesseract executable
poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"  # Path to poppler bin for PDF page conversion

import tempfile
from PyPDF2 import PdfReader
import re

# Load OpenAI API key securely from Streamlit secrets
OpenAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Set page configuration for Streamlit app
st.set_page_config(
    page_title="NoteMate",
    page_icon="favicon.ico",
    layout="centered"
)

# Initialize session state variables if not already present
if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = {}

if "pdf_chunks" not in st.session_state:
    st.session_state["pdf_chunks"] = {}

if "summary" not in st.session_state:
    st.session_state["summary"] = {}

if "pdf_text" not in st.session_state:
    st.session_state["pdf_text"] = {}

if "entity_groups" not in st.session_state:
    st.session_state["entity_groups"] = {}

if "summary_shown" not in st.session_state:
    st.session_state["summary_shown"] = False

if "sum_download_txt" not in st.session_state:
    st.session_state["sum_download_txt"] = False

if "sum_download_pdf" not in st.session_state:
    st.session_state["sum_download_pdf"] = False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# Helper functions to toggle download flags
def func_pdf():
    st.session_state["sum_download_pdf"] = True


def func_txt():
    st.session_state["sum_download_txt"] = True


# Simple user authentication dictionary
users = {
    "Unnati": "admin1",
    "admin": "admin2"
}

# Login form UI and logic
if not st.session_state["logged_in"]:
    with st.form("login_form"):
        st.subheader("🔒 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password ❌")

# Main app interface after successful login
else:
    st.title("RAG BOT")

    with st.sidebar:
        st.title("Sidebar")
        # Theme selection dropdown from predefined themes
        theme_option = st.selectbox("Select a theme", list(themes.keys()))
        # PDF file uploader in sidebar
        file = st.file_uploader("PDF Uploader", type="pdf")

        # FAQ and help section in expandable sidebar
        st.markdown("## Help & FAQ")
        with st.expander("Frequently Asked Questions"):
            st.markdown("""
                   **Q1:** How do I upload a PDF?  
                   *Click the upload button at the top of the sidebar.*

                   **Q2:** How do I ask questions?  
                   *Type your question in the input box once PDF is uploaded.*

                   **Q3:** Can I listen to summaries?  
                   *Yes, click the 'Read Me' button below the summary.*

                   📘 **Full Documentation:**  
                   <a href=" https://tourmaline-syrniki-880c58.netlify.app" target="_blank" style="text-decoration: underline;">
                   Click here to view</a>
                   """, unsafe_allow_html=True)

        # Logout button in sidebar
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

    # Apply the selected theme to the app UI
    selected_theme = themes[theme_option]
    apply_theme(selected_theme)

    # Handle uploaded PDF file processing
    if file is not None:
        filename = file.name
        file.seek(0)

        # Save uploaded file temporarily for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name

        # Check if PDF has selectable text, else apply OCR
        if not pdf_contains_text(tmp_path):
            if filename not in st.session_state["pdf_text"]:
                with st.spinner("Running OCR on PDF pages...🤖📄"):
                    pages = convert_from_path(tmp_path, poppler_path=poppler_path)
                    full_text = ""
                    for page_image in pages:
                        text = pytesseract.image_to_string(page_image)
                        cleaned_text = ' '.join(text.split())
                        full_text += cleaned_text + "\n"

                    st.session_state["pdf_text"][filename] = full_text
                    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50, length_function=len)
                    chunks = splitter.split_text(full_text)
                    if filename not in st.session_state["pdf_chunks"]:
                        st.session_state["pdf_chunks"][filename] = chunks

                    embeddings = OpenAIEmbeddings(api_key=OpenAI_API_KEY)
                    vector_store = FAISS.from_texts(chunks, embeddings)

        # If new file or not already processed, process normally for selectable text PDFs
        if filename not in st.session_state["uploaded_file_name"]:
            if "current_file" not in st.session_state:
                st.session_state["current_file"] = filename
                st.session_state["user_query"] = {}
            else:
                st.session_state["current_file"] = filename
                st.session_state["user_query"] = {}

            if filename not in st.session_state["pdf_text"]:
                with st.spinner("Processing your new PDF... ⏳ Please wait!"):
                    file.seek(0)
                    my_pdf = PdfReader(file)
                    text = ""
                    for page in my_pdf.pages:
                        text += page.extract_text()

                    st.session_state["pdf_text"][filename] = text
                    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50, length_function=len)
                    chunks = splitter.split_text(text)

                    if filename not in st.session_state["pdf_chunks"]:
                        st.session_state["pdf_chunks"][filename] = chunks

                    embeddings = OpenAIEmbeddings(api_key=OpenAI_API_KEY)
                    vector_store = FAISS.from_texts(chunks, embeddings)

            st.session_state["uploaded_file_name"][filename] = vector_store
            st.session_state["vector_store_ready"] = True
        else:
            # Use cached vector store if file already processed
            if filename != st.session_state["current_file"]:
                st.session_state["current_file"] = filename
                st.session_state["user_query"] = {}
            vector_store = st.session_state["uploaded_file_name"][filename]
            st.session_state["vector_store_ready"] = True

        # Layout: query input and summarize button side by side
        col1, col2 = st.columns([4, 1])
        with col1:
            user_query = st.text_input("Type your query here")
        with col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)  # Spacer
            summarize_button = st.button("Summarize PDF")

        placeholder = st.empty()  # Placeholder to display answers or summaries
        speech = ""

        # Show summary when summarize button clicked
        if summarize_button:
            st.session_state["summary_shown"] = True

        # Handle user query if typed
        elif user_query and user_query.strip():
            st.session_state["summary_shown"] = False
            normalized_query = user_query.lower().strip()
            normalized_query = re.sub(r"\s+", " ", normalized_query)  # Normalize whitespace

            vector_store = st.session_state["uploaded_file_name"][filename]

            # If answer not cached, perform similarity search and generate answer
            if normalized_query not in st.session_state["user_query"]:
                with st.spinner("Thinking... 🤔 Please wait!"):
                    matching_chunks = vector_store.similarity_search(user_query)
                    llm = ChatOpenAI(
                        api_key=OpenAI_API_KEY,
                        max_tokens=400,
                        temperature=0.5,
                        model="gpt-3.5-turbo"
                    )

                    # Prompt template ensuring answer is strictly based on PDF content
                    customized_prompt = ChatPromptTemplate.from_template(
                        """ You are an AI assistant designed to answer **only based on the context provided** from a PDF file.

When the context contains the necessary information to answer the user's question, provide a **detailed, comprehensive, and clear answer** in full sentences. Make sure the answer is informative and as complete as possible, without adding any information outside the given context.

If the context does **not contain clear information** to answer the user's question, strictly reply with:

> "The information required to answer your question does not appear to be available in the uploaded PDF. Please try rephrasing your query or check the PDF content."

DO NOT:
- Answer from general knowledge.
- Assume or guess anything outside the provided context.
- Give short or incomplete answers when the information is available.:
{context}
Question:  {input}
                        """
                    )

                    # Create and invoke the LangChain chain to get the answer
                    chain = create_stuff_documents_chain(llm, customized_prompt)
                    output = chain.invoke({"input": user_query, "context": matching_chunks})

                # Cache the output for repeated queries
                st.session_state["user_query"][normalized_query] = output
            else:
                with st.spinner("Fetching cached answer...🧠"):
                    time.sleep(2)
                    output = st.session_state["user_query"][normalized_query]

            # Display the answer with text-to-speech option
            with placeholder.container():
                st.markdown(output)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    "<b style='font-size:20px; font-weight:bold'>🗣️ Need to listen instead of read? Just click 'Read Me' to play the audio version of the text:</b>",
                    unsafe_allow_html=True
                )
                speech = st.session_state["user_query"][normalized_query]
                speech_work(speech)

        # Show summary section if summary flag is set
        if st.session_state["summary_shown"]:
            # If neither download button has been clicked yet, generate or fetch summary
            if not st.session_state["sum_download_txt"] and not st.session_state["sum_download_pdf"]:
                if filename not in st.session_state["summary"]:
                    with st.spinner("Summarizing your PDF📝✂️ ... Please wait!"):
                        llm = ChatOpenAI(
                            api_key=OpenAI_API_KEY,
                            model="gpt-3.5-turbo",
                            temperature=0.5,
                            max_tokens=500
                        )

                        # Initial prompt for bullet point summary
                        INITIAL_PROMPT = PromptTemplate.from_template(
                            """You are a helpful assistant. Summarize the following text into clear bullet points, ensuring you include all important topics and key points, even if they appeared earlier in the document.
{text}
Bullet point summary covering all key ideas:
"""
                        )

                        # Refine prompt to add missing key points without repetition
                        REFINED_PROMPT = PromptTemplate.from_template(
                            """You have an existing summary in bullet points:
{existing_answer}
Add any missing important points from the new text below. Make sure the final summary covers **all** key topics from the entire document. Do not repeat points.
New text:
{text}
Updated bullet point summary:"""
                        )

                        # Create summarization chain with refinement
                        chain = load_summarize_chain(llm, chain_type="refine", question_prompt=INITIAL_PROMPT,
                                                     refine_prompt=REFINED_PROMPT)
                        chunks = st.session_state["pdf_chunks"][filename]
                        docs = [Document(page_content=chunk) for chunk in chunks]
                        summary = chain.run(docs)

                        # Cache the summary
                        st.session_state["summary"][filename] = summary
                else:
                    with st.spinner("Fetching cached summary...🧠"):
                        time.sleep(2)
                        summary = st.session_state["summary"][filename]

                # Display summary and provide download options + text-to-speech
                with placeholder.container():
                    st.markdown(summary)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        "<b style='font-size:20px; font-weight:bold'>⬇️ Click below to download the summary as a TXT file:</b>",
                        unsafe_allow_html=True
                    )
                    st.download_button(
                        label="Download Summary as TXT file",
                        data=summary,
                        file_name="summary.txt",
                        mime="text/plain",
                        on_click=func_txt
                    )

                    pdf_file = create_pdf(summary)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        "<b style='font-size:20px; font-weight:bold'>⬇️ Click below to download the summary as a PDF file:</b>",
                        unsafe_allow_html=True
                    )
                    st.download_button(
                        label="Download Summary as PDF file",
                        data=pdf_file,
                        file_name="summary.pdf",
                        mime="application/pdf",
                        on_click=func_pdf
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        "<b style='font-size:20px; font-weight:bold'>🗣️ Need to listen instead of read? Just click 'Read Me' to play the audio version of the text:</b>",
                        unsafe_allow_html=True
                    )
                    speech = st.session_state["summary"][filename]
                    speech_work(speech)
            else:
                # If a download button was clicked, just show cached summary again with downloads
                summary = st.session_state["summary"][filename]
                with placeholder.container():
                    st.markdown(summary)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        "<b style='font-size:20px; font-weight:bold'>⬇️ Click below to download the summary as a TXT file:</b>",
                        unsafe_allow_html=True
                    )
                    st.download_button(
                        label="Download Summary as TXT file",
                        data=summary,
                        file_name="summary.txt",
                        mime="text/plain",
                        on_click=func_txt
                    )

                    pdf_file = create_pdf(summary)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        "<b style='font-size:20px; font-weight:bold'>⬇️ Click below to download the summary as a PDF file:</b>",
                        unsafe_allow_html=True
                    )
                    st.download_button(
                        label="Download Summary as PDF file",
                        data=pdf_file,
                        file_name="summary.pdf",
                        mime="application/pdf",
                        on_click=func_pdf
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        "<b style='font-size:20px; font-weight:bold'>🗣️ Need to listen instead of read? Just click 'Read Me' to play the audio version of the text:</b>",
                        unsafe_allow_html=True
                    )
                    speech = st.session_state["summary"][filename]
                    speech_work(speech)

                # Reset download flags after displaying summary again
                st.session_state["sum_download_txt"] = False
                st.session_state["sum_download_pdf"] = False

    else:
        st.session_state["summary_shown"] = False  # Reset summary shown flag when no file is uploaded
