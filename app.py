import os
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# 1. Konfiguration & API-Schlüssel
API_KEY = "AQ.Ab8RN6Kw1nCpIWb9ZRWm4Ewx5hhoqJTdi0ZajNVQwUodCegA0w"
genai.configure(api_key=API_KEY)

# 2. Modell-Initialisierung mit festem System-Prompt für A1
SYSTEM_PROMPT = """
Du bist ein geduldiger, freundlicher Lernpartner für Deutschlernende auf dem Niveau A1 (Anfänger).
Deine Lernenden sind schulungewohnt.

Regeln für deine Antworten:
1. Verwende EXTREM einfache Sprache (A1-Niveau).
2. Schreibe nur sehr kurze Sätze (maximal 5-8 Wörter pro Satz).
3. Nutze viele passende Emojis, um das Verständnis zu unterstützen.
4. Stelle pro Antwort immer genau EINE einfache Frage oder gib EINE kurze Aufgabe.
5. Verwende KEINE schwierigen Grammatikstrukturen (kein Passiv, kein Konjunktiv).
6. Korrigiere Fehler der Lernenden sanft und auf Deutsch.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash"
    system_instruction=SYSTEM_PROMPT
)

# 3. Streamlit Page Layout (A1-freundlich & übersichtlich)
st.set_page_config(page_title="Deutsch Lernpartner A1", page_icon="💬", layout="centered")

st.title("💬 Deutsch lernen mit KI")
st.write("Wähle ein Thema und übe einfache Sätze!")

# Session State für Chatverlauf & Thema
if "messages" not in st.session_state:
    st.session_state.messages = []
if "topic_selected" not in st.session_state:
    st.session_state.topic_selected = False

# 4. Themenauswahl über große Buttons (Kein Tippen nötig)
if not st.session_state.topic_selected:
    st.subheader("📌 Wähle ein Thema:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🛒 Einkaufen", use_container_width=True):
            prompt = "Starten wir ein einfaches Gespräch zum Thema Einkaufen im Supermarkt auf A1-Niveau. Begrüße mich kurz."
            st.session_state.topic_selected = True
            
        if st.button("💼 Arbeit & Beruf", use_container_width=True):
            prompt = "Starten wir ein einfaches Gespräch zum Thema Arbeit auf A1-Niveau. Begrüße mich kurz."
            st.session_state.topic_selected = True

    with col2:
        if st.button("☕ Im Café / Restaurant", use_container_width=True):
            prompt = "Starten wir ein einfaches Gespräch im Café auf A1-Niveau. Begrüße mich kurz."
            st.session_state.topic_selected = True
            
        if st.button("👋 Sich vorstellen", use_container_width=True):
            prompt = "Starten wir eine einfache Übung zum Sich-Vorstellen auf A1-Niveau. Begrüße mich kurz."
            st.session_state.topic_selected = True

    if st.session_state.topic_selected:
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        st.session_state.messages.append({"role": "model", "content": response.text})
        st.rerun()

# 5. Chat-Schnittstelle
else:
    if st.button("🔄 Neues Thema wählen"):
        st.session_state.messages = []
        st.session_state.topic_selected = False
        st.rerun()

    st.divider()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            if msg["role"] == "model":
                try:
                    tts = gTTS(text=msg["content"], lang='de')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    st.audio(fp, format='audio/mp3')
                except Exception:
                    pass

    st.write("👉 **Schnell-Antworten (oder tippe unten):**")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    user_input = None
    with btn_col1:
        if st.button("Ja, gerne! 👍"):
            user_input = "Ja, gerne!"
    with btn_col2:
        if st.button("Ich verstehe nicht 🤔"):
            user_input = "Ich verstehe das nicht. Bitte noch einfacher."
    with btn_col3:
        if st.button("Noch einmal bitte 🔁"):
            user_input = "Bitte wiederhole das."

    chat_input = st.chat_input("Schreibe eine Antwort...")
    if chat_input:
        user_input = chat_input

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        formatted_history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(user_input)
        
        st.session_state.messages.append({"role": "model", "content": response.text})
        st.rerun()
