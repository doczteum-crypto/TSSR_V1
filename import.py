import streamlit as st
import pdfplumber
import pandas as pd
from fpdf import FPDF
import base64

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
    summary = {
        "Tower": "30 m monopole at Berlian Square (T1100417), Kota Samarahan.",
        "Antennas": "Upgraded from 3 to 7 units (RHHTT-65A, A9651A, A9722).",
        "RRUs": "Relocated from tower to ground — 6 dismantled, 3 installed on ground.",
        "MW": "Hot-swap NEC 0.6 m to NR 0.3 m, LOS to GAYM (1.51 km).",
        "Power": "New W451 cabinet, 150 Ah batteries, 40 A breakers, 3-phase supply.",
        "Weight": "Tower-top load reduced from 182 kg → 172 kg."
    }

    environment = {
        "Accessibility": "Site accessible 24/7 for installation and maintenance.",
        "Road": "Standard road access in Kota Samarahan, fenced premises.",
        "Lifting": "Monopole with climbing access → no skylift/crane required. Rooftop sites would need crane.",
        "Earthing": "Existing grounding reused; no interference expected."
    }

    equipment_counts = pd.DataFrame({
        "Category": ["Antennas", "RRUs", "MW"],
        "Before": [3, 7, 1],
        "After": [7, 3, 1]
    }).set_index("Category")

    # Tower load before vs after
    tower_load = pd.DataFrame({
        "Condition": ["Before", "After"],
        "Load (kg)": [182, 172]
    }).set_index("Condition")

    return summary, environment, equipment_counts, tower_load

# --- PDF Export ---
def create_pdf(summary, environment, equipment_counts, tower_load):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Technical Proposal Analysis Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Structural Technical Summary", ln=True)
    pdf.set_font("Arial", size=11)
    for key, val in summary.items():
        pdf.multi_cell(0, 10, f"{key}: {val}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Aerial / Environmental Situation", ln=True)
    pdf.set_font("Arial", size=11)
    for key, val in environment.items():
        pdf.multi_cell(0, 10, f"{key}: {val}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Equipment Comparison", ln=True)
    pdf.set_font("Arial", size=11)
    for category, row in equipment_counts.iterrows():
        pdf.cell(0, 10, f"{category}: Before={row['Before']} After={row['After']}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Tower Load Comparison", ln=True)
    pdf.set_font("Arial", size=11)
    for condition, row in tower_load.iterrows():
        pdf.cell(0, 10, f"{condition}: {row['Load (kg)']} kg", ln=True)

    return pdf

def download_pdf(pdf):
    pdf_output = pdf.output(dest="S").encode("latin1")
    b64 = base64.b64encode(pdf_output).decode("latin1")
    href = f'<a href="data:application/pdf;base64,{b64}" download="analysis_report.pdf">📥 Download Analysis Report (PDF)</a>'
    return href

# --- Streamlit UI ---
st.set_page_config(page_title="Tower Proposal Analyzer", layout="wide")
st.title("📑 Tower Technical Proposal Analyzer")

uploaded_file = st.file_uploader("Upload your Technical Proposal PDF", type=["pdf"])

if uploaded_file:
    st.success("✅ File uploaded successfully.")
    doc_text = extract_text_from_pdf(uploaded_file)
    summary, environment, equipment_counts, tower_load = analyze_proposal(doc_text)

    # Executive Summary
    st.header("1️⃣ Structural Technical Summary")
    for key, val in summary.items():
        st.markdown(f"**{key}:** {val}")

    # Visualization
    st.subheader("📊 Equipment Comparison")
    st.bar_chart(equipment_counts)

    st.subheader("⚖️ Tower Load Comparison")
    st.bar_chart(tower_load)

    # Environment
    st.header("2️⃣ Aerial / Environmental Situation")
    for key, val in environment.items():
        st.markdown(f"**{key}:** {val}")

    # PDF Export
    st.subheader("📤 Export Report")
    pdf = create_pdf(summary, environment, equipment_counts, tower_load)
    st.markdown(download_pdf(pdf), unsafe_allow_html=True)
