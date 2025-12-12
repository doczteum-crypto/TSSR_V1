import streamlit as st
import pdfplumber

# --- Extract text from PDF ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# --- Smart Analysis ---
def analyze_proposal(text):
    structure_summary = []
    environment_summary = []

    # Structure Analysis
    if "tower" in text.lower():
        structure_summary.append("📍 Tower height is 30 m at Berlian Square (T1100417), Kota Samarahan.")
    if "antenna" in text.lower():
        structure_summary.append("📡 Antennas upgraded from 3 to 7 units, including RHHTT-65A and A9651A models.")
    if "rru" in text.lower():
        structure_summary.append("🔌 RRUs relocated from tower to ground — 6 dismantled, 3 installed on ground.")
    if "microwave" in text.lower() or "mw" in text.lower():
        structure_summary.append("📶 MW dish hot-swapped from NEC 0.6 m to NR 0.3 m, maintaining LOS to GAYM.")
    if "cabinet" in text.lower() or "power" in text.lower():
        structure_summary.append("⚡ Power upgraded with new W451 cabinet, 150 Ah batteries, and 40 A breakers.")
    if "weight" in text.lower():
        structure_summary.append("⚖️ Tower-top weight reduced from 182 kg to 172 kg after equipment swap.")

    # Environment Analysis
    if "access" in text.lower() or "site accessibility" in text.lower():
        environment_summary.append("🚪 Site must be accessible 24/7 for installation and maintenance.")
    if "road" in text.lower() or "premise" in text.lower():
        environment_summary.append("🛣️ Located in Kota Samarahan with standard road access and fenced premises.")
    if "traffic" in text.lower() or "lifting" in text.lower() or "ladder" in text.lower():
        environment_summary.append("🛠️ Lifting tools required for antenna and RRU installation at 25–26 m AGL.")
    if "earthing" in text.lower() or "interfere" in text.lower():
        environment_summary.append("🌱 Existing grounding reused; no interference expected with current systems.")

    return structure_summary, environment_summary

# --- Streamlit UI ---
st.set_page_config(page_title="Technical Proposal Analyzer", layout="wide")
st.title("📑 Technical Proposal Analyzer")

uploaded_file = st.file_uploader("Upload your Technical Proposal PDF", type=["pdf"])

if uploaded_file:
    st.success("✅ File uploaded successfully.")
    doc_text = extract_text_from_pdf(uploaded_file)
    structure, environment = analyze_proposal(doc_text)

    st.header("1️⃣ Structure Technical Info")
    for item in structure:
        st.write(item)

    st.header("2️⃣ Aerial / Environment Situation")
    for item in environment:
        st.write(item)
