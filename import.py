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

# --- Analysis function ---
def analyze_proposal(text: str):
    # Structural analysis
    structure = {
        "Tower & Site": [],
        "Antennas": [],
        "RRUs": [],
        "Microwave": [],
        "Cabinets & Power": [],
        "Weight Impact": []
    }

    # Environment analysis
    environment = {
        "Accessibility": [],
        "Road & Premise": [],
        "Traffic & Lifting Tools": [],
        "Environmental Impact": []
    }

    # Simple keyword-based grouping
    for line in text.splitlines():
        l = line.lower()
        if "tower" in l or "structure height" in l or "site name" in l:
            structure["Tower & Site"].append(line.strip())
        elif "antenna" in l:
            structure["Antennas"].append(line.strip())
        elif "rru" in l or "rrh" in l:
            structure["RRUs"].append(line.strip())
        elif "mw" in l or "microwave" in l:
            structure["Microwave"].append(line.strip())
        elif "cabinet" in l or "power" in l or "rectifier" in l or "breaker" in l:
            structure["Cabinets & Power"].append(line.strip())
        elif "weight" in l or "total weight" in l:
            structure["Weight Impact"].append(line.strip())

        # Environment
        if "access" in l or "site accessibility" in l:
            environment["Accessibility"].append(line.strip())
        elif "road" in l or "premise" in l:
            environment["Road & Premise"].append(line.strip())
        elif "traffic" in l or "lifting" in l or "ladder" in l or "boom" in l:
            environment["Traffic & Lifting Tools"].append(line.strip())
        elif "earthing" in l or "interfere" in l or "environment" in l:
            environment["Environmental Impact"].append(line.strip())

    return structure, environment

# --- Streamlit UI ---
st.title("📑 Technical Proposal Analyzer")

uploaded_file = st.file_uploader("Upload your Technical Proposal PDF", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")

    # Extract text
    doc_text = extract_text_from_pdf(uploaded_file)

    # Analyze
    structure, environment = analyze_proposal(doc_text)

    # Display results
    st.header("1️⃣ Structural Technical Analysis")
    for section, items in structure.items():
        st.subheader(section)
        if items:
            for item in items:
                st.write(f"- {item}")
        else:
            st.write("No details found.")

    st.header("2️⃣ Aerial / Environmental Situation")
    for section, items in environment.items():
        st.subheader(section)
        if items:
            for item in items:
                st.write(f"- {item}")
        else:
            st.write("No details found.")
