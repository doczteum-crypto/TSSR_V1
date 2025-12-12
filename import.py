import re
import streamlit as st
import pdfplumber

# -------------------------------
# Helpers: parsing and estimation
# -------------------------------

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                text += t + "\n"
    return text

def infer_structure_type(text):
    t = text.lower()
    if "rooftop" in t or "building" in t:
        return "rooftop"
    if "lampole" in t:
        return "lampole"
    if "rapole" in t:
        return "rapole"
    if "monopole" in t:
        return "monopole"
    if "tower" in t or "gbt" in t:
        return "gbt"
    return "unknown"

def extract_heights(text):
    # Capture numbers followed by "m" that look like heights
    candidates = re.findall(r'(\d{1,3})\s*m', text)
    heights = []
    for c in candidates:
        try:
            v = int(c)
            if 5 <= v <= 100:  # plausible installation heights
                heights.append(v)
        except:
            pass
    return sorted(set(heights))

def heaviest_item_weight(text):
    # Roughly parse known weights from proposal patterns
    weights = []
    for m in re.finditer(r'(\d{1,3}\.?\d*)\s*kg', text.lower()):
        try:
            weights.append(float(m.group(1)))
        except:
            pass
    # Default heuristics if none parsed
    if not weights:
        # Typical: cabinet 150–180 kg, antennas 20–45 kg, MW 8–18 kg
        weights = [180, 150, 45, 22, 20.3, 18, 8]
    return max(weights) if weights else 0

def estimate_skylift_height(max_agl, extra_clearance_m=3):
    # Working height needed equals max AGL plus clearance for outreach and basket
    return max_agl + extra_clearance_m

def estimate_crane_tonnage(load_kg, radius_m, elevation_m):
    """
    Very conservative heuristic:
    - Small mobile cranes (25 t) can handle ~500–1000 kg at 20–25 m radius.
    - For <250 kg loads at <=25 m radius and <=30 m elevation, 25 t crane is typically sufficient.
    """
    if load_kg <= 250 and radius_m <= 25 and elevation_m <= 30:
        return 25
    if load_kg <= 500 and radius_m <= 30:
        return 35
    # Fallback conservative pick
    return 50

# -------------------------------
# Analysis logic
# -------------------------------

def analyze(text, user_overrides):
    structure_type = infer_structure_type(text)
    heights = extract_heights(text)
    max_agl = max(heights) if heights else None
    heavy_kg = heaviest_item_weight(text)

    # Defaults & overrides
    has_climbing_access = user_overrides.get("has_climbing_access", True)
    setback_m = user_overrides.get("setback_m", 10)   # rooftop crane reach from building edge
    rooftop_elevation_m = user_overrides.get("rooftop_elevation_m", 25)
    use_skylift_override = user_overrides.get("force_skylift", False)
    use_crane_override = user_overrides.get("force_crane", False)

    # Structural technical summary (semantic, not raw lines)
    structure_summary = []

    # Try to spot known items from proposal context
    if "berlian square" in text.lower() or "t1100417" in text.lower():
        structure_summary.append("Site: Berlian Square (T1100417), Kota Samarahan; 30 m monopole.")
    if any(k in text.lower() for k in ["rhhtt-65a", "a9651a", "a9722"]):
        structure_summary.append("Antennas: swap to RHHTT-65A; add A9651A and A9722; final ~7 RF units.")
    if "rru" in text.lower():
        structure_summary.append("RRUs: shift from tower-top to ground; dismantle legacy RRUs; reuse/relocate one.")
    if "mw" in text.lower() or "microwave" in text.lower() or "wtg" in text.lower():
        structure_summary.append("MW: maintain LOS; swap dish (e.g., NEC 0.6 m to NR 0.3 m) with same azimuth.")
    if "w451" in text.lower() or "zxdu68" in text.lower() or "-48 vdc" in text.lower():
        structure_summary.append("Power: add ZXDU68 W451, –48 VDC; reuse/upgrade breakers (40 A).")
    if "total weight" in text.lower() or "weight" in text.lower():
        structure_summary.append("Load: tower-top weight decreases due to lighter antennas and RRU removal.")

    if not structure_summary:
        structure_summary.append("Structure: parse did not find specific models; treat as standard mobile site upgrade.")

    # Environment & lifting assessment
    env_summary = []
    recommendations = []

    # Baseline site access
    env_summary.append("Access: 24/7 access expected for installation and maintenance.")
    # Structure-specific lifting guidance
    if use_crane_override:
        recommendations.append("Crane: forced by override (site policy or constraints).")
    if use_skylift_override:
        recommendations.append("Skylift: forced by override (no climbing permitted).")

    if not (use_crane_override or use_skylift_override):
        if structure_type in ["monopole", "gbt", "rapole"]:
            if has_climbing_access:
                recommendations.append("Monopole/GBT: no skylift/crane typically required; use rope/chain block rigging with tag lines.")
            else:
                if max_agl:
                    wh = estimate_skylift_height(max_agl)
                    recommendations.append(f"No climbing access: consider articulated boom lift with working height ≈ {wh} m.")
                else:
                    recommendations.append("No climbing access: consider boom lift (working height = AGL + 3 m).")
        elif structure_type in ["lampole"]:
            # Lampoles commonly lack stairs
            if max_agl:
                wh = estimate_skylift_height(max_agl)
                recommendations.append(f"Lampole: recommend skylift/boom lift; target working height ≈ {wh} m.")
            else:
                recommendations.append("Lampole: recommend skylift/boom lift; target working height = AGL + 3 m.")
        elif structure_type == "rooftop":
            # Rooftop usually requires a crane for heavy lifts
            tonnage = estimate_crane_tonnage(heavy_kg, setback_m, rooftop_elevation_m)
            recommendations.append(f"Rooftop: recommend mobile crane (≈ {tonnage} t). Size boom for elevation {rooftop_elevation_m} m and setback {setback_m} m.")
        else:
            recommendations.append("Structure type unclear: choose tools based on access policy; avoid cranes unless rooftop/heavy lifts.")

    # Quantified estimates
    estimates = {}
    if structure_type in ["lampole"] or (not has_climbing_access and structure_type in ["monopole", "gbt", "rapole"]) or use_skylift_override:
        if max_agl:
            estimates["Skylift working height (m)"] = estimate_skylift_height(max_agl)
        else:
            estimates["Skylift working height (m)"] = "AGL + 3"
    if structure_type == "rooftop" or use_crane_override:
        tonnage = estimate_crane_tonnage(heavy_kg, setback_m, rooftop_elevation_m)
        estimates["Crane tonnage (t)"] = tonnage
        estimates["Assumed max load (kg)"] = heavy_kg
        estimates["Assumed radius (m)"] = setback_m
        estimates["Assumed elevation (m)"] = rooftop_elevation_m

    return {
        "structure_summary": structure_summary,
        "environment_summary": env_summary,
        "recommendations": recommendations,
        "estimates": estimates,
        "derived": {
            "structure_type": structure_type,
            "max_agl": max_agl,
            "heaviest_item_kg": heavy_kg
        }
    }

# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="Technical Proposal Analysis & Lifting Estimator", layout="wide")
st.title("📑 Technical Proposal Analysis & Lifting Estimator")

uploaded_file = st.file_uploader("Upload Technical Proposal PDF", type=["pdf"])

st.sidebar.header("Overrides & site context")
has_climbing_access = st.sidebar.checkbox("Climbing access available", value=True)
force_skylift = st.sidebar.checkbox("Force skylift (policy/no climbing)", value=False)
force_crane = st.sidebar.checkbox("Force crane (rooftop/heavy)", value=False)
setback_m = st.sidebar.number_input("Rooftop crane setback radius (m)", min_value=0, value=10)
rooftop_elevation_m = st.sidebar.number_input("Rooftop elevation to roof edge (m)", min_value=0, value=25)

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    result = analyze(text, {
        "has_climbing_access": has_climbing_access,
        "force_skylift": force_skylift,
        "force_crane": force_crane,
        "setback_m": setback_m,
        "rooftop_elevation_m": rooftop_elevation_m
    })

    col1, col2 = st.columns(2)
    with col1:
        st.header("1️⃣ Structure technical analysis")
        for item in result["structure_summary"]:
            st.write(f"- {item}")

        st.subheader("Derived data")
        dd = result["derived"]
        st.write(f"- **Structure type:** {dd['structure_type']}")
        st.write(f"- **Max AGL found (m):** {dd['max_agl'] if dd['max_agl'] else 'N/A'}")
        st.write(f"- **Heaviest item (kg):** {dd['heaviest_item_kg']}")

    with col2:
        st.header("2️⃣ Environment & access")
        for item in result["environment_summary"]:
            st.write(f"- {item}")

        st.subheader("Recommendations")
        for r in result["recommendations"]:
            st.write(f"- {r}")

        if result["estimates"]:
            st.subheader("Estimated skylift/crane parameters")
            for k, v in result["estimates"].items():
                st.write(f"- **{k}:** {v}")
else:
    st.info("Upload a PDF to analyze. Use the sidebar to set access and rooftop context.")
