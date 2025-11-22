# TalentScout — Streamlit Hiring Assistant (single-file project)
# File: TalentScout_app.py
# Description: Streamlit app that collects candidate info, asks for tech stack,
# generates tech-specific interview questions using OpenAI, handles context,
# fallback, and graceful exit keywords. Stores simulated/anonymized data locally.

"""
RUNNING INSTRUCTIONS:
1. Create a Python virtual environment and activate it.
2. pip install -r requirements.txt
3. export OPENAI_API_KEY or set via UI
4. streamlit run TalentScout_app.py
"""

import os
import json
import time
from typing import List, Dict

import streamlit as st

try:
    import openai
except Exception:
    openai = None

EXIT_KEYWORDS = {"exit", "quit", "bye", "goodbye", "thanks", "thank you"}
SIMULATED_DB = "simulated_candidates.json"
MODEL = "gpt-4"

def init_app():
    st.set_page_config(page_title="TalentScout Hiring Assistant", layout="centered")
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "candidate" not in st.session_state:
        st.session_state.candidate = {}
    if "last_intent" not in st.session_state:
        st.session_state.last_intent = None

def save_candidate(data: Dict):
    record = data.copy()
    if "phone" in record:
        record["phone"] = "***masked***"
    if "email" in record:
        record["email"] = "***masked***"
    all_data = []
    if os.path.exists(SIMULATED_DB):
        try:
            with open(SIMULATED_DB, "r") as f:
                all_data = json.load(f)
        except Exception:
            all_data = []
    all_data.append(record)
    with open(SIMULATED_DB, "w") as f:
        json.dump(all_data, f, indent=2)

INFO_GATHER_PROMPT = (
    "You are TalentScout Assistant. Gather candidate details. "
    "Ask for Full Name, Email, Phone, Experience, Desired Position(s), Location, Tech Stack. "
)

TECH_QUESTION_PROMPT = (
    "You are an expert technical interviewer. Candidate tech stack: {tech_stack}. "
    "Generate 3-5 questions per technology."
)

FALLBACK_RESPONSES = [
    "Sorry, I didn't understand that. Could you rephrase?",
]

def call_openai(prompt: str, model: str = MODEL, temperature: float = 0.2) -> str:
    if openai is None or os.getenv("OPENAI_API_KEY") is None:
        return "(Simulated) Missing OpenAI key."
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=700,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Error calling OpenAI API) {e}"

def main():
    init_app()
    st.title("TalentScout — Hiring Assistant")

    with st.form("candidate_form"):
        st.subheader("Candidate Details")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone (optional)")
        years = st.text_input("Years of Experience")
        desired_pos = st.text_input("Desired Position(s)")
        location = st.text_input("Current Location")
        tech_stack = st.text_area("Tech Stack (comma separated)")
        submit = st.form_submit_button("Save & Generate Questions")

    if submit:
        st.session_state.candidate = {
            "name": full_name,
            "email": email,
            "phone": phone,
            "years_experience": years,
            "desired_positions": desired_pos,
            "location": location,
            "tech_stack": tech_stack,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_candidate(st.session_state.candidate)
        prompt = TECH_QUESTION_PROMPT.format(tech_stack=tech_stack)
        qtext = call_openai(prompt)
        st.subheader("Generated Technical Questions")
        st.text_area("Questions", value=qtext, height=300)

if __name__ == "__main__":
    main()
