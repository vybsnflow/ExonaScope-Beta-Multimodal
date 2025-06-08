
import streamlit as st
import fitz  # PyMuPDF
import docx
import tempfile
import os
from openai import OpenAI

st.set_page_config(page_title="ExonaScope Beta – Multi-File Fact Extractor", layout="wide")
st.title("📂 ExonaScope – Upload & Extract Facts")

st.markdown("""
Upload case documents or surveillance audio. ExonaScope will extract facts in chronological order and prepare them for suppression analysis.

Supported formats:
- 📄 PDF, DOCX
- 🎧 MP3, WAV
""")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
raw_facts = []

uploaded_files = st.file_uploader("📎 Upload case materials", accept_multiple_files=True,
                                  type=["pdf", "docx", "mp3", "wav"])

def parse_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def parse_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def transcribe_audio(file, suffix):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    with open(tmp_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    os.remove(tmp_path)
    return transcript.text

if uploaded_files:
    st.subheader("📄 File Analysis & Transcription Preview")
    for file in uploaded_files:
        ext = os.path.splitext(file.name)[1].lower()
        st.write(f"Detected file: {file.name} ({ext})")
        try:
            if ext == ".pdf":
                parsed = parse_pdf(file)
            elif ext == ".docx":
                parsed = parse_docx(file)
            elif ext in [".mp3", ".wav"]:
                parsed = transcribe_audio(file, ext)
            else:
                parsed = "[Unsupported file type]"

            if parsed.strip():
                st.success(f"✅ Processed: {file.name}")
                st.write("🔎 Raw parsed preview:", parsed[:300])
                with st.expander(f"Preview: {file.name}"):
                    st.text(parsed[:2000])
                raw_facts.append(f"[{file.name}]\n{parsed}")
            else:
                st.warning(f"⚠️ No usable content found in: {file.name}")
        except Exception as e:
            st.error(f"❌ Error processing {file.name}: {e}")

if raw_facts and st.button("🔍 Generate Chronological Fact Pattern"):
    full_text = "\n\n".join(raw_facts)
    with st.spinner("Generating fact pattern..."):
        prompt = f"""You are a legal assistant. Based only on the factual information below (extracted from police reports, affidavits, and interviews), generate a neutral, strictly chronological, paragraph-based fact pattern. DO NOT infer facts or invent content. Label unclear details as (Unclear). Do NOT include legal conclusions.

SOURCE MATERIAL:
{full_text}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You generate legally neutral fact patterns for defense attorneys."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            result = response.choices[0].message.content.strip()
            st.session_state["fact_pattern"] = result
            st.success("✅ Fact pattern generated.")
        except Exception as e:
            st.error(f"❌ GPT Error: {e}")

if "fact_pattern" in st.session_state:
    st.subheader("📑 Generated Fact Pattern")
    st.text_area("You can copy this into your suppression analysis", value=st.session_state["fact_pattern"], height=300)
    st.download_button("💾 Download Fact Pattern (.txt)", st.session_state["fact_pattern"].encode(), file_name="fact_pattern.txt")
