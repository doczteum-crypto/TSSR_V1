import re

def summarize_proposal(text: str):
    summary = {"Structure Technical Info": [], "Aerial/Environment Situation": []}

    # --- 1. Structure Technical Info ---
    structure_keywords = [
        "tower", "antenna", "RRU", "MW", "cabinet", "rectifier", "power", "height",
        "dimension", "weight", "azimuth", "feeder", "cable", "breaker"
    ]
    for line in text.splitlines():
        if any(word.lower() in line.lower() for word in structure_keywords):
            summary["Structure Technical Info"].append(line.strip())

    # --- 2. Aerial/Environment Situation ---
    environment_keywords = [
        "road", "access", "traffic", "premise", "lifting", "tools", "site accessibility",
        "movement", "workers", "installation", "commissioning"
    ]
    for line in text.splitlines():
        if any(word.lower() in line.lower() for word in environment_keywords):
            summary["Aerial/Environment Situation"].append(line.strip())

    # --- Format Output ---
    print("\n=== SUMMARY REPORT ===\n")
    print("1. STRUCTURE TECHNICAL INFO")
    for item in summary["Structure Technical Info"]:
        print(f"- {item}")

    print("\n2. AERIAL / ENVIRONMENT SITUATION")
    for item in summary["Aerial/Environment Situation"]:
        print(f"- {item}")

    return summary


# Example usage:
if __name__ == "__main__":
    # Replace with actual text extraction from PDF
    with open("proposal_text.txt", "r", encoding="utf-8") as f:
        doc_text = f.read()

    summarize_proposal(doc_text)