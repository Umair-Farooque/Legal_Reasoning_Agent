import json
import re

# Load raw JSON
with open("pdf_data.json", "r", encoding="utf-8") as f:
    raw_docs = json.load(f)

structured_docs = []

# Regex patterns to detect hierarchy
part_pattern = re.compile(r"PART\s+([IVXLC]+)[.—\-]*\s*(.*)", re.IGNORECASE)
section_pattern = re.compile(r"(\d+)\.\s*(.*)")
subsection_pattern = re.compile(r"\(([a-zA-Z0-9]+)\)\s*(.*)")
page_pattern = re.compile(r"Page\s*\d+\s*of\s*\d+", re.IGNORECASE)

for doc in raw_docs:
    file_name = doc["file_name"]
    text = doc["text"]

    # Remove repeated page headers/footers
    text = re.sub(page_pattern, "", text)
    # Normalize whitespace
    text = re.sub(r"\n+", "\n", text).strip()

    current_doc = None
    current_part = None
    current_section = None
    current_subsection = None
    current_heading = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect PART
        part_match = part_pattern.match(line)
        if part_match:
            current_part = part_match.group(0)
            continue

        # Detect SECTION
        section_match = section_pattern.match(line)
        if section_match:
            # Save previous section if exists
            if current_doc:
                structured_docs.append(current_doc)

            current_section = section_match.group(1)
            current_heading = section_match.group(2).strip()
            current_subsection = None

            current_doc = {
                "file_name": file_name,
                "part": current_part,
                "section": current_section,
                "subsection": None,
                "heading": current_heading,
                "content": ""
            }
            continue

        # Detect SUBSECTION
        subsection_match = subsection_pattern.match(line)
        if subsection_match:
            # Save previous section/subsection if exists
            if current_doc:
                structured_docs.append(current_doc)

            current_subsection = subsection_match.group(1)
            sub_content = subsection_match.group(2).strip()

            current_doc = {
                "file_name": file_name,
                "part": current_part,
                "section": current_section,
                "subsection": current_subsection,
                "heading": None,
                "content": sub_content
            }
            continue

        # Otherwise → append content to the current section/subsection
        if current_doc:
            current_doc["content"] += " " + line

    # Save last open section/subsection
    if current_doc:
        structured_docs.append(current_doc)

# Clean extra whitespace in content
for doc in structured_docs:
    doc["content"] = re.sub(r"\s+", " ", doc["content"]).strip()

# Save structured JSON
with open("Pakistan_Laws_Structured.json", "w", encoding="utf-8") as f:
    json.dump(structured_docs, f, ensure_ascii=False, indent=2)

print(f"Structured {len(structured_docs)} sections/subsections from {len(raw_docs)} documents.")
