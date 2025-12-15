import os
import docx
import PyPDF2
from transformers import pipeline

# Initialize summarizer (you can swap model for domain-specific one)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_sections(text):
    """
    Simple keyword-based sectioning.
    You can replace with regex or semantic chunking.
    """
    sections = {
        "structure_info": [],
        "aerial_environment": []
    }
    lines = text.split("\n")
    for line in lines:
        lower = line.lower()
        if any(k in lower for k in ["tower", "antenna", "rru", "cabinet", "power", "mw"]):
            sections["structure_info"].append(line)
        if any(k in lower for k in ["road", "traffic", "access", "premise", "lifting", "crane", "tools"]):
            sections["aerial_environment"].append(line)
    return sections

def summarize_section(section_text):
    if not section_text.strip():
        return "No relevant information found."
    # Limit length for summarizer
    chunks = [section_text[i:i+1000] for i in range(0, len(section_text), 1000)]
    summaries = []
    for chunk in chunks:
        summaries.append(summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]['summary_text'])
    return " ".join(summaries)

def analyze_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        text = read_txt(file_path)
    elif ext == ".docx":
        text = read_docx(file_path)
    elif ext == ".pdf":
        text = read_pdf(file_path)
    else:
        raise ValueError("Unsupported file format")

    sections = extract_sections(text)
    results = {
        "Structure Technical Info Summary": summarize_section("\n".join(sections["structure_info"])),
        "Aerial/Environment Situation Summary": summarize_section("\n".join(sections["aerial_environment"]))
    }
    return results

# Example usage
if __name__ == "__main__":
    file_path = "proposal.pdf"  # replace with your file
    summaries = analyze_document(file_path)
    for key, val in summaries.items():
        print(f"\n{key}:\n{val}\n")