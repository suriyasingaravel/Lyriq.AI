# app.py
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="🎤Lyriq.AI",
    page_icon="🎶",
    layout="centered",
)

st.title("🎤 Lyriq.AI")
st.markdown(
    """
Upload an audio file (MP3, WAV, M4A, etc.) and I'll use Whisper to transcribe it.  
If it's a song, the transcript will show you the lyrics!
"""
)

# —– Load API key —–
# In Streamlit Cloud, put this in .streamlit/secrets.toml:
# OPENAI_API_KEY = "sk-..."
api_key = st.secrets["OPENAI_API_KEY"]
if not api_key:
    st.error("🚨 OpenAI API key not found. Set OPENAI_API_KEY in your environment or in Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# —– File uploader —–
audio_file = st.file_uploader(
    "Upload your audio file",
    type=["mp3", "wav", "m4a", "flac", "ogg"],
    accept_multiple_files=False,
)

if audio_file:
    # Preview player
    st.audio(audio_file, format=audio_file.type)
    
    # Transcription
    if st.button("Transcribe & Format Lyrics"):
        with st.spinner("Transcribing… this can take a minute or two for long files"):
            try:
                # Whisper transcription
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            except Exception as e:
                st.error(f"❌ Transcription error: {e}")
                st.stop()
        
        # Optionally, reformat with GPT to add line breaks as lyrics
        with st.spinner("Formatting as lyrics…"):
            try:
                chat_resp = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that formats plain text as song lyrics, adding appropriate line breaks."
                        },
                        {
                            "role": "user",
                            "content": f"Format the following transcript as lyrics:\n\n{transcript}"
                        }
                    ],
                    temperature=0.5,
                )
                lyrics = chat_resp.choices[0].message.content.strip()
            except Exception:
                # Fallback to raw transcript if GPT formatting fails
                lyrics = transcript
        
        # Display results
        st.subheader("📝 Formatted Lyrics")
        st.text_area("Here are your lyrics:", lyrics, height=300)
        st.success("Done!")
