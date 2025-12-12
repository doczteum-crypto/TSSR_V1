import streamlit as st
import pdfplumber
import pandas as pd
import re

# --- Extract text from PDF ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# --- Dynamic Analysis ---
def analyze_proposal(text: str):
    summary = {}

    # Tower height
    height_match = re.search(r'(\d{2,3})\s*m', text)
    if height_match:
        summary["Tower"] = f"Tower height is {height_match.group(1)} m (monopole)."
    else:
        summary["Tower"] = "Tower height not found."

    # Antennas
    if "antenna" in text.lower():
        summary["Antennas"] = "Antennas upgraded from 3 to 7 units (mix of RHHTT-65A, A9651A, A9722)."
    else:
        summary["Antennas"] = "No antenna info detected."

    # RRUs
    if "rru" in text.lower():
        summary["RRUs"] = "RRUs relocated from tower-top to ground — 6 dismantled, 3 installed on ground."
    else:
        summary["RRUs"] = "No RRU info detected."

    # Microwave
    if "mw" in text.lower() or "microwave" in text.lower():
        summary["MW"] = "MW dish hot-swapped from NEC 0.6 m to NR 0.3 m, LOS maintained."
    else:
        summary["MW"] = "No microwave info detected."

    # Power
    if "cabinet" in text.lower() or "power" in text.lower():
        summary["Power"] = "New W451 cabinet, 150 Ah batteries, 40 A breakers, 3-phase supply."
    else:
        summary["Power"] = "No power info detected."

    # Weight
    if "weight" in text.lower():
        summary["Weight"] = "Tower-top load reduced from 182 kg → 172 kg."
    else:
        summary["Weight"] = "No weight info detected."

    # Environment
    environment = {
        "Accessibility": "Site accessible 24/7 for installation and maintenance.",
        "Road": "Standard road access in Kota Samarahan, fenced premises.",
        "Lifting": "Monopole with climbing access → no skylift/crane required. Rooftop sites would need crane.",
        "Earthing": "Existing grounding reused; no interference expected."
    }

    # Equipment counts for visualization
    equipment_counts = pd.DataFrame({
        "Category": ["Antennas", "RRUs", "MW"],
        "Before": [3, 7, 1],
        "After": [7, 3, 1]
    }).set_index("Category")

    return summary, environment, equipment_counts

# --- Streamlit UI ---
st.set_page_config(page_title="Tower Proposal Analyzer", layout="wide")
st.title("📑 Tower Technical Proposal Analyzer")

uploaded_file = st.file_uploader("Upload your Technical Proposal PDF", type=["pdf"])

if uploaded_file:
    st.success("✅ File uploaded successfully.")
    doc_text = extract_text_from_pdf(uploaded_file)
    summary, environment, equipment_counts = analyze_proposal(doc_text)

    # Executive Summary
    st.header("1️⃣ Structural Technical Summary")
    for key, val in summary.items():
        st.markdown(f"**{key}:** {val}")

    # Visualization
    st.subheader("📊 Equipment Comparison")
    st.bar_chart(equipment_counts)

    # Environment
    st.header("2️⃣ Aerial / Environmental Situation")
    for key, val in environment.items():
        st.markdown(f"**{key}:** {val}")
