import pdfplumber
import streamlit as st

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def summarize_proposal(text: str):
    structure_summary = {
        "Tower": [],
        "Antennas": [],
        "RRU": [],
        "MW": [],
        "Cabinet/Power": []
    }
    environment_summary = []

    # --- Structure parsing ---
    for line in text.splitlines():
        l = line.lower()
        if "tower" in l or "structure height" in l:
            structure_summary["Tower"].append(line.strip())
        elif "antenna" in l:
            structure_summary["Antennas"].append(line.strip())
        elif "rru" in l or "rrh" in l:
            structure_summary["RRU"].append(line.strip())
        elif "mw" in l or "microwave" in l:
            structure_summary["MW"].append(line.strip())
        elif "cabinet" in l or "power" in l or "rectifier" in l or "breaker" in l:
            structure_summary["Cabinet/Power"].append(line.strip())

        # --- Environment parsing ---
        if any(word in l for word in ["road", "access", "traffic", "lifting", "site accessibility", "workers", "installation"]):
            environment_summary.append(line.strip())

    # --- Format summaries ---
    formatted_structure = {
        section: "\n".join([f"- {item}" for item in items]) if items else "No details found"
        for section, items in structure_summary.items()
    }
    formatted_environment = "\n".join([f"- {item}" for item in environment_summary]) if environment_summary else "No environment info found"

    return formatted_structure, formatted_environment


# --- Streamlit UI ---
st.title("📑 Technical Proposal Summarizer")

uploaded_file = st.file_uploader("Upload your Technical Proposal PDF", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")

    doc_text = extract_text_from_pdf(uploaded_file)
    structure, environment = summarize_proposal(doc_text)

    st.subheader("1️⃣ Structure Technical Info")
    for section, details in structure.items():
        st.markdown(f"**{section}**\n{details}")

    st.subheader("2️⃣ Aerial / Environment Situation")
    st.markdown(environment)
