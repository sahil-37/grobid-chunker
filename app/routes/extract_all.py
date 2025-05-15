from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import json
from datetime import datetime

from app.grobid_client import send_to_grobid
from app.extractors.methods_extractor import extract_methods_with_subsections
from app.extractors.section_extractor import extract_structured_sections

router = APIRouter(prefix="/extract-all", tags=["Extract All"])

def flatten_sections_to_content(section_obj: dict) -> dict:
    """Flatten nested section dict into a content list with subheadings inline."""
    if "sections" in section_obj:
        flattened = []
        subheadings = []
        for subhead, paras in section_obj["sections"].items():
            flattened.append(f"## {subhead}")
            flattened.extend(paras)
            subheadings.append(subhead)
        return {
            "heading": section_obj.get("heading", ""),
            "content": flattened,
            "subheadings": subheadings
        }
    return section_obj  # If already flat


@router.post("/")
async def extract_all_sections(files: List[UploadFile] = File(...)):
    responses = []
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    for up in files:
        pdf_bytes = await up.read()
        xml_str = send_to_grobid(pdf_bytes)

        if not xml_str:
            responses.append({"filename": up.filename, "error": "Failed to parse with GROBID"})
            continue

        full_sections = extract_structured_sections(xml_str)
        sections = {
            "title": full_sections.get("title", {}),
            "abstract": full_sections.get("abstract", {}),
            "results_discussion": flatten_sections_to_content(
                full_sections.get("results_discussion", {})
            )
        }

        # Step 3: Extract methods
        methods_struct, score, methods_heading, _, _ = extract_methods_with_subsections(xml_str)

        # Step 4: Flatten methods
        flattened_methods = []
        for subhead, paras in methods_struct.items():
            flattened_methods.append(f"## {subhead}")
            flattened_methods.extend(paras)

        sections["methods"] = {
            "heading": methods_heading or "Methods",
            "similarity_score": round(score, 3),
            "content": flattened_methods
        }

        # Step 5: Save outputs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_safe = up.filename.replace(" ", "_").replace("/", "_")

        # Save .json
        json_path = os.path.join(output_dir, f"{filename_safe}_{timestamp}_all.json")
        with open(json_path, "w") as f:
            json.dump(sections, f, indent=2)

        # Save .txt
        txt_path = os.path.join(output_dir, f"{filename_safe}_{timestamp}_all.txt")
        with open(txt_path, "w") as f:
            for sec_key, sec in sections.items():
                f.write(f"### {sec.get('heading', sec_key).upper()}\n\n")
                if "content" in sec:
                    for para in sec["content"]:
                        f.write(para + "\n\n")

        # Step 6: Response payload
        responses.append({
            "filename": up.filename,
            "tei_xml": xml_str,
            "extracted_sections": sections
        })

    return responses
