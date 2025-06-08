
# ExonaScope Beta (Multimodal Legal Fact Extractor)

This Streamlit app lets defense attorneys and investigators:
- Upload documents (PDF, DOCX), audio (MP3/WAV), and video (MP4/MOV)
- Automatically parse or transcribe them
- Generate a neutral fact pattern for legal motion preparation

## Deployment

1. Upload to GitHub
2. Deploy with Streamlit Cloud
3. Add your OpenAI API key under Secrets:
   OPENAI_API_KEY = "sk-..."

## Notes

- Uses Whisper API for transcription
- Supports GPT-3.5 for fact pattern generation
