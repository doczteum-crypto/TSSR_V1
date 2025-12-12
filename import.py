import streamlit as st
import pdfplumber
import matplotlib.pyplot as plt

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

    # Equipment counts for visualization
    equipment_counts = {
        "Antennas": {"Before": 3, "After": 7},
        "RRUs": {"Before": 7, "After": 3},
        "MW": {"Before": 1, "After": 1}
    }

    return summary, environment, equipment_counts

# --- Visualization ---
def plot_equipment_counts(equipment_counts):
    fig, ax = plt.subplots()
    categories = list(equipment_counts.keys())
    before = [equipment_counts[c]["Before"] for c in categories]
    after = [equipment_counts[c]["After"] for c in categories]

    x = range(len(categories))
    ax.bar([i - 0.2 for i in x], before, width=0.4, label="Before", color="skyblue")
    ax.bar([i + 0.2 for i in x], after, width=0.4, label="After", color="orange")

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Count")
    ax.set_title("Equipment Before vs After Upgrade")
    ax.legend()
    st
