import streamlit as st
import tempfile
import os
from google import genai
from google.genai import types

st.set_page_config(page_title="Golf Biomechanics Analyzer", layout="wide")

st.title("⛳ Golf Biomechanics & 16-Position Swing Analyzer")
st.write("Carica i due video dello swing e inserisci i timestamp di Partenza (P1) e Impatto (P7).")

# Recupera la chiave API in modo sicuro dalle impostazioni di Streamlit
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Trovata nessuna API Key! Inserisci GEMINI_API_KEY nei Secrets di Streamlit Cloud.")
    st.stop()

client = genai.Client(api_key=api_key)

# Interfaccia a 2 Colonne per i Video
col1, col2 = st.columns(2)

with col1:
    st.subheader("📹 1. Vista Frontale (Face-On)")
    video_front = st.file_uploader("Carica Video Frontale (MP4/MOV)", type=["mp4", "mov"], key="front")
    p1_front = st.text_input("Inizio Swing (P1) - Frontale", "00:01.0")
    p7_front = st.text_input("Impatto (P7) - Frontale", "00:02.0")

with col2:
    st.subheader("📹 2. Vista da Dietro (Down-The-Line)")
    video_dtl = st.file_uploader("Carica Video DTL (MP4/MOV)", type=["mp4", "mov"], key="dtl")
    p1_dtl = st.text_input("Inizio Swing (P1) - DTL", "00:01.0")
    p7_dtl = st.text_input("Impatto (P7) - DTL", "00:02.0")

if st.button("🚀 Avvia Analisi Biomeccanica TPI", type="primary"):
    if not video_front or not video_dtl:
        st.warning("Carica entrambi i video prima di avviare l'analisi.")
    else:
        with st.spinner("⏳ Caricamento dei video ed elaborazione dell'analisi in corso (circa 30-45 secondi)..."):
            try:
                # Salvataggio temporaneo per upload
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f_front:
                    f_front.write(video_front.read())
                    front_path = f_front.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f_dtl:
                    f_dtl.write(video_dtl.read())
                    dtl_path = f_dtl.name

                # Upload dei video all'API di Gemini
                file_front = client.files.upload(file=front_path)
                file_dtl = client.files.upload(file=dtl_path)

                system_instruction = """
                SEI UN ASSISTENTE SPECIALIZZATO IN ANALISI BIOMECCANICA DELLO SWING DA GOLF (PGA & TPI CERTIFIED LEVEL 3).
                APPLICA RIGOROSAMENTE LA MATRICE A 16 POSIZIONI (8 FACE-ON E 8 DTL).
                Calcola automaticamente i fotogrammi P2, P3, P4, P5, P6, P8 basandoti sui tempi P1 e P7 forniti.
                Applica la catena causale TPI (Limite corporeo -> Compenso -> Impatto -> Volo di palla).
                NON confrontare con i giocatori del PGA Tour.
                """

                prompt = f"""
                Analizza i due video allegati dello swing:
                - Video 1 (Face-On): P1 = {p1_front}, P7 = {p7_front}
                - Video 2 (DTL): P1 = {p1_dtl}, P7 = {p7_dtl}

                Esegui il calcolo dei 16 timestamp e restituisci la diagnosi completa.
                """

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[file_front, file_dtl, prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )

                st.success("✅ Analisi completata!")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Si è verificato un errore: {e}")
