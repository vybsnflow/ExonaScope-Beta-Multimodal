
import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from openai import OpenAI
import os

st.set_page_config(page_title="ExonaScope Minimal – PDF/DOCX to Fact Pattern", layout="centered")
st.title("📄 ExonaScope Minimal Beta")

st.markdown("""
Upload a **single PDF or DOCX** to extract factual content and generate a neutral, chronological fact pattern.

This is a **minimal version** for debugging and verifying end-to-end functionality.

- ✅ PDF and DOCX supported
- ✅ Raw text preview
- ✅ GPT-3.5-turbo summary
""")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

uploaded_file = st.file_uploader("Upload a single PDF or DOCX", type=["pdf", "docx"])

def parse_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def parse_docx(file):
    return "\n".join([p.text for p in Document(file).paragraphs])

parsed_text = ""

if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name}")
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext == ".pdf":
        parsed_text = parse_pdf(uploaded_file)
    elif ext == ".docx":
        parsed_text = parse_docx(uploaded_file)
    else:
        st.error("Unsupported file type.")
        st.stop()

    if parsed_text.strip():
        st.subheader("📄 Extracted Text")
        st.text_area("Preview (first 1000 chars)", parsed_text[:1000], height=200)
    else:
        st.warning("⚠️ No extractable text found in this document.")

if parsed_text and st.button("🧠 Generate Fact Pattern"):
    with st.spinner("Calling GPT-3.5..."):
        prompt = f"""You are a legal assistant. Based only on the factual content below, write a chronological, paragraph-based fact pattern suitable for a suppression motion. Do not invent facts. Do not summarize conclusions.

DOCUMENT CONTENT:
{parsed_text}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You generate legally neutral fact patterns."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            result = response.choices[0].message.content.strip()
            st.subheader("📑 Generated Fact Pattern")
            st.text_area("Fact Pattern", value=result, height=300)
            st.download_button("💾 Download Fact Pattern (.txt)", result.encode(), file_name="fact_pattern.txt")
        except Exception as e:
            st.error(f"❌ GPT Error: {e}")
